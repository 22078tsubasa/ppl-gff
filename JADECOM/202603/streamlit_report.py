from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent

FILES = {
    "全体勢力図": BASE_DIR / "dominant_territory_tsuge_30km.png",
    "都祁+上位5勢力図": BASE_DIR / "dominant_territory_tsuge_30km_tsuge_plus5.png",
    "Top3マトリクス図": BASE_DIR / "town_med_matrix_top3.png",
    "Top10ヒートマップ図": BASE_DIR / "town_med_heatmap_top10.png",
    "グラフ": BASE_DIR / "town_med_graph_top60.png",
}

CSV_FILES = {
    "全体勢力図データ": BASE_DIR / "dominant_territory_tsuge_30km_result.csv",
    "都祁+上位5勢力図データ": BASE_DIR / "dominant_territory_tsuge_30km_tsuge_plus5_result.csv",
    "Top3マトリクスCSV": BASE_DIR / "town_med_matrix_top3_only.csv",
    "Top10マトリクスCSV": BASE_DIR / "town_med_matrix_top10.csv",
    "施設ランキングCSV": BASE_DIR / "facility_rank_summary.csv",
}


def file_ok(path: Path) -> bool:
    return path.exists() and path.is_file()


def read_csv_safely(path: Path) -> pd.DataFrame:
    if not file_ok(path):
        return pd.DataFrame()
    return pd.read_csv(path)


def build_zip_bytes() -> bytes:
    memory = io.BytesIO()
    with zipfile.ZipFile(memory, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for _, p in FILES.items():
            if file_ok(p):
                zf.write(p, arcname=p.name)
        for _, p in CSV_FILES.items():
            if file_ok(p):
                zf.write(p, arcname=p.name)
    memory.seek(0)
    return memory.read()


st.set_page_config(page_title="都祁診療所競合分析", layout="wide")
st.title("都祁診療所競合分析")
st.caption("全体勢力図 / 都祁+上位5勢力図 / 上位3マトリクス / 上位10ヒートマップ")
st.markdown("### 表紙")
st.markdown("## 都祁診療所競合分析")
st.markdown("---")

missing = [name for name, p in {**FILES, **CSV_FILES}.items() if not file_ok(p)]
if missing:
    st.warning("不足ファイル: " + " / ".join(missing))

col_a, col_b = st.columns(2)
with col_a:
    st.subheader("勢力図")
    st.image(str(FILES["全体勢力図"]), caption="全体勢力図", use_container_width=True)
    st.image(str(FILES["都祁+上位5勢力図"]), caption="都祁+上位5勢力図（再計算）", use_container_width=True)
with col_b:
    st.subheader("ヒートマップ")
    st.image(str(FILES["Top3マトリクス図"]), caption="Top3マトリクス", use_container_width=True)
    st.image(str(FILES["Top10ヒートマップ図"]), caption="Top10ヒートマップ", use_container_width=True)

st.subheader("グラフ")
st.image(str(FILES["グラフ"]), caption="10km以内・近い順上位60町丁目 × 医療機関利用（月人数）", use_container_width=True)

st.markdown("---")
st.subheader("データ確認")

rank_df = read_csv_safely(CSV_FILES["施設ランキングCSV"])
if not rank_df.empty:
    st.write("施設ランキング（上位20）")
    rank_view = rank_df.head(20).rename(
        columns={
            "facility": "施設名",
            "total_patients": "総患者数",
            "top3_frequency": "上位3出現回数",
        }
    )
    st.dataframe(rank_view, use_container_width=True, hide_index=True)

plus5_df = read_csv_safely(CSV_FILES["都祁+上位5勢力図データ"])
if not plus5_df.empty and "sel_dominant" in plus5_df.columns:
    st.write("都祁+上位5の勢力分布（町丁目数）")
    plus5_view = (
        plus5_df["sel_dominant"]
        .fillna("未結合")
        .value_counts()
        .rename_axis("施設名")
        .reset_index(name="町丁目数")
    )
    st.dataframe(plus5_view, use_container_width=True, hide_index=True)

st.markdown("---")
st.subheader("ダウンロード")
for label, path in {**FILES, **CSV_FILES}.items():
    if file_ok(path):
        st.download_button(
            label=f"{label} をダウンロード",
            data=path.read_bytes(),
            file_name=path.name,
            mime="application/octet-stream",
            key=f"dl_{path.name}",
        )

zip_bytes = build_zip_bytes()
st.download_button(
    label="資料一式 ZIP をダウンロード",
    data=zip_bytes,
    file_name="tsuge_report_bundle.zip",
    mime="application/zip",
)

st.info("起動コマンド: `cd /Users/itotsubasa/IdeaProjects/pythoN && ./.venv/bin/streamlit run JADECOM/202603/streamlit_report.py`")
