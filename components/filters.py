from __future__ import annotations
import inspect
from pathlib import Path

import pandas as pd
import streamlit as st

from services.interpretation import dashboard_date_bounds


def calendar_period(year, month, today):
    """Return the date range represented by a year/month selector."""
    today = pd.Timestamp(today).normalize()
    if month == "전체":
        start = pd.Timestamp(int(year), 1, 1)
        end = pd.Timestamp(int(year), 12, 31)
        if int(year) == today.year:
            end = today
        return start, end

    month = int(month)
    start = pd.Timestamp(int(year), month, 1)
    end = start + pd.offsets.MonthEnd(0)
    if int(year) == today.year and month == today.month:
        end = today
    return start, end


def period_filter(frames,show_search=True):
    lo,hi=dashboard_date_bounds(frames)
    today=pd.Timestamp.now(tz="Asia/Seoul").tz_localize(None).normalize()
    initial_start=(today-pd.DateOffset(years=1)).to_period("M").start_time
    initial_end=today.to_period("M").end_time.normalize()
    min_year=min(lo.year,initial_start.year)
    max_year=max(hi.year,today.year)
    years=list(range(min_year,max_year+1)) or [today.year]

    # Keep each dashboard page's filter state independent.
    caller=Path(inspect.stack()[1].filename).stem
    prefix=f"period_{caller}"
    year_key=f"{prefix}_year"
    month_key=f"{prefix}_month"
    # v4 intentionally uses a fresh widget key so stale single-date state from
    # earlier versions cannot override the intended date-range default.
    range_key=f"{prefix}_range_v4"
    selector_key=f"{prefix}_selector_v4"

    with st.container(border=False):
        cols=st.columns([.8,.8,2.15,1.75] if show_search else [.8,.8,2.15],gap="small")
        c1,c2,c3=cols[:3]
        year=c1.selectbox(
            "연도",
            years,
            index=(years.index(today.year) if today.year in years else len(years)-1),
            key=year_key,
        )
        month=c2.selectbox(
            "월",
            ["전체"]+list(range(1,13)),
            index=(today.month if today.year==year else 0),
            key=month_key,
        )

        selector=(int(year),month)
        previous=st.session_state.get(selector_key)
        active_range_key=f"{prefix}_range_v5_{int(year)}_{month}"

        if previous is None:
            # First page load: same month one year ago (day 1) through current month end.
            default_start, default_end = initial_start, initial_end
            st.session_state[selector_key]=selector
        elif previous != selector:
            # Year/month changed: reset the date widget to the selected calendar period.
            default_start, default_end = calendar_period(year,month,today)
            st.session_state.pop(active_range_key, None)
            st.session_state[selector_key]=selector
        else:
            # Existing selector: the widget keeps any manually chosen range.
            default_start, default_end = initial_start, initial_end

        picked=c3.date_input(
            "조회 기간",
            value=(default_start.date(),default_end.date()),
            key=active_range_key,
        )
        query=cols[3].text_input("통합 검색",placeholder="주문번호, 상품, SKU…") if show_search else st.session_state.get("global_search","")

    if isinstance(picked,(tuple,list)):
        if len(picked)==2: start,end=picked
        elif len(picked)==1: start=end=picked[0]
        else: start,end=initial_start.date(),initial_end.date()
    else:
        start=end=picked
    return pd.Timestamp(start),pd.Timestamp(end),query


def multiselect(df,column,label=None):
    values=sorted(df[column].dropna().astype(str).unique().tolist()) if column in df else []
    return st.multiselect(label or column,values)


def search_rows(df,query):
    if not query or df.empty:return df
    return df[df.astype(str).apply(lambda c:c.str.contains(query,case=False,na=False)).any(axis=1)]
