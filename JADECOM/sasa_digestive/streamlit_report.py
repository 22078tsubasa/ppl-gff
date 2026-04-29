from __future__ import annotations

import base64
import hmac
import os
from pathlib import Path

import pandas as pd
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError


BASE_DIR = Path(__file__).resolve().parent

IMAGE_FILES = {
    "全体勢力図": BASE_DIR / "dominant_territory_sasa_car30_usersTop60_allLegend.png",
    "佐々総合病院+上位5勢力図": BASE_DIR / "dominant_territory_sasa_car30_sasaPlus5_other_allLegend.png",
    "上位10ヒートマップ図": BASE_DIR / "sasa_car30_usersTop60_town_med_heatmap_上位10_町丁目60.png",
    "上位3マトリクス図": BASE_DIR / "sasa_car30_usersTop60_town_med_matrix_上位3_町丁目60.png",
    "グラフ": BASE_DIR / "town_med_graph_top60.png",
}

CSV_FILES = {
    "全体勢力図データ": BASE_DIR / "dominant_territory_sasa_car30_usersTop60_allLegend_result.csv",
    "佐々+上位5勢力図データ": BASE_DIR / "dominant_territory_sasa_car30_sasaPlus5_other_allLegend_result.csv",
    "上位3マトリクスCSV": BASE_DIR / "sasa_car30_usersTop60_town_med_matrix_上位3のみ_町丁目60.csv",
    "上位10マトリクスCSV": BASE_DIR / "sasa_car30_usersTop60_town_med_matrix_上位10_町丁目60.csv",
    "施設ランキングCSV": BASE_DIR / "sasa_car30_usersTop60_facility_rank_summary.csv",
    "選定施設CSV": BASE_DIR / "sasa_car30_usersTop60_selected_facilities.csv",
    "佐々+上位5選定施設CSV": BASE_DIR / "sasa_car30_sasaPlus5_selected_facilities.csv",
}

PALETTE = {
    "bg": "#eef5ea",
    "main": "#70AD47",
    "deep": "#2f6b2f",
    "light": "#cfe8bf",
    "accent": "#9BC53D",
    "text": "#1f2d1f",
}

DEFAULT_PASSWORD = "shibaura2026"
IMAGE_VIEWPORT_HEIGHT = 760
ZOOM_MIN = 80
ZOOM_MAX = 400
ZOOM_STEP = 20
ZOOM_DEFAULT = 140


def file_ok(path: Path) -> bool:
    return path.exists() and path.is_file()


def read_csv_safely(path: Path) -> pd.DataFrame:
    if not file_ok(path):
        return pd.DataFrame()
    return pd.read_csv(path)


def get_expected_password() -> str:
    try:
        if "APP_PASSWORD" in st.secrets:
            return str(st.secrets["APP_PASSWORD"])
    except StreamlitSecretNotFoundError:
        pass
    return os.getenv("APP_PASSWORD", DEFAULT_PASSWORD)


def require_password() -> None:
    expected = get_expected_password()
    if st.session_state.get("authed", False):
        return

    st.title("佐々総合病院　競合分析（消化器外科）（閲覧認証）")
    st.caption("閲覧にはパスワードが必要です")
    pw = st.text_input("パスワード", type="password")
    if st.button("ログイン"):
        if hmac.compare_digest(pw, expected):
            st.session_state["authed"] = True
            st.rerun()
        st.error("パスワードが違います。")
    st.stop()


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
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        """
        <div class="hero-card">
          <div class="hero-title">佐々総合病院　競合分析（消化器外科）</div>
          <div class="hero-sub">町丁目別勢力図・ヒートマップ・マトリクス・グラフ</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def adjust_zoom(state_key: str, delta: int) -> None:
    current = int(st.session_state.get(state_key, ZOOM_DEFAULT))
    st.session_state[state_key] = max(ZOOM_MIN, min(ZOOM_MAX, current + delta))


def render_zoomable_image(title: str, path: Path, key_prefix: str) -> None:
    st.subheader(title)
    if not file_ok(path):
        st.warning(f"{title} が見つかりません。")
        return

    zoom_key = f"{key_prefix}_zoom"
    if zoom_key not in st.session_state:
        st.session_state[zoom_key] = ZOOM_DEFAULT

    c1, c2, c3 = st.columns([0.9, 1.4, 6.7])
    with c1:
        st.button(
            "−",
            key=f"{key_prefix}_zoom_out",
            on_click=adjust_zoom,
            args=(zoom_key, -ZOOM_STEP),
            use_container_width=True,
        )
    with c2:
        st.button(
            "+",
            key=f"{key_prefix}_zoom_in",
            on_click=adjust_zoom,
            args=(zoom_key, ZOOM_STEP),
            use_container_width=True,
        )
    with c3:
        st.caption(f"拡大率: {st.session_state[zoom_key]}%")

    zoom_pct = int(st.session_state[zoom_key])
    image_b64 = base64.b64encode(path.read_bytes()).decode("utf-8")
    st.markdown(
        f"""
        <div style="
            overflow: auto;
            height: {IMAGE_VIEWPORT_HEIGHT}px;
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


