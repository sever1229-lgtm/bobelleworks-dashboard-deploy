import plotly.express as px
import streamlit as st
from components.filters import multiselect,period_filter,search_rows
from components.kpi_cards import metrics,num,won
from components.style import chart_style,section_title
from components.tables import show
from runtime import context,title
from services.calculations import channel_summary,filter_dates,filter_text

d=context(); f=d.frames; title("주문·판매","판매 및 반품 원천 데이터를 채널과 주문 단위로 분석합니다.")
start,end,query=period_filter(f); base=filter_dates(f["판매 및 반품"],"처리일",start,end)
channels=multiselect(base,"판매채널","판매채널"); sales=search_rows(filter_text(base,{"판매채널":channels}),query)
sold=sales[sales["구분"]=="판매"]; returns=sales[sales["구분"]=="반품"]; orders=sold["주문번호"].nunique(); revenue=sales["매출 합계"].sum()
metrics([("총 주문건수",num(orders),None),("판매수량",num(sold["수량"].sum()),None),("반품건수",num(returns["주문번호"].nunique()),None),("순매출",won(revenue),None),("평균 주문금액",won(revenue/orders if orders else 0),None)],5)
summary=channel_summary(sales)
c1,c2=st.columns([1.2,1],gap="small")
with c1:
    with st.container(border=True):
        section_title("판매채널별 성과")
        if len(summary): st.plotly_chart(chart_style(px.bar(summary,x="판매채널",y=["매출","공헌이익"],barmode="group",color_discrete_sequence=["#3b82f6","#20b486"]),255),use_container_width=True,config={"displayModeBar":False})
with c2:
    with st.container(border=True):
        section_title("채널별 핵심 지표")
        show(summary,currency=["매출","공헌이익"],percent=["공헌이익률"],height=255)
section_title("최근 주문")
cols=["처리일","주문번호","판매채널","상품명 (자동)","SKU","수량","매출 합계","공헌이익","구분"]
show(sales.sort_values("처리일",ascending=False)[cols],currency=["매출 합계","공헌이익"])
