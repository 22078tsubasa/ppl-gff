# 佐々総合病院 競合分析（消化器外科） - 公開手順

## 1. 事前準備
- このフォルダ配下に以下があることを確認
  - `streamlit_report.py`
  - `dominant_territory_sasa_car30_usersTop60_allLegend.png`
  - `dominant_territory_sasa_car30_sasaPlus5_other_allLegend.png`
  - `sasa_car30_usersTop60_town_med_matrix_上位3_町丁目60.png`
  - `sasa_car30_usersTop60_town_med_heatmap_上位10_町丁目60.png`
  - 各CSVファイル
- ルートの `requirements.txt` に `streamlit` と `pandas` を追加済み

## 2. GitHub に push
1. このプロジェクトを GitHub リポジトリに push
2. `JADECOM/sasa_digestive/streamlit_report.py` が repo 上にある状態にする

## 3. Streamlit Community Cloud で公開
1. https://share.streamlit.io/ に GitHub アカウントでログイン
2. `New app` を押す
3. 設定
   - Repository: このプロジェクトのリポジトリ
   - Branch: `main`（使っているブランチ）
   - Main file path: `JADECOM/sasa_digestive/streamlit_report.py`
4. `Deploy` を押す

### 閲覧パスワード
- このアプリは閲覧時にパスワード入力が必要（デフォルト: `shibaura2026`）
- 変更したい場合は Streamlit Cloud の `Settings > Secrets` で設定

```toml
APP_PASSWORD = "任意のパスワード"
```

## 4. 先方共有
- デプロイ後に発行される `https://xxxx.streamlit.app` を先方へ送る
- このURLは `localhost` と違って、先方PCからも見られる

## 5. 更新時
- 画像やCSV、`streamlit_report.py` と画像/CSV を更新して GitHub に push
- 同じ URL で自動反映（反映に少し時間がかかることあり）

## 補足
- Streamlit Cloud がスリープしても、アクセス時に自動で再起動される
- 完全に常時稼働が必要なら、Render / Railway / VPS などの常時ホスティングも選択可