def render_header_panel() -> None:
    st.markdown(
        """
        <div class="hero-card">
          <div class="hero-title">佐々総合病院競合分析（消化器外科）</div>
          <div class="hero-sub">町丁目別勢力図・ヒートマップ・マトリクス・グラフ</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_map_tab() -> None:
    left, right = st.columns(2)
    with left:
        render_zoomable_image("全体勢力図", IMAGE_FILES["全体勢力図"], "map_all")
    with right:
        render_zoomable_image("佐々総合病院+上位5勢力図", IMAGE_FILES["佐々総合病院+上位5勢力図"], "map_plus5")


def render_heatmap_tab() -> None:
    render_zoomable_image("上位10ヒートマップ", IMAGE_FILES["上位10ヒートマップ図"], "heat_top10")


def render_matrix_tab() -> None:
    render_zoomable_image("上位3マトリクス", IMAGE_FILES["上位3マトリクス図"], "matrix_top3")


def render_graph_tab() -> None:
    render_zoomable_image("グラフ", IMAGE_FILES["グラフ"], "graph_top60")


def render_help_tab() -> None:
    st.subheader("使い方")
    st.markdown(
        """
        - 画面上部の `− / +` ボタンで拡大率を調整できます。広く見たいときは縮小、文字や境界を確認したいときは拡大してください。
        - 画像はスクロール可能です（表示枠高さは固定です）。
        - `データ確認` タブでランキング・対象施設の表を確認できます。
        - この画面の分析母集団は、佐々総合病院の自動車30分圏内の対象町丁目です。
        """
    )

    st.subheader("各可視化の見方")
    st.markdown(
        """
        - `勢力図`: 町丁目ごとに、どの医療機関の利用者数が相対的に強いかを色分けして見ます。
        - `佐々総合病院+上位5勢力図`: 佐々総合病院と競合上位5施設に絞って、競争関係を簡潔に確認します。
        - `ヒートマップ`: 町丁目と主要医療機関の組み合わせを濃淡で見て、利用が強い地点を把握します。
        - `マトリクス`: 上位施設に絞った比較図です。行と列を見比べることで、どの町丁目でどの施設の利用が強いかを確認します。
        - `グラフ`: 距離の近い順上位60町丁目での積み上げ表示です。
        - `データ確認`: 画面内で主要なCSV内容を表として確認します。
        """
    )

    st.subheader("データ一覧の意味")
    st.markdown(
        """
        - `全体勢力図データ`: 全町丁目を対象に、各町丁目で優勢な医療機関を整理したデータです。
        - `佐々+上位5勢力図データ`: 佐々総合病院と競合上位5施設に限定した勢力図の元データです。
        - `上位10マトリクスCSV`: 主要10施設を対象にしたヒートマップ用の集計表です。
        - `上位3マトリクスCSV`: 主要3施設に絞った比較用の行列データです。
        - `施設ランキングCSV`: 表示用に抽出した町丁目範囲内での施設別合計人数です。
        - `選定施設CSV`: 30分圏全体をもとに可視化対象として選定した施設一覧です。
        """
    )


def render_data_tab() -> None:
    st.subheader("用語と集計範囲")
    st.info(
        "この画面では『患者数』と『利用者数』は同じ意味（人数）です。"
        "表ごとに集計対象が異なるため、数値は一致しないことがあります。"
    )
    st.markdown(
        "- 一部抜粋60町丁目: 佐々総合病院からの距離（dist_km）が近い順の上位60町丁目\n"
        "- 施設ランキング: 一部抜粋（表示用の上位60町丁目）内での合計人数\n"
        "- 対象施設（利用者数TOP60）: 30分圏の全対象町丁目で選定した施設一覧"
    )

    rank_df = read_csv_safely(CSV_FILES["施設ランキングCSV"])
    if not rank_df.empty:
        st.subheader("施設ランキング（上位20 / 一部抜粋60町丁目ベース）")
        cols = rank_df.columns.tolist()
        if {"facility", "total_patients", "top3_frequency"}.issubset(set(cols)):
            rank_view = rank_df.head(20).rename(
                columns={"facility": "施設名", "total_patients": "総患者数", "top3_frequency": "上位3出現回数"}
            )
        else:
            rank_view = rank_df.head(20)
        st.dataframe(rank_view, use_container_width=True, hide_index=True)

    selected_df = read_csv_safely(CSV_FILES["選定施設CSV"])
    if not selected_df.empty:
        st.subheader("対象施設（利用者数TOP60 / 30分圏全町丁目ベース）")
        st.dataframe(selected_df, use_container_width=True, hide_index=True)

    plus5_df = read_csv_safely(CSV_FILES["佐々+上位5勢力図データ"])
    dom_col = None
    for c in ["dominant_sel6", "plot_label", "dominant"]:
        if c in plus5_df.columns:
            dom_col = c
            break
    if not plus5_df.empty and dom_col is not None:
        st.subheader("佐々総合病院+上位5の勢力分布（町丁目数）")
        plus5_view = plus5_df[dom_col].fillna("未結合").value_counts().rename_axis("施設名").reset_index(name="町丁目数")
        st.dataframe(plus5_view, use_container_width=True, hide_index=True)


st.set_page_config(page_title="佐々総合病院　競合分析（消化器外科）", layout="wide")
require_password()
inject_style()
render_header_panel()

missing = [name for name, p in {**IMAGE_FILES, **CSV_FILES}.items() if not file_ok(p)]
if missing:
    st.warning("不足ファイル: " + " / ".join(missing))

help_tab, map_tab, heat_tab, matrix_tab, graph_tab, data_tab = st.tabs(
    ["使い方", "勢力図", "ヒートマップ", "マトリクス", "グラフ", "データ確認"]
)

with help_tab:
    render_help_tab()
with map_tab:
    render_map_tab()
with heat_tab:
    render_heatmap_tab()
with matrix_tab:
    render_matrix_tab()
with graph_tab:
    render_graph_tab()
with data_tab:
    render_data_tab()
