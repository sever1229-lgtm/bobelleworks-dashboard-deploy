import streamlit as st

st.set_page_config(page_title="Bobelle Works", page_icon="◌", layout="wide", initial_sidebar_state="expanded")

pages = {
    "Overview": [
        st.Page("views/overall_overview.py", title="전체 대시보드", icon="📊", default=True),
    ],
    "쇼핑몰": [
        st.Page("views/overview.py", title="쇼핑몰 대시보드", icon="🛍️"),
        st.Page("views/profit.py", title="매출·손익", icon="📈"),
        st.Page("views/sales.py", title="주문·판매", icon="🧾"),
        st.Page("views/product_analysis.py", title="상품 분석", icon="🔎"),
        st.Page("views/inventory.py", title="재고", icon="📦"),
        st.Page("views/purchase_orders.py", title="발주", icon="🚚"),
        st.Page("views/expenses.py", title="비용", icon="💳"),
        st.Page("views/cashflow.py", title="자금", icon="🏦"),
    ],
    "통번역": [
        st.Page("views/interpretation_overview.py", title="통번역 대시보드", icon="🌐"),
        st.Page("views/interpretation_sales.py", title="매출 분석", icon="📈"),
        st.Page("views/interpretation_projects.py", title="프로젝트·매출 내역", icon="🗂️"),
        st.Page("views/clients.py", title="거래처 관리", icon="🤝"),
        st.Page("views/settlements.py", title="정산 현황", icon="💰"),
    ],
}

st.navigation(pages).run()
