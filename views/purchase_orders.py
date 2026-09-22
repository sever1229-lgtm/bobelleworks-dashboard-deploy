import pandas as pd
import plotly.express as px
import streamlit as st

from components.filters import multiselect, period_filter, search_rows
from components.kpi_cards import metrics, mini_metrics, num, won
from components.style import chart_style, footnote, section_title
from components.tables import show
from runtime import context, title
from services.calculations import delayed_orders, filter_dates, filter_text


d = context()
f = d.frames
title("발주", "발주 실적과 향후 예정 발주, 입고 잔량과 납기 위험을 관리합니다.")

start, end, query = period_filter(f)
today = pd.Timestamp.now(tz=d.settings.timezone).date()

orders = f["발주"].copy()
if "발주상태" not in orders.columns:
    orders["발주상태"] = ""

orders["발주상태"] = orders["발주상태"].fillna("").astype(str).str.strip()
missing_status = orders["발주상태"].eq("")
if missing_status.any():
    order_dates = pd.to_datetime(orders.loc[missing_status, "발주일"], errors="coerce")
    orders.loc[missing_status, "발주상태"] = order_dates.map(
        lambda value: "예정" if pd.notna(value) and value.date() > today else "발주완료"
    )

vendor_source = orders[orders["발주상태"] != "취소"]
vendors = multiselect(vendor_source, "거래처", "거래처")

actual_base = orders[orders["발주상태"] == "발주완료"]
actual_base = filter_dates(actual_base, "발주일", start, end)
po = search_rows(filter_text(actual_base, {"거래처": vendors}), query)

planned = orders[orders["발주상태"] == "예정"].copy()
planned = search_rows(filter_text(planned, {"거래처": vendors}), query)
planned_dates = pd.to_datetime(planned["발주일"], errors="coerce")
overdue_planned = planned[pd.notna(planned_dates) & (planned_dates.dt.date < today)]

late = delayed_orders(po, today)

metrics(
    [
        ("전체 발주", num(po["발주번호"].nunique()), "선택 기간 발주완료 건"),
        ("진행중", num((po["상태"] == "진행중").sum()), "선택 기간 발주완료 건"),
        ("완료", num((po["상태"] == "완료").sum()), "선택 기간 발주완료 건"),
        ("미입고수량", num(po["미입고수량"].sum()), "선택 기간 발주완료 건"),
        ("발주금액", won(po["예상 발주액"].sum()), "선택 기간 발주완료 건"),
        ("납기 지연", num(len(late)), "선택 기간 발주완료 건"),
    ],
    6,
)

if len(late):
    st.error(f"입고예정일이 지났지만 미입고수량이 남은 발주가 {len(late)}건 있습니다.")

po = po.copy()
po["표시상태"] = po["상태"]
po.loc[po.index.isin(late.index), "표시상태"] = "납기 확인"

with st.container(border=True):
    section_title("향후 발주 예정")
    future_dates = planned_dates[pd.notna(planned_dates) & (planned_dates.dt.date >= today)]
    next_order_date = future_dates.min().strftime("%y-%m-%d") if not future_dates.empty else "-"
    mini_metrics(
        [
            ("예정 발주", f"{planned['발주번호'].nunique():,}건"),
            ("예정수량", f"{planned['발주수량'].sum():,.0f}"),
            ("예정금액", won(planned["예상 발주액"].sum())),
            ("다음 예정일", next_order_date),
        ]
    )
    missing_price = int((pd.to_numeric(planned["예상 단가"], errors="coerce").fillna(0) <= 0).sum())
    if missing_price:
        footnote(
            f"예상 단가가 입력되지 않은 SKU {missing_price}행은 예정금액에 포함되지 않습니다."
        )
    if len(overdue_planned):
        st.warning(f"발주상태가 '예정'인데 예정일이 지난 행이 {len(overdue_planned)}건 있습니다.")

with st.container(border=True):
    section_title("거래처별 발주액")
    vendor = po.groupby("거래처")["예상 발주액"].sum().reset_index()
    if vendor.empty:
        st.info("선택 기간에 발주완료 실적이 없습니다.")
    else:
        st.plotly_chart(
            chart_style(
                px.bar(
                    vendor,
                    x="거래처",
                    y="예상 발주액",
                    color_discrete_sequence=["#3b82f6"],
                ),
                245,
                False,
            ),
            use_container_width=True,
            config={"displayModeBar": False},
        )

section_title("발주 상세")
cols = [
    "발주번호",
    "발주일",
    "거래처",
    "SKU",
    "상품명 (자동)",
    "발주수량",
    "누적 입고수량",
    "미입고수량",
    "입고예정일",
    "예상 발주액",
    "표시상태",
]
show(
    po.sort_values(["미입고수량", "입고예정일"], ascending=[False, True])[cols],
    currency=["예상 발주액"],
)

section_title("향후 발주 예정")
if planned.empty:
    st.info("현재 등록된 예정 발주가 없습니다.")
else:
    upcoming = planned.copy().sort_values("발주일")
    upcoming = upcoming.rename(columns={"발주일": "발주예정일"})
    upcoming_cols = [
        "발주예정일",
        "거래처",
        "SKU",
        "상품명 (자동)",
        "발주수량",
        "예상 단가",
        "예상 발주액",
        "입고예정일",
    ]
    show(
        upcoming[upcoming_cols],
        currency=["예상 단가", "예상 발주액"],
    )
