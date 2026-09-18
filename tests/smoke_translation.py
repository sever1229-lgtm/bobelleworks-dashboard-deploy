import pandas as pd

from services.interpretation import (
    INTERPRETATION_COLUMNS,
    dashboard_date_bounds,
    filter_interpretation,
    interpretation_frame,
    interpretation_metrics,
    monthly_business_summary,
    selected_period,
)


# Fully synthetic values. Never place operational figures in source control.
legacy_monthly = pd.DataFrame({
    "월 시작": pd.to_datetime(["2026-01-01"]),
    "매출": [100_000],
    "전체 매출": [100_000],
    "쇼핑몰 매출": [100_000],
    "통번역 매출": [pd.NA],
    "공헌이익": [40_000],
    "전체 공헌이익": [40_000],
    "관리손익": [30_000],
    "전체 관리손익": [30_000],
})
translation = interpretation_frame(pd.DataFrame({
    "업무일": ["2026-01-12"],
    "업무구분": ["통역"],
    "거래처": ["테스트 거래처"],
    "프로젝트": ["테스트 행사"],
    "매출액": [50_000],
    "원천징수 합계": [0],
    "실수령 예정액": [50_000],
    "입금상태": ["미정산"],
}))

# P1: a synthesized legacy value must not hide project-level translation revenue.
assert pd.isna(legacy_monthly.loc[0, "통번역 매출"])
combined = monthly_business_summary(legacy_monthly, translation)
assert combined.loc[0, "쇼핑몰 매출"] == 100_000
assert combined.loc[0, "통번역 매출"] == 50_000
assert combined.loc[0, "전체 매출"] == 150_000
assert combined.loc[0, "전체 공헌이익"] == 90_000
assert combined.loc[0, "전체 관리손익"] == 80_000

# P2: explicit formula zeros are values, while genuinely blank formulas use fallbacks.
assert translation.loc[0, "원천징수 합계 (자동)"] == 0
assert translation.loc[0, "실수령 예정액 (자동)"] == 50_000
fallback = interpretation_frame(pd.DataFrame({
    "업무일": ["2026-02-01"], "통번역 매출액": [100_000],
    "원천징수 합계 (자동)": [""], "실수령 예정액 (자동)": [""],
}))
assert fallback.loc[0, "원천징수 합계 (자동)"] == 3_300
assert fallback.loc[0, "실수령 예정액 (자동)"] == 96_700

# P1: Streamlit emits empty and one-date tuples while a range is being selected.
lo, hi = pd.Timestamp("2026-01-01"), pd.Timestamp("2026-01-31")
assert selected_period((), lo, hi) == (lo, hi)
assert selected_period((pd.Timestamp("2026-01-15"),), lo, hi) == (
    pd.Timestamp("2026-01-15"), pd.Timestamp("2026-01-15"),
)

# P2: translation-only years must participate in the overall date bounds.
frames = {
    "판매 및 반품": pd.DataFrame({"처리일": pd.to_datetime(["2025-06-01"])}),
    "운영비": pd.DataFrame({"발생일": pd.to_datetime([])}),
    "입출금": pd.DataFrame({"거래일": pd.to_datetime([])}),
    "통번역 매출": pd.DataFrame({"업무일": pd.to_datetime(["2027-03-04"])}),
}
assert dashboard_date_bounds(frames) == (pd.Timestamp("2025-06-01"), pd.Timestamp("2027-03-04"))

# Empty and filtered states remain stable.
empty = interpretation_frame(pd.DataFrame())
assert list(empty.columns) == INTERPRETATION_COLUMNS
assert interpretation_metrics(empty)["매출"] == 0
assert filter_interpretation(translation, lo, hi, types=["번역"]).empty

print("OK: translation compatibility, review regressions, filters, and empty states passed")
