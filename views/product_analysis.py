import plotly.express as px
import streamlit as st
from components.filters import multiselect,period_filter,search_rows
from components.kpi_cards import metrics,num,pct,won
from components.style import chart_style,section_title
from components.tables import show
from runtime import context,title
from services.calculations import filter_dates,filter_text,product_summary

d=context(); f=d.frames; title("상품 분석","SKU별 매출 규모와 실제 공헌이익률을 함께 봅니다.")
start,end,query=period_filter(f); sales=filter_dates(f["판매 및 반품"],"처리일",start,end)
products=multiselect(sales,"상품명 (자동)","상품"); skus=multiselect(sales,"SKU","SKU")
sales=search_rows(filter_text(sales,{"상품명 (자동)":products,"SKU":skus}),query); p=product_summary(sales)
total_revenue=p["매출"].sum() if len(p) else 0; total_profit=p["공헌이익"].sum() if len(p) else 0
metrics([("분석 SKU",num(len(p)),None),("판매수량",num(p["판매수량"].sum() if len(p) else 0),None),("매출",won(total_revenue),None),("공헌이익",won(total_profit),None),("공헌이익률",pct(total_profit/total_revenue if total_revenue else 0),None),("저수익 SKU",num(((p["공헌이익률"]<.2)&(p["매출"]>0)).sum() if len(p) else 0),"공헌이익률 20% 미만")],6)
order=st.selectbox("정렬",["매출 높은 순","공헌이익 높은 순","공헌이익률 높은 순","공헌이익률 낮은 순"])
mapping={"매출 높은 순":("매출",False),"공헌이익 높은 순":("공헌이익",False),"공헌이익률 높은 순":("공헌이익률",False),"공헌이익률 낮은 순":("공헌이익률",True)}
if len(p): p=p.sort_values(mapping[order][0],ascending=mapping[order][1])
c1,c2=st.columns(2)
with c1:
    with st.container(border=True):
        section_title("매출 TOP")
        if len(p):
            st.plotly_chart(chart_style(px.bar(p.nlargest(10,"매출"),x="SKU",y="매출",color_discrete_sequence=["#3b82f6"],labels={"SKU":"SKU","매출":"매출"}),260,False),use_container_width=True,config={"displayModeBar":False})
        else:
            st.info("선택 기간에 판매 데이터가 없습니다.")
with c2:
    with st.container(border=True):
        section_title("공헌이익 TOP")
        if len(p):
            st.plotly_chart(chart_style(px.bar(p.nlargest(10,"공헌이익"),x="SKU",y="공헌이익",color_discrete_sequence=["#20b486"],labels={"SKU":"SKU","공헌이익":"공헌이익"}),260,False),use_container_width=True,config={"displayModeBar":False})
        else:
            st.info("선택 기간에 판매 데이터가 없습니다.")
c3,c4=st.columns([1.35,1],gap="small")
with c3:
    with st.container(border=True):
        section_title("매출 vs 공헌이익률")
        if len(p):
            st.plotly_chart(chart_style(px.scatter(p,x="매출",y="공헌이익률",size="판매수량",color="상품명 (자동)",hover_name="SKU"),250),use_container_width=True,config={"displayModeBar":False})
        else:
            st.info("선택 기간에 판매 데이터가 없습니다.")
with c4:
    with st.container(border=True):
        section_title("저수익 상품"); show(p[p["매출"]>0].nsmallest(5,"공헌이익률")[["SKU","상품명 (자동)","매출","공헌이익","공헌이익률"]],currency=["매출","공헌이익"],percent=["공헌이익률"],height=250)
section_title("상품별 수익성"); show(p,currency=["매출","매출원가","판매부대비","공헌이익"],percent=["공헌이익률"])
