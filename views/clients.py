import pandas as pd
import plotly.express as px
import streamlit as st

from components.kpi_cards import metrics, num, won
from components.style import COLORS, chart_style, section_title
from components.tables import show
from runtime import context, title
from services.interpretation import interpretation_frame, period_bounds, filter_interpretation, selected_period, with_status_columns


d = context()
f = d.frames
title("거래처 관리", "거래처·에이전시별 프로젝트 실적과 미정산 금액을 관리하세요.")
translation = interpretation_frame(f.get("통역 매출"))
lo, hi = period_bounds(translation, d.settings.timezone)
reference_date = pd.Timestamp.now(tz=d.settings.timezone).tz_localize(None).normalize()
default_start = reference_date.to_period("M").start_time
picked = st.date_input("조회 기간", (default_start.date(), reference_date.date()), key="clients_period")
start, end = selected_period(picked, lo, hi)
selected = with_status_columns(filter_interpretation(translation, start, end))

if len(selected):
    clients = selected.groupby("거래처 / 에이전시", dropna=False).agg(
        프로젝트수=("프로젝트 / 행사명", lambda values: values.fillna("").astype(str).str.strip().str.replace(r"\\s+", " ", regex=True).replace("", pd.NA).dropna().nunique()),
        누적매출=("통역 매출액", "sum"),
        미정산금액=("실수령 예정액 (자동)", lambda values: values.loc[values.index.intersection(selected.index[selected["정산구분"] != "입금완료"])].sum()),
    ).reset_index()
    clients["평균프로젝트금액"] = clients["누적매출"].div(clients["프로젝트수"].replace(0, pd.NA)).fillna(0)
    # Recalculate the conditional amount directly to preserve grouping semantics with repeated client names.
    unpaid = selected[selected["정산구분"] != "입금완료"].groupby("거래처 / 에이전시", dropna=False)["실수령 예정액 (자동)"].sum()
    clients["미정산금액"] = clients["거래처 / 에이전시"].map(unpaid).fillna(0)
else:
    clients = pd.DataFrame(columns=["거래처 / 에이전시", "프로젝트수", "누적매출", "평균프로젝트금액", "미정산금액"])

metrics(
    [
        ("거래처 수", num(clients["거래처 / 에이전시"].replace("", pd.NA).dropna().nunique()), "조회 기간 기준"),
        ("누적 매출", won(clients["누적매출"].sum() if len(clients) else 0), "원천징수 전 매출"),
        ("미정산 금액", won(clients["미정산금액"].sum() if len(clients) else 0), "입금완료 외 실수령 예정액"),
    ],
    3,
)

with st.container(border=True):
    section_title("거래처별 매출")
    chart = clients.sort_values("누적매출", ascending=False).head(12)
    st.plotly_chart(
        chart_style(
            px.bar(
                chart,
                x="거래처 / 에이전시",
                y="누적매출",
                color_discrete_sequence=[COLORS["blue"]],
                labels={"거래처 / 에이전시": "거래처", "누적매출": "매출"},
            ),
            280,
            False,
        ),
        use_container_width=True,
        config={"displayModeBar": False},
    )

section_title("거래처별 정산 요약")
show(clients.sort_values("누적매출", ascending=False), currency=["누적매출", "평균프로젝트금액", "미정산금액"])
