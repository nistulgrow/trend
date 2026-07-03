# 프린트 PDF 차트 디자인 가이드

이 문서는 판매 분석 데이터를 PDF로 출력할 때 사용하는 디자인 기준입니다.

화면용 대시보드는 `sales_chartdesign_guide.md`를 따르지만, 프린트/PDF 출력은 이 문서를 따릅니다.

핵심 원칙:

```text
흰 배경
잉크 절약
프린트 가독성
고정 레이아웃
PDF/PPT 삽입 적합성
```

---

## 1. 출력 종류

두 가지 출력을 기본으로 합니다.

| 출력 | 용도 | 파일명 |
| --- | --- | --- |
| A4 세로 보고서 | 종이 출력, 내부 보고서 | `a4_report_YYYYMMDD.pdf` |
| 4:3 가로 발표용 | PPT 삽입, 회의 발표 | `slide_4x3_YYYYMMDD.pdf` |

저장 위치:

```text
print_output/
```

---

## 2. 공통 디자인 원칙

### 2-1. 배경

```css
body {
  background: #ffffff;
  color: #111827;
}
```

어두운 배경, 큰 컬러 면적, 진한 그라데이션은 사용하지 않습니다.

### 2-2. 색상

차트 색상은 화면용보다 밝고 절제된 색을 사용합니다.

권장 팔레트:

```css
--blue:   #2563eb;
--sky:    #0284c7;
--green:  #059669;
--orange: #d97706;
--red:    #dc2626;
--purple: #7c3aed;
--gray:   #6b7280;
--line:   #d1d5db;
--text:   #111827;
--muted:  #6b7280;
```

넓은 면적을 채울 때는 투명도를 낮춥니다.

```css
background: rgba(37, 99, 235, 0.08);
```

### 2-3. 폰트

한국어 프린트 가독성을 우선합니다.

```css
font-family: "Apple SD Gothic Neo", "Malgun Gothic", Arial, sans-serif;
```

기본 글자 크기:

```text
본문: 9~10pt
보조문구: 7.5~8pt
차트 축: 7.5~8.5pt
표 제목: 10~12pt
페이지 제목: 16~20pt
```

작은 글씨로 많은 정보를 넣기보다 페이지를 나눕니다.

---

## 3. A4 세로 보고서

### 3-1. 페이지 설정

```css
@page {
  size: A4 portrait;
  margin: 10mm;
}
```

권장 화면 기준 크기:

```text
폭: 794px
높이: 1123px
```

HTML은 PDF 변환 시 CSS page size를 우선 사용합니다.

### 3-2. 페이지 구조

한 페이지는 아래 구조를 기본으로 합니다.

```text
상단 헤더
KPI 요약
메인 차트
보조 차트 또는 작은 표
하단 메모
```

예:

```html
<section class="page a4">
  <header class="page-header">...</header>
  <div class="kpi-row">...</div>
  <div class="chart-block main">...</div>
  <div class="chart-block sub">...</div>
  <footer class="page-note">...</footer>
</section>
```

### 3-3. 여백

```css
.page {
  padding: 0;
}

.page-header {
  margin-bottom: 10px;
}

.kpi-row {
  margin-bottom: 10px;
}

.chart-block {
  margin-bottom: 8px;
}
```

불필요한 장식 여백을 줄이고 차트 영역을 크게 둡니다.

### 3-4. KPI

KPI는 작은 카드 형태로 배치하되, 진한 배경을 쓰지 않습니다.

```css
.kpi-card {
  border: 1px solid #e5e7eb;
  background: #f9fafb;
  border-radius: 6px;
  padding: 7px 8px;
}
```

KPI는 한 줄에 3~5개 정도가 적당합니다.

---

## 4. 4:3 가로 발표용 PDF

### 4-1. 페이지 설정

4:3 비율을 사용합니다.

```css
@page {
  size: 10in 7.5in;
  margin: 0.35in;
}
```

권장 화면 기준 크기:

```text
폭: 960px
높이: 720px
```

### 4-2. 슬라이드 구조

한 장에 하나의 메시지를 담습니다.

```text
상단: 제목 + 기준 기간
중앙: 큰 차트 1개
하단: 핵심 수치 또는 해석 1줄
```

예:

```html
<section class="slide">
  <header class="slide-header">...</header>
  <div class="slide-chart">...</div>
  <footer class="slide-note">...</footer>
</section>
```

### 4-3. 차트 크기

차트는 슬라이드 중앙 대부분을 차지해야 합니다.

```css
.slide-chart {
  height: 520px;
}
```

범례는 차트 위나 오른쪽에 작게 배치합니다.

---

## 5. 차트 스타일

### 5-1. 축과 그리드

축은 얇고 선명하게, 그리드는 아주 연하게 둡니다.

```js
scales: {
  x: {
    grid: { color: 'rgba(209, 213, 219, 0.45)' },
    ticks: { color: '#374151' }
  },
  y: {
    grid: { color: 'rgba(209, 213, 219, 0.55)' },
    ticks: { color: '#374151' }
  }
}
```

### 5-2. 선 그래프

```js
borderWidth: 2,
pointRadius: 0,
pointHoverRadius: 3,
tension: 0.25
```

PDF에서는 점을 너무 많이 찍지 않습니다.

### 5-3. 막대 그래프

```js
borderWidth: 0,
borderRadius: 2,
barPercentage: 0.78,
categoryPercentage: 0.72
```

누적 막대는 색 면적이 커지므로 너무 진한 색을 피합니다.

