from __future__ import annotations

from typing import Iterable

import pandas as pd


INTERPRETATION_COLUMNS = [
    "업무일", "업무구분", "거래처 / 에이전시", "프로젝트 / 행사명", "통역 매출액",
    "소득세 3%", "지방소득세 0.3%", "원천징수 합계 (자동)", "실수령 예정액 (자동)",
    "지급명세서 여부", "입금상태", "메모", "장소",
]

_COLUMN_ALIASES = {
    "업무일": ("업무일", "일자", "작업일"),
    "업무구분": ("업무구분", "구분", "업무 종류"),
    "거래처 / 에이전시": ("거래처 / 에이전시", "거래처/에이전시", "거래처", "에이전시"),
    "프로젝트 / 행사명": ("프로젝트 / 행사명", "프로젝트/행사명", "프로젝트", "행사명"),
    "통역 매출액": ("통역 매출액", "통역매출액", "통번역 매출액", "통번역매출액", "매출액", "번역 매출액"),
    "소득세 3%": ("소득세 3%", "소득세"),
    "지방소득세 0.3%": ("지방소득세 0.3%", "지방소득세"),
    "원천징수 합계 (자동)": ("원천징수 합계 (자동)", "원천징수 합계", "원천징수액"),
    "실수령 예정액 (자동)": ("실수령 예정액 (자동)", "실수령 예정액", "실수령액"),
    "지급명세서 여부": ("지급명세서 여부", "지급명세서"),
    "입금상태": ("입금상태", "정산상태", "입금 상태"),
    "메모": ("메모", "비고", "내용"),
    "장소": ("장소", "업무장소", "행사장소", "장소구분"),
}


def _key(value: object) -> str:
    return str(value).replace(" ", "").replace("/", "").replace("(", "").replace(")", "").lower()


def _number(value: object) -> float:
    if value is None or pd.isna(value) or value == "":
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "").replace("₩", "").replace("원", "")
    try:
        return float(text)
    except ValueError:
        return 0.0


def _missing(values: pd.Series) -> pd.Series:
    """Identify blank sheet cells before numeric normalization loses that signal."""
    return values.isna() | values.astype("string").str.strip().eq("").fillna(True)


def interpretation_frame(df: pd.DataFrame | None) -> pd.DataFrame:
    """Return a stable, typed frame even when the new Google Sheet is empty or absent."""
    source = df.copy() if isinstance(df, pd.DataFrame) else pd.DataFrame()
    keys = {_key(column): column for column in source.columns}
    out = pd.DataFrame(index=source.index)

    for target in INTERPRETATION_COLUMNS:
        found = next((keys[_key(alias)] for alias in _COLUMN_ALIASES[target] if _key(alias) in keys), None)
        out[target] = source[found] if found else pd.NA

    out["업무일"] = pd.to_datetime(out["업무일"], errors="coerce")
    income_tax_missing = _missing(out["소득세 3%"])
    local_tax_missing = _missing(out["지방소득세 0.3%"])
    withholding_missing = _missing(out["원천징수 합계 (자동)"])
    net_missing = _missing(out["실수령 예정액 (자동)"])
    for column in ["통역 매출액", "소득세 3%", "지방소득세 0.3%", "원천징수 합계 (자동)", "실수령 예정액 (자동)"]:
        out[column] = out[column].map(_number)

    # Sheet formulas are the source of truth. These fallbacks only make incomplete rows usable.
    tax_sum = out["소득세 3%"] + out["지방소득세 0.3%"]
    tax_parts_present = ~(income_tax_missing & local_tax_missing)
    fallback_tax = tax_sum.where(tax_parts_present, out["통역 매출액"] * 0.033)
    out["원천징수 합계 (자동)"] = out["원천징수 합계 (자동)"].where(
        ~withholding_missing,
        tax_sum.where(tax_sum.ne(0), fallback_tax),
    )
    fallback_net = out["통역 매출액"] - out["원천징수 합계 (자동)"]
    out["실수령 예정액 (자동)"] = out["실수령 예정액 (자동)"].where(
        ~net_missing,
        fallback_net,
    )
    for column in ["업무구분", "거래처 / 에이전시", "프로젝트 / 행사명", "지급명세서 여부", "입금상태", "메모", "장소"]:
        out[column] = out[column].fillna("").astype(str).str.strip()
    return out.dropna(how="all").reset_index(drop=True)


