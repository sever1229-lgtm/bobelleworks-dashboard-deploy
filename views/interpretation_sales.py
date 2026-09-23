import pandas as pd
import plotly.express as px
import streamlit as st

from components.kpi_cards import metrics, pct, won
from components.style import COLORS, chart_style, section_title
from components.tables import show
from runtime import context, title
from services.interpretation import filter_interpretation, interpretation_frame, interpretation_metrics, period_bounds, selected_period


d = context()
f = d.frames
title("통역 매출 분석", "업무구분과 월별 기준으로 통역 매출을 분석합니다.")
translation = interpretation_frame(f.get("통역 매출"))
lo, hi = period_bounds(translation, d.settings.timezone)
reference_date = pd.Timestamp.now(tz=d.settings.timezone).tz_localize(None).normalize()
default_start = reference_date.to_period("M").start_time
picked = st.date_input("조회 기간", (default_start.date(), reference_date.date()), key="interpretation_sales_period")
start, end = selected_period(picked, lo, hi)
types = st.multiselect("업무구분", sorted(value for value in translation["업무구분"].unique() if value))
selected = filter_interpretation(translation, start, end, types=types)
summary = interpretation_metrics(selected)
withholding_rate = summary["원천징수 합계"] / summary["매출"] if summary["매출"] else 0.0

metrics(
    [
        ("통역 매출", won(summary["매출"]), "원천징수 전 매출"),
        ("실수령 예정액", won(summary["실수령 예정액"]), "원천징수 후 예상 금액"),
        ("원천징수 합계", won(summary["원천징수 합계"]), "소득세·지방소득세 합계"),
        ("원천징수율", pct(withholding_rate), "원천징수÷매출"),
    ],
    4,
)

work = selected.copy()
if len(work):
    work["월"] = work["업무일"].dt.to_period("M").dt.to_timestamp()
    monthly = work.groupby("월", as_index=False)["통역 매출액"].sum()
    by_type = work.groupby("업무구분", as_index=False).agg(통역건수=("프로젝트 / 행사명", "size"), 매출=("통역 매출액", "sum"), 실수령예정액=("실수령 예정액 (자동)", "sum"))
else:
    monthly = pd.DataFrame(columns=["월", "통역 매출액"])
    by_type = pd.DataFrame(columns=["업무구분", "통역건수", "매출", "실수령예정액"])

c1, c2 = st.columns(2, gap="small")
with c1:
    with st.container(border=True):
        section_title("월별 통역 매출")
        st.plotly_chart(chart_style(px.line(monthly, x="월", y="통역 매출액", markers=True, color_discrete_sequence=[COLORS["blue"]]), 260, False), use_container_width=True, config={"displayModeBar": False})
with c2:
    with st.container(border=True):
        section_title("업무구분별 매출")
        st.plotly_chart(chart_style(px.bar(by_type, x="업무구분", y="매출", color_discrete_sequence=[COLORS["green"]]), 260, False), use_container_width=True, config={"displayModeBar": False})

section_title("업무구분별 실적")
show(by_type, currency=["매출", "실수령예정액"])
