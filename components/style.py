import streamlit as st

def apply_style():
    st.markdown("""<style>
    .stApp{background:#f7f8fb;color:#18212f}.block-container{padding-top:2rem;max-width:1500px}
    [data-testid="stSidebar"]{background:#fff;border-right:1px solid #e7eaf0}
    div[data-testid="stMetric"]{background:#fff;border:1px solid #e7eaf0;border-radius:16px;padding:16px 18px;box-shadow:0 5px 20px rgba(27,38,59,.04)}
    div[data-testid="stMetricLabel"]{color:#667085}div[data-testid="stMetricValue"]{font-weight:750;color:#152238}
    .bw-title{font-size:2rem;font-weight:800;letter-spacing:-.04em}.bw-sub{color:#667085;margin:-8px 0 20px}
    .insight{background:#fff;border:1px solid #e7eaf0;border-left:4px solid #6b7cff;border-radius:12px;padding:12px 14px;margin:8px 0}
    .ok{border-left-color:#25a46f}.warn{border-left-color:#f59e0b}.danger{border-left-color:#e05252}
    @media(max-width:900px){.block-container{padding:1rem}.bw-title{font-size:1.55rem}}
    </style>""",unsafe_allow_html=True)

