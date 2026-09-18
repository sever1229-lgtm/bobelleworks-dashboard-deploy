from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pandas as pd
import streamlit as st

from config.settings import (
    DATE_COLUMNS, EMPTY_FRAME_COLUMNS, EXPECTED_SHEETS, NUMERIC_COLUMNS,
    OPTIONAL_SHEETS, RANGES, Settings,
)
from services.google_sheets import GoogleSheetsError, open_spreadsheet, read_range, spreadsheet_timezone


@dataclass
class DashboardData:
    frames: dict[str, pd.DataFrame]
    sheet_timezone: str
    loaded_at: datetime
    settings: Settings


def _to_frame(values: list[list[Any]]) -> pd.DataFrame:
    if not values:
        return pd.DataFrame()
    width = len(values[0])
    rows = [(row + [None] * width)[:width] for row in values[1:]]
    df = pd.DataFrame(rows, columns=[str(x).strip() for x in values[0]])
    df = df.dropna(how="all")
    if len(df.columns):
        df = df[df.iloc[:, 0].notna() & (df.iloc[:, 0].astype(str).str.strip() != "")]
    return df.reset_index(drop=True)


def _number(value: Any) -> float:
    if value is None or value == "":
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "").replace("₩", "").replace("원", "")
    if text in {"-", "—"}:
        return 0.0
    if text.endswith("%"):
        text = text[:-1]
        try:
            return float(text) / 100
        except ValueError:
            return 0.0
    try:
        return float(text)
    except ValueError:
        return 0.0


def _date(value: Any):
    if value in (None, ""):
        return pd.NaT
    if isinstance(value, (int, float)):
        return pd.Timestamp("1899-12-30") + pd.to_timedelta(float(value), unit="D")
    return pd.to_datetime(value, errors="coerce")


def _add_monthly_compatibility_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Expose stable generic columns while using Smile Peachino-branded sheet columns."""
    out = df.copy()

    if "전체 매출" not in out and "매출" in out:
        out["전체 매출"] = out["매출"]

    if "스마일피치노 매출" not in out:
        out["스마일피치노 매출"] = out.get("매출", out.get("전체 매출", 0))

    if "통역 매출" not in out:
        out["통역 매출"] = pd.NA

    # Existing Smile Peachino detail pages use generic metric names internally.
    if "매출" not in out:
        out["매출"] = out.get("스마일피치노 매출", out.get("전체 매출", 0))
    if "매출원가" not in out and "스마일피치노 매출원가" in out:
        out["매출원가"] = out["스마일피치노 매출원가"]
    if "판매 부대비" not in out and "스마일피치노 판매 부대비" in out:
        out["판매 부대비"] = out["스마일피치노 판매 부대비"]

    # Preserve current dashboard behavior where only total profit columns exist.
    if "공헌이익" not in out and "전체 공헌이익" in out:
        out["공헌이익"] = out["전체 공헌이익"]
    if "관리손익" not in out and "전체 관리손익" in out:
        out["관리손익"] = out["전체 관리손익"]
    if "전체 공헌이익" not in out:
        out["전체 공헌이익"] = out.get("공헌이익", 0)
    if "전체 관리손익" not in out:
        out["전체 관리손익"] = out.get("관리손익", 0)

    return out


def normalize_frame(name: str, df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for column in NUMERIC_COLUMNS.get(name, []):
        if column in out:
            out[column] = out[column].map(_number)
    for column in DATE_COLUMNS.get(name, []):
        if column in out:
            out[column] = out[column].map(_date)
    if name == "월별실적":
        out = _add_monthly_compatibility_columns(out)
    return out


def _dashboard_settings(book) -> dict[str, Any]:
    values = read_range(book, "대시보드", "A4:E15")

    def cell(r: int, c: int, default=None):
        try:
            return values[r][c]
        except (IndexError, TypeError):
            return default

    return {
        "조회 연도": cell(0, 1), "조회 월": cell(1, 1), "조회 시작": _date(cell(0, 4)),
        "조회 종료": _date(cell(1, 4)), "시작 기초자금": _number(cell(2, 1)),
        "기록 시작일": _date(cell(3, 1)),
    }


def _empty_optional_frame(name: str) -> pd.DataFrame:
    return normalize_frame(name, pd.DataFrame(columns=EMPTY_FRAME_COLUMNS.get(name, [])))


def _load_uncached(spreadsheet_id: str, timezone: str, cache_buster: int) -> DashboardData:
    settings = Settings(spreadsheet_id=spreadsheet_id, timezone=timezone)
    book = open_spreadsheet(spreadsheet_id)
    available = {ws.title for ws in book.worksheets()}
    missing = set(EXPECTED_SHEETS) - available
    if missing:
        raise ValueError("필수 시트가 없습니다: " + ", ".join(sorted(missing)))

    frames = {}
    for name, a1 in RANGES.items():
        if name == "대시보드":
            continue
        if name in OPTIONAL_SHEETS and name not in available:
            frames[name] = _empty_optional_frame(name)
            continue
        frames[name] = normalize_frame(name, _to_frame(read_range(book, name, a1)))

    frames["대시보드"] = pd.DataFrame([_dashboard_settings(book)])
    return DashboardData(frames, spreadsheet_timezone(book), datetime.now(), settings)


@st.cache_data(ttl=Settings().cache_ttl, show_spinner="Google Sheets에서 최신 데이터를 불러오는 중입니다...")
def load_dashboard_data(spreadsheet_id: str, timezone: str, cache_buster: int = 0) -> DashboardData:
    return _load_uncached(spreadsheet_id, timezone, cache_buster)