### 5-4. 범례

범례는 간결해야 합니다.

```js
plugins: {
  legend: {
    labels: {
      boxWidth: 10,
      boxHeight: 10,
      color: '#374151',
      font: { size: 10 }
    }
  }
}
```

### 5-5. 툴팁

PDF에서는 툴팁이 필요 없습니다.

```js
tooltip: { enabled: false }
```

---

## 6. 데이터 표시 방식

### 6-1. 기간 단위

PDF는 너무 촘촘한 기간을 피합니다.

권장:

| 출력 | 기본 기간 |
| --- | --- |
| A4 보고서 | 월 또는 분기 |
| 4:3 발표용 | 월 또는 분기 |

주간 데이터는 최근 흐름을 강조할 때만 사용합니다.

연간 데이터는 장기 요약 페이지에 사용합니다.

### 6-2. 시작점

PDF는 고정 출력물이므로 시작점 조절 막대를 넣지 않습니다.

대신 페이지 제목이나 메모에 기준 기간을 표시합니다.

예:

```text
기준 기간: 2014.06 ~ 2026.07.02
```

### 6-3. 배송 형태

배송 형태가 필요한 경우 페이지나 슬라이드를 나눕니다.

예:

```text
전체
자체/수도권
현대물류
에바다
```

한 차트 안에 모든 배송 형태를 억지로 넣지 않습니다.

---

## 7. A4 보고서 권장 페이지

### 7-1. 1페이지: 전체 요약

```text
제목: 니스툴그로우 침대 책상 판매 분석
KPI: 전체 침대, 아기침대, 주니어 침대, 책상
차트: 침대류 vs 책상류 월별 추이
보조: 최근 기간 핵심 수치
```

### 7-2. 2페이지: 아기침대

```text
KPI: 아이비, 네티류, 아이비 비중
차트: 아이비 vs 네티류 비중 변화
보조: 네티/네티플러스/네티맥스 구성
```

### 7-3. 3페이지: 주니어 침대

```text
KPI: 헤이, 캠퍼, 스틴스
차트: 헤이 vs 캠퍼 vs 스틴스 비중 변화
보조: 싱글/로우벙커/미드/하이/이층 구조 변화
```

### 7-4. 4페이지: 책상류

```text
KPI: 전체 데스크, 플라이우드 상판, 오크 상판
차트: 데스크 전체 수량 추이
보조: 상판/리어탑 구성 비중
```

---

## 8. 4:3 발표용 권장 슬라이드

### 8-1. 1장: 전체 흐름

```text
제목: 침대/책상 판매 흐름
차트: 월별 전체 판매 추이
하단 문구: 최근 기간 변화 요약
```

### 8-2. 2장: 아기침대

```text
제목: 아기침대 내 아이비/네티류 비중
차트: 아이비 vs 네티류 비중 변화
```

### 8-3. 3장: 주니어 침대 브랜드

```text
제목: 주니어 침대 브랜드 비중
차트: 헤이 vs 캠퍼 vs 스틴스 비중 변화
```

### 8-4. 4장: 주니어 침대 구조

```text
제목: 싱글/로우벙커/미드/하이/이층 구조 변화
차트: 구조별 비중 변화
```

### 8-5. 5장: 책상류

```text
제목: 책상 판매와 상판 구성
차트: 데스크 전체 수량 + 상판/리어탑 구성
```

---

## 9. HTML/PDF 생성 기준

### 9-1. 공통 HTML

```html
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
</head>
<body>
  ...
</body>
</html>
```

### 9-2. 인쇄 CSS

```css
@media print {
  * {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }

  body {
    margin: 0;
  }

  .page,
  .slide {
    break-after: page;
    page-break-after: always;
  }
}
```

### 9-3. 페이지 넘김

각 페이지/슬라이드는 독립된 `section`으로 만듭니다.

```html
<section class="page">...</section>
<section class="page">...</section>
```

마지막 페이지는 불필요한 빈 페이지가 생기지 않도록 처리합니다.

```css
.page:last-child,
.slide:last-child {
  break-after: auto;
  page-break-after: auto;
}
```

---

## 10. 검증 체크리스트

PDF를 만들기 전:

```text
[ ] 최신 데이터 기준일이 표시되어 있다.
[ ] 화면용 DATA와 숫자가 일치한다.
[ ] 차트별 기간 단위가 명확하다.
[ ] 마지막 미완성 기간 포함 여부가 명확하다.
```

PDF를 만든 후:

```text
[ ] A4 세로 PDF는 A4 portrait로 출력된다.
[ ] 4:3 PDF는 10in x 7.5in 또는 같은 4:3 비율이다.
[ ] 배경이 흰색이다.
[ ] 차트가 페이지 밖으로 잘리지 않는다.
[ ] 제목, 축, 범례가 겹치지 않는다.
[ ] 글자가 프린트에서 읽을 수 있는 크기다.
[ ] 넓은 진한 배경 면적이 없다.
[ ] 흑백 출력에서도 주요 선/막대 구분이 가능하다.
```

---

## 11. 금지 사항

```text
검은 배경을 사용하지 않는다.
화면용 다크 테마 색상을 그대로 쓰지 않는다.
툴팁이나 버튼 같은 인터랙션 요소를 넣지 않는다.
한 페이지에 모든 정보를 몰아넣지 않는다.
작은 글씨로 무리하게 많은 시리즈를 넣지 않는다.
넓은 면적에 진한 색을 채우지 않는다.
```
