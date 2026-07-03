# 판매 분석 대시보드 차트 디자인 가이드

이 문서는 `integrated_category_dashboard_sample.html`의 화면 디자인, 배치, 인터랙션만 정의합니다.  
숫자 산정은 `category_counting_guide.md`, 데이터 키 구조는 `sales_dashboard_data_spec.md`를 따릅니다.

---

## 1. 기본 원칙

```text
용도: PC 화면에서 침대/책상 판매 흐름을 한눈에 보는 업무용 대시보드
모바일 대응: 하지 않음
스타일: 다크 테마, 컴팩트한 컨트롤, 큰 차트 영역
라이브러리: Chart.js 4.4.1 CDN
출력 형태: 단일 HTML 파일
```

페이지 최소 폭:

```css
body { min-width: 1180px; }
```

---

## 2. 전체 레이아웃

위에서 아래 순서로 배치합니다.

```text
1. 타이틀/로고/부제목/메타
2. 옵션 패널
3. 섹션 제목
4. KPI 한 줄
5. 그래프 탭 + 배송 형태 필터
6. 차트 박스
7. 짧은 설명 문구
```

페이지 여백:

```css
body {
  padding: 18px 22px;
}

.page {
  max-width: 1440px;
  margin: 0 auto;
}
```

---

## 3. 타이틀 영역

타이틀은 로고와 텍스트를 한 줄로 둡니다.

```html
<h1>
  <span class="title-logo">n</span>
  <span class="title-text">니스툴그로우 침대 책상 판매 분석</span>
</h1>
```

타이틀 스펙:

```css
h1 {
  font-size: 22px;
  color: #f5f5f5;
  display: flex;
  align-items: center;
  gap: 10px;
}
```

로고 스펙:

```css
.title-logo {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: rgba(238,29,58,.6);
  color: rgba(255,255,255,.9);
  font-size: 28px;
  font-weight: 900;
}
```

부제목:

```css
.sub {
  font-size: 12px;
  color: #777;
  line-height: 1.45;
  margin-top: 4px;
}
```

메타:

```css
.meta {
  font-size: 11px;
  color: #64748b;
  white-space: nowrap;
}
```

---

## 4. 옵션 패널

옵션 패널은 한 줄 PC 레이아웃입니다.

```text
기간 단위 | 카테고리 | 분석 대상 | 세부 보기
```

그리드:

```css
.filter-grid {
  display: grid;
  grid-template-columns: 230px 160px 330px auto;
  gap: 0;
  align-items: start;
}
```

블록 구분:

```css
.filter-block {
  min-height: 54px;
  padding: 0 18px;
  border-right: 1px solid rgba(148,163,184,.28);
}

.filter-block:first-child { padding-left: 0; }
.filter-block:last-child { border-right: 0; padding-right: 0; }
.filter-block:first-child .buttons { flex-wrap: nowrap; }
```

버튼:

```css
.btn {
  height: 28px;
  padding: 0 11px;
  border: 1px solid #2e3448;
  border-radius: 16px;
  background: #111624;
  color: #8e96a8;
  font-size: 12px;
}

.btn.on {
  background: #1e2d4a;
  border-color: #3b82f6;
  color: #93c5fd;
}
```

기간 단위 버튼은 반드시 한 줄입니다.

```text
주 / 월 / 분기 / 연
```

---

## 5. KPI 카드

KPI는 데스크탑에서 한 줄에 유지합니다.

```css
.kpi {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 7px;
  margin-bottom: 10px;
}

.kpi-card {
  background: #1a2035;
  border: 1px solid #242c44;
  border-radius: 7px;
  padding: 8px 9px;
  min-height: 58px;
  min-width: 0;
}

.kpi-label {
  font-size: 11px;
  color: #7b8498;
  margin-bottom: 4px;
}

.kpi-val {
  font-size: 17px;
  font-weight: 800;
  line-height: 1.2;
  white-space: nowrap;
}
```

KPI 구성:

```text
1. 선택 구간 합계
2. 최근 기간 수량
3~7. 현재 선택된 시리즈별 최근 기간 수량과 비중
```

---

## 6. 탭과 배송 필터

차트 위에는 그래프 탭과 배송 형태 필터를 둡니다.

```text
전체 추이 / 비중 변화 / 누적 막대     배송 형태: 전체 / 자체 / 현대물류 / 에바다
```

```css
.chart-controls {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  gap: 34px;
  margin-bottom: 8px;
}

.tabs {
  display: flex;
  gap: 6px;
}

.ship-filter {
  display: flex;
  align-items: center;
  gap: 8px;
}
```

배송 형태는 너무 오른쪽으로 밀지 않고 탭 옆 중간 위치에 둡니다.

---

## 7. 차트 박스

차트는 화면에서 가장 큰 영역이어야 합니다.

