import pandas as pd
import streamlit as st


def _won_text(value):
    if value is None or pd.isna(value) or value == "":
        return ""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    sign = "-" if number < 0 else ""
    return f"{sign}₩{abs(number):,.0f}"


def show(df: pd.DataFrame, currency=(), percent=(), height=420):
    display = df.copy()

    # Dashboard tables show calendar dates only. Time is not an operational field.
    for c in display.columns:
        if pd.api.types.is_datetime64_any_dtype(display[c]):
            display[c] = display[c].dt.strftime("%y-%m-%d").fillna("")

    # Currency columns are rendered as text so thousands separators are always
    # visible consistently in Streamlit dataframes (e.g. ₩1,000,000).
    for c in currency:
        if c in display:
            display[c] = display[c].map(_won_text)

    formats = {}
    for c in percent:
        if c in display:
            display[c] = pd.to_numeric(display[c], errors="coerce") * 100
            formats[c] = st.column_config.NumberColumn(c, format="%.1f%%")

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        height=min(height, 38 * (len(display) + 1) + 4),
        column_config=formats,
    )
