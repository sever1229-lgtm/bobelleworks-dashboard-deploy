from __future__ import annotations

import json
import os
from typing import Any

import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly", "https://www.googleapis.com/auth/drive.readonly"]


class GoogleSheetsError(RuntimeError):
    pass


def _secret(name: str, default: Any = None) -> Any:
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


def _credentials() -> Credentials:
    secret_info = _secret("gcp_service_account")
    if secret_info:
        return Credentials.from_service_account_info(dict(secret_info), scopes=SCOPES)
    raw = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if raw:
        return Credentials.from_service_account_info(json.loads(raw), scopes=SCOPES)
    path = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
    if path:
        return Credentials.from_service_account_file(path, scopes=SCOPES)
    raise GoogleSheetsError("Google 인증정보가 없습니다. .streamlit/secrets.toml 또는 .env를 설정해 주세요.")


def open_spreadsheet(spreadsheet_id: str):
    try:
        return gspread.authorize(_credentials()).open_by_key(spreadsheet_id)
    except GoogleSheetsError:
        raise
    except Exception as exc:
        raise GoogleSheetsError(f"Google Spreadsheet 연결에 실패했습니다: {exc}") from exc


def read_range(book, sheet_name: str, a1_range: str) -> list[list[Any]]:
    try:
        return book.worksheet(sheet_name).get(a1_range, value_render_option="UNFORMATTED_VALUE")
    except Exception as exc:
        raise GoogleSheetsError(f"'{sheet_name}' 데이터를 읽지 못했습니다: {exc}") from exc


def spreadsheet_timezone(book) -> str:
    try:
        return book.fetch_sheet_metadata(params={"fields": "properties.timeZone"})["properties"]["timeZone"]
    except Exception:
        return "알 수 없음"

