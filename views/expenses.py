import plotly.express as px
import streamlit as st
from components.filters import multiselect,period_filter,search_rows
from components.kpi_cards import metrics,num,won
from components.style import chart_style,section_title
from components.tables import show
from runtime import context,title
from services.calculations import filter_dates,filter_text

d=context(); f=d.frames; title("비용","운영비의 발생 시점과 항목별 비중을 분석합니다.")
start,end,query=period_filter(f); base=filter_dates(f["운영비"],"발생일",start,end)
types=multiselect(base,"비용구분","비용구분"); ex=search_rows(filter_text(base,{"비용구분":types}),query)
all_ex=f["운영비"]; current_month=all_ex[all_ex["발생일"].dt.to_period("M")==end.to_period("M")]
metrics([("이번 달 운영비",won(current_month["금액"].sum()),None),("선택 기간 운영비",won(ex["금액"].sum()),None),("누적 운영비",won(all_ex["금액"].sum()),None),("비용 항목 수",num(ex["비용구분"].nunique()),None)],4)
ex=ex.copy(); ex["월"]=ex["발생일"].dt.to_period("M").astype(str)
c1,c2=st.columns(2)
with c1:
    with st.container(border=True):
        section_title("월별 운영비"); st.plotly_chart(chart_style(px.line(ex.groupby("월")["금액"].sum().reset_index(),x="월",y="금액",markers=True,color_discrete_sequence=["#3b82f6"]),250,False),use_container_width=True,config={"displayModeBar":False})
with c2:
    with st.container(border=True):
        section_title("비용 비중"); by=ex.groupby("비용구분")["금액"].sum().reset_index(); st.plotly_chart(chart_style(px.pie(by,names="비용구분",values="금액",hole=.62,color_discrete_sequence=["#3b82f6","#20b486","#ec5f8c","#8b5cf6","#f59e42"]),250),use_container_width=True,config={"displayModeBar":False})
with st.container(border=True):
    section_title("월 × 비용구분"); stack=ex.groupby(["월","비용구분"])["금액"].sum().reset_index(); st.plotly_chart(chart_style(px.bar(stack,x="월",y="금액",color="비용구분",barmode="stack"),235),use_container_width=True,config={"displayModeBar":False})
section_title("비용 상세"); show(ex[["발생일","비용구분","거래처","내용","금액","증빙 / 메모"]],currency=["금액"])
