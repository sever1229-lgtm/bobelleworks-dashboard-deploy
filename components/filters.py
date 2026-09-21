from __future__ import annotations
import pandas as pd
import streamlit as st

from services.interpretation import dashboard_date_bounds

def period_filter(frames,show_search=True):
    lo,hi=dashboard_date_bounds(frames)
    today=pd.Timestamp.now(tz="Asia/Seoul").tz_localize(None).normalize()
    max_year=max(hi.year,today.year)
    years=list(range(lo.year,max_year+1)) or [today.year]
    with st.container(border=False):
        cols=st.columns([.8,.8,2.15,1.75] if show_search else [.8,.8,2.15],gap="small")
        c1,c2,c3=cols[:3]
        year=c1.selectbox("연도",years,index=(years.index(today.year) if today.year in years else len(years)-1))
        month=c2.selectbox("월",["전체"]+list(range(1,13)),index=(today.month if today.year==year else 0))
        default_start=pd.Timestamp(year,1 if month=="전체" else month,1)
        default_end=default_start+(pd.offsets.YearEnd(0) if month=="전체" else pd.offsets.MonthEnd(0))
        # Default query range always begins on the first day of the selected month/year.
        # Do not move the start date forward to the first date that happens to contain data.
        a=default_start
        if year==today.year and (month=="전체" or month==today.month):
            b=min(default_end,today)
        else:
            b=default_end
        if a>b: a,b=default_start,default_end
        picked=c3.date_input("조회 기간",(a.date(),b.date()))
        query=cols[3].text_input("통합 검색",placeholder="주문번호, 상품, SKU…") if show_search else st.session_state.get("global_search","")
    if isinstance(picked,(tuple,list)):
        if len(picked)==2: start,end=picked
        elif len(picked)==1: start=end=picked[0]
        else: start,end=a.date(),b.date()
    else: start=end=picked
    return pd.Timestamp(start),pd.Timestamp(end),query

def multiselect(df,column,label=None):
    values=sorted(df[column].dropna().astype(str).unique().tolist()) if column in df else []
    return st.multiselect(label or column,values)
def search_rows(df,query):
    if not query or df.empty:return df
    return df[df.astype(str).apply(lambda c:c.str.contains(query,case=False,na=False)).any(axis=1)]
