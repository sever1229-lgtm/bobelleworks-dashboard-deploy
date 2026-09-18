import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from components.kpi_cards import metrics, num, won
from components.style import COLORS, chart_style, section_title
from runtime import context, title
from services.interpretation import (
    filter_interpretation, interpretation_frame, interpretation_metrics, period_bounds, selected_period,
)


d = context()
f = d.frames
title("통번역 대시보드", "통역·번역 프로젝트 매출과 정산 진행 상태를 한눈에 확인하세요.")
translation = interpretation_frame(f.get("통번역 매출"))
lo, hi = period_bounds(translation, d.settings.timezone)
picked = st.date_input("조회 기간", (lo.date(), hi.date()), key="interpretation_overview_period")
start, end = selected_period(picked, lo, hi)
selected = filter_interpretation(translation, start, end)
summary = interpretation_metrics(selected)

metrics(
    [
        ("통번역 매출", won(summary["매출"]), "원천징수 전 매출"),
        ("프로젝트 수", num(summary["프로젝트 수"]), "입력된 통번역 매출 행 수"),
        ("평균 프로젝트 금액", won(summary["평균 프로젝트 금액"]), "통번역 매출÷프로젝트 수"),
        ("원천징수 합계", won(summary["원천징수 합계"]), "비용으로 차감하지 않음"),
        ("실수령 예정액", won(summary["실수령 예정액"]), "매출−원천징수"),
        ("미정산 금액", won(summary["미정산 금액"]), "입금완료 외 실수령 예정액"),
    ],
    6,
)

base = selected.copy()
if len(base):
    base["월"] = base["업무일"].dt.to_period("M").dt.to_timestamp()
    monthly = base.groupby("월", as_index=False)["통번역 매출액"].sum()
    kind = base.groupby("업무구분", as_index=False)["통번역 매출액"].sum()
    clients = base.groupby("거래처 / 에이전시", as_index=False)["통번역 매출액"].sum().sort_values("통번역 매출액", ascending=False).head(10)
else:
    monthly = pd.DataFrame(columns=["월", "통번역 매출액"])
    kind = pd.DataFrame({"업무구분": ["데이터 없음"], "통번역 매출액": [1]})
    clients = pd.DataFrame(columns=["거래처 / 에이전시", "통번역 매출액"])

c1, c2, c3 = st.columns([1.4, 1, 1], gap="small")
with c1:
    with st.container(border=True):
        section_title("월별 매출 추이")
        st.plotly_chart(chart_style(px.bar(monthly, x="월", y="통번역 매출액", color_discrete_sequence=[COLORS["blue"]], labels={"통번역 매출액": "매출"}), 275, False), use_container_width=True, config={"displayModeBar": False})
with c2:
    with st.container(border=True):
        section_title("통역 / 번역 매출 비중")
        fig = go.Figure(go.Pie(labels=kind["업무구분"].replace("", "미분류"), values=kind["통번역 매출액"].abs(), hole=.66, textinfo="none", marker_colors=[COLORS["blue"], COLORS["green"], COLORS["purple"], COLORS["orange"]]))
        fig.add_annotation(text=won(summary["매출"]), x=.5, y=.5, showarrow=False, font=dict(size=13, color=COLORS["text"]))
        st.plotly_chart(chart_style(fig, 275), use_container_width=True, config={"displayModeBar": False})
with c3:
    with st.container(border=True):
        section_title("거래처별 매출")
        st.plotly_chart(chart_style(px.bar(clients, x="통번역 매출액", y="거래처 / 에이전시", orientation="h", color_discrete_sequence=[COLORS["purple"]]), 275, False), use_container_width=True, config={"displayModeBar": False})

if selected.empty:
    st.info("아직 통번역 매출 데이터가 없습니다. Google Sheets의 ‘통번역 매출’ 시트에 입력하면 자동으로 표시됩니다.")
