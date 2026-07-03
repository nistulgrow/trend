# 더월 차트 에이전트

이 에이전트는 `rawdata` 폴더에 새 셀메이트 CSV가 들어온 뒤, 사용자가 "차트 만들어줘", "데이터 업데이트하고 차트 다시 만들어줘"처럼 요청했을 때 따라야 할 전체 실행 절차입니다.

목표는 아래 작업을 한 흐름으로 끝내는 것입니다.

```text
rawdata 신규 파일 반영
→ uptodate 일별 파일 업데이트
→ 주/월/분기/연 집계 파일 생성
→ 제품별 판매 수량 카운팅
→ 대시보드 DATA 생성
→ HTML 차트 생성
→ 검증
```

---

## 1. 반드시 읽을 가이드

작업 시작 전 아래 4개 문서를 먼저 확인합니다.

```text
guides/uptodate_data_pipeline_guide.md
guides/category_counting_guide.md
guides/sales_dashboard_data_spec.md
guides/sales_chartdesign_guide.md
```

역할:

| 파일 | 역할 |
| --- | --- |
| `uptodate_data_pipeline_guide.md` | rawdata를 최신 uptodate 파일로 업데이트하는 절차 |
| `category_counting_guide.md` | 침대/책상 판매 대수 계산 규칙 |
| `sales_dashboard_data_spec.md` | HTML 안에 넣을 `DATA` 객체 구조 |
| `sales_chartdesign_guide.md` | HTML 화면 디자인, 배치, 인터랙션 |

---

## 2. 작업 원칙

### 2-1. 데이터 기준

`rawdata` 루트의 최신 `uptodate_YYYYMMDD.csv`를 기준 원장으로 사용합니다.

새로 들어온 raw 파일은 기존 uptodate 마지막 날짜 이후의 날짜를 붙이고, 최신 raw 파일의 마지막 날짜 기준 최대 한 달 전까지의 겹치는 날짜는 새 raw 값으로 교체합니다.

예:

```text
기존 uptodate: 20140601 ~ 20260610
신규 raw:      20260602 ~ 20260702
교체 대상:     20260602 ~ 20260610
추가 대상:     20260611 ~ 20260702
```

이렇게 하는 이유는 취소되었거나 변경된 주문 수량을 최신 raw 기준으로 반영하기 위해서입니다. 단, 교체 범위는 최신 raw 마지막 날짜 기준 최대 한 달 전까지만 허용합니다.

### 2-2. 병합 기준

행 순서는 절대 믿지 않습니다.

모든 병합 기준은 항상:

```text
상품명
옵션내용
```

즉:

```text
(상품명, 옵션내용)
```

입니다.

### 2-3. 고정 컬럼 처리

일별 uptodate 파일의 앞 6개 컬럼은 아래 순서를 유지합니다.

```text
상품명
옵션내용
현재고
미발송수
주문수
주문금액
```

처리 기준:

- `현재고`: 최신 raw 파일 기준으로 갱신
- `미발송수`: 최신 raw 파일 기준으로 갱신
- `주문수`: 빈칸
- `주문금액`: 빈칸

최신 raw에 없는 기존 상품/옵션은 기존 `현재고`, `미발송수`를 유지합니다.

---

## 3. 1단계: uptodate 데이터 업데이트

`guides/uptodate_data_pipeline_guide.md`를 기준으로 실행합니다.

### 3-1. 입력

```text
rawdata/uptodate_YYYYMMDD.csv
rawdata/신규_raw.csv
```

### 3-2. 출력

```text
rawdata/uptodate_YYYYMMDD.csv
input/uptodate_YYYYMMDD.csv
input/uptodate_YYYYMMDD_week.csv
input/uptodate_YYYYMMDD_month.csv
input/uptodate_YYYYMMDD_quater.csv
input/uptodate_YYYYMMDD_year.csv
```

### 3-3. 필수 검증

아래 검증을 통과해야 다음 단계로 넘어갑니다.

