import streamlit as st

def won(value):
    value=float(value or 0); sign="-" if value<0 else ""; return f"{sign}₩{abs(value):,.0f}"
def pct(value): return f"{float(value or 0):.1%}"
def num(value): return f"{float(value or 0):,.0f}"
def metrics(items, columns=4):
    cols=st.columns(columns)
    for i,(label,value,help_text) in enumerate(items): cols[i%columns].metric(label,value,help=help_text)

