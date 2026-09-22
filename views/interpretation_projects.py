import pandas as pd
import streamlit as st

from components.kpi_cards import metric_card, num, split_metric_card, won
from components.tables import show
from runtime import context, title
from services.interpretation import filter_interpretation, interpretation_frame, interpretation_metrics, period_bounds, selected_period


d = context()
f = d.frames
title("프로젝트·매출 내역", "업무일과 거래처, 프로젝트 단위로 통역 매출과 정산 상태를 확인하세요.")
translation = interpretation_frame(f.get("통역 매출"))
lo, hi = period_bounds(translation, d.settings.timezone)
filters = st.columns(5, gap="small")
reference_date = pd.Timestamp.now(tz=d.settings.timezone).tz_localize(None).normalize()
default_start = reference_date.to_period("M").start_time
picked = filters[0].date_input("업무 기간", (default_start.date(), reference_date.date()), key="interpretation_projects_period")
types = filters[1].multiselect("업무구분", sorted(value for value in translation["업무구분"].unique() if value))
clients = filters[2].multiselect("거래처 / 에이전시", sorted(value for value in translation["거래처 / 에이전시"].unique() if value))
venues = filters[3].multiselect("장소", sorted(value for value in translation["장소"].unique() if value))
query = filters[4].text_input("검색", placeholder="프로젝트명, 메모…")
start, end = selected_period(picked, lo, hi)
selected = filter_interpretation(translation, start, end, types=types, clients=clients, venues=venues, query=query)
summary = interpretation_metrics(selected)

kpi_cols = st.columns([1.35, 1, 1, 1], gap="small")
with kpi_cols[0]:
    split_metric_card(
        ("통역 건수", num(summary["통역 건수"]), "필터 적용 통역 행 수"),
        ("프로젝트 수", num(summary["프로젝트 수"]), "고유 프로젝트명 수"),
    )
with kpi_cols[1]:
    metric_card("통역 매출", won(summary["매출"]), "원천징수 전 매출", 1)
with kpi_cols[2]:
    metric_card("실수령 예정액", won(summary["실수령 예정액"]), "매출−원천징수", 2)
with kpi_cols[3]:
    metric_card("미정산 금액", won(summary["미정산 금액"]), "입금완료 외 실수령 예정액", 3)

columns = [
    "업무일", "업무구분", "거래처 / 에이전시", "프로젝트 / 행사명", "장소", "통역 매출액",
    "원천징수 합계 (자동)", "실수령 예정액 (자동)", "지급명세서 여부", "입금상태",
]
show(selected.sort_values("업무일", ascending=False)[columns], currency=["통역 매출액", "원천징수 합계 (자동)", "실수령 예정액 (자동)"])
