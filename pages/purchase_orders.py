import pandas as pd
import plotly.express as px
import streamlit as st
from components.filters import multiselect,period_filter,search_rows
from components.kpi_cards import metrics,num,won
from components.style import chart_style,section_title
from components.tables import show
from runtime import context,title
from services.calculations import delayed_orders,filter_dates,filter_text

d=context(); f=d.frames; title("발주","발주 진행, 입고 잔량과 납기 위험을 관리합니다.")
start,end,query=period_filter(f); base=filter_dates(f["발주"],"발주일",start,end)
vendors=multiselect(base,"거래처","거래처"); po=search_rows(filter_text(base,{"거래처":vendors}),query)
today=pd.Timestamp.now(tz=d.settings.timezone).date(); late=delayed_orders(po,today)
metrics([("전체 발주",num(po["발주번호"].nunique()),None),("진행중",num((po["상태"]=="진행중").sum()),None),("완료",num((po["상태"]=="완료").sum()),None),("미입고수량",num(po["미입고수량"].sum()),None),("발주 예정금액",won(po["예상 발주액"].sum()),None),("납기 지연",num(len(late)),None)],6)
if len(late): st.error(f"입고예정일이 지났지만 미입고수량이 남은 발주가 {len(late)}건 있습니다.")
po=po.copy(); po["표시상태"]=po["상태"]
po.loc[po.index.isin(late.index),"표시상태"]="납기 확인"
with st.container(border=True):
    section_title("거래처별 발주액"); vendor=po.groupby("거래처")["예상 발주액"].sum().reset_index()
    st.plotly_chart(chart_style(px.bar(vendor,x="거래처",y="예상 발주액",color_discrete_sequence=["#3b82f6"]),245,False),use_container_width=True,config={"displayModeBar":False})
section_title("발주 상세"); cols=["발주번호","발주일","거래처","SKU","상품명 (자동)","발주수량","누적 입고수량","미입고수량","입고예정일","예상 발주액","표시상태"]
show(po.sort_values(["미입고수량","입고예정일"],ascending=[False,True])[cols],currency=["예상 발주액"])
