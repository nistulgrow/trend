#!/usr/bin/env python3
"""Regenerate dashboard HTML from the latest input uptodate files.

The latest raw update may replace recent historical dates to reflect canceled
or changed orders. The dashboard therefore preserves only periods that end
before the replacement window and recalculates every period that overlaps it.
"""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "input"
HTML_FILES = [
    ROOT / "index.html",
    INPUT / "integrated_category_dashboard_sample.html",
    ROOT / "integrated_category_dashboard_sample.html",
]
PERIOD_SUFFIX = {
    "week": "_week.csv",
    "month": "_month.csv",
    "quarter": "_quater.csv",
    "year": "_year.csv",
}
SHIPS = ("all", "self", "hd", "eb")
SERIES_KEYS = [
    "baby_ivy",
    "neti",
    "neti_plus",
    "neti_max",
    "baby_neti",
    "junior_hey",
    "junior_camper",
    "junior_stins",
    "junior_single",
    "junior_lowbunk",
    "junior_mid",
    "junior_high",
    "junior_bunk",
    "desk_total",
    "desk_plywood_top",
    "desk_oak_top",
    "desk_plywood_rear",
    "desk_oak_rear",
    "desk_oak_est",
    "junior_unclassified_stins",
]
EXCLUDE_WORDS = (
    "B급",
    "AS용",
    "CS팀",
    "검수",
    "범퍼가드",
    "펠트도어",
    "하단 서랍",
    "안전가드",
    "침구",
    "매트리스",
    "커버",
    "패드",
    "증정품",
    "부품",
    "스페어",
)


def latest_input_date() -> str:
    candidates = []
    for path in INPUT.glob("uptodate_*.csv"):
        match = re.fullmatch(r"uptodate_(\d{8})\.csv", path.name)
        if match:
            candidates.append(match.group(1))
    if not candidates:
        raise SystemExit("No input/uptodate_YYYYMMDD.csv found.")
    return max(candidates)


def period_files(date_key: str) -> dict[str, Path]:
    files = {key: INPUT / f"uptodate_{date_key}{suffix}" for key, suffix in PERIOD_SUFFIX.items()}
    missing = [str(path) for path in files.values() if not path.exists()]
    if missing:
        raise SystemExit("Missing aggregate files:\n" + "\n".join(missing))
    return files


def read_base(html_path: Path) -> tuple[dict, str]:
    html = html_path.read_text(encoding="utf-8")
    data_match = re.search(r"const DATA=(.*?);const state=", html, flags=re.S)
    date_match = re.search(r"const LAST_DATE='(\d{8})'", html)
    if not data_match or not date_match:
        raise SystemExit(f"Could not read DATA/LAST_DATE from {html_path}")
    return json.loads(data_match.group(1)), date_match.group(1)


def date_columns(header: list[str]) -> list[str]:
    return [c for c in header if re.fullmatch(r"\d{8}_\d{8}|\d{6}|\d{4}Q\d|\d{4}", c)]