```text
교체 기간 raw 대비 불일치 0건
신규 기간 raw 대비 불일치 0건
신규 raw 상품/옵션 누락 0건
날짜 컬럼 오름차순
주문수/주문금액 빈칸
```

### 3-4. 정리

검증 완료 후:

```text
이전 rawdata/uptodate_YYYYMMDD.csv -> rawdata/old/
반영 완료한 신규 raw 파일 -> rawdata/old/
rawdata 루트에는 최신 uptodate 파일만 유지
input 폴더에는 최신 uptodate 5개 파일 유지
```

---

## 4. 2단계: 판매 수량 카운팅

`guides/category_counting_guide.md`를 기준으로 계산합니다.

입력은 반드시 `input` 폴더의 최신 집계 파일입니다.

```text
input/uptodate_YYYYMMDD_week.csv
input/uptodate_YYYYMMDD_month.csv
input/uptodate_YYYYMMDD_quater.csv
input/uptodate_YYYYMMDD_year.csv
```

### 4-1. 배송 구분

모든 시리즈는 배송 구분별로 계산합니다.

```text
all  = 전체
self = 자체/수도권
hd   = 현대물류용
eb   = 에바다용
```

배송 구분은 차트에서 선택할 수 있어야 합니다.

### 4-2. 침대류 필수 시리즈

```text
baby_ivy
baby_neti
neti
neti_plus
neti_max
junior_hey
junior_camper
junior_stins
junior_single
junior_lowbunk
junior_mid
junior_high
junior_bunk
```

주의:

- 아이비는 박스1/박스2 `min()` 기준을 적용합니다.
- 네티류는 네티/네티플러스/네티맥스 구분을 유지합니다.
- 헤이/캠퍼/스틴스는 싱글, 로우벙커, 미드, 하이, 이층 구조를 구분합니다.
- 미드/하이/이층에 포함되는 싱글 본체 중복을 차감합니다.
- 스틴스 과거 확장키트만 구매한 수요는 단독 싱글 하한값 계산에 영향을 줄 수 있으므로 가이드의 메모를 확인합니다.
- 아이비를 캠퍼로 바꾸는 전환키트는 캠퍼 신규 판매량에 섞지 않습니다.

### 4-3. 책상류 필수 시리즈

```text
desk_total
desk_plywood_top
desk_oak_top
desk_plywood_rear
desk_oak_rear
desk_oak_est
```

주의:

- 전체 데스크 수량은 프레임 기준입니다.
- 과거 프레임과 상판이 같이 포장된 전환기 데이터는 스탠다드+커브 합산 기준을 적용합니다.
- 2021년 말처럼 프레임 기록이 누락된 전환기에는 상판/리어탑 병목 수량으로 보정합니다.
- 상판/리어탑은 전체 수량을 다시 더하는 용도가 아니라 플라이우드/오크 구성 비중을 보기 위한 시리즈입니다.

---

## 5. 3단계: DATA 객체 생성

`guides/sales_dashboard_data_spec.md`를 기준으로 HTML 안에 넣을 `DATA` 객체를 생성합니다.

현재 이 단계는 아래 스크립트로 실행합니다.

```text
python3 chart_agent/generate_dashboard_html.py
```

이 스크립트는 최신 `input/uptodate_YYYYMMDD_*` 집계 파일의 마지막 날짜 기준 최대 한 달 전부터 겹치는 기간을 다시 계산합니다. 그보다 이전에 끝난 기간의 기존 `DATA` 값은 보존합니다.

기간 단위:

```text
week
month
quarter
year
```

배송 구분:

```text
all
self
hd
eb
```

구조:

```js
const DATA = {
  week: {
    all:  { labels: [...], series: {...} },
    self: { labels: [...], series: {...} },
    hd:   { labels: [...], series: {...} },
    eb:   { labels: [...], series: {...} }
  },
  month: { ... },
  quarter: { ... },
  year: { ... }
}
```

`labels`와 모든 `series` 배열 길이는 반드시 같아야 합니다.

---

## 6. 4단계: HTML 차트 생성

