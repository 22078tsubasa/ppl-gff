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

    st.title("佐々総合病院競合分析（閲覧認証）")
    st.caption("閲覧にはパスワードが必要です")
    pw = st.text_input("パスワード", type="password")
    if st.button("ログイン"):
        if hmac.compare_digest(pw, expected):
            st.session_state["authed"] = True
            st.rerun()
        else:
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
          <div class="hero-title">佐々総合病院競合分析</div>
          <div class="hero-sub">町丁目別勢力図・ヒートマップ・マトリクス・グラフ</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_zoomable_image(title: str, path: Path, key_prefix: str) -> None:
    st.subheader(title)
    if not file_ok(path):
        st.warning(f"{title} が見つかりません。")
        return

    zoom_key = f"{key_prefix}_zoom"
    if zoom_key not in st.session_state:
        st.session_state[zoom_key] = 140

    c1, c2, c3 = st.columns([1, 1, 8])
    with c1:
        if st.button("−", key=f"{key_prefix}_minus"):
            st.session_state[zoom_key] = max(80, int(st.session_state[zoom_key]) - 10)
    with c2:
        if st.button("+", key=f"{key_prefix}_plus"):
            st.session_state[zoom_key] = min(400, int(st.session_state[zoom_key]) + 10)
    with c3:
        st.caption(f"拡大率: {st.session_state[zoom_key]}%（+ / − で調整）")

    zoom_pct = int(st.session_state[zoom_key])
    viewport_h = 760

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


def render_data_tab() -> None:
    st.info(
        "このタブの2表は集計範囲が異なります。"
        "施設ランキングは「佐々総合病院から近い60町丁目」ベース、"
        "対象施設TOP60は「自動車30分圏全体」ベースです。"
    )
    rank_df = read_csv_safely(CSV_FILES["施設ランキングCSV"])
    if not rank_df.empty:
        flag_cols = [c for c in rank_df.columns if ("フラグ" in str(c)) or ("flag" in str(c).lower())]
        if flag_cols:
            rank_df = rank_df.drop(columns=flag_cols)
        rank_df.columns = [str(c).replace("患者", "利用者") for c in rank_df.columns]
        st.subheader("施設ランキング（全件 / 佐々総合病院から近い60町丁目ベース）")
        st.dataframe(rank_df, use_container_width=True, hide_index=True)

    selected_df = read_csv_safely(CSV_FILES["選定施設CSV"])
    if not selected_df.empty:
        flag_cols = [c for c in selected_df.columns if ("フラグ" in str(c)) or ("flag" in str(c).lower())]
        if flag_cols:
            selected_df = selected_df.drop(columns=flag_cols)
        selected_df.columns = [str(c).replace("患者", "利用者") for c in selected_df.columns]
        selected_df.columns = [str(c).replace("施設名_実データ列", "施設名") for c in selected_df.columns]
        st.subheader("対象施設（利用者数TOP60・全件 / 自動車30分圏全体ベース）")
        st.dataframe(selected_df, use_container_width=True, hide_index=True)


def render_usage_tab() -> None:
    st.subheader("使い方")
    st.markdown(
        "- 画面上部の `+ / −` ボタンで拡大率を調整できます\n"
        "- 画像はスクロール可能です（表示枠高さは固定）\n"
        "- `データ確認` タブでランキング・対象施設の表を確認できます"
    )
    st.subheader("分析範囲の前提")
    st.markdown(
        "- 分析母集団: 佐々総合病院の自動車30分圏内の対象町丁目（全体）\n"
        "- 可視化（ヒートマップ/マトリクス/グラフ）の表示対象: 佐々総合病院から距離が近い順の60町丁目\n"
        "- 施設選定: 利用者数TOP60施設"
    )
    st.subheader("可視化の説明")
    st.markdown(
        "- `勢力図`：町丁目ごとに最も利用者数が多い医療機関を表示\n"
        "- `ヒートマップ`：町丁目×医療機関（上位10）を色で可視化\n"
        "- `マトリクス`：各町丁目で利用者数が多い医療機関上位3つの人数を表示。"
        "上位3に頻出する医療機関の上位3施設は色付きで強調（それ以外の上位3は灰色表示）\n"
        "- `グラフ`：佐々総合病院からの距離が近い順の60町丁目について、"
        "町丁目ごとの医療機関利用人数を積み上げ棒で表示"
    )
    st.subheader("データ確認の表の説明")
    st.markdown(
        "- `施設ランキング`：佐々総合病院から近い60町丁目での人数合計ランキング\n"
        "- `対象施設（利用者数TOP60）`：自動車30分圏全体を母集団に選定した医療機関一覧\n"
        "- 注意：2表は集計範囲が異なるため、数値は一致しない場合があります"
    )


st.set_page_config(page_title="佐々総合病院競合分析", layout="wide")
require_password()
inject_style()
render_header()

missing = [name for name, p in {**IMAGE_FILES, **CSV_FILES}.items() if not file_ok(p)]
if missing:
    st.warning("不足ファイル: " + " / ".join(missing))

usage_tab, map_tab, heat_tab, matrix_tab, graph_tab, data_tab = st.tabs(
    ["使い方", "勢力図", "ヒートマップ", "マトリクス", "グラフ", "データ確認"]
)

with usage_tab:
    render_usage_tab()
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