def natural_end(label: str) -> str:
    if "_" in label:
        return label.split("_", 1)[1]
    if "Q" in label:
        year, q = label.split("Q", 1)
        return year + ("0331", "0630", "0930", "1231")[int(q) - 1]
    if len(label) == 6:
        year = int(label[:4])
        month = int(label[4:6])
        days = [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        return f"{year:04d}{month:02d}{days[month - 1]:02d}"
    return label + "1231"


def replacement_start(last_date: str) -> str:
    """Return the first date in the maximum one-month replacement window."""
    year = int(last_date[:4])
    month = int(last_date[4:6])
    day = int(last_date[6:8])
    month -= 1
    if month == 0:
        year -= 1
        month = 12
    days = [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    day = min(day, days[month - 1])
    return f"{year:04d}{month:02d}{day:02d}"


def zero(n: int) -> list[int]:
    return [0] * n


def add_to(bucket: dict[str, list[int]], key: str, values: list[int]) -> None:
    arr = bucket[key]
    for i, value in enumerate(values):
        arr[i] += value


def values(row: dict[str, str], labels: list[str]) -> list[int]:
    out = []
    for label in labels:
        raw = (row.get(label) or "").replace(",", "").strip()
        try:
            out.append(int(float(raw)) if raw else 0)
        except ValueError:
            out.append(0)
    return out


def arr_sum(*arrays: list[int]) -> list[int]:
    return [sum(items) for items in zip(*arrays)] if arrays else []


def arr_min(*arrays: list[int]) -> list[int]:
    return [min(items) for items in zip(*arrays)] if arrays else []


def arr_div_floor(array: list[int], divisor: int) -> list[int]:
    return [value // divisor for value in array]


def arr_sub_floor(base: list[int], *subs: list[int]) -> list[int]:
    return [max(0, value - sum(items)) for value, *items in zip(base, *subs)]


def clean_name(name: str) -> str:
    for prefix in ("자체 ", "현대물류용 ", "에바다용 "):
        if name.startswith(prefix):
            return name[len(prefix) :]
    return name


def ship_of(name: str) -> str:
    if name.startswith("현대물류용 "):
        return "hd"
    if name.startswith("에바다용 "):
        return "eb"
    return "self"


def excluded(name: str, option: str) -> bool:
    text = name + " " + option
    if "모듈변경" in text or "통판 1세트" in text or "통판 1ea" in text:
        return True
    return any(word in text for word in EXCLUDE_WORDS)


def wanted_ship(actual: str, target: str) -> bool:
    return target == "all" or actual == target


def compute_file(path: Path) -> dict[str, dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        labels = date_columns(reader.fieldnames or [])
        rows = list(reader)

    n = len(labels)
    output = {ship: {"labels": labels, "series": {key: zero(n) for key in SERIES_KEYS}} for ship in SHIPS}

    for target_ship in SHIPS:
        comp = defaultdict(lambda: zero(n))
        series = output[target_ship]["series"]

        for row in rows:
            raw_name = row["상품명"].strip()
            option = row["옵션내용"].strip()
            name = clean_name(raw_name)
            actual_ship = ship_of(raw_name)
            if not wanted_ship(actual_ship, target_ship):
                continue
            vals = values(row, labels)
            skip = excluded(name, option)

            if ("하이가드 유아침대 아이비" in name or "아이비 (Ivy)" in name) and not skip:
                if "SS 1" in option:
                    add_to(comp, "ivy_ss1", vals)
                elif "SS 2" in option:
                    add_to(comp, "ivy_ss2", vals)
                elif "ES 1" in option:
                    add_to(comp, "ivy_es1", vals)
                elif "ES 2" in option:
                    add_to(comp, "ivy_es2", vals)

            if name == "네티" and not skip:
                add_to(series, "neti", vals)
            elif name.startswith("네티 플러스") and not skip and "드랍사이드" not in option and "변형" not in option:
                add_to(series, "neti_plus", vals)
            elif name == "네티 맥스" and not skip:
                color = "oak" if "오크" in option else "almond" if "아몬드" in option else "other"
                if "1번" in option:
                    add_to(comp, f"netimax_{color}_1", vals)
                elif "2번" in option:
                    add_to(comp, f"netimax_{color}_2", vals)

            if "헤이(HEJ) 단층침대" in name and not skip:
                add_to(comp, "hey_single_1" if "1번" in option else "hey_single_2" if "2번" in option else "ignore", vals)
            if "헤이(HEJ) 로우벙커" in name and not skip:
                add_to(comp, "hey_low_1" if "1번" in option else "hey_low_2" if "2번" in option else "ignore", vals)
            if "헤이(HEJ) 미드확장키트" in name and not skip:
                if "3번" in option:
                    add_to(comp, "hey_mid_3", vals)
                elif "4번" in option:
                    add_to(comp, "hey_mid_4", vals)
                else:
                    add_to(comp, "hey_mid_new", vals)
            if "헤이(HEJ) 하이확장키트" in name and not skip:
                add_to(comp, "hey_high_1" if "1번" in option else "hey_high_2" if "2번" in option else "ignore", vals)
            if "헤이(HEJ) 2층확장키트" in name and not skip:
                if "1번" in option:
                    add_to(comp, "hey_bunk_es_1", vals)
                elif "2번" in option:
                    add_to(comp, "hey_bunk_es_2", vals)
                elif "짧은키트" in option:
                    add_to(comp, "hey_bunk_es_short", vals)
            if "헤이(HEJ), 캠퍼(Camper) 공용 2층확장키트" in name and not skip:
                if "1번" in option:
                    add_to(comp, "common_bunk_1", vals)
                elif "2번" in option:
                    add_to(comp, "common_bunk_2", vals)
                elif "캠퍼용" in option:
                    add_to(comp, "camper_bunk_short", vals)
                elif "짧은키트" in option or "헤이용" in option:
                    add_to(comp, "hey_bunk_short", vals)

            if "캠퍼(Camper) 미드" in name and not skip:
                if "캠퍼단층" in option and "1번" in option:
                    add_to(comp, "camper_mid_body1", vals)
                elif "캠퍼단층" in option and "2번" in option:
                    add_to(comp, "camper_mid_body2", vals)
                elif "캠퍼단층" in option and "3번" in option:
                    add_to(comp, "camper_mid_body3", vals)
                elif "미드확장키트" in option:
                    add_to(comp, "camper_mid_kit", vals)
                elif "사다리" in option:
                    add_to(comp, "camper_mid_ladder", vals)
            if "캠퍼(Camper) 하이확장키트" in name and not skip:
                if "1번" in option:
                    add_to(comp, "camper_high_1", vals)
                elif "2번" in option:
                    add_to(comp, "camper_high_2", vals)
                elif "사다리" in option:
                    add_to(comp, "camper_high_ladder", vals)

            if not skip:
                if name == "싱글침대":
                    add_to(comp, "stins_single_body", vals)
                elif name == "미드확장키트":
                    add_to(comp, "stins_mid", vals)
                elif name == "하이확장키트":
                    add_to(comp, "stins_high", vals)
                elif name == "벙커확장키트":
                    add_to(comp, "stins_bunk", vals)
                elif name == "DP용 스틴스":
                    if "싱글침대" in option or "싱글가드침대" in option:
                        add_to(comp, "stins_single_body", vals)
                    elif "미드침대" in option:
                        add_to(comp, "stins_mid", vals)
                    elif "하이침대" in option:
                        add_to(comp, "stins_high", vals)
                    elif "2층침대" in option or "이층침대" in option:
                        add_to(comp, "stins_bunk", vals)

            if not skip:
                if name == "그로우 데스크":
                    if "다리W" in option or "다리G" in option:
                        add_to(comp, "grow_legs", vals)
                    if "상판SN" in option or "상판CN" in option:
                        add_to(comp, "grow_top", vals)
                        add_to(comp, "desk_plywood_top", vals)
                    if "리어탑SN" in option or "리어탑CN" in option:
                        add_to(comp, "grow_rear", vals)
                        add_to(comp, "desk_plywood_rear", vals)
                if name == "뉴트럴 플라이우드 데스크":
                    if option == "프레임-오프화이트":
                        add_to(comp, "neutral_frame", vals)
                    if option.startswith("상판-"):
                        add_to(comp, "neutral_oak_top" if "오크솔리드원목" in option else "neutral_plywood_top", vals)
                    if option.startswith("리어탑-"):
                        add_to(comp, "neutral_oak_rear" if "오크솔리드원목" in option else "neutral_plywood_rear", vals)

        series["baby_ivy"] = arr_sum(arr_min(comp["ivy_ss1"], comp["ivy_ss2"]), arr_min(comp["ivy_es1"], comp["ivy_es2"]))
        series["neti_max"] = arr_sum(
            arr_min(comp["netimax_almond_1"], comp["netimax_almond_2"]),
            arr_min(comp["netimax_oak_1"], comp["netimax_oak_2"]),
            arr_min(comp["netimax_other_1"], comp["netimax_other_2"]),
        )
        series["baby_neti"] = arr_sum(series["neti"], series["neti_plus"], series["neti_max"])

        hey_single = arr_min(comp["hey_single_1"], comp["hey_single_2"])
        hey_low = arr_min(comp["hey_low_1"], comp["hey_low_2"])
        hey_mid = arr_sum(arr_min(comp["hey_mid_3"], comp["hey_mid_4"]), comp["hey_mid_new"])
        hey_high = arr_min(comp["hey_high_1"], comp["hey_high_2"])
        hey_bunk = arr_sum(
            arr_min(comp["common_bunk_1"], comp["common_bunk_2"], comp["hey_bunk_short"]),
            arr_min(comp["hey_bunk_es_1"], comp["hey_bunk_es_2"], comp["hey_bunk_es_short"]),
        )
        camper_mid_body = arr_min(comp["camper_mid_body1"], comp["camper_mid_body2"])
        if any(comp["camper_mid_body3"]):
            camper_mid_body = arr_min(comp["camper_mid_body1"], comp["camper_mid_body2"], comp["camper_mid_body3"])
        camper_mid = arr_min(camper_mid_body, comp["camper_mid_kit"], comp["camper_mid_ladder"])
        camper_high = arr_min(comp["camper_high_1"], comp["camper_high_2"], comp["camper_high_ladder"])
        camper_bunk = arr_min(comp["common_bunk_1"], comp["common_bunk_2"], arr_div_floor(comp["camper_bunk_short"], 2))
        stins_mid = comp["stins_mid"]
        stins_high = comp["stins_high"]
        stins_bunk = comp["stins_bunk"]
        stins_single = arr_sub_floor(comp["stins_single_body"], stins_mid, stins_high, [2 * v for v in stins_bunk])

        series["junior_single"] = arr_sum(hey_single, stins_single)
        series["junior_lowbunk"] = hey_low
        series["junior_mid"] = arr_sum(hey_mid, camper_mid, stins_mid)
        series["junior_high"] = arr_sum(hey_high, camper_high, stins_high)
        series["junior_bunk"] = arr_sum(hey_bunk, camper_bunk, stins_bunk)
        series["junior_hey"] = arr_sum(hey_single, hey_low, hey_mid, hey_high, hey_bunk)
        series["junior_camper"] = arr_sum(camper_mid, camper_high, camper_bunk)
        series["junior_stins"] = arr_sum(stins_single, stins_mid, stins_high, stins_bunk)

        series["desk_plywood_top"] = arr_sum(comp["desk_plywood_top"], comp["neutral_plywood_top"])
        series["desk_oak_top"] = comp["neutral_oak_top"]
        series["desk_plywood_rear"] = arr_sum(comp["desk_plywood_rear"], comp["neutral_plywood_rear"])
        series["desk_oak_rear"] = comp["neutral_oak_rear"]
        series["desk_oak_est"] = arr_min(series["desk_oak_top"], series["desk_oak_rear"])
        desk_total = []
        for i, label in enumerate(labels):
            year = int(label[:4])
            if year < 2018:
                desk_total.append(comp["grow_legs"][i])
            else:
                neutral_top = comp["neutral_plywood_top"][i] + comp["neutral_oak_top"][i]
                neutral_rear = comp["neutral_plywood_rear"][i] + comp["neutral_oak_rear"][i]
                neutral = max(comp["neutral_frame"][i], min(neutral_top, neutral_rear))
                desk_total.append(comp["grow_top"][i] + neutral)
        series["desk_total"] = desk_total

    return output


def splice_data(base: dict, calculated: dict, keep_before: str) -> dict:
    merged = {}
    for period, period_data in calculated.items():
        merged[period] = {}
        for ship, ship_data in period_data.items():
            labels = ship_data["labels"]
            merged[period][ship] = {"labels": labels, "series": {}}
            base_labels = base.get(period, {}).get(ship, {}).get("labels", [])
            base_index = {label: i for i, label in enumerate(base_labels)}
            for key in SERIES_KEYS:
                values_out = []
                calc_values = ship_data["series"].get(key, zero(len(labels)))
                base_values = base.get(period, {}).get(ship, {}).get("series", {}).get(key, [])
                for i, label in enumerate(labels):
                    if natural_end(label) < keep_before and label in base_index:
                        values_out.append(base_values[base_index[label]])
                    else:
                        values_out.append(calc_values[i])
                merged[period][ship]["series"][key] = values_out
    return merged


def display_date(date_key: str) -> str:
    return f"{date_key[:4]}.{date_key[4:6]}.{date_key[6:8]}"


def update_html(path: Path, data: dict, last_date: str) -> None:
    html = path.read_text(encoding="utf-8")
    data_json = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    html = re.sub(r"const DATA=.*?;const state=", f"const DATA={data_json};const state=", html, count=1, flags=re.S)
    html = re.sub(
        r'<div class="meta">데이터: .*?</div>',
        f'<div class="meta">데이터: 2014.06~{display_date(last_date)} · PC 화면 전용 · 수정버전 {display_date(last_date).replace(".", "-")}</div>',
        html,
        count=1,
    )
    html = re.sub(r"const LAST_DATE='\d{8}';", f"const LAST_DATE='{last_date}';", html, count=1)
    dynamic_format = (
        "function lastMonthKey(){return LAST_DATE.slice(0,6)}"
        "function lastYearKey(){return LAST_DATE.slice(0,4)}"
        "function lastQuarterKey(){const m=Number(LAST_DATE.slice(4,6));return lastYearKey()+'Q'+Math.ceil(m/3)}"
        "function lastSuffix(){return '~'+Number(LAST_DATE.slice(4,6))+'/'+Number(LAST_DATE.slice(6,8))}"
        "function formatLabel(x){if(x.includes('_')){const a=x.slice(0,8);let b=x.slice(9,17);if(b>LAST_DATE)b=LAST_DATE;return fmtDate8(a)+'~'+fmtDate8(b)}"
        "if(x===lastQuarterKey())return x+'('+lastSuffix()+')';if(x===lastYearKey())return x+'('+lastSuffix()+')';"
        "if(x===lastMonthKey())return x.slice(0,4)+'.'+x.slice(4)+'(~'+Number(LAST_DATE.slice(6,8))+'일)';"
        "if(x.includes('Q'))return x;if(x.length===6)return x.slice(0,4)+'.'+x.slice(4);return x}"
        "function pct"
    )
    html = re.sub(r"function formatLabel\(x\).*?function pct", dynamic_format, html, count=1, flags=re.S)
    html = re.sub(
        r"마지막 데이터는 .*?까지입니다\. 마지막 주/월/분기/연은 .*?까지의 부분 기간입니다\.",
        f"마지막 데이터는 {int(last_date[:4])}년 {int(last_date[4:6])}월 {int(last_date[6:8])}일까지입니다. 마지막 주/월/분기/연은 {int(last_date[4:6])}월 {int(last_date[6:8])}일까지의 부분 기간입니다.",
        html,
        count=1,
    )
    path.write_text(html, encoding="utf-8")


def main() -> None:
    latest = latest_input_date()
    base_data, base_last = read_base(ROOT / "index.html")
    replace_from = replacement_start(latest)
    calculated = {period: compute_file(path) for period, path in period_files(latest).items()}
    data = splice_data(base_data, calculated, replace_from)
    for path in HTML_FILES:
        if path.exists():
            update_html(path, data, latest)
    print(f"Base LAST_DATE: {base_last}")
    print(f"Latest input date: {latest}")
    print(f"Replacement window starts: {replace_from}")
    for period in ("week", "month", "quarter", "year"):
        labels = data[period]["all"]["labels"]
        print(f"{period}: {labels[0]} -> {labels[-1]} ({len(labels)})")


if __name__ == "__main__":
    main()
