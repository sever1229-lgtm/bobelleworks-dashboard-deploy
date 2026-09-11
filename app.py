import streamlit as st
st.set_page_config(page_title="Bobelle Works",page_icon="◌",layout="wide",initial_sidebar_state="expanded")
pages={"경영 현황":[st.Page("pages/overview.py",title="Overview",icon="📊",default=True),st.Page("pages/profit.py",title="매출·손익",icon="📈"),st.Page("pages/sales.py",title="주문·판매",icon="🧾"),st.Page("pages/product_analysis.py",title="상품 분석",icon="🔎")],"운영":[st.Page("pages/inventory.py",title="재고",icon="📦"),st.Page("pages/purchase_orders.py",title="발주",icon="🚚"),st.Page("pages/expenses.py",title="비용",icon="💳"),st.Page("pages/cashflow.py",title="자금",icon="🏦")]}
st.navigation(pages).run()
