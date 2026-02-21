# 📊 Autonomous Macro-Economy Monitor Pipeline

日本の時価総額トップ30企業および主要インデックスの資金循環（セクターローテーション）を自律的に監視・視覚化する完全自動化データパイプライン。

## 🎯 目的 (Objective)
就職活動および高度なキャリア戦略における企業分析において、マクロ経済（金利・為替・政治動向）の変動ファクトをリアルタイムで収集・可視化し、データドリブンな意思決定を行うための監視ダッシュボード基盤。

## ⚙️ システムアーキテクチャ (Architecture)
- **Infrastructure**: Ubuntu Server (Core i5-6th / 16GB)
- **Containerization**: Docker (Jupyter Data Science Environment)
- **Automation**: Cron (平日16:00 バッチ自動実行)
- **Core Logic**: Python 3 (yfinance, pandas, matplotlib)
- **Notification**: Discord Webhook (テキストレポート + 生成画像)

## 💼 監視ポートフォリオ構成 (Portfolio Allocation)
仮想資金100万円をベースに、日本の産業を網羅する36銘柄の変動を監視。
- **Core Index & Alternative (70%)**: オルカン, S&P500, 日経225, 金ETF, 東証REIT, BTC-JPY
- **Japan Top 30 (30%)**: トヨタ, 三菱UFJ, ソニーG, キーエンス, NTT等、日本の全産業セクター

## 🚀 コア機能 (Features)
1. **完全無人自律稼働**: サーバー上で独立動作し、日本市場の大引け後（JST 16:00）に評価プロセスを自動発火。
2. **証券コードの自動翻訳**: ティッカーシンボル（例: `7203.T`）を直感的な企業名（`トヨタ`）およびセクター（`Auto/Mfg`）へ動的にマッピング変換。
3. **視覚的インサイトの動的生成**: matplotlibを用い、セクター別アロケーション（円グラフ）と総資産推移（折れ線グラフ）を生成し、Discordへ画像データをダイレクト配信。
