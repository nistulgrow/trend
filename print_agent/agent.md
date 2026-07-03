# 더월 프린트 PDF 에이전트

이 에이전트는 화면용 HTML 대시보드가 아니라, 프린트와 발표 자료에 넣기 좋은 **흰 배경 PDF 차트**를 만드는 절차입니다.

기본 역할:

```text
최신 판매 분석 DATA 확인
→ 프린트용 흰 배경 차트 HTML 생성
→ A4 세로 PDF 생성
→ 4:3 가로 발표용 PDF 생성
→ print_output 폴더 저장
→ PDF 잘림/가독성 검증
```

---

## 1. 관계 정의

`chart_agent`와 `print_agent`는 역할이 다릅니다.

| 에이전트 | 역할 |
| --- | --- |
| `chart_agent` | rawdata 업데이트, 수량 카운팅, 화면용 HTML 대시보드 생성 |
| `print_agent` | 이미 계산된 최신 데이터를 프린트/PDF용 흰 배경 차트로 출력 |

프린트 에이전트는 숫자 계산 규칙을 새로 만들지 않습니다. 숫자 계산은 기존 가이드를 그대로 따릅니다.

---

## 2. 반드시 읽을 가이드

작업 시작 전 아래 문서를 확인합니다.

```text
chart_agent/agent.md
guides/category_counting_guide.md
guides/sales_dashboard_data_spec.md
guides/print_chartdesign_guide.md
```

필요할 때만 추가로 확인:

```text
guides/uptodate_data_pipeline_guide.md
guides/sales_chartdesign_guide.md
```

역할:

| 파일 | 역할 |
| --- | --- |
| `chart_agent/agent.md` | 최신 데이터와 DATA 생성 흐름 확인 |
| `category_counting_guide.md` | 제품별 판매 대수 계산 규칙 |
| `sales_dashboard_data_spec.md` | DATA 객체 구조 |
| `print_chartdesign_guide.md` | PDF 출력용 디자인, 크기, 여백, 색상 규칙 |

---

## 3. 입력 데이터

프린트 PDF는 최신 판매 분석 DATA를 사용합니다.

기본 입력 후보:

```text
input/integrated_category_dashboard_sample.html
```

이 파일 안의 `DATA` 객체를 읽어 프린트용 차트를 만듭니다.

단, 화면용 HTML이 최신 CSV 기준으로 재생성되지 않은 경우에는 먼저 `chart_agent` 기준으로 DATA를 새로 만들어야 합니다.

확인할 것:

```text
input/uptodate_YYYYMMDD.csv
input/uptodate_YYYYMMDD_week.csv
input/uptodate_YYYYMMDD_month.csv
input/uptodate_YYYYMMDD_quater.csv
input/uptodate_YYYYMMDD_year.csv
input/integrated_category_dashboard_sample.html
```

HTML 안의 데이터 기간과 최신 `uptodate_YYYYMMDD` 날짜가 맞아야 합니다.

---

## 4. 출력물

PDF 출력물은 `print_output` 폴더에 저장합니다.

```text
print_output/
  a4_report_YYYYMMDD.pdf
  slide_4x3_YYYYMMDD.pdf
```

필요하면 중간 HTML도 보관할 수 있습니다.

```text
print_output/
  a4_report_YYYYMMDD.html
  slide_4x3_YYYYMMDD.html
```

중간 HTML은 PDF 검증이나 재출력이 필요할 때 유용합니다.

---

## 5. 출력 종류

### 5-1. A4 세로 보고서

용도:

```text
종이 출력
내부 보고서
보관용 자료
```

파일명:

```text
print_output/a4_report_YYYYMMDD.pdf
```

기본 설정:

```text
용지: A4
방향: 세로
배경: 흰색
색상: 잉크 절약형
구성: 한 페이지에 핵심 차트 1~2개
```

### 5-2. 4:3 가로 발표용 PDF

용도:

```text
PPT 삽입
회의 발표 자료
가로형 프린트
```

파일명:

```text
print_output/slide_4x3_YYYYMMDD.pdf
```

기본 설정:

```text
비율: 4:3
방향: 가로
배경: 흰색
색상: 잉크 절약형
구성: 한 장에 하나의 메시지
```

---

## 6. 작업 흐름

### 6-1. 최신 데이터 확인

1. `input` 폴더의 최신 `uptodate_YYYYMMDD.csv`를 확인합니다.
2. 같은 날짜의 주/월/분기/연 집계 파일이 있는지 확인합니다.
3. `integrated_category_dashboard_sample.html`의 데이터 기간이 최신 날짜와 맞는지 확인합니다.

맞지 않으면 먼저 `chart_agent` 흐름을 수행해 화면용 HTML과 DATA를 갱신합니다.

### 6-2. 출력 목적 결정

사용자 요청에 따라 아래 중 하나를 선택합니다.

```text
A4 세로 보고서만
4:3 가로 발표용만
둘 다
```

사용자가 따로 말하지 않으면 둘 다 생성합니다.

### 6-3. 프린트용 HTML 생성

`guides/print_chartdesign_guide.md` 기준으로 흰 배경 HTML을 만듭니다.

화면용 HTML을 그대로 PDF로 찍지 않습니다.

이유:

