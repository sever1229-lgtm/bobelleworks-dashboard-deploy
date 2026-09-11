# Bobelle Works 운영 대시보드

Google Spreadsheet `bobelleworks_운영대시보드`를 Master Data Source로 사용하는 조회·분석 전용 Streamlit 앱입니다. 원본 시트는 변경하지 않습니다.

## 구현 범위

- Overview: 핵심 KPI, 월별 추이, 재고 상태, 최근 판매, 규칙 기반 Insight
- 매출·손익: 월별실적 KPI, Waterfall, 판매부대비 구성
- 주문·판매: 주문·반품 KPI, 채널별 분석, 최근 주문
- 상품 분석: SKU별 매출·원가·공헌이익, 순위와 Scatter
- 재고: 현재고·안전재고·재고자산·보충 상태
- 발주: 진행 상태, 미입고와 납기 지연
- 비용: 월별·비용구분별 운영비 분석
- 자금: 실제 입출금·순현금흐름·월말 자금, 관리손익 비교
- 검증: `월별실적`과 Raw Data 재계산 값을 월·항목별 비교

## 확인한 실제 원본 구조

2026-09-11에 연결된 파일을 직접 읽어 확인했습니다.

- Locale: `ko_KR`
- 원본 timezone: `America/Los_Angeles`
- 실제 헤더: 각 운영 표의 5행
- 데이터 범위: 상품·재고·발주 6~105행, 거래 데이터 6~505행, 월별실적 6~17행

| 지표 | 실제 원본 매핑 |
|---|---|
| 매출 | `판매 및 반품`의 `매출 합계`(Q), 월별 KPI는 `월별실적`의 `매출` |
| 매출원가 | `판매 및 반품`의 `매출원가`(R) |
| 판매부대비 | `수수료`(L) + `택배비`(M) + `포장비`(N) |
| 공헌이익 | `판매 및 반품`의 `공헌이익`(S) |
| 관리손익 | 월별 공헌이익 − 운영비 |
| 현재고·재고자산 | `재고현황`의 H·K열 |
| 미입고 | `발주`의 `미입고수량`(O) |
| 순현금흐름 | `입출금`의 입금(F) − 출금(G) |

앱은 `Asia/Seoul` 기준으로 오늘과 납기를 비교하며, 원본 시간대가 다르면 경고합니다.

## Google Sheets 연결

1. Google Cloud에서 Google Sheets API와 Google Drive API를 활성화합니다.
2. 읽기용 서비스 계정을 만들고 JSON 키를 발급합니다.
3. 원본 Spreadsheet를 서비스 계정의 `client_email`에 **뷰어**로 공유합니다.
4. 로컬에서는 `.env.example`을 `.env`로 복사하고 `GOOGLE_SERVICE_ACCOUNT_FILE`에 JSON 경로를 넣습니다. 또는 `.streamlit/secrets.example.toml`을 `.streamlit/secrets.toml`로 복사해 실제 값을 채웁니다.

인증 파일, `.env`, `.streamlit/secrets.toml`은 저장소에 커밋하지 마세요.

## 실행

Python 3.11 이상을 권장합니다.

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
streamlit run app.py
```

왼쪽의 `최신 데이터 새로고침` 버튼은 캐시를 비우고 Google Sheets를 다시 읽습니다. 기본 캐시는 120초입니다.

## 배포

Streamlit Community Cloud에서 저장소와 `app.py`를 선택하고, App Secrets에 `.streamlit/secrets.example.toml` 형식의 값을 등록합니다. 다른 환경에서는 `streamlit run app.py`를 시작 명령으로 쓰고 서비스 계정 JSON을 `GOOGLE_SERVICE_ACCOUNT_JSON` Secret에 저장할 수 있습니다.

배포가 완료되면 `https://...streamlit.app` 형태의 주소가 생성됩니다. 이 주소로 접속하는 사용자는 Python을 설치할 필요가 없습니다. Google Sheet 변경 내용은 최대 120초 후 또는 화면의 새로고침 버튼을 누르면 반영됩니다.

배포 후 Overview의 `Google Sheet 값 검증`을 열어 모든 항목이 `일치`인지 확인합니다. 허용 오차는 ₩1입니다. 실제 사업 수치와 Spreadsheet ID는 저장소에 기록하지 않고 배포 환경의 Secrets에서만 관리합니다.

차이가 있으면 해당 월의 `판매 및 반품`, `운영비`, `입출금`의 날짜와 입력 확인 열을 먼저 확인하세요.
