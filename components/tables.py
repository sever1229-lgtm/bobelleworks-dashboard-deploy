import pandas as pd
import streamlit as st

def show(df: pd.DataFrame, currency=(), percent=(), height=420):
    formats={c:st.column_config.NumberColumn(c,format="₩%d") for c in currency if c in df}
    formats.update({c:st.column_config.NumberColumn(c,format="%.1f%%") for c in percent if c in df})
    display=df.copy()
    for c in percent:
        if c in display: display[c]=display[c]*100
    st.dataframe(display,use_container_width=True,hide_index=True,height=min(height,38*(len(display)+1)+4),column_config=formats)

