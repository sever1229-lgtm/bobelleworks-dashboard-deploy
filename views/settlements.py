import pandas as pd
import plotly.express as px
import streamlit as st

from components.kpi_cards import metrics, num, won
from components.style import COLORS, chart_style, section_title
from components.tables import show
from runtime import context, title
from services.interpretation import filter_interpretation, interpretation_frame, period_bounds, selected_period, with_status_columns


d = context()
f = d.frames
title("정산 현황", "입금상태와 지급명세서 확인 여부를 프로젝트별로 점검하세요.")
translation = interpretation_frame(f.get("통역 매출"))
lo, hi = period_bounds(translation, d.settings.timezone)
default_start = hi.to_period("M").start_time
picked = st.date_input("조회 기간", (default_start.date(), hi.date()), key="settlements_period")
start, end = selected_period(picked, lo, hi)
selected = with_status_columns(filter_interpretation(translation, start, end))

bucket = selected.groupby("정산구분", as_index=False)["실수령 예정액 (자동)"].sum() if len(selected) else pd.DataFrame(columns=["정산구분", "실수령 예정액 (자동)"])
def amount(name):
    values = bucket.loc[bucket["정산구분"] == name, "실수령 예정액 (자동)"]
    return float(values.iloc[0]) if len(values) else 0.0
confirmed = int(selected["지급명세서확인"].sum()) if len(selected) else 0
unconfirmed = len(selected) - confirmed

metrics(
    [
        ("입금완료", won(amount("입금완료")), "실수령 예정액 기준"),
        ("입금예정", won(amount("입금예정")), "실수령 예정액 기준"),
        ("미정산", won(amount("미정산")), "상태 미입력 포함"),
        ("지급명세서 확인", num(confirmed), "확인·발급·제출·완료"),
        ("지급명세서 미확인", num(unconfirmed), "확인 외 상태"),
    ],
    5,
)

c1, c2 = st.columns([1, 1.25], gap="small")
with c1:
    with st.container(border=True):
        section_title("정산 상태별 금액")
        display = bucket if len(bucket) else pd.DataFrame({"정산구분": ["데이터 없음"], "실수령 예정액 (자동)": [1]})
        st.plotly_chart(chart_style(px.pie(display, names="정산구분", values="실수령 예정액 (자동)", hole=.62, color="정산구분", color_discrete_map={"입금완료": COLORS["green"], "입금예정": COLORS["blue"], "미정산": COLORS["orange"], "데이터 없음": COLORS["muted"]}), 260, False), use_container_width=True, config={"displayModeBar": False})
with c2:
    with st.container(border=True):
        section_title("정산 확인 대상")
        pending = selected[selected["정산구분"] != "입금완료"] if len(selected) else selected
        columns = ["업무일", "거래처 / 에이전시", "프로젝트 / 행사명", "실수령 예정액 (자동)", "입금상태", "지급명세서 여부"]
        show(pending.sort_values("업무일", ascending=False)[columns], currency=["실수령 예정액 (자동)"], height=260)

section_title("전체 정산 내역")
columns = ["업무일", "업무구분", "거래처 / 에이전시", "프로젝트 / 행사명", "통역 매출액", "원천징수 합계 (자동)", "실수령 예정액 (자동)", "정산구분", "지급명세서 여부", "입금상태"]
show(selected.sort_values("업무일", ascending=False)[columns], currency=["통역 매출액", "원천징수 합계 (자동)", "실수령 예정액 (자동)"])
