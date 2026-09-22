from __future__ import annotations

from datetime import date
import pandas as pd


DATE_BY_SHEET = {"판매 및 반품":"처리일", "발주":"발주일", "운영비":"발생일", "입출금":"거래일", "입고 및 재고 조정":"일자", "월별실적":"월 시작"}


def filter_dates(df: pd.DataFrame, column: str, start, end) -> pd.DataFrame:
    if df.empty or column not in df:
        return df.copy()
    dates = pd.to_datetime(df[column], errors="coerce")
    return df.loc[dates.between(pd.Timestamp(start), pd.Timestamp(end), inclusive="both")].copy()


def filter_text(df: pd.DataFrame, selections: dict[str, list[str] | str]) -> pd.DataFrame:
    out = df.copy()
    for col, values in selections.items():
        if col not in out or values in (None, "", []):
            continue
        vals = [values] if isinstance(values, str) else values
        out = out[out[col].astype(str).isin(vals)]
    return out


def monthly_raw(sales: pd.DataFrame, expenses: pd.DataFrame, cash: pd.DataFrame) -> pd.DataFrame:
    parts = []
    if not sales.empty:
        x=sales.copy(); x["월"]=x["처리일"].dt.to_period("M").dt.to_timestamp()
        x["판매 부대비"]=x[["수수료","택배비","포장비"]].sum(axis=1)
        parts.append(x.groupby("월")[["매출 합계","매출원가","판매 부대비","공헌이익"]].sum().rename(columns={"매출 합계":"매출"}))
    result = parts[0] if parts else pd.DataFrame(index=pd.DatetimeIndex([], name="월"))
    if not expenses.empty:
        x=expenses.copy(); x["월"]=x["발생일"].dt.to_period("M").dt.to_timestamp()
        result=result.join(x.groupby("월")["금액"].sum().rename("운영비"), how="outer")
    if not cash.empty:
        x=cash.copy(); x["월"]=x["거래일"].dt.to_period("M").dt.to_timestamp()
        result=result.join(x.groupby("월")[["입금","출금"]].sum().rename(columns={"입금":"실제 입금","출금":"실제 출금"}), how="outer")
    result=result.fillna(0).reset_index()
    result["관리손익"]=result.get("공헌이익",0)-result.get("운영비",0)
    result["순현금흐름"]=result.get("실제 입금",0)-result.get("실제 출금",0)
    return result


def product_summary(sales: pd.DataFrame) -> pd.DataFrame:
    columns = ["SKU","상품명 (자동)","판매수량","매출","매출원가","판매부대비","공헌이익","공헌이익률"]
    if sales.empty:
        return pd.DataFrame(columns=columns)
    x=sales.copy(); x["판매부대비"]=x[["수수료","택배비","포장비"]].sum(axis=1)
    out=x.groupby(["SKU","상품명 (자동)"],dropna=False).agg(판매수량=("재고 차감수량","sum"),매출=("매출 합계","sum"),매출원가=("매출원가","sum"),판매부대비=("판매부대비","sum"),공헌이익=("공헌이익","sum")).reset_index()
    out["공헌이익률"]=out["공헌이익"].div(out["매출"].replace(0,pd.NA)).fillna(0)
    return out


def channel_summary(sales: pd.DataFrame) -> pd.DataFrame:
    columns = ["판매채널","주문건수","판매수량","매출","공헌이익","공헌이익률"]
    if sales.empty:
        return pd.DataFrame(columns=columns)
    return sales.groupby("판매채널",dropna=False).agg(주문건수=("주문번호","nunique"),판매수량=("재고 차감수량","sum"),매출=("매출 합계","sum"),공헌이익=("공헌이익","sum")).reset_index().assign(공헌이익률=lambda x:x["공헌이익"].div(x["매출"].replace(0,pd.NA)).fillna(0))


def delayed_orders(purchases: pd.DataFrame, today: date) -> pd.DataFrame:
    if purchases.empty:
        return purchases.copy()
    due=pd.to_datetime(purchases["입고예정일"],errors="coerce")
    return purchases[(purchases["미입고수량"]>0)&(due.dt.date<today)].copy()

