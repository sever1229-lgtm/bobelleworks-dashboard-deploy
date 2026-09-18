import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from components.filters import period_filter
from components.kpi_cards import metrics,pct,won
from components.style import chart_style,footnote,section_title
from components.tables import show
from runtime import context,title
from services.calculations import filter_dates

d=context(); f=d.frames; title("매출·손익","월별실적을 기준으로 수익 구조와 판매부대비를 분석합니다.")
start,end,_=period_filter(f); monthly=f["월별실적"]
m=monthly[monthly["월 시작"].between(start.to_period("M").start_time,end.to_period("M").start_time)].copy()
sales=filter_dates(f["판매 및 반품"],"처리일",start,end); t=m.select_dtypes("number").sum(); rev=t.get("매출",0); rate=t.get("공헌이익",0)/rev if rev else 0
metrics([("매출",won(rev),None),("매출원가",won(t.get("매출원가",0)),None),("판매부대비",won(t.get("판매 부대비",0)),None),("공헌이익",won(t.get("공헌이익",0)),"회계상 순이익과 다른 내부 운영 지표"),("공헌이익률",pct(rate),None),("운영비",won(t.get("운영비",0)),None),("관리손익",won(t.get("관리손익",0)),"세금·감가상각을 반영한 당기순이익과 다름")],7)
c1,c2=st.columns(2)
with c1:
    with st.container(border=True):
        section_title("손익 구조")
        vals=[rev,-t.get("매출원가",0),-t.get("판매 부대비",0),t.get("공헌이익",0),-t.get("운영비",0),t.get("관리손익",0)]
        fig=go.Figure(go.Waterfall(x=["매출","매출원가","판매부대비","공헌이익","운영비","관리손익"],measure=["absolute","relative","relative","total","relative","total"],y=vals,connector={"line":{"color":"#ccd2df"}})); st.plotly_chart(chart_style(fig,260),use_container_width=True,config={"displayModeBar":False})
with c2:
    with st.container(border=True):
        section_title("판매부대비 구성")
        side=pd.DataFrame({"항목":["수수료","택배비","포장비"],"금액":[sales["수수료"].sum(),sales["택배비"].sum(),sales["포장비"].sum()]})
        fig=px.pie(side,names="항목",values="금액",hole=.62,color_discrete_sequence=["#3b82f6","#20b486","#f59e42"])
        st.plotly_chart(chart_style(fig,260),use_container_width=True,config={"displayModeBar":False})
with st.container(border=True):
    section_title("월별 매출·이익 추이")
    long=m.melt(id_vars=["월 시작"],value_vars=["매출","공헌이익","관리손익"],var_name="항목",value_name="금액")
    st.plotly_chart(chart_style(px.bar(long,x="월 시작",y="금액",color="항목",barmode="group",color_discrete_sequence=["#3b82f6","#20b486","#ec5f8c"]),260),use_container_width=True,config={"displayModeBar":False})
footnote("공헌이익과 관리손익은 내부 운영 판단용 지표입니다. 세금, 감가상각 등 회계 조정을 포함한 회계상 순이익과 다릅니다.", boxed=True)
