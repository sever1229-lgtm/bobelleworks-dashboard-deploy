from datetime import date, datetime
from numbers import Number

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


COLORS = {
    "navy": "#14243a",
    "blue": "#3b82f6",
    "green": "#20b486",
    "pink": "#ec5f8c",
    "purple": "#8b5cf6",
    "cyan": "#3b9bdc",
    "orange": "#f59e42",
    "red": "#ef5b5b",
    "grid": "#edf1f7",
    "text": "#172033",
    "muted": "#778196",
}


def apply_style():
    st.markdown(
        """<style>
        :root{--bw-navy:#14243a;--bw-blue:#3b82f6;--bw-text:#172033;--bw-muted:#778196;--bw-line:#e8edf5;--bw-bg:#f4f7fb}
        .stApp{background:var(--bw-bg);color:var(--bw-text)}
        .block-container{padding:.65rem 1.55rem 1.35rem;max-width:none;width:100%}
        header[data-testid="stHeader"]{display:block!important;visibility:visible!important;background:transparent;height:2.2rem;z-index:1001}
        [data-testid="stToolbar"] button:not([data-testid="stExpandSidebarButton"]),[data-testid="stToolbar"] a{display:none!important}
        [data-testid="stExpandSidebarButton"]{background:#1c2c42!important;border-radius:7px!important;z-index:1002!important}
        [data-testid="stExpandSidebarButton"] span{color:#fff!important}
        [data-testid="stSidebarCollapseButton"]{visibility:visible!important}
        [data-testid="stSidebar"]{background:linear-gradient(180deg,#1c2c42 0%,#14243a 72%,#1f2d3e 100%);border-right:0;min-width:236px;max-width:236px}
        [data-testid="stSidebar"] *{color:#dce6f4}
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2{color:#fff;font-size:1.02rem;letter-spacing:.01em;margin:.2rem 0 0}
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"]{color:#8191a8;font-size:.69rem;letter-spacing:.04em}
        [data-testid="stSidebarNav"]{padding-top:.7rem}
        [data-testid="stSidebarNav"] span{font-size:.82rem}
        [data-testid="stSidebarNav"] li{margin:.18rem .45rem;border-radius:7px}
        [data-testid="stSidebarNav"] li a{padding:.55rem .65rem;border-radius:7px}
        [data-testid="stSidebarNav"] li a[aria-current="page"]{background:#2468c9;color:white;box-shadow:0 5px 14px rgba(0,0,0,.16)}
        [data-testid="stSidebarNav"] li a:hover{background:#1d3553;color:white}
        [data-testid="stSidebarNav"] ul>li>div{color:#71839c;text-transform:uppercase;font-size:.63rem;letter-spacing:.08em}
        [data-testid="stSidebar"] .stButton>button{background:#1c304b;border:1px solid #294362;color:#dce6f4;border-radius:7px;font-size:.75rem}
        [data-testid="stSidebar"] .stButton>button:hover{border-color:#4d8fe8;color:white}
        .st-key-bw_topbar{margin:-.65rem -1.55rem .7rem;padding:.42rem 1.55rem .28rem;border-bottom:1px solid #e6ebf3;background:rgba(255,255,255,.94)}
        .st-key-bw_topbar [data-testid="stTextInput"]{max-width:680px}.st-key-bw_topbar [data-testid="stTextInput"] input{background:#f5f8fc;border-color:#e0e7f0;height:34px}
        .bw-user{display:flex;align-items:center;gap:13px;color:#536074;font-size:.69rem}.bw-avatar{width:29px;height:29px;border-radius:50%;background:#617086;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800}
        .bw-head{display:flex;justify-content:space-between;align-items:flex-start;margin:.15rem 0 .72rem}
        .bw-title{font-size:1.72rem;font-weight:850;letter-spacing:-.045em;color:#141c2b;line-height:1.15}
        .bw-sub{color:var(--bw-muted);font-size:.78rem;margin-top:.35rem}
        .bw-eyebrow{color:#3b82f6;font-size:.66rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;margin-bottom:.15rem}
        div[data-testid="stVerticalBlockBorderWrapper"]>div{background:#fff;border-color:var(--bw-line)!important;border-radius:10px!important;box-shadow:0 3px 12px rgba(22,38,63,.035)}
        .bw-kpi{background:#fff;border:1px solid var(--bw-line);border-radius:10px;padding:13px 15px 8px;min-height:142px;box-shadow:0 4px 16px rgba(22,38,63,.045);overflow:hidden}
        .bw-kpi-top{display:flex;align-items:center;gap:8px;margin-bottom:7px}
        .bw-kpi-icon{width:26px;height:26px;border-radius:7px;display:inline-flex;align-items:center;justify-content:center;font-size:.78rem;font-weight:800}
        .bw-kpi-label{font-size:.7rem;color:#596579;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
        .bw-kpi-value{font-size:1.33rem;line-height:1.2;color:#111827;font-weight:850;letter-spacing:-.035em;white-space:nowrap}
        .bw-kpi-help{font-size:.64rem;color:#98a2b3;margin-top:5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
        .bw-spark{height:30px;margin:5px -3px -2px}.bw-spark svg{width:100%;height:100%;overflow:visible}.bw-spark path{fill:none;stroke-width:2}.bw-spark polygon{opacity:.1}
        .bw-accent-0 .bw-kpi-icon{color:#c77713;background:#fff1db}.bw-accent-0{border-bottom:2px solid #f4b55d}
        .bw-accent-1 .bw-kpi-icon{color:#159b72;background:#dcf8ef}.bw-accent-1{border-bottom:2px solid #4bcba4}
        .bw-accent-2 .bw-kpi-icon{color:#d84f7b;background:#ffe6ef}.bw-accent-2{border-bottom:2px solid #f083a5}
        .bw-accent-3 .bw-kpi-icon{color:#7546dc;background:#eee7ff}.bw-accent-3{border-bottom:2px solid #9e7aed}
        .bw-accent-4 .bw-kpi-icon{color:#287eb7;background:#e1f2ff}.bw-accent-4{border-bottom:2px solid #69b5e6}
        .bw-accent-5 .bw-kpi-icon{color:#2563c7;background:#e3edff}.bw-accent-5{border-bottom:2px solid #5f91e5}
        .bw-section{font-size:.84rem;font-weight:800;color:#202a3b;margin:.05rem 0 .65rem;letter-spacing:-.02em}
        .bw-mini-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:.7rem 0 1rem}
        .bw-mini{background:white;border:1px solid var(--bw-line);border-radius:8px;padding:9px 12px}
        .bw-mini b{display:block;font-size:.96rem;color:#1b2536}.bw-mini span{font-size:.65rem;color:#8490a3}
        .bw-stock-cards{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:2px 0 12px}.bw-stock-card{background:#f7faff;border:1px solid #edf1f7;border-radius:8px;padding:12px 9px;text-align:center}.bw-stock-card b{font-size:1.35rem;display:block;margin:7px 0 2px}.bw-stock-card span{font-size:.66rem;color:#718096}.bw-stock-card.warn{background:#fff7f8}.bw-stock-card.blue{background:#f3f8ff}
        .bw-highlight{display:flex;gap:12px;align-items:flex-start;margin-top:8px;padding:12px 14px;border:1px solid #dcefe5;border-radius:9px;background:linear-gradient(110deg,#f1fff8,#f7fffb);min-height:72px}.bw-highlight-icon{width:31px;height:31px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:#dcfaea;color:#17a768;font-size:1rem}.bw-highlight b{display:block;font-size:.74rem;color:#253247;margin-bottom:3px}.bw-highlight span{display:block;font-size:.67rem;line-height:1.45;color:#657287}.bw-highlight.warn{background:linear-gradient(110deg,#fffaf0,#fffdf8);border-color:#f5e4be}.bw-highlight.warn .bw-highlight-icon{background:#fff0cc;color:#d78a13}.bw-highlight.danger{background:#fff6f7;border-color:#f3d8dd}.bw-highlight.danger .bw-highlight-icon{background:#ffe2e6;color:#d84f64}
        .st-key-bw_sidebar_footer{position:relative!important;width:auto;box-sizing:border-box;margin:1.25rem .75rem .65rem;padding:.15rem 0 0;background:transparent;border:0;box-shadow:none}
        .st-key-bw_sidebar_footer .bw-ci-logo{height:70px;overflow:hidden;display:flex;align-items:center;justify-content:center;margin:0 0 .42rem}
        .st-key-bw_sidebar_footer .bw-ci-logo svg{display:block;width:172px;height:auto;overflow:visible}
        .st-key-bw_sidebar_footer .bw-ci-main{fill:#fff;font-family:"Arial Black","Arial",sans-serif;font-size:72px;font-weight:900;letter-spacing:-5px}
        .st-key-bw_sidebar_footer .bw-ci-kr{fill:#fff;font-family:"Noto Sans KR","Malgun Gothic","Arial",sans-serif;font-size:23px;font-weight:900;letter-spacing:-1px}
        .st-key-bw_sidebar_footer .stButton>button{height:36px;background:#1c304b!important;border:1px solid #335274!important;color:#fff!important;font-weight:700}
        .st-key-bw_sidebar_footer [data-testid="stCaptionContainer"]{margin-top:.25rem!important;text-align:center;color:#8191a8!important;font-size:.61rem!important}
        .insight{background:#f8fbff;border:1px solid #e5ebf5;border-left:3px solid #5b8def;border-radius:7px;padding:9px 10px;margin:7px 0;font-size:.72rem;line-height:1.45;color:#465268}
        .ok{border-left-color:#25a46f;background:#f4fcf8}.warn{border-left-color:#f0a332;background:#fffaf0}.danger{border-left-color:#e35d6a;background:#fff6f7}
        h1,h2,h3{letter-spacing:-.035em;color:#1a2232}
        h3{font-size:.86rem!important;margin:.15rem 0 .45rem!important}
        [data-testid="stPlotlyChart"]{border-radius:8px;overflow:hidden}
        [data-testid="stDataFrame"]{border:1px solid var(--bw-line);border-radius:8px;overflow:hidden}
        [data-testid="stExpander"]{background:white;border-color:var(--bw-line);border-radius:8px}
        [data-testid="stAlert"]{border-radius:8px;font-size:.75rem}
        .stSelectbox label,.stDateInput label,.stTextInput label,.stMultiSelect label{font-size:.66rem;color:#69758a;font-weight:700}
        .stSelectbox div[data-baseweb="select"]>div,.stDateInput input,.stTextInput input,.stMultiSelect div[data-baseweb="select"]>div{border-color:#e3e9f2;background:#fff;border-radius:7px;font-size:.75rem;min-height:36px}
        .stButton>button{border-radius:7px;font-size:.72rem}
        .bw-footnote{font-size:10px!important;line-height:1.45;color:#718198;font-style:italic;margin:.35rem 0 .15rem}
        .bw-footnote.boxed{padding:7px 10px;border-radius:7px;background:#dceafd;color:#547092;border:1px solid rgba(80,120,170,.06)}
        @media(max-width:1100px){[data-testid="stSidebar"]{min-width:190px;max-width:190px}.st-key-bw_sidebar_footer{width:auto;margin-left:.6rem;margin-right:.6rem}.st-key-bw_sidebar_footer .bw-ci-logo svg{width:152px}.block-container{padding:1rem}.st-key-bw_topbar{margin:-1rem -1rem .8rem}.bw-kpi{min-height:118px;padding:11px}.bw-kpi-value{font-size:1rem}.bw-mini-grid{grid-template-columns:repeat(2,1fr)}}
        @media(max-width:760px){.bw-title{font-size:1.35rem}.bw-mini-grid{grid-template-columns:1fr 1fr}div[data-testid="stHorizontalBlock"]:has(.bw-kpi){flex-wrap:wrap!important;gap:.5rem!important}div[data-testid="stHorizontalBlock"]:has(.bw-kpi)>div[data-testid="stColumn"]{min-width:calc(50% - .25rem)!important;flex:1 1 calc(50% - .25rem)!important}.bw-kpi{min-height:108px}.bw-kpi-value{font-size:1.05rem}}
        </style>""",
        unsafe_allow_html=True,
    )


