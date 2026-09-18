import pandas as pd
import streamlit as st

from components.kpi_cards import metrics, num, won
from components.tables import show
from runtime import context, title
from services.interpretation import filter_interpretation, interpretation_frame, interpretation_metrics, period_bounds, selected_period


d = context()
f = d.frames
title("프로젝트·매출 내역", "업무일과 거래처, 프로젝트 단위로 통번역 매출과 정산 상태를 확인하세요.")
translation = interpretation_frame(f.get("통번역 매출"))
lo, hi = period_bounds(translation, d.settings.timezone)
filters = st.columns(4, gap="small")
picked = filters[0].date_input("업무 기간", (lo.date(), hi.date()), key="interpretation_projects_period")
types = filters[1].multiselect("업무구분", sorted(value for value in translation["업무구분"].unique() if value))
clients = filters[2].multiselect("거래처 / 에이전시", sorted(value for value in translation["거래처 / 에이전시"].unique() if value))
query = filters[3].text_input("검색", placeholder="프로젝트명, 메모…")
start, end = selected_period(picked, lo, hi)
selected = filter_interpretation(translation, start, end, types=types, clients=clients, query=query)
summary = interpretation_metrics(selected)

metrics(
    [
        ("프로젝트 수", num(summary["프로젝트 수"]), "필터 적용 행 수"),
        ("통번역 매출", won(summary["매출"]), "원천징수 전 매출"),
        ("실수령 예정액", won(summary["실수령 예정액"]), "매출−원천징수"),
        ("미정산 금액", won(summary["미정산 금액"]), "입금완료 외 실수령 예정액"),
    ],
    4,
)

columns = [
    "업무일", "업무구분", "거래처 / 에이전시", "프로젝트 / 행사명", "통번역 매출액",
    "원천징수 합계 (자동)", "실수령 예정액 (자동)", "지급명세서 여부", "입금상태",
]
show(selected.sort_values("업무일", ascending=False)[columns], currency=["통번역 매출액", "원천징수 합계 (자동)", "실수령 예정액 (자동)"])