def period_bounds(df: pd.DataFrame, timezone: str = "Asia/Seoul") -> tuple[pd.Timestamp, pd.Timestamp]:
    today = pd.Timestamp.now(tz=timezone).tz_localize(None).normalize()
    dates = df["업무일"].dropna() if "업무일" in df else pd.Series(dtype="datetime64[ns]")
    if dates.empty:
        return today.replace(day=1), today
    return dates.min().normalize(), dates.max().normalize()


def dashboard_date_bounds(
    frames: dict[str, pd.DataFrame], timezone: str = "Asia/Seoul",
) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Return shared filter bounds, including interpretation-only activity."""
    dates: list[object] = []
    for name, column in [
        ("판매 및 반품", "처리일"), ("운영비", "발생일"),
        ("입출금", "거래일"), ("통역 매출", "업무일"),
    ]:
        frame = frames.get(name)
        if frame is not None and column in frame:
            dates.extend(frame[column].dropna().tolist())
    today = pd.Timestamp.now(tz=timezone).tz_localize(None).normalize()
    return (min(dates), max(dates)) if dates else (today.replace(day=1), today)


def selected_period(
    picked: object, fallback_start: pd.Timestamp, fallback_end: pd.Timestamp,
) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Normalize Streamlit's empty, partial, and complete date-range states."""
    if isinstance(picked, (tuple, list)):
        if len(picked) >= 2:
            return pd.Timestamp(picked[0]), pd.Timestamp(picked[1])
        if len(picked) == 1:
            day = pd.Timestamp(picked[0])
            return day, day
        return pd.Timestamp(fallback_start), pd.Timestamp(fallback_end)
    if picked is None:
        return pd.Timestamp(fallback_start), pd.Timestamp(fallback_end)
    day = pd.Timestamp(picked)
    return day, day


def filter_interpretation(
    df: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp,
    types: Iterable[str] = (), clients: Iterable[str] = (), venues: Iterable[str] = (),
    query: str = "",
) -> pd.DataFrame:
    out = df.copy()
    if not out.empty:
        out = out[out["업무일"].between(pd.Timestamp(start), pd.Timestamp(end), inclusive="both")]
    if types:
        out = out[out["업무구분"].isin(list(types))]
    if clients:
        out = out[out["거래처 / 에이전시"].isin(list(clients))]
    if venues:
        out = out[out["장소"].isin(list(venues))]
    if query:
        out = out[out.astype(str).apply(lambda col: col.str.contains(query, case=False, na=False)).any(axis=1)]
    return out