def _axis_values(fig: go.Figure, attr: str) -> list:
    out = []
    for trace in fig.data:
        values = getattr(trace, attr, None)
        if values is None:
            continue
        try:
            out.extend([value for value in values if value is not None])
        except TypeError:
            continue
    return out


def _axis_has_numeric_values(fig: go.Figure, attr: str) -> bool:
    values = _axis_values(fig, attr)
    if not values:
        return False
    first = values[0]
    if isinstance(first, (pd.Timestamp, datetime, date)):
        return False
    return isinstance(first, Number) and not isinstance(first, bool)


def _date_axis_format(fig: go.Figure, attr: str):
    values = _axis_values(fig, attr)
    if not values:
        return None
    try:
        dates = pd.to_datetime(pd.Series(values), errors="coerce").dropna()
    except Exception:
        return None
    if dates.empty or len(dates) != len(values):
        return None

    # Monthly dashboard series are stored as month-start timestamps.
    monthly = bool(((dates.dt.day == 1) & (dates.dt.hour == 0) & (dates.dt.minute == 0) & (dates.dt.second == 0)).all())
    if monthly:
        return {"tickformat": "%y-%m", "hoverformat": "%y-%m", "dtick": "M1"}

    unique_days = dates.dt.normalize().nunique()
    config = {"tickformat": "%y-%m-%d", "hoverformat": "%y-%m-%d"}
    # A single date otherwise gets fractional-day tick marks around midnight.
    if unique_days <= 1:
        config["dtick"] = 24 * 60 * 60 * 1000
    return config


