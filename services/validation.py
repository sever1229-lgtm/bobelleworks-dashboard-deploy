from __future__ import annotations
import pandas as pd
from services.calculations import monthly_raw


def validate_aggregates(frames: dict[str, pd.DataFrame], tolerance: float = 1.0) -> pd.DataFrame:
    """Validate Smile Piccino dashboard metrics against raw source data.

    The monthly sheet also contains overall business metrics that include interpretation
    revenue. This validator is shown on the Smile Piccino dashboard, so its profit
    metrics must be derived from Smile Piccino-specific revenue/cost columns rather
    than the overall contribution/management-profit columns.
    """
    sheet = frames["월별실적"].copy()
    sheet["월"] = sheet["월 시작"].dt.to_period("M").dt.to_timestamp()

    # Build Smile Piccino-specific sheet-side metrics.
    sheet["매출"] = pd.to_numeric(sheet.get("스마일피치노 매출", 0), errors="coerce").fillna(0)
    sheet["매출원가"] = pd.to_numeric(sheet.get("스마일피치노 매출원가", 0), errors="coerce").fillna(0)
    sheet["판매 부대비"] = pd.to_numeric(sheet.get("스마일피치노 판매 부대비", 0), errors="coerce").fillna(0)
    sheet["공헌이익"] = sheet["매출"] - sheet["매출원가"] - sheet["판매 부대비"]
    sheet["운영비"] = pd.to_numeric(sheet.get("운영비", 0), errors="coerce").fillna(0)
    sheet["관리손익"] = sheet["공헌이익"] - sheet["운영비"]

    # Cash metrics remain overall cashbook metrics and are validated against the same
    # cashbook raw data, so their comparison basis is unchanged.
    for col in ["실제 입금", "실제 출금", "순현금흐름"]:
        sheet[col] = pd.to_numeric(sheet.get(col, 0), errors="coerce").fillna(0)

    raw = monthly_raw(frames["판매 및 반품"], frames["운영비"], frames["입출금"])
    metrics = ["매출", "매출원가", "판매 부대비", "공헌이익", "운영비", "관리손익", "실제 입금", "실제 출금", "순현금흐름"]
    joined = sheet[["월"] + metrics].merge(raw, on="월", how="left", suffixes=("_시트", "_웹")).fillna(0)

    rows = []
    for _, r in joined.iterrows():
        for m in metrics:
            delta = float(r[f"{m}_웹"] - r[f"{m}_시트"])
            rows.append({
                "월": r["월"],
                "항목": m,
                "시트 값": r[f"{m}_시트"],
                "웹 계산": r[f"{m}_웹"],
                "차이": delta,
                "상태": "일치" if abs(delta) <= tolerance else "확인 필요",
            })
    return pd.DataFrame(rows)
