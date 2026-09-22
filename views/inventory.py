import plotly.express as px
import streamlit as st
from components.filters import multiselect,period_filter,search_rows
from components.kpi_cards import metrics,num,won
from components.style import chart_style,section_title
from components.tables import show
from runtime import context,title

d=context(); f=d.frames; title("재고","현재고, 안전재고와 재고자산을 SKU 단위로 확인합니다.")
_,_,query=period_filter(f); inv=f["재고현황"].merge(f["상품·SKU관리"][["SKU","카테고리"]],on="SKU",how="left")
status=st.selectbox("재고 상태",["전체","보충 필요 우선","보충 필요","음수재고 확인","정상"])
if status=="보충 필요 우선": inv["_priority"]=inv["상태"].map({"음수재고 확인":0,"보충 필요":1}).fillna(2); inv=inv.sort_values(["_priority","보충 필요수량"],ascending=[True,False])
elif status=="정상": inv=inv[inv["상태"].fillna("")==""]
elif status!="전체": inv=inv[inv["상태"]==status]
inv=search_rows(inv,query); po=f["발주"]
metrics([("현재고",num(f["재고현황"]["현재고"].sum()),None),("재고자산",won(f["재고현황"]["참고 재고가액"].sum()),None),("보충 필요 SKU",num((f["재고현황"]["상태"]=="보충 필요").sum()),None),("음수재고 SKU",num((f["재고현황"]["상태"]=="음수재고 확인").sum()),None),("미입고수량",num(po["미입고수량"].sum()),None)],5)
c1,c2=st.columns([1.6,1])
with c1:
    with st.container(border=True):
        section_title("SKU별 현재고 vs 안전재고"); long=inv.melt(id_vars=["SKU"],value_vars=["현재고","안전재고"],var_name="구분",value_name="수량")
        st.plotly_chart(chart_style(px.bar(long,x="SKU",y="수량",color="구분",barmode="group",color_discrete_sequence=["#3b82f6","#ec5f8c"]),260),use_container_width=True,config={"displayModeBar":False})
with c2:
    with st.container(border=True):
        section_title("카테고리별 재고자산"); cat=inv.groupby("카테고리",dropna=False)["참고 재고가액"].sum().reset_index()
        st.plotly_chart(chart_style(px.pie(cat,names="카테고리",values="참고 재고가액",hole=.62,color_discrete_sequence=["#3b82f6","#20b486","#ec5f8c","#8b5cf6"]),260),use_container_width=True,config={"displayModeBar":False})
section_title("재고 상세")
color_text = inv["색상"].fillna("").astype(str).str.replace(r"\.0$", "", regex=True)
size_text = inv["사이즈"].fillna("").astype(str).str.replace(r"\.0$", "", regex=True)
option_text = (color_text + " / " + size_text).str.strip(" /")
table=inv.assign(옵션=option_text,상태=inv["상태"].replace("","정상").fillna("정상"))
show(table[["SKU","상품명","옵션","카테고리","현재고","안전재고","보충 필요수량","참고 재고가액","상태"]],currency=["참고 재고가액"])
