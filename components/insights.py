import pandas as pd
from services.calculations import delayed_orders


def _actual_orders(frame: pd.DataFrame) -> pd.DataFrame:
    if frame is None or frame.empty:
        return frame.copy() if isinstance(frame, pd.DataFrame) else pd.DataFrame()
    if "발주상태" not in frame:
        return frame.copy()
    status = frame["발주상태"].fillna("").astype(str).str.strip()
    return frame[status.eq("발주완료")].copy()


def build(frames, monthly, today):
    messages = []
    inv = frames["재고현황"]
    replenish = int((inv["상태"] == "보충 필요").sum())
    negative = int((inv["상태"] == "음수재고 확인").sum())
    if replenish:
        messages.append(("warn", f"안전재고 이하 SKU가 {replenish}개 있습니다."))
    if negative:
        messages.append(("danger", f"음수 재고 SKU가 {negative}개 있습니다. 거래 입력을 확인하세요."))

    actual_orders = _actual_orders(frames["발주"])
    late = len(delayed_orders(actual_orders, today))
    if late:
        messages.append(("danger", f"입고예정일이 지난 미입고 발주가 {late}건 있습니다."))

    errors = 0
    for name, column, value in [
        ("판매 및 반품", "입력 확인", "입력 확인"),
        ("입고 및 재고 조정", "입력 확인", "입력 확인"),
        ("상품·SKU관리", "중복 확인", "중복 확인"),
    ]:
        errors += int((frames[name].get(column, pd.Series(dtype=str)).astype(str) == value).sum())
    errors += int((actual_orders.get("상태", pd.Series(dtype=str)).astype(str) == "입력 확인").sum())
    if errors:
        messages.append(("danger", f"원본 시트에 입력 확인이 필요한 행이 {errors}건 있습니다."))

    m = monthly.sort_values("월 시작") if "월 시작" in monthly else monthly
    if len(m) >= 2:
        a, b = m.iloc[-2], m.iloc[-1]
        pm = a["공헌이익"] / a["매출"] if a["매출"] else 0
        cm = b["공헌이익"] / b["매출"] if b["매출"] else 0
        if pm - cm >= .05:
            messages.append(("warn", f"공헌이익률이 전월보다 {(pm-cm)*100:.1f}%p 하락했습니다."))
        ps = a["판매 부대비"] / a["매출"] if a["매출"] else 0
        cs = b["판매 부대비"] / b["매출"] if b["매출"] else 0
        if cs - ps >= .03:
            messages.append(("warn", f"판매부대비율이 전월보다 {(cs-ps)*100:.1f}%p 증가했습니다."))
        if a["운영비"] and b["운영비"] > a["운영비"] * 1.3:
            messages.append(("warn", f"운영비가 전월보다 {(b['운영비']/a['운영비']-1):.1%} 증가했습니다."))
        if b["관리손익"] < a["관리손익"]:
            messages.append(("warn", f"관리손익이 전월보다 ₩{a['관리손익']-b['관리손익']:,.0f} 감소했습니다."))
        if a.get("월말 자금", 0) > 0 and b.get("월말 자금", 0) < a["월말 자금"] * .8:
            messages.append(("danger", f"월말 자금이 전월보다 {(1-b['월말 자금']/a['월말 자금']):.1%} 감소했습니다."))
    return messages or [("ok", "현재 기준에서 우선 확인할 경영 알림이 없습니다.")]


def render(messages):
    import streamlit as st
    for level, text in messages:
        st.markdown(f'<div class="insight {level}">{text}</div>', unsafe_allow_html=True)
    st.button("AI 분석하기", disabled=True, help="향후 OpenAI API 연결을 위한 확장 지점입니다.")
