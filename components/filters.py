from __future__ import annotations
import pandas as pd
import streamlit as st

def period_filter(frames):
    dates=[]
    for name,col in [("판매 및 반품","처리일"),("운영비","발생일"),("입출금","거래일")]:
        if col in frames[name]: dates.extend(frames[name][col].dropna().tolist())
    today=pd.Timestamp.now(tz="Asia/Seoul").tz_localize(None).normalize()
    lo=min(dates) if dates else today.replace(day=1); hi=max(dates) if dates else today
    years=list(range(lo.year,hi.year+1)) or [today.year]
    with st.container(border=True):
        c1,c2,c3,c4=st.columns([1,1,2.2,2])
        year=c1.selectbox("연도",years,index=len(years)-1)
        month=c2.selectbox("월",["전체"]+list(range(1,13)),index=(hi.month if hi.year==year else 0))
        default_start=pd.Timestamp(year,1 if month=="전체" else month,1)
        default_end=default_start+(pd.offsets.YearEnd(0) if month=="전체" else pd.offsets.MonthEnd(0))
        a=max(default_start,lo); b=min(default_end,hi) if default_end>=lo else default_end
        if a>b: a,b=default_start,default_end
        picked=c3.date_input("조회 기간",(a.date(),b.date()))
        query=c4.text_input("검색",placeholder="주문번호, 상품, SKU…")
    if isinstance(picked,(tuple,list)) and len(picked)==2: start,end=picked
    else: start=end=picked
    return pd.Timestamp(start),pd.Timestamp(end),query

def multiselect(df,column,label=None):
    values=sorted(df[column].dropna().astype(str).unique().tolist()) if column in df else []
    return st.multiselect(label or column,values)
def search_rows(df,query):
    if not query or df.empty:return df
    return df[df.astype(str).apply(lambda c:c.str.contains(query,case=False,na=False)).any(axis=1)]

