import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from components.filters import period_filter
from components.kpi_cards import metrics, won
from components.style import COLORS, chart_style, section_title
from runtime import context, title
from services.interpretation import interpretation_frame, monthly_business_summary


d = context()
f = d.frames
title("전체 대시보드", "스마일피치노와 통역 사업의 매출, 수익성 및 자금 흐름을 통합해서 확인하세요.")
start, end, _ = period_filter(f, show_search=False)

translation = interpretation_frame(f.get("통역 매출"))
monthly = monthly_business_summary(f["월별실적"], translation)
selected = monthly[monthly["월 시작"].between(start.to_period("M").start_time, end.to_period("M").start_time)].copy()
trend = monthly[monthly["월 시작"] <= end.to_period("M").start_time].tail(12).copy()
totals = selected.select_dtypes("number").sum() if len(selected) else pd.Series(dtype=float)

cash = float(selected.iloc[-1]["월말 자금"]) if len(selected) and "월말 자금" in selected else 0.0
total_revenue = totals.get("전체 매출", 0.0)
shop_revenue = totals.get("스마일피치노 매출", 0.0)
translation_revenue = totals.get("통역 매출", 0.0)

metrics(
    [
        ("전체 매출", won(total_revenue), "월별실적의 전체 매출 기준"),
        ("스마일피치노 매출", won(shop_revenue), "스마일피치노 사업 매출"),
        ("통역 매출", won(translation_revenue), "원천징수 전 통역 매출"),
        ("전체 공헌이익", won(totals.get("전체 공헌이익", 0)), "통역 직접비 미입력 시 매출을 반영"),
        ("전체 관리손익", won(totals.get("전체 관리손익", 0)), "통역 개별 비용 미입력 기준"),
        ("현재자금", won(cash), "선택 기간 마지막 월말 자금"),
    ],
    6,
)

left, right = st.columns([1.6, 1], gap="small")
with left:
    with st.container(border=True):
        section_title("월별 사업별 매출 추이")
        revenue_columns = ["전체 매출", "스마일피치노 매출", "통역 매출"]
        trend_revenue = trend.copy()
        for column in revenue_columns:
            if column not in trend_revenue:
                trend_revenue[column] = 0.0
        long = trend_revenue.melt(
            id_vars=["월 시작"], value_vars=revenue_columns,
            var_name="구분", value_name="사업매출",
        ) if len(trend_revenue) else pd.DataFrame(columns=["월 시작", "구분", "사업매출"])
        fig = px.bar(
            long, x="월 시작", y="사업매출", color="구분", barmode="group",
            color_discrete_map={"전체 매출": COLORS["blue"], "스마일피치노 매출": COLORS["green"], "통역 매출": COLORS["purple"]},
        )
        st.plotly_chart(chart_style(fig, 310), use_container_width=True, config={"displayModeBar": False})

with right:
    with st.container(border=True):
        section_title("스마일피치노 vs 통역 매출 비중")
        mix = pd.DataFrame({"사업": ["스마일피치노", "통역"], "매출": [shop_revenue, translation_revenue]})
        display = mix if mix["매출"].abs().sum() else pd.DataFrame({"사업": ["데이터 없음"], "매출": [1]})
        fig = go.Figure(go.Pie(
            labels=display["사업"], values=display["매출"].abs(), hole=.66, textinfo="none",
            marker_colors=[COLORS["blue"], COLORS["purple"]],
        ))
        fig.add_annotation(text=won(total_revenue), x=.5, y=.5, showarrow=False, font=dict(size=13, color=COLORS["text"]))
        st.plotly_chart(chart_style(fig, 310), use_container_width=True, config={"displayModeBar": False})
        st.caption("매출은 스마일피치노와 통역 모두 세전 기준으로 표시합니다.")

with st.container(border=True):
    section_title("월별 전체 수익성 및 현금흐름")
    columns = [column for column in ["전체 공헌이익", "전체 관리손익", "순현금흐름"] if column in trend]
    long = trend.melt(id_vars=["월 시작"], value_vars=columns, var_name="구분", value_name="금액") if columns else pd.DataFrame(columns=["월 시작", "구분", "금액"])
    fig = px.bar(
        long, x="월 시작", y="금액", color="구분", barmode="group",
        color_discrete_map={"전체 공헌이익": COLORS["green"], "전체 관리손익": COLORS["purple"], "순현금흐름": COLORS["blue"]},
    )
    st.plotly_chart(chart_style(fig, 265), use_container_width=True, config={"displayModeBar": False})

st.info("통역 매출은 원천징수 전 금액입니다. 원천징수액은 비용으로 차감하지 않으며, 실제 현금 유입은 입출금 시트의 ‘통역수입’ 기록을 기준으로 자금에 반영됩니다.")
