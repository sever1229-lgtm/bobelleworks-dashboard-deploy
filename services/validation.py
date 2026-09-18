from __future__ import annotations
import pandas as pd
from services.calculations import monthly_raw

def validate_aggregates(frames: dict[str,pd.DataFrame], tolerance: float = 1.0) -> pd.DataFrame:
    sheet=frames["월별실적"].copy(); sheet["월"]=sheet["월 시작"].dt.to_period("M").dt.to_timestamp()
    raw=monthly_raw(frames["판매 및 반품"],frames["운영비"],frames["입출금"])
    metrics=["매출","매출원가","판매 부대비","공헌이익","운영비","관리손익","실제 입금","실제 출금","순현금흐름"]
    joined=sheet[["월"]+metrics].merge(raw,on="월",how="left",suffixes=("_시트","_웹")).fillna(0)
    rows=[]
    for _,r in joined.iterrows():
        for m in metrics:
            delta=float(r[f"{m}_웹"]-r[f"{m}_시트"])
            rows.append({"월":r["월"],"항목":m,"시트 값":r[f"{m}_시트"],"웹 계산":r[f"{m}_웹"],"차이":delta,"상태":"일치" if abs(delta)<=tolerance else "확인 필요"})
    return pd.DataFrame(rows)