def venue_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Return interpretation-job counts and shares by venue, including missing venue data."""
    if df.empty:
        return pd.DataFrame(columns=["장소", "건수", "비중"])
    work = df.copy()
    work["장소"] = work["장소"].fillna("").astype(str).str.strip().replace("", "미입력")
    counts = work.groupby("장소", as_index=False).size().rename(columns={"size": "건수"})
    total = counts["건수"].sum()
    counts["비중"] = counts["건수"] / total if total else 0.0
    return counts.sort_values(["건수", "장소"], ascending=[False, True]).reset_index(drop=True)


def settlement_bucket(status: object) -> str:
    text = str(status or "").strip().replace(" ", "")
    if any(token in text for token in ("입금완료", "지급완료", "수령완료", "정산완료")):
        return "입금완료"
    if any(token in text for token in ("입금예정", "지급예정", "정산예정", "예정")):
        return "입금예정"
    return "미정산"


def statement_confirmed(value: object) -> bool:
    text = str(value or "").strip().lower().replace(" ", "")
    return text in {"y", "yes", "예", "확인", "확인완료", "제출", "발급", "완료"}


def with_status_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if out.empty:
        out["정산구분"] = pd.Series(dtype=str)
        out["지급명세서확인"] = pd.Series(dtype=bool)
        return out
    out["정산구분"] = out["입금상태"].map(settlement_bucket)
    out["지급명세서확인"] = out["지급명세서 여부"].map(statement_confirmed)
    return out


def interpretation_metrics(df: pd.DataFrame) -> dict[str, float]:
    checked = with_status_columns(df)
    revenue = float(checked["통역 매출액"].sum()) if "통역 매출액" in checked else 0.0
    withholding = float(checked["원천징수 합계 (자동)"].sum()) if "원천징수 합계 (자동)" in checked else 0.0
    net = float(checked["실수령 예정액 (자동)"].sum()) if "실수령 예정액 (자동)" in checked else 0.0
    unsettled = float(checked.loc[checked["정산구분"] != "입금완료", "실수령 예정액 (자동)"].sum()) if len(checked) else 0.0

    interpretation_count = int(len(checked))
    project_names = (
        checked["프로젝트 / 행사명"].fillna("").astype(str)
        .str.strip()
        .str.replace(r"\\s+", " ", regex=True)
    ) if "프로젝트 / 행사명" in checked else pd.Series(dtype=str)
    project_count = int(project_names[project_names.ne("")].nunique())

    return {
        "매출": revenue,
        "통역 건수": float(interpretation_count),
        "프로젝트 수": float(project_count),
        "평균 프로젝트 금액": revenue / project_count if project_count else 0.0,
        "원천징수 합계": withholding,
        "실수령 예정액": net,
        "미정산 금액": unsettled,
    }


def monthly_business_summary(monthly: pd.DataFrame, interpretation: pd.DataFrame) -> pd.DataFrame:
    base = monthly.copy()
    if base.empty:
        base = pd.DataFrame(columns=["월 시작"])
    if "월 시작" not in base:
        base["월 시작"] = pd.NaT
    base["월 시작"] = pd.to_datetime(base["월 시작"], errors="coerce")
    base = base.dropna(subset=["월 시작"]).copy()

    trans = interpretation.copy()
    if not trans.empty:
        trans = trans.dropna(subset=["업무일"]).copy()
        trans["월 시작"] = trans["업무일"].dt.to_period("M").dt.to_timestamp()
        trans = trans.groupby("월 시작", as_index=False)["통역 매출액"].sum()
    else:
        trans = pd.DataFrame({
            "월 시작": pd.Series(dtype="datetime64[ns]"),
            "통역 매출액": pd.Series(dtype=float),
        })

    out = base.merge(trans, on="월 시작", how="outer", suffixes=("", "_원천"))
    def numeric_column(name: str, default: float = 0.0) -> pd.Series:
        if name in out:
            return pd.to_numeric(out[name], errors="coerce").fillna(default)
        return pd.Series(default, index=out.index, dtype=float)

    if "통역 매출액_원천" in out:
        derived = out["통역 매출액_원천"].fillna(0)
    elif "통역 매출액" in out:
        derived = out["통역 매출액"].fillna(0)
    else:
        derived = pd.Series(0.0, index=out.index)
    if "통역 매출" in out:
        out["통역 매출"] = pd.to_numeric(out["통역 매출"], errors="coerce").fillna(derived)
    else:
        out["통역 매출"] = derived
    out["스마일피치노 매출"] = numeric_column("스마일피치노 매출") if "스마일피치노 매출" in out else numeric_column("매출")
    if "전체 매출" in out:
        overall = pd.to_numeric(out["전체 매출"], errors="coerce")
        # Legacy loaders expose 전체 매출=스마일피치노 매출. When a new translation
        # row exists, derive the combined amount until the sheet formula is filled.
        fallback = out["스마일피치노 매출"] + out["통역 매출"]
        out["전체 매출"] = overall.where(
            overall.notna() & ~((overall == out["스마일피치노 매출"]) & out["통역 매출"].ne(0)),
            fallback,
        )
    else:
        out["전체 매출"] = out["스마일피치노 매출"] + out["통역 매출"]

    shop_contribution = numeric_column("공헌이익")
    shop_management = numeric_column("관리손익")
    contribution = numeric_column("전체 공헌이익") if "전체 공헌이익" in out else shop_contribution
    management = numeric_column("전체 관리손익") if "전체 관리손익" in out else shop_management
    out["전체 공헌이익"] = contribution.where(
        contribution.notna() & ~((contribution == shop_contribution) & out["통역 매출"].ne(0)),
        shop_contribution + out["통역 매출"],
    )
    out["전체 관리손익"] = management.where(
        management.notna() & ~((management == shop_management) & out["통역 매출"].ne(0)),
        shop_management + out["통역 매출"],
    )
    return out.sort_values("월 시작").reset_index(drop=True)
