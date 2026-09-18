import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.filters import multiselect, period_filter, search_rows
from components.insights import build, render
from components.kpi_cards import metrics, pct, won
from components.style import COLORS, chart_style, footnote, section_title
from components.tables import show
from runtime import context, title
from services.calculations import filter_dates, filter_text


d = context()
f = d.frames
title("자금", "실제 입출금, 월말 자금과 운영상 손익을 명확히 구분해 확인하세요.")
start, end, query = period_filter(f)
base = filter_dates(f["입출금"], "거래일", start, end)
types = multiselect(base, "구분", "입출금 구분")
cash = search_rows(filter_text(base, {"구분": types}), query)
monthly = f["월별실적"]
m = monthly[
    monthly["월 시작"].between(start.to_period("M").start_time, end.to_period("M").start_time)
].copy()

current = float(m.iloc[-1]["월말 자금"]) if len(m) else 0
opening = float(f["대시보드"].iloc[0]["시작 기초자금"])
deposit = float(cash["입금"].sum())
withdrawal = float(cash["출금"].sum())
net = deposit - withdrawal
revenue = float(m["매출"].sum()) if len(m) else 0

metrics(
    [
        ("현재자금", won(current), "선택 기간 마지막 월말 자금"),
        ("입금", won(deposit), "선택 기간 실제 현금 유입"),
        ("출금", won(withdrawal), "선택 기간 실제 현금 유출"),
        ("순현금흐름", won(net), "실제 현금 유입−유출"),
        ("시작 기초자금", won(opening), "대시보드 설정값"),
        ("현금흐름률", pct(net / revenue if revenue else 0), "순현금흐름÷매출"),
    ],
    6,
)

c1, c2, c3 = st.columns([1.35, 1, 1], gap="small")
with c1:
    with st.container(border=True):
        section_title("월별 자금 흐름 추이")
        fig = go.Figure()
        fig.add_bar(x=m["월 시작"], y=m["실제 입금"], name="입금", marker_color=COLORS["green"])
        fig.add_bar(x=m["월 시작"], y=m["실제 출금"], name="출금", marker_color=COLORS["pink"])
        fig.add_scatter(x=m["월 시작"], y=m["순현금흐름"], name="순현금흐름", mode="lines+markers", line=dict(color=COLORS["blue"], width=2))
        fig.update_layout(barmode="group")
        st.plotly_chart(chart_style(fig, 255), use_container_width=True, config={"displayModeBar": False})

with c2:
    with st.container(border=True):
        section_title("월말 자금 잔액")
        fig = go.Figure(go.Scatter(
            x=m["월 시작"],
            y=m["월말 자금"],
            mode="lines+markers",
            line=dict(color=COLORS["blue"], width=2.5),
            marker=dict(size=6, color=COLORS["blue"]),
            fill="tozeroy",
            fillcolor="rgba(59,130,246,.10)",
        ))
        st.plotly_chart(chart_style(fig, 255, False), use_container_width=True, config={"displayModeBar": False})

with c3:
    with st.container(border=True):
        section_title("출금 구성")
        outflow = cash.groupby("구분", dropna=False)["출금"].sum().reset_index()
        outflow = outflow[outflow["출금"] > 0]
        if outflow.empty:
            outflow = pd.DataFrame({"구분": ["출금 없음"], "출금": [1]})
        fig = go.Figure(go.Pie(
            labels=outflow["구분"].fillna("미분류"),
            values=outflow["출금"],
            hole=.66,
            textinfo="none",
            marker_colors=[COLORS["blue"], COLORS["green"], COLORS["pink"], COLORS["purple"], COLORS["orange"], COLORS["cyan"]],
        ))
        fig.add_annotation(text=won(withdrawal), x=.5, y=.5, showarrow=False, font=dict(size=13, color=COLORS["text"]))
        st.plotly_chart(chart_style(fig, 255), use_container_width=True, config={"displayModeBar": False})

table_col, compare_col = st.columns([1.65, 1], gap="small")
with table_col:
    with st.container(border=True):
        section_title("자금 거래 내역")
        show(
            cash.sort_values("거래일", ascending=False)[
                ["거래일", "계좌", "구분", "연결 주문 / 발주번호", "내용", "입금", "출금"]
            ],
            currency=["입금", "출금"],
            height=315,
        )

with compare_col:
    with st.container(border=True):
        section_title("관리손익 vs 순현금흐름")
        compare = go.Figure()
        compare.add_bar(x=m["월 시작"], y=m["관리손익"], name="관리손익", marker_color=COLORS["purple"])
        compare.add_bar(x=m["월 시작"], y=m["순현금흐름"], name="순현금흐름", marker_color=COLORS["green"])
        compare.update_layout(barmode="group")
        st.plotly_chart(chart_style(compare, 175), use_container_width=True, config={"displayModeBar": False})
        footnote("관리손익은 사업의 운영 수익성이고, 순현금흐름은 실제 현금 유입에서 유출을 뺀 값입니다.")
        today = pd.Timestamp.now(tz=d.settings.timezone).date()
        render(build(f, m, today)[:2])
