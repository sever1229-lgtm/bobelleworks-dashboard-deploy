import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from components.kpi_cards import metrics, num, won
from components.style import COLORS, chart_style, section_title
from runtime import context, title
from services.interpretation import (
    filter_interpretation, interpretation_frame, interpretation_metrics, period_bounds, selected_period,
    venue_distribution,
)


d = context()
f = d.frames
translation = interpretation_frame(f.get("통역 매출"))
lo, hi = period_bounds(translation, d.settings.timezone)
reference_date = pd.Timestamp.now(tz=d.settings.timezone).tz_localize(None).normalize()

head_left, head_right = st.columns([1.12, 1.48], vertical_alignment="bottom")
with head_left:
    title(
        "통역 대시보드",
        "통역 프로젝트의 매출과 정산 진행 상태를 한눈에 확인하세요.",
        eyebrow="BOBELLE WORKS",
    )

with head_right:
    max_year = max(hi.year, reference_date.year)
    years = list(range(lo.year, max_year + 1)) or [reference_date.year]
    filter_cols = st.columns([.8, .8, 2.15], gap="small")
    selected_year = filter_cols[0].selectbox(
        "연도",
        years,
        index=(years.index(reference_date.year) if reference_date.year in years else len(years) - 1),
        key="interpretation_overview_year",
    )
    selected_month = filter_cols[1].selectbox(
        "월",
        ["전체"] + list(range(1, 13)),
        index=(reference_date.month if reference_date.year == selected_year else 0),
        key="interpretation_overview_month",
    )

    default_start = pd.Timestamp(selected_year, 1 if selected_month == "전체" else selected_month, 1)
    default_end = default_start + (
        pd.offsets.YearEnd(0) if selected_month == "전체" else pd.offsets.MonthEnd(0)
    )
    range_start = default_start
    if selected_year == reference_date.year and (selected_month == "전체" or selected_month == reference_date.month):
        range_end = min(default_end, reference_date)
    else:
        range_end = default_end
    if range_start > range_end:
        range_start, range_end = default_start, default_end

    picked = filter_cols[2].date_input(
        "조회 기간",
        (range_start.date(), range_end.date()),
        key="interpretation_overview_period",
    )

start, end = selected_period(picked, lo, hi)
selected = filter_interpretation(translation, start, end)
summary = interpretation_metrics(selected)

metrics(
    [
        ("통역 매출", won(summary["매출"]), "원천징수 전 매출"),
        ("통역 건수", num(summary["통역 건수"]), "입력된 통역 매출 행 수"),
        ("원천징수 합계", won(summary["원천징수 합계"]), "비용으로 차감하지 않음"),
        ("실수령 예정액", won(summary["실수령 예정액"]), "매출−원천징수"),
        ("미정산 금액", won(summary["미정산 금액"]), "입금완료 외 실수령 예정액"),
    ],
    5,
)

base = selected.copy()
if len(base):
    base["월"] = base["업무일"].dt.to_period("M").dt.to_timestamp()
    monthly = base.groupby("월", as_index=False)["통역 매출액"].sum()
    kind = base.groupby("업무구분", as_index=False)["통역 매출액"].sum()
    clients = base.groupby("거래처 / 에이전시", as_index=False)["통역 매출액"].sum().sort_values("통역 매출액", ascending=False).head(10)
    venues = venue_distribution(base)
else:
    monthly = pd.DataFrame(columns=["월", "통역 매출액"])
    kind = pd.DataFrame({"업무구분": ["데이터 없음"], "통역 매출액": [1]})
    clients = pd.DataFrame(columns=["거래처 / 에이전시", "통역 매출액"])
    venues = pd.DataFrame(columns=["장소", "건수", "비중"])

c1, c2, c3 = st.columns([1.4, 1, 1], gap="small")
with c1:
    with st.container(border=True):
        section_title("월별 매출 추이")
        st.plotly_chart(chart_style(px.bar(monthly, x="월", y="통역 매출액", color_discrete_sequence=[COLORS["blue"]], labels={"통역 매출액": "매출"}), 275, False), use_container_width=True, config={"displayModeBar": False})
with c2:
    with st.container(border=True):
        section_title("업무구분별 매출 비중")
        fig = go.Figure(go.Pie(labels=kind["업무구분"].replace("", "미분류"), values=kind["통역 매출액"].abs(), hole=.66, textinfo="none", marker_colors=[COLORS["blue"], COLORS["green"], COLORS["purple"], COLORS["orange"]]))
        fig.add_annotation(text=won(summary["매출"]), x=.5, y=.5, showarrow=False, font=dict(size=13, color=COLORS["text"]))
        st.plotly_chart(chart_style(fig, 275), use_container_width=True, config={"displayModeBar": False})
with c3:
    with st.container(border=True):
        section_title("통역 장소 비중")
        venue_display = venues if len(venues) else pd.DataFrame({"장소": ["데이터 없음"], "건수": [1]})
        fig = go.Figure(go.Pie(
            labels=venue_display["장소"], values=venue_display["건수"], hole=.66,
            textinfo="percent" if len(venues) else "none",
            marker_colors=[COLORS["blue"], COLORS["green"], COLORS["purple"], COLORS["orange"]],
        ))
        fig.add_annotation(
            text=f"통역 {int(venues['건수'].sum()) if len(venues) else 0}건",
            x=.5, y=.5, showarrow=False, font=dict(size=13, color=COLORS["text"]),
        )
        venue_fig = chart_style(fig, 275)
        venue_fig.update_layout(
            margin=dict(l=8, r=8, t=36, b=8),
            legend=dict(
                orientation="h",
                y=1.10,
                x=.5,
                xanchor="center",
                yanchor="bottom",
                title_text="",
                font_size=9,
            ),
        )
        st.plotly_chart(venue_fig, use_container_width=True, config={"displayModeBar": False})

with st.container(border=True):
    section_title("거래처별 매출")
    st.plotly_chart(
        chart_style(
            px.bar(
                clients,
                x="거래처 / 에이전시",
                y="통역 매출액",
                color_discrete_sequence=[COLORS["purple"]],
                labels={"통역 매출액": "매출", "거래처 / 에이전시": "거래처"},
            ),
            260, False,
        ),
        use_container_width=True,
        config={"displayModeBar": False},
    )

if selected.empty:
    st.info("아직 통역 매출 데이터가 없습니다. Google Sheets의 ‘통역 매출’ 시트에 입력하면 자동으로 표시됩니다.")
