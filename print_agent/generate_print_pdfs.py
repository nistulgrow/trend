from __future__ import annotations

import re
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/thewalldata_matplotlib")

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import font_manager


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "input"
OUTPUT = ROOT / "print_output"
OUTPUT.mkdir(exist_ok=True)


FIXED = ["상품명", "옵션내용", "현재고", "미발송수", "주문수", "주문금액"]


def setup_font() -> None:
    candidates = [
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
        "/Library/Fonts/AppleGothic.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            font_manager.fontManager.addfont(candidate)
            prop = font_manager.FontProperties(fname=candidate)
            plt.rcParams["font.family"] = prop.get_name()
            break
    plt.rcParams["axes.unicode_minus"] = False


def latest_base_date() -> str:
    files = sorted(INPUT.glob("uptodate_????????.csv"))
    if not files:
        raise FileNotFoundError("input/uptodate_YYYYMMDD.csv 파일이 없습니다.")
    return re.search(r"uptodate_(\d{8})\.csv", files[-1].name).group(1)


def read_period(kind: str, base: str) -> tuple[pd.DataFrame, list[str]]:
    suffix = "" if kind == "day" else f"_{kind}"
    path = INPUT / f"uptodate_{base}{suffix}.csv"
    df = pd.read_csv(path, encoding="utf-8-sig", dtype=str).fillna("")
    periods = [c for c in df.columns if c not in FIXED]
    for c in periods:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    return df, periods


def contains(series: pd.Series, text: str) -> pd.Series:
    return series.str.contains(text, regex=False, na=False)


def row_sum(df: pd.DataFrame, periods: list[str], mask: pd.Series) -> np.ndarray:
    if mask.sum() == 0:
        return np.zeros(len(periods), dtype=float)
    return df.loc[mask, periods].sum(axis=0).to_numpy(dtype=float)


def box_no(option: str) -> int | None:
    m = re.search(r"\b([1234])\b|([1234])번", option)
    if not m:
        return None
    return int(m.group(1) or m.group(2))


def opt_box_mask(df: pd.DataFrame, nums: set[int]) -> pd.Series:
    return df["옵션내용"].map(lambda x: box_no(x) in nums)


def min_arrays(*arrays: np.ndarray) -> np.ndarray:
    if not arrays:
        return np.array([])
    return np.minimum.reduce(arrays)


def min_positive_components(*arrays: np.ndarray) -> np.ndarray:
    if not arrays:
        return np.array([])
    stacked = np.vstack(arrays)
    out = np.zeros(stacked.shape[1], dtype=float)
    for i in range(stacked.shape[1]):
        vals = stacked[:, i]
        vals = vals[vals > 0]
        out[i] = vals.min() if len(vals) else 0
    return out


def clean_mask(df: pd.DataFrame) -> pd.Series:
    text = df["상품명"] + " " + df["옵션내용"]
    excluded = ["B급", "AS용", "범퍼가드", "펠트도어", "서랍", "커버", "완장", "쿠키", "안전가드"]
    mask = pd.Series(True, index=df.index)
    for word in excluded:
        mask &= ~contains(text, word)
    return mask


def count_ivy(df: pd.DataFrame, periods: list[str]) -> np.ndarray:
    text = df["상품명"] + " " + df["옵션내용"]
    mask = (contains(text, "아이비") | contains(text, "Ivy")) & clean_mask(df)
    mask &= ~contains(text, "통판 1세트") & ~contains(text, "통판 1ea") & ~contains(text, "모듈변경")
    ss = mask & contains(df["옵션내용"], "SS")
    es = mask & contains(df["옵션내용"], "ES")
    ss1 = row_sum(df, periods, ss & opt_box_mask(df, {1}))
    ss2 = row_sum(df, periods, ss & opt_box_mask(df, {2}))
    es1 = row_sum(df, periods, es & opt_box_mask(df, {1}))
    es2 = row_sum(df, periods, es & opt_box_mask(df, {2}))
    return min_arrays(ss1, ss2) + min_arrays(es1, es2)


def count_neti(df: pd.DataFrame, periods: list[str]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    text = df["상품명"] + " " + df["옵션내용"]
    base_clean = clean_mask(df) & ~contains(text, "변형키트")
    neti = contains(df["상품명"], "네티") & ~contains(df["상품명"], "플러스") & ~contains(df["상품명"], "맥스") & base_clean
    plus = contains(df["상품명"], "네티 플러스") & base_clean
    max_mask = contains(df["상품명"], "네티 맥스") & base_clean
    max1 = row_sum(df, periods, max_mask & contains(df["옵션내용"], "1번"))
    max2 = row_sum(df, periods, max_mask & contains(df["옵션내용"], "2번"))
    return row_sum(df, periods, neti), row_sum(df, periods, plus), min_arrays(max1, max2)


def count_hey(df: pd.DataFrame, periods: list[str]) -> dict[str, np.ndarray]:
    name, opt = df["상품명"], df["옵션내용"]
    clean = clean_mask(df)
    single_mask = contains(name, "헤이(HEJ) 단층침대") & clean
    single = min_arrays(
        row_sum(df, periods, single_mask & opt_box_mask(df, {1})),
        row_sum(df, periods, single_mask & opt_box_mask(df, {2})),
    )
    low_mask = contains(name, "헤이(HEJ) 로우벙커") & clean
    low = min_arrays(
        row_sum(df, periods, low_mask & opt_box_mask(df, {1})),
        row_sum(df, periods, low_mask & opt_box_mask(df, {2})),
    )
    mid_mask = contains(name, "헤이(HEJ) 미드확장키트") & clean
    old_mid = min_arrays(
        row_sum(df, periods, mid_mask & opt_box_mask(df, {3})),
        row_sum(df, periods, mid_mask & opt_box_mask(df, {4})),
    )
    new_mid = row_sum(df, periods, mid_mask & ~opt_box_mask(df, {1, 2, 3, 4}))
    mid = old_mid + new_mid
    high_mask = contains(name, "헤이(HEJ) 하이확장키트") & clean
    high = min_arrays(
        row_sum(df, periods, high_mask & opt_box_mask(df, {1})),
        row_sum(df, periods, high_mask & opt_box_mask(df, {2})),
    )
    common = contains(name, "헤이(HEJ), 캠퍼(Camper) 공용 2층확장키트") & clean
    hey_common = min_positive_components(
        row_sum(df, periods, common & opt_box_mask(df, {1})),
        row_sum(df, periods, common & opt_box_mask(df, {2})),
        row_sum(df, periods, common & contains(opt, "헤이용 짧은키트")),
    )
    es = contains(name, "헤이(HEJ) 2층확장키트 ES") & clean
    hey_es = min_positive_components(
        row_sum(df, periods, es & opt_box_mask(df, {1})),
        row_sum(df, periods, es & opt_box_mask(df, {2})),
        row_sum(df, periods, es & contains(opt, "짧은키트")),
    )
    bunk = hey_common + hey_es
    standalone_single = np.maximum(0, single - mid - high - 2 * bunk)
    return {
        "brand": standalone_single + low + mid + high + bunk,
        "single": standalone_single,
        "low": low,
        "mid": mid,
        "high": high,
        "bunk": bunk,
    }


def count_camper(df: pd.DataFrame, periods: list[str]) -> dict[str, np.ndarray]:
    name, opt = df["상품명"], df["옵션내용"]
    clean = clean_mask(df)
    mid_mask = contains(name, "캠퍼(Camper) 미드") & clean
    mid = min_positive_components(
        row_sum(df, periods, mid_mask & opt_box_mask(df, {1})),
        row_sum(df, periods, mid_mask & opt_box_mask(df, {2})),
        row_sum(df, periods, mid_mask & opt_box_mask(df, {3})),
        row_sum(df, periods, mid_mask & contains(opt, "미드확장키트")),
        row_sum(df, periods, mid_mask & contains(opt, "사다리")),
    )
    high_mask = contains(name, "캠퍼(Camper) 하이확장키트") & clean
    high = min_positive_components(
        row_sum(df, periods, high_mask & opt_box_mask(df, {1})),
        row_sum(df, periods, high_mask & opt_box_mask(df, {2})),
        row_sum(df, periods, high_mask & contains(opt, "사다리")),
    )
    common = contains(name, "헤이(HEJ), 캠퍼(Camper) 공용 2층확장키트") & clean
    bunk = min_positive_components(
        row_sum(df, periods, common & opt_box_mask(df, {1})),
        row_sum(df, periods, common & opt_box_mask(df, {2})),
        row_sum(df, periods, common & contains(opt, "캠퍼용 짧은키트")) / 2,
    )
    return {
        "brand": mid + high + bunk,
        "single": np.zeros(len(periods)),
        "low": np.zeros(len(periods)),
        "mid": mid,
        "high": high,
        "bunk": bunk,
    }


def strip_ship(name: str) -> str:
    for p in ["자체 ", "현대물류용 ", "에바다용 "]:
        if name.startswith(p):
            return name[len(p):]
    return name


def count_stins(df: pd.DataFrame, periods: list[str]) -> dict[str, np.ndarray]:
    name, opt = df["상품명"], df["옵션내용"]
    clean = clean_mask(df)
    stripped = name.map(strip_ship)
    old_single = (stripped == "싱글침대") & clean
    old_mid = (stripped == "미드확장키트") & clean
    old_high = (stripped == "하이확장키트") & clean
    old_bunk = (stripped == "벙커확장키트") & clean
    dp = contains(name, "DP용 스틴스") & clean
    single_body = row_sum(df, periods, old_single | (dp & (contains(opt, "싱글침대") | contains(opt, "싱글가드침대"))))
    mid = row_sum(df, periods, old_mid | (dp & contains(opt, "미드침대")))
    high = row_sum(df, periods, old_high | (dp & contains(opt, "하이침대")))
    bunk = row_sum(df, periods, old_bunk | (dp & (contains(opt, "2층침대") | contains(opt, "이층침대"))))
    standalone_single = np.maximum(0, single_body - mid - high - 2 * bunk)
    return {
        "brand": standalone_single + mid + high + bunk,
        "single": standalone_single,
        "low": np.zeros(len(periods)),
        "mid": mid,
        "high": high,
        "bunk": bunk,
    }


def count_desk(df: pd.DataFrame, periods: list[str]) -> dict[str, np.ndarray]:
    name, opt = df["상품명"], df["옵션내용"]
    clean = clean_mask(df)
    grow = contains(name, "그로우 데스크") & clean
    neutral = contains(name, "뉴트럴 플라이우드 데스크") & clean
    legs = row_sum(df, periods, grow & (contains(opt, "다리W") | contains(opt, "다리G")))
    grow_top = row_sum(df, periods, grow & (contains(opt, "상판SN") | contains(opt, "상판CN")))
    frame = row_sum(df, periods, neutral & contains(opt, "프레임-오프화이트"))
    plywood_top = row_sum(
        df,
        periods,
        (grow & (contains(opt, "상판SN") | contains(opt, "상판CN")))
        | (neutral & contains(opt, "상판-") & ~contains(opt, "오크솔리드원목")),
    )
    oak_top = row_sum(df, periods, neutral & contains(opt, "상판-오크솔리드원목"))
    plywood_rear = row_sum(
        df,
        periods,
        (grow & (contains(opt, "리어탑SN") | contains(opt, "리어탑CN")))
        | (neutral & contains(opt, "리어탑-") & ~contains(opt, "오크솔리드원목")),
    )
    oak_rear = row_sum(df, periods, neutral & contains(opt, "리어탑-오크솔리드원목"))
    neutral_top_all = row_sum(df, periods, neutral & contains(opt, "상판-"))
    neutral_rear_all = row_sum(df, periods, neutral & contains(opt, "리어탑-"))
    neutral_corrected = np.maximum(frame, np.minimum(neutral_top_all, neutral_rear_all))
    total = np.zeros(len(periods))
    for i, p in enumerate(periods):
        year = int(str(p)[:4])
        if year < 2018:
            total[i] = legs[i]
        else:
            total[i] = grow_top[i] + neutral_corrected[i]
    return {
        "total": total,
        "plywood_top": plywood_top,
        "oak_top": oak_top,
        "plywood_rear": plywood_rear,
        "oak_rear": oak_rear,
        "oak_est": np.minimum(oak_top, oak_rear),
    }


def compute(df: pd.DataFrame, periods: list[str]) -> dict[str, np.ndarray]:
    ivy = count_ivy(df, periods)
    neti, neti_plus, neti_max = count_neti(df, periods)
    hey = count_hey(df, periods)
    camper = count_camper(df, periods)
    stins = count_stins(df, periods)
    desk = count_desk(df, periods)
    baby_neti = neti + neti_plus + neti_max
    return {
        "baby_ivy": ivy,
        "baby_neti": baby_neti,
        "neti": neti,
        "neti_plus": neti_plus,
        "neti_max": neti_max,
        "junior_hey": hey["brand"],
        "junior_camper": camper["brand"],
        "junior_stins": stins["brand"],
        "junior_single": hey["single"] + camper["single"] + stins["single"],
        "junior_lowbunk": hey["low"] + camper["low"] + stins["low"],
        "junior_mid": hey["mid"] + camper["mid"] + stins["mid"],
        "junior_high": hey["high"] + camper["high"] + stins["high"],
        "junior_bunk": hey["bunk"] + camper["bunk"] + stins["bunk"],
        "desk_total": desk["total"],
        "desk_plywood_top": desk["plywood_top"],
        "desk_oak_top": desk["oak_top"],
        "desk_plywood_rear": desk["plywood_rear"],
        "desk_oak_rear": desk["oak_rear"],
        "desk_oak_est": desk["oak_est"],
    }


def fmt(n: float) -> str:
    return f"{int(round(n)):,}"


def label_month(p: str) -> str:
    return f"{p[:4]}.{p[4:6]}"


def label_quarter(p: str) -> str:
    return p.replace("Q", " Q")


def recent_slice(labels: list[str], data: dict[str, np.ndarray], n: int) -> tuple[list[str], dict[str, np.ndarray]]:
    return labels[-n:], {k: v[-n:] for k, v in data.items()}


def style_axes(ax):
    ax.set_facecolor("white")
    ax.grid(axis="y", color="#e5e7eb", linewidth=0.7)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color("#d1d5db")
    ax.spines["bottom"].set_color("#d1d5db")
    ax.tick_params(colors="#374151", labelsize=8)


def draw_header(fig, title: str, subtitle: str):
    fig.text(0.05, 0.965, title, fontsize=18, weight="bold", color="#111827", va="top")
    fig.text(0.05, 0.937, subtitle, fontsize=9, color="#6b7280", va="top")


def draw_kpis(fig, items: list[tuple[str, str]], y: float = 0.885):
    count = len(items)
    width = 0.90 / count
    for i, (label, value) in enumerate(items):
        x = 0.05 + i * width
        rect = plt.Rectangle((x, y - 0.048), width - 0.012, 0.055, transform=fig.transFigure,
                             facecolor="#f9fafb", edgecolor="#e5e7eb", linewidth=0.8)
        fig.patches.append(rect)
        fig.text(x + 0.010, y - 0.007, label, fontsize=8, color="#6b7280", va="top")
        fig.text(x + 0.010, y - 0.030, value, fontsize=13, weight="bold", color="#111827", va="top")


def stacked_area(ax, x, series, labels, colors, title):
    ax.stackplot(x, series, labels=labels, colors=colors, alpha=0.78)
    ax.set_title(title, loc="left", fontsize=11, weight="bold", color="#111827", pad=8)
    style_axes(ax)
    ax.legend(loc="upper left", ncol=len(labels), fontsize=8, frameon=False)


def line_plot(ax, x, series, labels, colors, title):
    for s, label, color in zip(series, labels, colors):
        ax.plot(x, s, label=label, color=color, linewidth=2)
    ax.set_title(title, loc="left", fontsize=11, weight="bold", color="#111827", pad=8)
    style_axes(ax)
    ax.legend(loc="upper left", ncol=min(4, len(labels)), fontsize=8, frameon=False)


def bar_plot(ax, names, values, colors, title):
    ax.bar(names, values, color=colors, alpha=0.88)
    ax.set_title(title, loc="left", fontsize=11, weight="bold", color="#111827", pad=8)
    style_axes(ax)
    for i, v in enumerate(values):
        ax.text(i, v, fmt(v), ha="center", va="bottom", fontsize=8, color="#374151")


def apply_xlabels(ax, labels, step):
    ax.set_xticks(np.arange(0, len(labels), step))
    ax.set_xticklabels([labels[i] for i in range(0, len(labels), step)], rotation=0, ha="center")


def make_a4(base: str, month_labels: list[str], month: dict[str, np.ndarray], q_labels: list[str], quarter: dict[str, np.ndarray]) -> Path:
    path = OUTPUT / f"a4_report_{base}.pdf"
    colors = ["#2563eb", "#059669", "#d97706", "#7c3aed", "#dc2626"]
    with PdfPages(path) as pdf:
        # Page 1
        fig = plt.figure(figsize=(8.27, 11.69), facecolor="white")
        draw_header(fig, "니스툴그로우 침대 책상 판매 분석", f"프린트용 A4 보고서 · 데이터 기준 {base[:4]}.{base[4:6]}.{base[6:8]}")
        total_baby = month["baby_ivy"] + month["baby_neti"]
        total_junior = month["junior_hey"] + month["junior_camper"] + month["junior_stins"]
        total_bed = total_baby + total_junior
        draw_kpis(fig, [
            ("침대 누적", fmt(total_bed.sum())),
            ("아기침대", fmt(total_baby.sum())),
            ("주니어침대", fmt(total_junior.sum())),
            ("책상 누적", fmt(month["desk_total"].sum())),
        ])
        labels36, m36 = recent_slice(month_labels, month, 36)
        x = np.arange(len(labels36))
        ax1 = fig.add_axes([0.08, 0.55, 0.84, 0.27])
        line_plot(ax1, x, [m36["baby_ivy"] + m36["baby_neti"], m36["junior_hey"] + m36["junior_camper"] + m36["junior_stins"], m36["desk_total"]], ["아기침대", "주니어침대", "책상"], colors[:3], "최근 36개월 주요 카테고리 추이")
        apply_xlabels(ax1, labels36, 6)
        ax2 = fig.add_axes([0.08, 0.18, 0.84, 0.27])
        qs = [quarter["baby_ivy"] + quarter["baby_neti"], quarter["junior_hey"] + quarter["junior_camper"] + quarter["junior_stins"], quarter["desk_total"]]
        qlab, qdata = recent_slice(q_labels, {"baby": qs[0], "junior": qs[1], "desk": qs[2]}, 20)
        xq = np.arange(len(qlab))
        line_plot(ax2, xq, [qdata["baby"], qdata["junior"], qdata["desk"]], ["아기침대", "주니어침대", "책상"], colors[:3], "최근 20분기 흐름")
        apply_xlabels(ax2, qlab, 4)
        fig.text(0.05, 0.08, "메모: 마지막 월/분기는 완료되지 않은 기간이어도 up-to-date 기준으로 포함합니다.", fontsize=8, color="#6b7280")
        pdf.savefig(fig)
        plt.close(fig)

        # Page 2 baby
        fig = plt.figure(figsize=(8.27, 11.69), facecolor="white")
        draw_header(fig, "아기침대 분석", "아이비와 네티류 비중 변화")
        baby_recent = total_baby[-1]
        ivy_share = month["baby_ivy"][-1] / baby_recent * 100 if baby_recent else 0
        draw_kpis(fig, [
            ("최근월 아이비", fmt(month["baby_ivy"][-1])),
            ("최근월 네티류", fmt(month["baby_neti"][-1])),
            ("아이비 비중", f"{ivy_share:.1f}%"),
        ])
        labels48, m48 = recent_slice(month_labels, month, 48)
        x = np.arange(len(labels48))
        ax1 = fig.add_axes([0.08, 0.55, 0.84, 0.27])
        line_plot(ax1, x, [m48["baby_ivy"], m48["baby_neti"]], ["아이비", "네티류"], ["#2563eb", "#059669"], "최근 48개월 아기침대")
        apply_xlabels(ax1, labels48, 8)
        ax2 = fig.add_axes([0.08, 0.18, 0.84, 0.27])
        total = np.maximum(1, m48["baby_ivy"] + m48["baby_neti"])
        stacked_area(ax2, x, [m48["baby_ivy"] / total * 100, m48["baby_neti"] / total * 100], ["아이비", "네티류"], ["#93c5fd", "#86efac"], "아기침대 비중")
        ax2.set_ylim(0, 100)
        apply_xlabels(ax2, labels48, 8)
        pdf.savefig(fig)
        plt.close(fig)

        # Page 3 junior
        fig = plt.figure(figsize=(8.27, 11.69), facecolor="white")
        draw_header(fig, "주니어 침대 분석", "브랜드와 구조 비중 변화")
        jr_recent = month["junior_hey"][-1] + month["junior_camper"][-1] + month["junior_stins"][-1]
        draw_kpis(fig, [
            ("최근월 헤이", fmt(month["junior_hey"][-1])),
            ("최근월 캠퍼", fmt(month["junior_camper"][-1])),
            ("최근월 스틴스", fmt(month["junior_stins"][-1])),
            ("최근월 주니어", fmt(jr_recent)),
        ])
        labels48, m48 = recent_slice(month_labels, month, 48)
        x = np.arange(len(labels48))
        ax1 = fig.add_axes([0.08, 0.55, 0.84, 0.27])
        total = np.maximum(1, m48["junior_hey"] + m48["junior_camper"] + m48["junior_stins"])
        stacked_area(ax1, x, [m48["junior_hey"] / total * 100, m48["junior_camper"] / total * 100, m48["junior_stins"] / total * 100], ["헤이", "캠퍼", "스틴스"], ["#60a5fa", "#34d399", "#f59e0b"], "주니어 브랜드 비중")
        ax1.set_ylim(0, 100)
        apply_xlabels(ax1, labels48, 8)
        ax2 = fig.add_axes([0.08, 0.18, 0.84, 0.27])
        struct = [m48["junior_single"], m48["junior_lowbunk"], m48["junior_mid"], m48["junior_high"], m48["junior_bunk"]]
        total_s = np.maximum(1, sum(struct))
        stacked_area(ax2, x, [s / total_s * 100 for s in struct], ["싱글", "로우벙커", "미드", "하이", "이층"], ["#94a3b8", "#22c55e", "#38bdf8", "#eab308", "#ef4444"], "주니어 구조 비중")
        ax2.set_ylim(0, 100)
        apply_xlabels(ax2, labels48, 8)
        fig.text(0.05, 0.08, "메모: 스틴스 싱글은 미드/하이/이층 포함분을 차감한 단독 싱글 하한값입니다.", fontsize=8, color="#6b7280")
        pdf.savefig(fig)
        plt.close(fig)

        # Page 4 desk
        fig = plt.figure(figsize=(8.27, 11.69), facecolor="white")
        draw_header(fig, "책상류 분석", "전체 수량과 상판/리어탑 구성")
        draw_kpis(fig, [
            ("최근월 책상", fmt(month["desk_total"][-1])),
            ("최근월 오크 추정", fmt(month["desk_oak_est"][-1])),
            ("상판 오크 비중", f"{(month['desk_oak_top'][-1] / max(1, month['desk_oak_top'][-1] + month['desk_plywood_top'][-1]) * 100):.1f}%"),
        ])
        labels48, m48 = recent_slice(month_labels, month, 48)
        x = np.arange(len(labels48))
        ax1 = fig.add_axes([0.08, 0.55, 0.84, 0.27])
        line_plot(ax1, x, [m48["desk_total"]], ["책상 전체"], ["#2563eb"], "최근 48개월 책상 전체")
        apply_xlabels(ax1, labels48, 8)
        ax2 = fig.add_axes([0.08, 0.18, 0.38, 0.27])
        bar_plot(ax2, ["플라이우드", "오크"], [m48["desk_plywood_top"][-12:].sum(), m48["desk_oak_top"][-12:].sum()], ["#38bdf8", "#d97706"], "최근 12개월 상판 구성")
        ax3 = fig.add_axes([0.54, 0.18, 0.38, 0.27])
        bar_plot(ax3, ["플라이우드", "오크"], [m48["desk_plywood_rear"][-12:].sum(), m48["desk_oak_rear"][-12:].sum()], ["#38bdf8", "#d97706"], "최근 12개월 리어탑 구성")
        fig.text(0.05, 0.08, "메모: 책상 전체는 시기별 기준이 다릅니다. 구형은 다리, 2018년 이후 그로우는 상판, 뉴트럴은 프레임/전환기 보정 기준입니다.", fontsize=8, color="#6b7280")
        pdf.savefig(fig)
        plt.close(fig)
    return path


def make_slide(base: str, month_labels: list[str], month: dict[str, np.ndarray]) -> Path:
    path = OUTPUT / f"slide_4x3_{base}.pdf"
    with PdfPages(path) as pdf:
        pages = [
            ("침대/책상 판매 흐름", ["아기침대", "주니어침대", "책상"], [month["baby_ivy"] + month["baby_neti"], month["junior_hey"] + month["junior_camper"] + month["junior_stins"], month["desk_total"]], ["#2563eb", "#059669", "#d97706"]),
            ("아기침대 내 아이비/네티류 비중", ["아이비", "네티류"], [month["baby_ivy"], month["baby_neti"]], ["#2563eb", "#059669"]),
            ("주니어 침대 브랜드 비중", ["헤이", "캠퍼", "스틴스"], [month["junior_hey"], month["junior_camper"], month["junior_stins"]], ["#60a5fa", "#34d399", "#f59e0b"]),
            ("주니어 침대 구조 비중", ["싱글", "로우벙커", "미드", "하이", "이층"], [month["junior_single"], month["junior_lowbunk"], month["junior_mid"], month["junior_high"], month["junior_bunk"]], ["#94a3b8", "#22c55e", "#38bdf8", "#eab308", "#ef4444"]),
            ("책상 판매와 상판 구성", ["책상 전체", "오크 추정"], [month["desk_total"], month["desk_oak_est"]], ["#2563eb", "#d97706"]),
        ]
        labels48, m48 = recent_slice(month_labels, month, 48)
        x = np.arange(len(labels48))
        for title, names, arrs, colors in pages:
            fig = plt.figure(figsize=(10, 7.5), facecolor="white")
            fig.text(0.055, 0.94, title, fontsize=20, weight="bold", color="#111827", va="top")
            fig.text(0.055, 0.895, f"기준 {base[:4]}.{base[4:6]}.{base[6:8]} · 최근 48개월 월별", fontsize=10, color="#6b7280", va="top")
            ax = fig.add_axes([0.08, 0.19, 0.86, 0.60])
            sliced = [a[-48:] for a in arrs]
            if "비중" in title:
                total = np.maximum(1, sum(sliced))
                stacked_area(ax, x, [s / total * 100 for s in sliced], names, colors, "")
                ax.set_ylim(0, 100)
                ax.set_ylabel("%", color="#374151", fontsize=9)
            else:
                line_plot(ax, x, sliced, names, colors, "")
            apply_xlabels(ax, labels48, 8)
            recent_vals = [s[-1] for s in sliced]
            note = " · ".join([f"{n} 최근월 {fmt(v)}" for n, v in zip(names, recent_vals)])
            fig.text(0.055, 0.08, note, fontsize=11, color="#374151")
            pdf.savefig(fig)
            plt.close(fig)
    return path


def main() -> None:
    setup_font()
    base = latest_base_date()
    month_df, month_periods = read_period("month", base)
    quarter_df, quarter_periods = read_period("quater", base)
    month = compute(month_df, month_periods)
    quarter = compute(quarter_df, quarter_periods)
    month_labels = [label_month(p) for p in month_periods]
    quarter_labels = [label_quarter(p) for p in quarter_periods]
    a4 = make_a4(base, month_labels, month, quarter_labels, quarter)
    slide = make_slide(base, month_labels, month)
    print(f"base={base}")
    print(f"a4={a4}")
    print(f"slide={slide}")
    print(f"latest_month={month_periods[-1]}")
    print(f"recent_baby_ivy={fmt(month['baby_ivy'][-1])}")
    print(f"recent_baby_neti={fmt(month['baby_neti'][-1])}")
    print(f"recent_junior={fmt((month['junior_hey'][-1] + month['junior_camper'][-1] + month['junior_stins'][-1]))}")
    print(f"recent_desk={fmt(month['desk_total'][-1])}")


if __name__ == "__main__":
    main()
