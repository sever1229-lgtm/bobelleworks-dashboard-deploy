from html import escape

import streamlit as st


def won(value):
    value = float(value or 0)
    sign = "-" if value < 0 else ""
    return f"{sign}₩{abs(value):,.0f}"


def pct(value):
    return f"{float(value or 0):.1%}"


def num(value):
    return f"{float(value or 0):,.0f}"


ICONS = {
    "매출": "₩", "공헌이익": "↗", "공헌이익률": "%", "관리손익": "◆",
    "현재자금": "₩", "재고자산": "▦", "현재고": "▤", "보충 필요 SKU": "!",
    "미입고수량": "↘", "입력 오류": "!", "입금": "+", "출금": "−",
    "순현금흐름": "↕", "시작 기초자금": "◇", "현금흐름률": "%",
}


def metrics(items, columns=4):
    cols = st.columns(columns, gap="small")
    for i, (label, value, help_text) in enumerate(items):
        icon = ICONS.get(label, "•")
        helper = help_text or "선택 기간 기준"
        points = [24, 17, 20, 18, 21, 14, 17, 8]
        if i % 2: points = [23, 16, 21, 18, 20, 14, 17, 7]
        coords = " ".join(f"{n * 14},{y}" for n, y in enumerate(points))
        stroke = ["#4f8ef7", "#29b88a", "#b36cf3", "#f05e82", "#f2a252", "#4f8ef7"][i % 6]
        html = f"""
        <div class="bw-kpi bw-accent-{i % 6}" title="{escape(helper)}">
          <div class="bw-kpi-top"><span class="bw-kpi-icon">{escape(icon)}</span><span class="bw-kpi-label">{escape(label)}</span></div>
          <div class="bw-kpi-value">{escape(str(value))}</div>
          <div class="bw-kpi-help">{escape(helper)}</div>
          <div class="bw-spark"><svg viewBox="0 0 100 30" preserveAspectRatio="none"><polygon points="0,30 {coords} 98,30" fill="{stroke}"/><path d="M {coords.replace(' ', ' L ')}" stroke="{stroke}"/></svg></div>
        </div>"""
        cols[i % columns].markdown(html, unsafe_allow_html=True)


def mini_metrics(items):
    cards = "".join(
        f'<div class="bw-mini"><b>{escape(str(value))}</b><span>{escape(label)}</span></div>'
        for label, value in items
    )
    st.markdown(f'<div class="bw-mini-grid">{cards}</div>', unsafe_allow_html=True)
