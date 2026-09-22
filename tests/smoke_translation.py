import pandas as pd

from services.interpretation import (
    INTERPRETATION_COLUMNS,
    dashboard_date_bounds,
    filter_interpretation,
    interpretation_frame,
    interpretation_metrics,
    monthly_business_summary,
    selected_period,
    venue_distribution,
)


# Fully synthetic values. Never place operational figures in source control.
legacy_monthly = pd.DataFrame({
    "월 시작": pd.to_datetime(["2026-01-01"]),
    "매출": [100_000],
    "전체 매출": [100_000],
    "스마일피치노 매출": [100_000],
    "통역 매출": [pd.NA],
    "공헌이익": [40_000],
    "전체 공헌이익": [40_000],
    "관리손익": [30_000],
    "전체 관리손익": [30_000],
})
translation = interpretation_frame(pd.DataFrame({
    "업무일": ["2026-01-12"],
    "업무구분": ["의류"],
    "거래처": ["테스트 거래처"],
    "프로젝트": ["테스트 행사"],
    "장소": ["코엑스"],
    "매출액": [50_000],
    "원천징수 합계": [0],
    "실수령 예정액": [50_000],
    "입금상태": ["미정산"],
}))

# P1: a synthesized legacy value must not hide project-level translation revenue.
assert pd.isna(legacy_monthly.loc[0, "통역 매출"])
combined = monthly_business_summary(legacy_monthly, translation)
assert combined.loc[0, "스마일피치노 매출"] == 100_000
assert combined.loc[0, "통역 매출"] == 50_000
assert combined.loc[0, "전체 매출"] == 150_000
assert combined.loc[0, "전체 공헌이익"] == 90_000
assert combined.loc[0, "전체 관리손익"] == 80_000

# P2: explicit formula zeros are values, while genuinely blank formulas use fallbacks.
assert translation.loc[0, "원천징수 합계 (자동)"] == 0
assert translation.loc[0, "실수령 예정액 (자동)"] == 50_000
fallback = interpretation_frame(pd.DataFrame({
    "업무일": ["2026-02-01"], "통역 매출액": [100_000],
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
    "통역 매출": pd.DataFrame({"업무일": pd.to_datetime(["2027-03-04"])}),
}
assert dashboard_date_bounds(frames) == (pd.Timestamp("2025-06-01"), pd.Timestamp("2027-03-04"))

# Venue distribution is based on interpretation-job counts, not revenue.
venue = venue_distribution(translation)
assert venue.loc[0, "장소"] == "코엑스"
assert venue.loc[0, "건수"] == 1
assert venue.loc[0, "비중"] == 1.0
assert len(filter_interpretation(translation, lo, hi, venues=["코엑스"])) == 1
assert filter_interpretation(translation, lo, hi, venues=["킨텍스"]).empty

# Empty and filtered states remain stable.
empty = interpretation_frame(pd.DataFrame())
assert list(empty.columns) == INTERPRETATION_COLUMNS
assert interpretation_metrics(empty)["매출"] == 0
assert filter_interpretation(translation, lo, hi, types=["식품"]).empty

print("OK: translation compatibility, review regressions, filters, and empty states passed")


# Regression: each row is one interpretation job, while repeated project names count once.
metric_frame = pd.DataFrame({
    "업무일": pd.to_datetime(["2026-09-01", "2026-09-01", "2026-09-02"]),
    "업무구분": ["교육", "교육", "의료"],
    "거래처 / 에이전시": ["A", "A", "B"],
    "프로젝트 / 행사명": ["Project X", "Project X", "Project Y"],
    "통역 매출액": [100000, 100000, 150000],
    "소득세 3%": [3000, 3000, 4500],
    "지방소득세 0.3%": [300, 300, 450],
    "원천징수 합계 (자동)": [3300, 3300, 4950],
    "실수령 예정액 (자동)": [96700, 96700, 145050],
    "지급명세서 여부": ["미확인"] * 3,
    "입금상태": ["미정산"] * 3,
    "메모": [""] * 3,
    "장소": ["코엑스", "코엑스", "서울(기타)"],
})
metric_frame = interpretation_frame(metric_frame)
metric_result = interpretation_metrics(metric_frame)
assert metric_result["통역 건수"] == 3, metric_result
assert metric_result["프로젝트 수"] == 2, metric_result
print("OK: same project on multiple rows counts as one project; every row counts as one interpretation")
