import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
from config.settings import Settings
from services.data_loader import load_dashboard_data
from services.google_sheets import GoogleSheetsError
from components.style import apply_style

def context():
    apply_style(); settings=Settings()
    try:
        secret_sheet_id=st.secrets.get("GOOGLE_SPREADSHEET_ID","")
    except Exception:
        secret_sheet_id=""
    if secret_sheet_id: settings=Settings(spreadsheet_id=secret_sheet_id,timezone=settings.timezone,cache_ttl=settings.cache_ttl)
    if not settings.spreadsheet_id:
        st.error("Google Spreadsheet ID가 설정되지 않았습니다."); st.info("배포 환경의 Secrets에 GOOGLE_SPREADSHEET_ID를 등록해 주세요."); st.stop()
    try: data=load_dashboard_data(settings.spreadsheet_id,settings.timezone,st.session_state.get("cache_buster",0))
    except (GoogleSheetsError,ValueError) as exc:
        st.error(str(exc)); st.info("README의 Google Sheets 연결 방법에 따라 읽기 전용 서비스 계정을 설정한 뒤 다시 시도하세요."); st.stop()
    now=datetime.now(ZoneInfo(settings.timezone))
    with st.container(key="bw_topbar"):
        search_col,user_col=st.columns([3.2,1],vertical_alignment="center")
        search_col.text_input("전체 검색",placeholder="상품명, 주문번호, SKU, 거래처 등을 검색하세요...",key="global_search",label_visibility="collapsed")
        user_col.markdown(f'<div class="bw-user"><span>{now:%y년 %m월 %d일}</span><span>●</span><span class="bw-avatar">B</span><b>보벨웍스<br><small>운영자</small></b></div>',unsafe_allow_html=True)
    if data.sheet_timezone!=settings.timezone: st.caption(f"⚠ 시트 시간대 {data.sheet_timezone} · 날짜 비교는 한국시간 기준")
    with st.sidebar:
        with st.container(key="bw_sidebar_footer"):
            st.markdown(
                """
                <div class="bw-ci-logo" aria-label="Bobelle Works">
                  <svg viewBox="0 0 370 165" role="img" aria-label="Bobelle Works 보벨웍스">
                    <text x="7" y="66" class="bw-ci-main">Bobelle</text>
                    <text x="7" y="139" class="bw-ci-main">works</text>
                    <text x="250" y="137" class="bw-ci-kr">보벨웍스</text>
                  </svg>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("↻ 최신 데이터 새로고침", use_container_width=True, key="bw_refresh_bottom"):
                st.session_state["cache_buster"] = st.session_state.get("cache_buster", 0) + 1
                st.cache_data.clear()
                st.rerun()
            st.caption(f"데이터 기준: {data.loaded_at:%y-%m-%d %H:%M:%S}")
    return data

def title(name, description, eyebrow="BOBELLE WORKS"):
    st.markdown(
        f'<div class="bw-head"><div><div class="bw-eyebrow">{eyebrow}</div><div class="bw-title">{name}</div><div class="bw-sub">{description}</div></div></div>',
        unsafe_allow_html=True,
    )
