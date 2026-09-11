import streamlit as st
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
    with st.sidebar:
        st.markdown("## Bobelle Works"); st.caption("Operations Dashboard")
        if st.button("↻ 최신 데이터 새로고침",use_container_width=True):
            st.session_state["cache_buster"]=st.session_state.get("cache_buster",0)+1; st.cache_data.clear(); st.rerun()
    if not settings.spreadsheet_id:
        st.error("Google Spreadsheet ID가 설정되지 않았습니다."); st.info("배포 환경의 Secrets에 GOOGLE_SPREADSHEET_ID를 등록해 주세요."); st.stop()
    try: data=load_dashboard_data(settings.spreadsheet_id,settings.timezone,st.session_state.get("cache_buster",0))
    except (GoogleSheetsError,ValueError) as exc:
        st.error(str(exc)); st.info("README의 Google Sheets 연결 방법에 따라 읽기 전용 서비스 계정을 설정한 뒤 다시 시도하세요."); st.stop()
    if data.sheet_timezone!=settings.timezone: st.warning(f"Google Spreadsheet 시간대는 {data.sheet_timezone}, 웹앱은 {settings.timezone}입니다. 납기 비교는 한국시간 기준입니다.",icon="⚠️")
    with st.sidebar: st.caption(f"마지막 로드: {data.loaded_at:%Y-%m-%d %H:%M:%S}")
    return data

def title(name,description): st.markdown(f'<div class="bw-title">{name}</div><div class="bw-sub">{description}</div>',unsafe_allow_html=True)
