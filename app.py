"""
A/B 테스트 위닝 아카이브 — 라운지 배포용 (읽기 전용 뷰어)

이 버전은 사내 라운지(bind-internal.web.app) 배포 전용입니다.
- 로그인 토큰이 전혀 필요 없습니다 (저장된 archive.csv + 공개 CDN 이미지만 사용)
- 새 A/B 비교/저장 기능은 없습니다 (그 기능은 로컬 편집용 app.py에서 사용)
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path

st.set_page_config(
    page_title="A/B 테스트 위닝 아카이브",
    page_icon="🏆",
    layout="wide",
)

ARCHIVE_FILE = Path(__file__).parent / "archive.csv"
IMAGE_WIDTH = 240


def load_archive():
    if ARCHIVE_FILE.exists():
        return pd.read_csv(ARCHIVE_FILE)
    return pd.DataFrame()


def month_label(date_str):
    try:
        d = datetime.strptime(str(date_str), "%Y-%m-%d")
        return f"{d.year}년 {d.month:02d}월"
    except Exception:
        return "날짜 미상"


def render_side(row, side: str, is_winner: bool):
    cid = row.get(f"{side}_콘텐츠ID", "")
    name = row.get(f"{side}_콘텐츠명", "")
    main = row.get(f"{side}_메인카피", "")
    sub = row.get(f"{side}_서브카피", "")
    img = row.get(f"{side}_이미지URL", "")

    if is_winner:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#FFF4D6,#FFE9A8); border:2.5px solid #F5A623;
                    border-radius:10px; padding:10px 14px; margin-bottom:10px;">
            <span style="font-size:17px; font-weight:800; color:#9A6700;">🏆 {side} 콘텐츠 · 위닝</span>
            <span style="font-size:12px; color:#B8860B; margin-left:8px;">ID {cid}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background:#F2F2F2; border:1px solid #DDD; border-radius:10px;
                    padding:10px 14px; margin-bottom:10px;">
            <span style="font-size:15px; font-weight:600; color:#999;">{side} 콘텐츠</span>
            <span style="font-size:12px; color:#BBB; margin-left:8px;">ID {cid}</span>
        </div>
        """, unsafe_allow_html=True)

    if pd.notna(img) and img:
        st.image(img, width=IMAGE_WIDTH)

    # 성과 지표 (저장된 CTR)
    imp = row.get(f"{side}_노출수", "")
    clk = row.get(f"{side}_클릭수", "")
    ctr = row.get(f"{side}_CTR", "")
    if pd.notna(ctr) and str(ctr) != "":
        try:
            imp_s = f"{int(float(imp)):,}" if pd.notna(imp) and str(imp) != "" else "-"
            clk_s = f"{int(float(clk)):,}" if pd.notna(clk) and str(clk) != "" else "-"
        except Exception:
            imp_s, clk_s = str(imp), str(clk)
        ctr_c = "#1A7F37" if is_winner else "#888"
        st.markdown(
            f"<div style='border:1px solid {'#1A7F37' if is_winner else '#DDD'}; border-radius:6px; "
            f"padding:6px 10px; margin:4px 0; font-size:13px;'>"
            f"📈 노출 <b>{imp_s}</b> · 클릭 <b>{clk_s}</b> · "
            f"<span style='color:{ctr_c}; font-weight:800; font-size:15px;'>CTR {float(ctr):.2f}%</span></div>",
            unsafe_allow_html=True,
        )

    if is_winner:
        st.markdown(f"**콘텐츠명:** {name}")
        st.markdown(f"**메인카피:** {main}")
        st.markdown(f"**서브카피:** {sub}")
    else:
        st.markdown(f"<span style='color:#999'><b>콘텐츠명:</b> {name}</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:#999'><b>메인카피:</b> {main}</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:#999'><b>서브카피:</b> {sub}</span>", unsafe_allow_html=True)


def render_row(row):
    winner_label = row["위닝"]
    header = f"🗓 {row['저장일시']}  |  {row.get('페이지_설명','') or '(설명 없음)'}  |  🏆 위닝: {winner_label}"
    with st.expander(header):
        st.markdown(f"""
        <div style="text-align:center; background:#FFF8E1; border-radius:8px; padding:8px;
                    margin-bottom:14px; font-weight:700; color:#9A6700; font-size:15px;">
            🏆 이 테스트의 위닝 콘텐츠는 <span style="font-size:18px;">{winner_label}</span> 입니다
        </div>
        """, unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            render_side(row, "A", winner_label == "A")
        with c2:
            render_side(row, "B", winner_label == "B")
        if row.get("메모") and pd.notna(row.get("메모")):
            st.markdown(f"📝 **메모:** {row['메모']}")


# ══════════════════════════════════════════════════════════
st.title("🏆 A/B 테스트 위닝 아카이브")
st.caption("MD 콘텐츠 A/B 테스트 위닝 기록 모음 · 읽기 전용")
st.divider()

df = load_archive()
if df.empty:
    st.info("아직 저장된 아카이브가 없어요.")
else:
    df = df.copy()
    df["_월"] = df["저장일시"].apply(month_label)
    months = sorted(df["_월"].unique(), reverse=True)

    top1, top2 = st.columns([1, 2])
    with top1:
        folder = st.selectbox("📁 폴더 (월별)", ["전체"] + months)
    with top2:
        search = st.text_input("🔍 검색 (콘텐츠명, 카피, 페이지 설명)", "")

    view_df = df
    if folder != "전체":
        view_df = view_df[view_df["_월"] == folder]
    if search:
        mask = view_df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)
        view_df = view_df[mask]

    st.markdown(f"**총 {len(view_df)}건** ({folder})")
    st.divider()

    display_months = [folder] if folder != "전체" else months
    for m in display_months:
        month_rows = view_df[view_df["_월"] == m]
        if month_rows.empty:
            continue
        st.markdown(f"""
        <div style="background:#EEF3FB; border-left:5px solid #4A90D9; border-radius:6px;
                    padding:10px 16px; margin:10px 0 6px 0; font-size:16px; font-weight:700; color:#2C5F94;">
            📁 {m} <span style="font-size:13px; color:#6B8FB5; font-weight:500;">· {len(month_rows)}건</span>
        </div>
        """, unsafe_allow_html=True)
        for _, row in month_rows.iterrows():
            render_row(row)
