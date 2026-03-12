from __future__ import annotations

import base64
import io
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent

IMAGE_FILES = {
    "全体勢力図": BASE_DIR / "dominant_territory_tsuge_30km.png",
    "都祁診療所+上位5勢力図": BASE_DIR / "dominant_territory_tsuge_30km_tsuge_plus5.png",
    "上位3マトリクス図": BASE_DIR / "town_med_matrix_top3.png",
    "上位10ヒートマップ図": BASE_DIR / "town_med_heatmap_top10.png",
}

CSV_FILES = {
    "全体勢力図データ": BASE_DIR / "dominant_territory_tsuge_30km_result.csv",
    "都祁+上位5勢力図データ": BASE_DIR / "dominant_territory_tsuge_30km_tsuge_plus5_result.csv",
    "上位3マトリクスCSV": BASE_DIR / "town_med_matrix_top3_only.csv",
    "上位10マトリクスCSV": BASE_DIR / "town_med_matrix_top10.csv",
    "施設ランキングCSV": BASE_DIR / "facility_rank_summary.csv",
}


PALETTE = {
    "bg": "#eef5ea",
    "main": "#70AD47",
    "deep": "#2f6b2f",
    "light": "#cfe8bf",
    "accent": "#9BC53D",
    "text": "#1f2d1f",
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
        for _, p in IMAGE_FILES.items():
            if file_ok(p):
                zf.write(p, arcname=p.name)
        for _, p in CSV_FILES.items():
            if file_ok(p):
                zf.write(p, arcname=p.name)
    memory.seek(0)
    return memory.read()


def inject_style() -> None:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background:
              radial-gradient(circle at 8% 10%, #dcefcf 0%, transparent 30%),
              radial-gradient(circle at 88% 18%, #d2e9c0 0%, transparent 28%),
              linear-gradient(180deg, {PALETTE['bg']} 0%, #f7fbf4 100%);
            color: {PALETTE['text']};
        }}
        .hero-card {{
            background: linear-gradient(120deg, {PALETTE['main']} 0%, {PALETTE['deep']} 100%);
            padding: 1.4rem 1.6rem;
            border-radius: 18px;
            color: white;
            box-shadow: 0 10px 26px rgba(30,60,30,0.16);
            position: relative;
            overflow: hidden;
        }}
        .hero-card:before {{
            content: "";
            position: absolute;
            width: 220px;
            height: 220px;
            border-radius: 999px;
            right: -70px;
            top: -70px;
            background: rgba(255,255,255,0.14);
        }}
        .hero-card:after {{
            content: "";
            position: absolute;
            width: 180px;
            height: 180px;
            border-radius: 999px;
            left: -70px;
            bottom: -90px;
            background: rgba(255,255,255,0.12);
        }}
        .hero-title {{
            font-size: 2rem;
            font-weight: 800;
            letter-spacing: 0.03em;
            margin-bottom: 0.2rem;
        }}
        .hero-sub {{
            font-size: 1rem;
            opacity: 0.95;
        }}
        .leaf-banner {{
            margin-top: 0.8rem;
            color: #2e5f2e;
            font-size: 0.9rem;
            font-weight: 600;
            text-align: right;
        }}
        .section-note {{
            background: #ffffff;
            border-left: 6px solid {PALETTE['main']};
            border-radius: 10px;
            padding: 0.8rem 1rem;
            box-shadow: 0 4px 14px rgba(50,80,30,0.06);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        """
        <div class="hero-card">
          <div class="hero-title">都祁診療所競合分析</div>
          <div class="hero-sub">地域医療振興協会 共同研究 / 町丁目別勢力図・需要ヒートマップ</div>
        </div>
        <div class="leaf-banner">Leaf Theme / Nara Tsuge Clinic Research</div>
        """,
        unsafe_allow_html=True,
    )


def render_overview() -> None:
    st.markdown("### 概要")
    st.markdown(
        """
        <div class="section-note">
        本ページは、都祁診療所周辺の町丁目別データをもとに、
        <b>全体勢力図</b>、<b>都祁診療所+上位5施設の再計算勢力図</b>、
        <b>上位3/上位10ヒートマップ</b>を一体で確認できる共有用レポートです。
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_zoomable_image(title: str, path: Path, key_prefix: str) -> None:
    st.subheader(title)
    if not file_ok(path):
        st.warning(f"{title} が見つかりません。")
        return

    c1, c2 = st.columns([1, 1])
    with c1:
        zoom_pct = st.slider("拡大率(%)", 80, 400, 140, 10, key=f"{key_prefix}_zoom")
    with c2:
        viewport_h = st.slider("表示枠の高さ(px)", 300, 1400, 760, 20, key=f"{key_prefix}_height")

    image_b64 = base64.b64encode(path.read_bytes()).decode("utf-8")
    st.markdown(
        f"""
        <div style="
            overflow: auto;
            max-height: {viewport_h}px;
            border: 1px solid #aacb98;
            border-radius: 10px;
            background: white;
            box-shadow: inset 0 0 0 1px #e8f2e0;
            padding: 8px;
        ">
            <img src="data:image/png;base64,{image_b64}"
                 style="width: {zoom_pct}%; max-width: none; height: auto;" />
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("拡大率を上げると高解像度のまま細部を確認できます。ドラッグ/スクロールで移動してください。")
    st.download_button(
        label=f"{title}（原寸PNG）をダウンロード",
        data=path.read_bytes(),
        file_name=path.name,
        mime="image/png",
        key=f"{key_prefix}_png_dl",
    )


def render_map_tab() -> None:
    left, right = st.columns(2)
    with left:
        render_zoomable_image("全体勢力図", IMAGE_FILES["全体勢力図"], "map_all")
    with right:
        render_zoomable_image("都祁診療所+上位5勢力図", IMAGE_FILES["都祁診療所+上位5勢力図"], "map_plus5")


def render_matrix_tab() -> None:
    render_zoomable_image("上位3マトリクス", IMAGE_FILES["上位3マトリクス図"], "matrix_top3")


def render_heatmap_tab() -> None:
    render_zoomable_image("上位10ヒートマップ", IMAGE_FILES["上位10ヒートマップ図"], "heat_top10")


def render_data_tab() -> None:
    rank_df = read_csv_safely(CSV_FILES["施設ランキングCSV"])
    if not rank_df.empty:
        st.subheader("施設ランキング（上位20）")
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
        st.subheader("都祁+上位5の勢力分布（町丁目数）")
        plus5_view = (
            plus5_df["sel_dominant"]
            .fillna("未結合")
            .value_counts()
            .rename_axis("施設名")
            .reset_index(name="町丁目数")
        )
        st.dataframe(plus5_view, use_container_width=True, hide_index=True)


def render_share_tab() -> None:
    st.subheader("資料ダウンロード")
    for label, path in {**IMAGE_FILES, **CSV_FILES}.items():
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

    st.subheader("更新時の運用")
    st.markdown(
        """
1. `ppl-gff` の `JADECOM/202603/` 内ファイル（画像・CSV・アプリ）を更新
2. `git add .` → `git commit -m "update report"` → `git push`
3. Streamlit Cloud 側で同じURLに自動反映（通常1〜3分）

- URLは固定で使えるため、先方は同じリンクを継続利用できます。
- 一時停止してもアクセス時に自動起動されます。
        """
    )


st.set_page_config(page_title="都祁診療所競合分析", layout="wide")
inject_style()
render_header()

missing = [name for name, p in {**IMAGE_FILES, **CSV_FILES}.items() if not file_ok(p)]
if missing:
    st.warning("不足ファイル: " + " / ".join(missing))

c1, c2, c3, c4 = st.columns(4)
c1.metric("勢力図", "2種")
c2.metric("マトリクス", "1種")
c3.metric("ヒートマップ", "1種")
c4.metric("更新日", datetime.now().strftime("%Y-%m-%d"))

map_tab, matrix_tab, heat_tab, data_tab, share_tab = st.tabs(["勢力図", "マトリクス", "ヒートマップ", "データ", "共有・更新"])

with map_tab:
    render_map_tab()
with matrix_tab:
    render_matrix_tab()
with heat_tab:
    render_heatmap_tab()
with data_tab:
    render_data_tab()
with share_tab:
    render_share_tab()
