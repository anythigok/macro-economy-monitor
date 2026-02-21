import json
import yfinance as yf
import pandas as pd
from datetime import datetime
import os
import requests
import matplotlib.pyplot as plt
from dotenv import load_dotenv # 追加

# .envファイルから環境変数を読み込む
load_dotenv()

PORTFOLIO_FILE = 'portfolio_data.json'
HISTORY_FILE = 'valuation_history.csv'
IMAGE_FILE = 'portfolio_summary.png'

# コードへの直書きを廃止し、環境変数から安全に取得する
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')

if not DISCORD_WEBHOOK_URL:
    print("[警告] Webhook URLが設定されていません。Discord通知はスキップされます。")

# セクターマッピング
SECTOR_MAP = {
    "2559.T": "Index", "1655.T": "Index", "1321.T": "Index",
    "1540.T": "Alternative", "BTC-JPY": "Alternative", "1343.T": "Alternative",
    "7203.T": "Auto/Mfg", "7267.T": "Auto/Mfg", "6902.T": "Auto/Mfg", "6594.T": "Auto/Mfg", "6367.T": "Auto/Mfg",
    "8306.T": "Financials", "8316.T": "Financials", "8411.T": "Financials", "8766.T": "Financials",
    "8058.T": "Trading", "8001.T": "Trading", "8031.T": "Trading", "8053.T": "Trading",
    "8035.T": "Semi/Precision", "6861.T": "Semi/Precision", "6920.T": "Semi/Precision", "7741.T": "Semi/Precision",
    "6758.T": "Tech/Telecom", "9432.T": "Tech/Telecom", "9433.T": "Tech/Telecom", "9434.T": "Tech/Telecom", "7974.T": "Tech/Telecom", "6098.T": "Tech/Telecom",
    "9983.T": "Other/Retail", "4063.T": "Other/Retail", "6501.T": "Other/Retail", "4568.T": "Other/Retail", "4502.T": "Other/Retail", "3382.T": "Other/Retail", "6503.T": "Other/Retail"
}

# ▼新規追加：企業名・商品名の日本語マッピング辞書
NAME_MAP = {
    "2559.T": "ｵﾙｶﾝ", "1655.T": "S&P500", "1321.T": "日経平均",
    "1540.T": "金ETF", "BTC-JPY": "ﾋﾞｯﾄｺｲﾝ", "1343.T": "東証REIT",
    "7203.T": "トヨタ", "7267.T": "ホンダ", "6902.T": "デンソー", "6594.T": "ニデック", "6367.T": "ダイキン",
    "8306.T": "三菱UFJ", "8316.T": "三井住友", "8411.T": "みずほ", "8766.T": "東京海上",
    "8058.T": "三菱商事", "8001.T": "伊藤忠", "8031.T": "三井物産", "8053.T": "住友商事",
    "8035.T": "東エレク", "6861.T": "キーエンス", "6920.T": "レーザーT", "7741.T": "HOYA",
    "6758.T": "ソニーG", "9432.T": "NTT", "9433.T": "KDDI", "9434.T": "ソフトバンク", "7974.T": "任天堂", "6098.T": "リクルート",
    "9983.T": "ファストリ", "4063.T": "信越化学", "6501.T": "日立", "4568.T": "第一三共", "4502.T": "武田薬品", "3382.T": "セブン&アイ", "6503.T": "三菱電機"
}

def send_discord_notification(message, image_path=None):
    if not DISCORD_WEBHOOK_URL:
        return
    try:
        if image_path and os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                response = requests.post(
                    DISCORD_WEBHOOK_URL, 
                    data={'content': message}, 
                    files={'file': (os.path.basename(image_path), f, 'image/png')}
                )
        else:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(DISCORD_WEBHOOK_URL, headers=headers, json={'content': message})
            
        if response.status_code not in [200, 204]:
            print(f"[エラー] 通知失敗: HTTPステータス {response.status_code}")
    except Exception as e:
        print(f"[エラー] 通信障害が発生しました: {e}")

def run_daily_valuation():
    if not os.path.exists(PORTFOLIO_FILE):
        return
        
    with open(PORTFOLIO_FILE, 'r') as f:
        data = json.load(f)
        
    cash = data['cash']
    holdings = data['holdings']
    
    sector_values = {}
    details_by_sector = {}
    total_stock_value = 0
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    for ticker, info in holdings.items():
        shares = info['shares']
        avg_price = info['avg_price']
        sector = SECTOR_MAP.get(ticker, "Unknown")
        
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")
        if hist.empty:
            latest_price = avg_price
        else:
            latest_price = hist['Close'].iloc[-1]
            
        current_value = shares * latest_price
        total_stock_value += current_value
        sector_values[sector] = sector_values.get(sector, 0) + current_value
        
        # ▼変更：ティッカーを日本語名に変換して出力
        display_name = NAME_MAP.get(ticker, ticker)
        pl_pct = ((latest_price / avg_price) - 1) * 100
        line = f"`{display_name}`: {pl_pct:+.1f}%"
        
        if sector not in details_by_sector:
            details_by_sector[sector] = []
        details_by_sector[sector].append(line)
        
    total_assets = cash + total_stock_value
    
    # グラフ生成
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.pie(list(sector_values.values()), labels=list(sector_values.keys()), autopct='%1.1f%%', startangle=140, colors=plt.cm.tab20.colors)
    plt.title('Portfolio Allocation by Sector', fontsize=14, fontweight='bold')
    
    plt.subplot(1, 2, 2)
    if os.path.exists(HISTORY_FILE):
        df_hist = pd.read_csv(HISTORY_FILE).tail(14)
        plt.plot(df_hist['Date'], df_hist['TotalAssets'], marker='o', color='#1f77b4', linewidth=2)
        plt.title('Total Assets Trend (JPY)', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.ticklabel_format(style='plain', axis='y')
        
    plt.tight_layout()
    plt.savefig(IMAGE_FILE, dpi=150)
    plt.close()
    
    # メッセージ組み立て
    report_lines = [
        f"📊 **日次ポートフォリオ評価レポート ({now_str})**", 
        f"💰 **総資産額: {total_assets:,.0f}円**", 
        "---------------------------------"
    ]
    for sector, lines in details_by_sector.items():
        report_lines.append(f"**【{sector}】**")
        report_lines.append(" | ".join(lines))
        
    notification_message = "\n".join(report_lines)
    send_discord_notification(notification_message, IMAGE_FILE)
    
    # CSV記録
    date_str = datetime.now().strftime('%Y-%m-%d')
    new_record = pd.DataFrame([{'Date': date_str, 'Cash': cash, 'StockValue': total_stock_value, 'TotalAssets': total_assets}])
    if os.path.exists(HISTORY_FILE):
        new_record.to_csv(HISTORY_FILE, mode='a', header=False, index=False)
    else:
        new_record.to_csv(HISTORY_FILE, mode='w', header=True, index=False)

if __name__ == "__main__":
    run_daily_valuation()
