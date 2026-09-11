from __future__ import annotations

import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

import streamlit as st


APP_ROOT = Path(tempfile.gettempdir()) / "bobelleworks_dashboard"
BUNDLE = Path(__file__).with_name("app_bundle.zip")


def prepare_bundle() -> Path:
    if not BUNDLE.is_file():
        st.error("배포 모듈을 불러오지 못했습니다.")
        st.stop()

    target = APP_ROOT / str(BUNDLE.stat().st_mtime_ns)
    if not target.exists():
        shutil.rmtree(APP_ROOT, ignore_errors=True)
        target.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(BUNDLE) as archive:
            archive.extractall(target)
    if str(target) not in sys.path:
        sys.path.insert(0, str(target))
    return target


root = prepare_bundle()
st.set_page_config(
    page_title="Bobelle Works",
    page_icon="◌",
    layout="wide",
    initial_sidebar_state="expanded",
)
pages = {
    "경영 현황": [
        st.Page(str(root / "pages" / "overview.py"), title="Overview", icon="📊", default=True),
        st.Page(str(root / "pages" / "profit.py"), title="매출·손익", icon="📈"),
        st.Page(str(root / "pages" / "sales.py"), title="주문·판매", icon="🧾"),
        st.Page(str(root / "pages" / "product_analysis.py"), title="상품 분석", icon="🔎"),
    ],
    "운영": [
        st.Page(str(root / "pages" / "inventory.py"), title="재고", icon="📦"),
        st.Page(str(root / "pages" / "purchase_orders.py"), title="발주", icon="🚚"),
        st.Page(str(root / "pages" / "expenses.py"), title="비용", icon="💳"),
        st.Page(str(root / "pages" / "cashflow.py"), title="자금", icon="🏦"),
    ],
}
st.navigation(pages).run()
