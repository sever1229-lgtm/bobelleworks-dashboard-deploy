import pandas as pd
from services.calculations import product_summary, channel_summary, delayed_orders
from services.validation import validate_aggregates

# Fully synthetic values. Never place operational figures in source control.
sales=pd.DataFrame({
    "처리일":pd.to_datetime(["2026-01-02"]*2), "주문번호":["TEST-1","TEST-2"],
    "판매채널":["테스트채널","테스트채널"], "SKU":["TEST-A","TEST-B"],
    "상품명 (자동)":["테스트상품A","테스트상품B"], "구분":["판매","판매"],
    "수량":[1,1], "재입고 수량":[0,0], "수수료":[100,100], "택배비":[100,100],
    "포장비":[50,50], "매출 합계":[2000,3000], "매출원가":[500,1000],
    "공헌이익":[1250,1750], "재고 차감수량":[1,1],
})
expense=pd.DataFrame({"발생일":pd.to_datetime(["2026-01-03"]),"금액":[500]})
cash=pd.DataFrame({"거래일":pd.to_datetime(["2026-01-04"]),"입금":[4000],"출금":[1000]})
monthly=pd.DataFrame({
    "월 시작":[pd.Timestamp("2026-01-01")],"매출":[5000.0],"매출원가":[1500.0],
    "판매 부대비":[500.0],"공헌이익":[3000.0],"운영비":[500.0],"관리손익":[2500.0],
    "실제 입금":[4000.0],"실제 출금":[1000.0],"순현금흐름":[3000.0],"월말 자금":[10000.0],
})
frames={"월별실적":monthly,"판매 및 반품":sales,"운영비":expense,"입출금":cash}
checks=validate_aggregates(frames)
assert (checks["상태"]=="일치").all(), checks[checks["상태"]!="일치"]
assert product_summary(sales)["매출"].sum()==5000
assert channel_summary(sales)["매출"].sum()==5000
print(f"OK: {len(checks)} synthetic sheet/raw checks passed")

# Regression: pandas datetime64 due dates must compare safely with Python date values.
purchases = pd.DataFrame({
    "입고예정일": pd.to_datetime(["2026-01-01", None]),
    "미입고수량": [1, 2],
})
late = delayed_orders(purchases, pd.Timestamp("2026-01-02").date())
assert len(late) == 1, late

# Empty-period summaries must retain their schema for dashboard rendering.
assert list(product_summary(pd.DataFrame()).columns) == ["SKU","상품명 (자동)","판매수량","매출","매출원가","판매부대비","공헌이익","공헌이익률"]
assert list(channel_summary(pd.DataFrame()).columns) == ["판매채널","주문건수","판매수량","매출","공헌이익","공헌이익률"]
print("OK: date-comparison regression and empty-period schemas passed")