def chart_style(fig: go.Figure, height: int = 275, legend: bool = True) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=18, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial, sans-serif", size=10, color=COLORS["muted"]),
        hoverlabel=dict(bgcolor="white", font_size=11),
        legend=dict(orientation="h", y=1.14, x=1, xanchor="right", title_text="", font_size=9),
        showlegend=legend,
        separators=".,",
    )

    numeric_x = _axis_has_numeric_values(fig, "x")
    numeric_y = _axis_has_numeric_values(fig, "y")
    date_x = _date_axis_format(fig, "x")
    date_y = _date_axis_format(fig, "y")

    x_kwargs = dict(
        showgrid=False,
        zeroline=False,
        title_text="",
        tickfont_size=9,
        tickformat=",.0f" if numeric_x else None,
        separatethousands=True if numeric_x else None,
        exponentformat="none" if numeric_x else None,
    )
    if date_x:
        x_kwargs.update(type="date", **date_x)

    y_kwargs = dict(
        gridcolor=COLORS["grid"],
        zeroline=False,
        title_text="",
        tickfont_size=9,
        tickformat=",.0f" if numeric_y else None,
        separatethousands=True if numeric_y else None,
        exponentformat="none" if numeric_y else None,
    )
    if date_y:
        y_kwargs.update(type="date", **date_y)

    fig.update_xaxes(**x_kwargs)
    fig.update_yaxes(**y_kwargs)
    return fig


def footnote(text: str, boxed: bool = False):
    cls = "bw-footnote boxed" if boxed else "bw-footnote"
    st.markdown(f'<div class="{cls}">{text}</div>', unsafe_allow_html=True)


def section_title(text: str):
    st.markdown(f'<div class="bw-section">{text}</div>', unsafe_allow_html=True)
