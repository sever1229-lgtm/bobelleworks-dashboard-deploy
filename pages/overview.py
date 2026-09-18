import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.filters import period_filter, search_rows
from components.insights import build, render
from components.kpi_cards import metrics, mini_metrics, num, pct, won
from components.style import COLORS, chart_style, section_title
from components.tables import show
from runtime import context, title
from services.calculations import filter_dates
from services.validation import validate_aggregates


d = context()
f = d.frames
head_left,head_right=st.columns([1.05,1.55],vertical_alignment="bottom")
with head_left:
    title("Overview", "Bobelle Works의 매출, 수익성, 자금과 운영 상태를 한눈에 확인하세요.")
with head_right:
    start, end, query = period_filter(f,show_search=False)

monthly = f["월별실적"]
m = monthly[
    monthly["월 시작"].between(start.to_period("M").start_time, end.to_period("M").start_time)
].copy()
trend_m=monthly[monthly["월 시작"]<=end.to_period("M").start_time].sort_values("월 시작").tail(6).copy()
inv = f["재고현황"]
po = f["발주"]
sales = filter_dates(f["판매 및 반품"], "처리일", start, end)
tot = (
    m[["매출", "매출원가", "판매 부대비", "공헌이익", "운영비", "관리손익", "순현금흐름"]].sum()
    if len(m)
    else pd.Series(dtype=float)
)
cash = float(m.iloc[-1]["월말 자금"]) if len(m) else 0
revenue = tot.get("매출", 0)
margin = tot.get("공헌이익", 0) / revenue if revenue else 0
errors = sum(
    (f[n].get(c, pd.Series(dtype=str)).astype(str) == v).sum()
    for n, c, v in [
        ("판매 및 반품", "입력 확인", "입력 확인"),
        ("입고 및 재고 조정", "입력 확인", "입력 확인"),
        ("발주", "상태", "입력 확인"),
        ("상품·SKU관리", "중복 확인", "중복 확인"),
    ]
)
today = pd.Timestamp.now(tz=d.settings.timezone).date()
record_start = f["대시보드"].iloc[0]["기록 시작일"]
history = monthly[
    (monthly["월 시작"] >= record_start.to_period("M").start_time)
    & (monthly["월 시작"] <= end.to_period("M").start_time)
]
insights = build(f, history, today)

metrics(
    [
        ("매출", won(revenue), "월별실적 집계값"),
        ("공헌이익", won(tot.get("공헌이익", 0)), "매출−매출원가−판매부대비"),
        ("공헌이익률", pct(margin), "공헌이익÷매출"),
        ("관리손익", won(tot.get("관리손익", 0)), "공헌이익−운영비"),
        ("현재자금", won(cash), "선택 기간 마지막 월말 자금"),
        ("재고자산", won(inv["참고 재고가액"].sum()), "재고현황 계산값"),
    ],
    6,
)

left, middle, right = st.columns([1.55, .92, 1.02], gap="small")
with left:
    with st.container(border=True):
        section_title("월별 주요 지표 추이")
        fig = go.Figure()
        for col, color in [("매출", COLORS["blue"]), ("공헌이익", COLORS["green"]), ("관리손익", COLORS["pink"])]:
            fig.add_bar(x=trend_m["월 시작"], y=trend_m[col], name=col, marker_color=color, opacity=.9)
        fig.update_layout(barmode="group", bargap=.25)
        st.plotly_chart(chart_style(fig, 292), use_container_width=True, config={"displayModeBar": False})

with middle:
    with st.container(border=True):
        section_title("재고 및 운영 현황")
        normal = int((inv["상태"].replace("", "정상").fillna("정상") == "정상").sum())
        replenish = int((inv["상태"] == "보충 필요").sum())
        negative = int((inv["상태"] == "음수재고 확인").sum())
        late = int(((pd.to_numeric(po["미입고수량"], errors="coerce").fillna(0) > 0) & (po["입고예정일"].dt.date < pd.Timestamp.now(tz=d.settings.timezone).date())).sum())
        st.markdown(f'''<div class="bw-stock-cards"><div class="bw-stock-card blue"><span>▦ 현재고</span><b>{num(inv["현재고"].sum())}</b><span>전체 SKU 기준</span></div><div class="bw-stock-card warn"><span>⚠ 보충 필요</span><b>{num(replenish)}</b><span>안전재고 미만</span></div><div class="bw-stock-card"><span>▣ 미입고</span><b>{num(po["미입고수량"].sum())}</b><span>발주 확정 기준</span></div></div>''',unsafe_allow_html=True)
        summary=pd.DataFrame({"구분":["정상 재고","품절 SKU","보충 필요 SKU","납기 지연"],"수량":[normal,negative,replenish,late]})
        show(summary,height=172)

with right:
    with st.container(border=True):
        section_title("매출 구성")
        channel = (
            sales.groupby("판매채널", dropna=False)["매출 합계"].sum().reset_index()
            if len(sales)
            else pd.DataFrame({"판매채널": ["데이터 없음"], "매출 합계": [1]})
        )
        fig = go.Figure(go.Pie(
            labels=channel["판매채널"].fillna("미분류"),
            values=channel["매출 합계"].abs(),
            hole=.66,
            marker_colors=[COLORS["blue"], COLORS["green"], COLORS["pink"], COLORS["purple"], COLORS["orange"]],
            textinfo="none",
        ))
        fig.add_annotation(text=won(revenue), x=.5, y=.5, showarrow=False, font=dict(size=13, color=COLORS["text"]))
        st.plotly_chart(chart_style(fig, 292), use_container_width=True, config={"displayModeBar": False})
        level, highlight = insights[0]
        st.markdown(f'<div class="bw-highlight {level}"><div class="bw-highlight-icon">☼</div><div><b>이번 달 하이라이트</b><span>{highlight}</span></div></div>', unsafe_allow_html=True)

table_col, insight_col = st.columns([1, 1], gap="small")
with table_col:
    with st.container(border=True):
        section_title("최근 주문 내역")
        recent = search_rows(sales, query).sort_values("처리일", ascending=False).head(8)
        columns = ["처리일", "주문번호", "판매채널", "상품명 (자동)", "SKU", "구분", "재고 차감수량", "매출 합계", "공헌이익"]
        show(recent[columns], currency=["매출 합계", "공헌이익"], height=238)

with insight_col:
    with st.container(border=True):
        section_title("최근 주요 활동")
        activity=recent[["처리일","구분","주문번호","상품명 (자동)"]].copy()
        activity["내용"]=activity["주문번호"].astype(str)+" · "+activity["상품명 (자동)"].astype(str)
        show(activity[["처리일","구분","내용"]],height=170)
        render(insights[1:] or [("ok", "상세 알림은 모두 확인되었습니다.")])

with st.expander("Google Sheet 값 검증"):
    checks = validate_aggregates(f)
    selected = checks[
        checks["월"].between(start.to_period("M").start_time, end.to_period("M").start_time)
    ]
    bad = selected[selected["상태"] != "일치"]
    if bad.empty:
        st.success(f"선택 기간의 {len(selected):,}개 집계 항목이 일치합니다.")
    else:
        st.error(f"{len(bad)}개 항목에서 차이가 발견되었습니다.")
    show(bad if len(bad) else selected, currency=["시트 값", "웹 계산", "차이"], height=300)