`guides/sales_chartdesign_guide.md`를 기준으로 단일 HTML 파일을 생성합니다.

출력 파일:

```text
input/integrated_category_dashboard_sample.html
```

화면 기본 조건:

```text
PC 전용
다크 테마
Chart.js 4.4.1 CDN
컴팩트한 상단 옵션 패널
큰 차트 영역
시작점 조절 막대 포함
전체 기간 복귀 버튼 포함
배송 형태 필터 포함
```

차트 제목:

```text
니스툴그로우 침대 책상 판매 분석
```

---

## 7. 5단계: 차트 검증

HTML 생성 후 아래를 확인합니다.

### 7-1. 데이터 검증

```text
기간별 labels 길이와 series 길이가 같은지
baby_neti = neti + neti_plus + neti_max 관계가 맞는지
주니어 구조 합계가 음수로 떨어지지 않는지
책상 전체 수량이 상판+프레임 중복 합산으로 부풀지 않았는지
마지막 기간이 부분 기간이어도 포함되었는지
```

### 7-2. 화면 검증

가능하면 브라우저에서 직접 확인합니다.

확인 항목:

```text
HTML 파일이 열린다.
주/월/분기/연 탭이 동작한다.
침대류/책상류 선택이 동작한다.
분석 대상/세부 보기 선택이 동작한다.
배송 형태 필터가 동작한다.
시작점 조절 막대가 동작한다.
전체 기간 복귀 버튼이 동작한다.
마우스 툴팁이 포인터 위치의 데이터를 보여준다.
KPI가 현재 선택 조건 기준으로 바뀐다.
```

---

## 8. 완료 보고 형식

작업이 끝나면 사용자에게 아래 내용을 짧게 보고합니다.

```text
데이터 기준 날짜: YYYYMMDD
추가 반영 기간: YYYYMMDD ~ YYYYMMDD
겹친 기간 처리: 최신 raw 마지막 날짜 기준 최대 한 달 전까지 새 raw 값으로 교체
생성 파일:
- input/uptodate_YYYYMMDD.csv
- input/uptodate_YYYYMMDD_week.csv
- input/uptodate_YYYYMMDD_month.csv
- input/uptodate_YYYYMMDD_quater.csv
- input/uptodate_YYYYMMDD_year.csv
- input/integrated_category_dashboard_sample.html
검증 결과:
- 데이터 불일치 0건
- 차트 렌더 확인
```

---

## 9. 금지 사항

```text
행 번호 기준으로 날짜값을 붙이지 않는다.
최신 raw 마지막 날짜 기준 최대 한 달 전까지만 겹치는 날짜를 새 raw 값으로 교체한다.
주문수/주문금액에 raw 파일의 합계를 남기지 않는다.
검증 전에 기존 input 파일을 삭제하지 않는다.
검증 전에 raw 파일을 old로 이동하지 않는다.
상판과 프레임을 단순 합산해서 책상 전체 수량으로 만들지 않는다.
아이비→캠퍼 전환키트를 캠퍼 신규 판매량에 섞지 않는다.
```

---

## 10. 빠른 실행 체크리스트

```text
[ ] 4개 가이드를 읽었다.
[ ] rawdata의 기존 uptodate 파일을 확인했다.
[ ] 신규 raw 파일의 날짜 범위를 확인했다.
[ ] 최신 raw 마지막 날짜 기준 최대 한 달 전까지 겹치는 날짜를 교체했다.
[ ] 기존 마지막 날짜 이후 날짜를 추가했다.
[ ] 상품명+옵션내용 키로 병합했다.
[ ] 일별/주간/월간/분기/연간 파일을 생성했다.
[ ] 데이터 검증 0건을 확인했다.
[ ] category_counting_guide 기준으로 숫자를 계산했다.
[ ] sales_dashboard_data_spec 기준으로 DATA를 만들었다.
[ ] sales_chartdesign_guide 기준으로 HTML을 만들었다.
[ ] 브라우저에서 차트 동작을 확인했다.
[ ] 사용자에게 생성 파일과 검증 결과를 보고했다.
```
