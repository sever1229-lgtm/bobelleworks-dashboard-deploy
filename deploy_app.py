import streamlit as st

st.set_page_config(page_title="Bobelle Works", page_icon="◌", layout="wide", initial_sidebar_state="expanded")

pages = {
    "Overview": [
        st.Page("pages/overall_overview.py", title="전체 대시보드", icon="📊", default=True),
    ],
    "쇼핑몰": [
        st.Page("pages/overview.py", title="쇼핑몰 대시보드", icon="🛍️"),
        st.Page("pages/profit.py", title="매출·손익", icon="📈"),
        st.Page("pages/sales.py", title="주문·판매", icon="🧾"),
        st.Page("pages/product_analysis.py", title="상품 분석", icon="🔎"),
        st.Page("pages/inventory.py", title="재고", icon="📦"),
        st.Page("pages/purchase_orders.py", title="발주", icon="🚚"),
        st.Page("pages/expenses.py", title="비용", icon="💳"),
        st.Page("pages/cashflow.py", title="자금", icon="🏦"),
    ],
    "통번역": [
        st.Page("pages/interpretation_overview.py", title="통번역 대시보드", icon="🌐"),
        st.Page("pages/interpretation_sales.py", title="매출 분석", icon="📈"),
        st.Page("pages/interpretation_projects.py", title="프로젝트·매출 내역", icon="🗂️"),
        st.Page("pages/clients.py", title="거래처 관리", icon="🤝"),
        st.Page("pages/settlements.py", title="정산 현황", icon="💰"),
    ],
}

st.navigation(pages).run()
