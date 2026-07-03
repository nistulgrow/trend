# 판매 분석 대시보드 데이터 구조 가이드

이 문서는 `integrated_category_dashboard_sample.html`에 넣을 데이터 구조만 정의합니다.  
숫자를 어떻게 계산하는지는 `category_counting_guide.md`, 화면을 어떻게 그리는지는 `sales_chartdesign_guide.md`를 따릅니다.

---

## 1. 입력 파일

대시보드는 `input` 폴더의 up-to-date 집계 파일에서 생성합니다.

```text
input/uptodate_YYYYMMDD_week.csv
input/uptodate_YYYYMMDD_month.csv
input/uptodate_YYYYMMDD_quater.csv
input/uptodate_YYYYMMDD_year.csv
```

파일명 날짜는 고정하지 않고, `input` 폴더에 있는 최신 `uptodate_YYYYMMDD.csv`의 `YYYYMMDD`를 기준으로 맞춥니다.

예:

```text
input/uptodate_20260702.csv
input/uptodate_20260702_week.csv
input/uptodate_20260702_month.csv
input/uptodate_20260702_quater.csv
input/uptodate_20260702_year.csv
```

마지막 기간은 완성 기간이 아니어도 포함합니다. 예를 들어 2026년 7월 데이터가 7월 2일까지 있으면 `202607` 월 컬럼과 `2026Q3` 분기 컬럼은 7월 2일까지의 부분 기간으로 포함합니다.

---

## 2. 출력 데이터 객체

HTML 안에는 하나의 `DATA` 객체를 넣습니다.

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

배송 키:

| 키 | 의미 |
| --- | --- |
| `all` | 전체 배송 합산 |
| `self` | 자체/수도권. `현대물류용`, `에바다용` prefix가 없는 과거 SKU 포함 |
| `hd` | 현대물류용 |
| `eb` | 에바다용 |

기간 키:

| 키 | labels 형식 |
| --- | --- |
| `week` | `YYYYMMDD_YYYYMMDD` |
| `month` | `YYYYMM` |
| `quarter` | `YYYYQn` |
| `year` | `YYYY` |

---

## 3. 필수 시리즈 키

모든 기간 단위와 배송 구분에 같은 시리즈 키를 넣습니다. 값은 labels와 같은 길이의 숫자 배열입니다.

### 3-1. 아기침대

```text
baby_ivy
baby_neti
neti
neti_plus
neti_max
```

관계:

```text
baby_neti = neti + neti_plus + neti_max
아기침대 전체 = baby_ivy + baby_neti
```

### 3-2. 주니어 침대 브랜드

```text
junior_hey
junior_camper
junior_stins
```

관계:

```text
주니어 침대 전체 = junior_hey + junior_camper + junior_stins
```

### 3-3. 주니어 침대 구조

```text
junior_single
junior_lowbunk
junior_mid
junior_high
junior_bunk
```

관계:

```text
주니어 구조 전체 = junior_single + junior_lowbunk + junior_mid + junior_high + junior_bunk
```

주의:

```text
junior_single은 단순 싱글 본체 전체가 아니라, 미드/하이/2층에 포함된 싱글 본체를 차감한 단독 싱글 하한값입니다.
스틴스 확장키트만 구매한 기존 고객 수요가 섞일 수 있으므로 category_counting_guide.md의 스틴스 메모를 반드시 확인합니다.
```

### 3-4. 책상

```text
desk_total
desk_plywood_top
desk_oak_top
desk_plywood_rear
desk_oak_rear
desk_oak_est
```

관계:

```text
상판 구성 = desk_plywood_top + desk_oak_top
리어탑 구성 = desk_plywood_rear + desk_oak_rear
오크원목 추정 = desk_oak_est
```

`desk_total`은 프레임/상판/전환기 보정 기준을 적용한 전체 데스크 수량입니다. 2021년 말 뉴트럴 전환기처럼 프레임 기록이 누락된 달은 상판/리어탑 병목 수량으로 보정합니다.

---

## 4. 화면 선택값과 시리즈 매핑

### 4-1. 침대류

| 분석 대상 | 세부 보기 | 사용하는 시리즈 |
| --- | --- | --- |
| 전체 침대 | 아기 vs 주니어 | `baby_ivy + baby_neti`, `junior_hey + junior_camper + junior_stins` |
| 아기침대 | 아이비 vs 네티류 | `baby_ivy`, `baby_neti` |
| 아기침대 | 네티 세부 | `neti`, `neti_plus`, `neti_max` |
| 주니어 침대 | 헤이 vs 캠퍼 vs 스틴스 | `junior_hey`, `junior_camper`, `junior_stins` |
| 주니어 침대 | 싱글/로우벙커/미드/하이/이층 | `junior_single`, `junior_lowbunk`, `junior_mid`, `junior_high`, `junior_bunk` |

### 4-2. 책상류

| 세부 보기 | 사용하는 시리즈 |
| --- | --- |
| 전체 수량 | `desk_total` |
| 상판 구성 | `desk_plywood_top`, `desk_oak_top` |
| 리어탑 구성 | `desk_plywood_rear`, `desk_oak_rear` |

---

## 5. 시작점 필터

차트의 시작점 조절 막대는 인덱스가 아니라 실제 날짜값으로 저장합니다.

```js
state.startDate = 'YYYYMMDD'
```

기간 단위를 바꿔도 같은 시작 시점을 유지합니다.

예:

```text
startDate = 20180101
year    -> 2018부터
quarter -> 2018Q1부터
month   -> 201801부터
week    -> 20180101이 포함된 주부터
```

`전체 기간` 버튼은 `state.startDate = ''`로 초기화합니다.

---

## 6. KPI 데이터 규칙

KPI는 현재 선택된 기간 단위, 배송형태, 카테고리, 분석 대상, 세부 보기, 시작점 필터를 모두 반영합니다.

| KPI | 계산 |
| --- | --- |
| 선택 구간 합계 | 현재 시작점 이후 전체 visible 기간 합계 |
| 최근 기간 | visible labels의 마지막 기간 수량 |
| 세부 시리즈 카드 | 최근 기간의 각 시리즈 수량과 비중 |

비중:

```text
각 시리즈 최근값 / 최근 기간 전체값
```

---

## 7. 검증 규칙

차트용 DATA 생성 후 아래를 확인합니다.

```text
baby_neti = neti + neti_plus + neti_max
junior 브랜드 합계와 구조 합계가 큰 폭으로 어긋나지 않는지 확인
desk_total과 상판/리어탑 구성 합계가 전환기 보정 후 큰 폭으로 어긋나지 않는지 확인
모든 series 배열 길이 = labels 길이
week/month/quarter/year 모두 같은 series key 보유
마지막 기간은 2026-06-10까지의 부분 기간으로 포함
```

허용되는 해석 차이:

```text
스틴스 단독 싱글은 하한값입니다.
스틴스 미드/하이/이층은 신규 완성침대뿐 아니라 기존 고객 확장 수요가 섞일 수 있습니다.
```