- 화면용은 어두운 배경이라 인쇄에 부적합합니다.
- 화면용은 인터랙션 중심이고, PDF는 고정 레이아웃 중심입니다.
- PDF는 페이지 잘림, 여백, 글자 크기, 잉크 사용량이 더 중요합니다.

### 6-4. PDF 렌더링

프린트용 HTML을 브라우저 렌더링 후 PDF로 저장합니다.

권장:

```text
Chromium/Playwright 기반 PDF 출력
```

기본 PDF 옵션:

```text
printBackground: true
preferCSSPageSize: true
```

현재 구현된 기본 실행 스크립트:

```text
print_agent/generate_print_pdfs.py
```

실행:

```text
python3 print_agent/generate_print_pdfs.py
```

이 스크립트는 최신 `input/uptodate_YYYYMMDD_month.csv`와 `input/uptodate_YYYYMMDD_quater.csv`를 읽어 아래 PDF를 생성합니다.

```text
print_output/a4_report_YYYYMMDD.pdf
print_output/slide_4x3_YYYYMMDD.pdf
```

스크립트는 `guides/category_counting_guide.md`와 `guides/print_chartdesign_guide.md`의 핵심 기준을 반영합니다.

### 6-5. 출력 폴더 저장

결과물은 반드시 `print_output` 폴더에 저장합니다.

```text
print_output/a4_report_YYYYMMDD.pdf
print_output/slide_4x3_YYYYMMDD.pdf
```

---

## 7. A4 보고서 구성

기본 페이지 순서:

```text
1페이지: 전체 요약
2페이지: 침대류 분석
3페이지: 주니어 침대 구조 변화
4페이지: 책상류 분석
```

필요하면 페이지를 줄일 수 있습니다.

각 페이지 구성:

```text
상단: 제목, 기간, 기준일
중단: KPI 3~5개
하단: 차트 1~2개
맨 아래: 계산 기준 짧은 메모
```

문구는 짧게 유지합니다.

---

## 8. 4:3 발표용 구성

기본 슬라이드 순서:

```text
1장: 전체 침대/책상 흐름
2장: 아기침대 - 아이비 vs 네티류
3장: 주니어 침대 - 헤이 vs 캠퍼 vs 스틴스
4장: 주니어 구조 - 싱글/로우벙커/미드/하이/이층
5장: 책상류 - 전체 수량과 상판/리어탑 구성
```

각 슬라이드 구성:

```text
상단: 짧은 제목
좌상단 또는 우상단: 기준 기간
중앙: 큰 차트 1개
하단: 핵심 수치 또는 짧은 해석 1줄
```

한 장에 너무 많은 차트를 넣지 않습니다.

---

## 9. 검증 기준

### 9-1. 데이터 검증

PDF 출력 전에 확인합니다.

```text
최신 uptodate 날짜와 PDF 기준 날짜가 같은지
DATA labels와 series 길이가 같은지
주/월/분기/연 중 선택한 기간 단위가 맞는지
마지막 미완성 기간이 포함되어 있는지
침대/책상 숫자가 화면용 DATA와 같은지
```

### 9-2. PDF 검증

PDF 생성 후 확인합니다.

```text
페이지 크기가 의도와 맞는지
A4 세로 PDF가 A4 portrait인지
4:3 PDF가 가로 비율인지
차트가 잘리지 않는지
글자가 너무 작지 않은지
축/범례/수치가 겹치지 않는지
흰 배경으로 출력되는지
불필요하게 진한 배경 면적이 없는지
```

### 9-3. 프린트 적합성

```text
검정 텍스트가 선명한지
회색 보조 텍스트가 너무 흐리지 않은지
색상 구분이 흑백 출력에서도 어느 정도 가능한지
넓은 색상 면적을 과도하게 쓰지 않았는지
```

---

## 10. 완료 보고 형식

작업 완료 후 사용자에게 아래 내용을 짧게 보고합니다.

```text
PDF 기준 데이터: YYYYMMDD
생성 파일:
- print_output/a4_report_YYYYMMDD.pdf
- print_output/slide_4x3_YYYYMMDD.pdf

검증:
- A4 세로 크기 확인
- 4:3 가로 크기 확인
- 차트 잘림 없음
- 흰 배경 출력 확인
```

---

## 11. 금지 사항

```text
화면용 어두운 HTML을 그대로 PDF로 출력하지 않는다.
넓은 검정/진한 배경을 사용하지 않는다.
PDF에서 인터랙션을 전제로 하지 않는다.
한 페이지에 너무 많은 차트를 넣지 않는다.
작은 글씨로 억지로 많은 정보를 넣지 않는다.
최신 DATA 여부를 확인하지 않고 PDF를 만들지 않는다.
```

---

## 12. 빠른 체크리스트

```text
[ ] 최신 uptodate 날짜를 확인했다.
[ ] 화면용 HTML/DATA가 최신인지 확인했다.
[ ] 필요하면 chart_agent 흐름으로 DATA를 먼저 갱신했다.
[ ] print_chartdesign_guide.md를 읽었다.
[ ] A4 세로 프린트 HTML을 만들었다.
[ ] 4:3 가로 발표용 HTML을 만들었다.
[ ] PDF를 print_output 폴더에 저장했다.
[ ] 페이지 크기와 방향을 확인했다.
[ ] 차트와 글자가 잘리지 않는지 확인했다.
[ ] 흰 배경과 잉크 절약형 색상을 확인했다.
```