```css
.chart-box {
  background: #13182a;
  border: 1px solid #1e2438;
  border-radius: 10px;
  padding: 8px 12px 2px;
  height: 500px;
  position: relative;
}

.chart-box canvas {
  display: block;
  width: 100%;
  height: 488px;
}
```

날짜축과 설명문 사이 간격은 최소화합니다.

```css
.note {
  font-size: 10px;
  color: #687083;
  line-height: 1.35;
  margin-top: 3px;
}
```

---

## 8. 시작점 조절 막대

차트 안에는 기간 시작점을 조절하는 세로 막대를 둡니다.

동작:

```text
드래그 중: 그래프는 고정, 막대와 음영만 이동
마우스 릴리즈: 그 위치의 기간이 새 시작점으로 적용
적용 후: 막대는 차트 왼쪽에 붙고 차트는 새 시작점부터 다시 그림
전체 기간 버튼: 원래 시작점으로 복귀
```

막대:

```css
.start-handle {
  position: absolute;
  top: 8px;
  bottom: 14px;
  width: 1.3px;
  background: #60a5fa;
  cursor: ew-resize;
  z-index: 4;
}
```

클릭 영역은 막대보다 넓게 잡습니다.

```css
.start-handle:before {
  content: '';
  position: absolute;
  left: -7px;
  right: -7px;
  top: 0;
  bottom: 0;
}
```

시작점 컨트롤:

```html
<div class="start-bubble">
  <button class="range-reset">전체 기간</button>
  <span class="start-current">2018.01</span>
</div>
```

```css
.start-bubble {
  position: absolute;
  top: 8px;
  left: 8px;
  display: flex;
  gap: 6px;
  align-items: center;
  z-index: 6;
}

.range-reset,
.start-current {
  height: 22px;
  padding: 0 9px;
  border-radius: 999px;
  font-size: 10px;
  border: 1px solid #3b82f6;
  background: #1e2d4a;
  color: #bfdbfe;
}
```

---

## 9. Chart.js 옵션

기본 옵션:

```js
{
  responsive: true,
  maintainAspectRatio: false,
  layout: { padding: { top: 4, right: 4, bottom: 0, left: 0 } },
  animation: { duration: 500 },
  hover: { animationDuration: 500 },
  interaction: { mode: 'nearest', intersect: false, axis: 'xy' }
}
```

툴팁:

```js
tooltip: {
  position: 'nearest',
  animation: { duration: 500 },
  backgroundColor: '#1a2035',
  borderColor: '#2e3a5c',
  borderWidth: 1,
  titleColor: '#e0e0e0',
  bodyColor: '#bbb'
}
```

중요:

```text
툴팁 값은 풍선 위치가 아니라 마우스 포인터가 올라간 데이터 포인트 기준으로 표시합니다.
```

X축:

```text
월: 45도 회전, autoSkip false
분기/연: 수평, autoSkip false
주: maxTicksLimit 22
```

Y축:

```text
0부터 시작
판매 대수는 천 단위 콤마
비중 변화 탭은 % 단위
```

---

## 10. 시리즈 색상

```js
const colors = {
  ivy: '#3b82f6',
  neti: '#10b981',
  hey: '#a78bfa',
  camper: '#f59e0b',
  stins: '#fb7185',
  single: '#94a3b8',
  lowbunk: '#22c55e',
  mid: '#38bdf8',
  high: '#facc15',
  bunk: '#ef4444',
  desk: '#60a5fa',
  plywood: '#7dd3fc',
  oak: '#d4a574',
  rear: '#c084fc',
  avg: '#f472b6'
}
```

색상은 한 화면이 한 계열로만 보이지 않도록 분산합니다. 하늘색은 주요 포인트로 사용하되 전체 UI가 하늘색만으로 보이지 않게 합니다.

---

## 11. 탭별 차트 형태

| 탭 | 차트 형태 |
| --- | --- |
| 전체 추이 | line |
| 비중 변화 | line, y축 % |
| 누적 막대 | stacked bar |
| 책상 상판 구성 | stacked bar |
| 책상 리어탑 구성 | stacked bar |

`전체 추이`에서 시리즈가 2개 이상이면 `합계 3기간 평균` 이동평균선을 추가합니다.

---

## 12. 최종 확인 항목

차트를 수정한 뒤 아래를 확인합니다.

```text
상단 옵션이 한 화면에 컴팩트하게 보이는가
기간 단위 주/월/분기/연이 한 줄인가
KPI가 데스크탑에서 한 줄인가
차트 높이가 충분히 큰가
날짜축과 설명문 사이 간격이 좁은가
시작점 막대가 드래그 중에는 차트를 바꾸지 않고, 릴리즈 후에만 적용되는가
전체 기간 버튼이 막대 옆에 있고 정상 초기화되는가
툴팁이 마우스 포인터 위치의 데이터를 보여주는가
마지막 기간 2026-06-10 부분 데이터가 표시되는가
```
