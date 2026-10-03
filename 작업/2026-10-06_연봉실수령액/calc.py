#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""연봉 실수령액 계산 — B1006-2/1 (계산기 쪽, 표준 라이브러리만)

입력(compute 열쇠, 계산기 입력칸 name과 같다)
  salary  : 연봉(원, 1년 세전 총액 — 12개월 같은 금액으로 받는다고 본다, 상여 따로 없음)
  nontax  : 한 달 비과세 합계(원, 예: 식대 월 20만원)
  family  : 공제대상가족 수(본인 포함, 1~11)
  kids    : 그중 8세 이상 20세 이하 자녀 수

공식(끝수: 항목마다 10원 미만 버림 — 국고금 관리법 제47조①)
  월 세전      = salary ÷ 12 (원 미만 버림)
  과세 월급여  = 월 세전 − nontax
  국민연금     = 기준소득월액(과세 월급여의 천원 미만 버림, 41만~659만원 안으로) × 9.5% ÷ 2
  건강보험     = 과세 월급여 × 7.19% ÷ 2
  장기요양     = 건강보험(본인) × 9,448 / 71,900 (장기요양보험료율 0.9448% ÷ 건강보험료율 7.19%)
  고용보험     = 과세 월급여 × 1.8% ÷ 2
  소득세       = 근로소득 간이세액표(소득세법 시행령 별표 2) 해당 칸 − 자녀 공제(1명 20,830 · 2명 45,830 · 3명부터 1명당 33,330 더함), 음수면 0
                 1,000만원 초과 구간은 별표 2의 계산식
  지방소득세   = 소득세 × 10%
  월 실수령    = 월 세전 − (국민연금 + 건강보험 + 장기요양 + 고용보험 + 소득세 + 지방소득세)

근거 조항 · 원문 URL (2026-10-03 열어 확인)
  국민연금 9.5%(2026년), 기준소득월액 41만~659만원(2026.7.1.~2027.6.30.), 천원 미만 절사
    https://www.nps.or.kr/pnsinfo/ntpsklg/getOHAF0038M0.do?menuId=MN24001113
  건강보험료율 1만분의 719 — 국민건강보험법 시행령 제44조①(시행 2026. 10. 1.)
    https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=289701&joNo=0044&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  본인 100분의 50 — 국민건강보험법 제76조①
    https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=276651&joNo=0076&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  장기요양보험료율 100만분의 9,448 — 노인장기요양보험법 시행령 제4조 / 산정 = 건강보험료 × 건강보험료율 대비 비율 — 노인장기요양보험법 제9조①
    https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=286011&joNo=0004&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  실업급여 보험료율 1천분의 18 — 고용산재보험료징수법 시행령 제12조①2 / 근로자 2분의 1 — 같은 법 제13조②
    https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280527&joNo=0012&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  식대 월 20만원 이하 비과세 — 소득세법 제12조 제3호 러목
    https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280405&joNo=0012&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  근로소득 간이세액표 — 소득세법 시행령 제194조①·별표 2(개정 2026. 2. 27., 시행령 현행 2026. 10. 1. 판)
    별표 2 PDF https://www.law.go.kr/LSW/flDownload.do?flSeq=169798151 → pdftotext -layout → 원문_별표2_간이세액표.txt(같은 폴더)
  지방소득세 = 소득세의 100분의 10 — 지방세법 제103조의13
    https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=282559&joNo=0103&joBrNo=13&docCls=jo&urlMode=lsScJoRltInfoR
  10원 미만 끝수 — 국고금 관리법 제47조①
    https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=276079&joNo=0047&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
기준일 2026-10-03. 같은 입력이면 같은 출력. 실행: python3 calc.py (표), python3 calc.py --js (계산기 스크립트용 상수)
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "원문_별표2_간이세액표.txt")

# ── 요율·한도(정수 분수) ──
PENSION_RATE = (95, 1000)          # 9.5% — 2026년(국민연금공단 안내)
PENSION_MIN, PENSION_MAX = 410_000, 6_590_000   # 2026.7.1.~2027.6.30.
PENSION_MAX_OLD = 6_370_000        # 2025.7.1.~2026.6.30.
HEALTH_RATE = (719, 10000)         # 7.19%
CARE_RATE = (9448, 1_000_000)      # 0.9448%
EMPLOY_RATE = (18, 1000)           # 1.8%(실업급여), 근로자 절반
CHILD_1, CHILD_2, CHILD_MORE = 20_830, 45_830, 33_330
CHILD_OLD_1, CHILD_OLD_2 = 12_500, 29_160   # 국세청 원천세 안내 쪽 사례에 적힌 금액(2026-10-03 열람)
TOP = 10_000_000                   # 월급여 1,000만원 — 그 위는 별표 2 계산식
# 1,000만원 초과: (하한, 상한, 더하는 금액, 초과분에 곱하는 비율(분자, 분모), 고정 가산)
OVER = [
    (10_000_000, 14_000_000, 0, (98 * 35, 10000), 25_000),
    (14_000_000, 28_000_000, 1_397_000, (98 * 38, 10000), 0),
    (28_000_000, 30_000_000, 6_610_600, (98 * 40, 10000), 0),
    (30_000_000, 45_000_000, 7_394_600, (40, 100), 0),
    (45_000_000, 87_000_000, 13_394_600, (42, 100), 0),
    (87_000_000, None, 31_034_600, (45, 100), 0),
]


def load_table():
    """별표 2 글자 표 → [(이상 천원, 미만 천원, [가족 1~11 세액])], 1,000만원 줄"""
    rows, top = [], None
    for ln in open(SRC, encoding="utf-8"):
        m = re.match(r"^\s*([\d,]+)\s+([\d,]+)\s+((?:[\d,]+|-)(?:\s+(?:[\d,]+|-)){10})\s*$", ln)
        if m:
            vals = [0 if v == "-" else int(v.replace(",", "")) for v in m.group(3).split()]
            rows.append((int(m.group(1).replace(",", "")), int(m.group(2).replace(",", "")), vals))
            continue
        m = re.match(r"^\s*10,000천원\s+((?:[\d,]+\s+){10}[\d,]+)\s*$", ln)
        if m:
            top = [int(v.replace(",", "")) for v in m.group(1).split()]
    assert len(rows) == 646 and rows[0][0] == 770 and rows[-1][1] == 10000 and top, "별표 2 읽기 실패"
    for a, b in zip(rows, rows[1:]):
        assert a[1] == b[0]
    return rows, top


ROWS, TOPROW = load_table()


def fl10(x):
    return x // 10 * 10


def table_tax(m, fam):
    """과세 월급여 m(원) · 공제대상가족 fam(1~11) → 간이세액표 세액(자녀 공제 전)"""
    if m < ROWS[0][0] * 1000:
        return 0
    if m < TOP:
        for lo, hi, vals in ROWS:
            if lo * 1000 <= m < hi * 1000:
                return vals[fam - 1]
    base = TOPROW[fam - 1]
    if m == TOP:
        return base
    for lo, hi, add, (n, d), plus in OVER:
        if hi is None or m <= hi:
            return fl10(base + add + (m - lo) * n // d + plus)
    raise ValueError(m)


def child_cut(kids):
    if kids <= 0:
        return 0
    if kids == 1:
        return CHILD_1
    return CHILD_2 + (kids - 2) * CHILD_MORE


def compute(salary, nontax=0, family=1, kids=0):
    salary, nontax, family, kids = int(salary), int(nontax), int(family), int(kids)
    family = min(max(family, 1), 11)
    kids = min(max(kids, 0), family - 1)
    gross = salary // 12
    m = max(gross - max(nontax, 0), 0)
    pbase = min(max(m // 1000 * 1000, PENSION_MIN), PENSION_MAX) if m > 0 else 0
    pension = fl10(pbase * PENSION_RATE[0] // (PENSION_RATE[1] * 2))
    health = fl10(m * HEALTH_RATE[0] // (HEALTH_RATE[1] * 2))
    care = fl10(health * CARE_RATE[0] * HEALTH_RATE[1] // (CARE_RATE[1] * HEALTH_RATE[0]))
    employ = fl10(m * EMPLOY_RATE[0] // (EMPLOY_RATE[1] * 2))
    tax = max(table_tax(m, family) - child_cut(kids), 0)
    local = fl10(tax // 10)
    total = pension + health + care + employ + tax + local
    net = gross - total
    return {"월세전": gross, "국민연금": pension, "건강보험": health, "장기요양": care, "고용보험": employ,
            "소득세": tax, "지방소득세": local, "공제합계": total, "월실수령": net, "연실수령": net * 12}


# 시험 입력 10개(경계값 포함) — 대조 스크립트가 HTML calcCompute와 맞댄다
TESTS = [
    {"salary": 25_000_000, "nontax": 200_000, "family": 1, "kids": 0},
    {"salary": 30_000_000, "nontax": 200_000, "family": 1, "kids": 0},
    {"salary": 40_000_000, "nontax": 200_000, "family": 1, "kids": 0},
    {"salary": 50_000_000, "nontax": 200_000, "family": 1, "kids": 0},
    {"salary": 50_000_000, "nontax": 0, "family": 1, "kids": 0},
    {"salary": 60_000_000, "nontax": 200_000, "family": 2, "kids": 0},
    {"salary": 80_000_000, "nontax": 200_000, "family": 4, "kids": 2},
    {"salary": 81_480_000, "nontax": 200_000, "family": 1, "kids": 0},
    {"salary": 100_000_000, "nontax": 200_000, "family": 1, "kids": 0},
    {"salary": 150_000_000, "nontax": 200_000, "family": 3, "kids": 1},
]


def won(n):
    return f"{n:,}원"


def man(n):
    """연봉 칸 표기: 2,500만원 · 1억원 · 1억 2,000만원"""
    e, r = divmod(n, 100_000_000)
    if e and r:
        return f"{e}억 {r // 10_000:,}만원"
    if e:
        return f"{e}억원"
    return f"{n // 10_000:,}만원"


def b36(n):
    s, o = "0123456789abcdefghijklmnopqrstuvwxyz", ""
    if n == 0:
        return "0"
    neg = n < 0
    n = abs(n)
    while n:
        o = s[n % 36] + o
        n //= 36
    return ("-" if neg else "") + o


def js_consts():
    """계산기 스크립트에 옮길 상수 — 간이세액표는 줄마다 앞 줄과의 차이(10원 단위, 36진수)"""
    prev, pl, out = [0] * 11, 0, []
    for lo, hi, vals in ROWS:
        out.append(",".join([b36(lo - pl)] + [b36(v // 10 - p) for v, p in zip(vals, prev)]))
        prev, pl = [v // 10 for v in vals], lo
    return ("var TABLE=\"" + ";".join(out) + "\";\n"
            + "var TOPROW=" + str(TOPROW).replace(" ", "") + ";\n")


def main():
    if "--js" in sys.argv:
        print(js_consts(), end="")
        return
    print("# 연봉 실수령액 — calc.py 출력(2026-10-03 원문 기준)\n")
    print(f"별표 2 읽은 줄 {len(ROWS)}줄 · 월급여 {ROWS[0][0]:,}천원~{ROWS[-1][1]:,}천원 · 1,000만원 줄 {TOPROW[0]:,}원(가족 1명)\n")

    print("표: 연봉별 월 실수령액(2026년 10월 3일 원문 기준, 식대 비과세 월 20만원·공제대상가족 1명·자녀 0명)")
    print("| 연봉 | 월 세전 | 4대보험 본인 부담 | 소득세+지방소득세 | 월 실수령 |")
    print("|---|---|---|---|---|")
    T1 = [25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 120, 150]
    for s in T1:
        r = compute(s * 1_000_000, 200_000, 1, 0)
        ins = r["국민연금"] + r["건강보험"] + r["장기요양"] + r["고용보험"]
        print(f"| {man(s * 1_000_000)} | {won(r['월세전'])} | {won(ins)} | {won(r['소득세'] + r['지방소득세'])} | {won(r['월실수령'])} |")
    print()

    print("표: 월급에서 빠지는 여섯 가지와 2026년 본인 부담 비율")
    print("| 항목 | 본인 부담(2026년 10월) | 근거 |")
    print("|---|---|---|")
    print(f"| 국민연금 | 기준소득월액의 4.75%(보험료율 9.5%의 절반), 기준소득월액 {PENSION_MIN // 10_000}만~{PENSION_MAX // 10_000:,}만원 | 국민연금공단 보험료 안내 |")
    print("| 건강보험 | 과세 월급여의 3.595%(보험료율 7.19%의 절반) | 국민건강보험법 시행령 제44조, 법 제76조 |")
    print("| 장기요양보험 | 건강보험료 × 9,448/71,900(약 13.14%) | 노인장기요양보험법 제9조, 시행령 제4조 |")
    print("| 고용보험 | 과세 월급여의 0.9%(실업급여 보험료율 1.8%의 절반) | 고용산재보험료징수법 제13조, 시행령 제12조 |")
    print("| 소득세 | 근로소득 간이세액표 해당 칸 | 소득세법 시행령 제194조·별표 2 |")
    print("| 지방소득세 | 소득세의 10% | 지방세법 제103조의13 |")
    print()

    r = compute(50_000_000, 200_000, 1, 0)
    m = r["월세전"] - 200_000
    pb = min(max(m // 1000 * 1000, PENSION_MIN), PENSION_MAX)
    print("표: 연봉 5,000만원 직접 계산(식대 월 20만원·본인 1명, 10원 미만 버림)")
    print("| 단계 | 계산 | 금액 |")
    print("|---|---|---|")
    print(f"| 월 세전 | 50,000,000원 ÷ 12 | {won(r['월세전'])} |")
    print(f"| 과세 월급여 | {won(r['월세전'])} − 200,000원 | {won(m)} |")
    print(f"| 국민연금 | {won(pb)} × 4.75% | {won(r['국민연금'])} |")
    print(f"| 건강보험 | {won(m)} × 3.595% | {won(r['건강보험'])} |")
    print(f"| 장기요양보험 | {won(r['건강보험'])} × 9,448/71,900 | {won(r['장기요양'])} |")
    print(f"| 고용보험 | {won(m)} × 0.9% | {won(r['고용보험'])} |")
    print(f"| 소득세 | 간이세액표 {m // 1000 // 20 * 20:,}천원 이상 {m // 1000 // 20 * 20 + 20:,}천원 미만, 가족 1명 칸 | {won(r['소득세'])} |")
    print(f"| 지방소득세 | {won(r['소득세'])} × 10% | {won(r['지방소득세'])} |")
    print(f"| 공제 합계 | 여섯 항목 더하기 | {won(r['공제합계'])} |")
    print(f"| 월 실수령 | {won(r['월세전'])} − {won(r['공제합계'])} | {won(r['월실수령'])} |")
    print()

    print("표: 연봉 5,000만원에서 공제대상가족·자녀 수에 따른 차이(식대 월 20만원)")
    print("| 공제대상가족 | 소득세 | 지방소득세 | 월 실수령 |")
    print("|---|---|---|---|")
    for fam, kids, lab in [(1, 0, "본인 1명"), (2, 0, "본인·배우자 2명"), (3, 1, "3명(8~20세 자녀 1명 포함)"), (4, 2, "4명(8~20세 자녀 2명 포함)")]:
        q = compute(50_000_000, 200_000, fam, kids)
        print(f"| {lab} | {won(q['소득세'])} | {won(q['지방소득세'])} | {won(q['월실수령'])} |")
    print()

    # 본문 문장에 쓰는 숫자
    print("## 본문 숫자")
    a = compute(50_000_000, 200_000, 1, 0)
    b = compute(50_000_000, 0, 1, 0)
    print(f"- 연봉 5,000만원 식대 20만원 월 실수령 {won(a['월실수령'])} · 식대 0원 {won(b['월실수령'])} · 차이 {won(a['월실수령'] - b['월실수령'])} · 연 {won((a['월실수령'] - b['월실수령']) * 12)}")
    print(f"- 연봉 5,000만원 월 실수령 만원 아래 버림 {a['월실수령'] // 10_000:,}만원 · 연봉 1억원 연 실수령 만원 아래 버림 {compute(100_000_000, 200_000, 1, 0)['연실수령'] // 10_000:,}만원")
    print(f"- 식대 20만원일 때 기준소득월액 상한에 걸리는 연봉 ({won(PENSION_MAX)} + 200,000원) × 12 = {man((PENSION_MAX + 200_000) * 12)}")
    print(f"- 연봉 5,000만원 공제 합계 {won(a['공제합계'])} · 연 실수령 {won(a['연실수령'])} · 4대보험 {won(a['국민연금'] + a['건강보험'] + a['장기요양'] + a['고용보험'])}")
    c = compute(100_000_000, 200_000, 1, 0)
    print(f"- 연봉 1억원 국민연금 {won(c['국민연금'])}(상한 {won(PENSION_MAX)} × 4.75%) · 소득세 {won(c['소득세'])} · 월 실수령 {won(c['월실수령'])} · 연 실수령 {won(c['연실수령'])}")
    up = fl10(PENSION_MAX * 95 // 2000) - fl10(PENSION_MAX_OLD * 95 // 2000)
    old9 = fl10(PENSION_MAX_OLD * 90 // 2000)
    print(f"- 상한자 국민연금 본인: 2025년 하반기 9% {won(old9)} · 2026년 1~6월 9.5% {won(fl10(PENSION_MAX_OLD * 95 // 2000))} · 7월부터 {won(fl10(PENSION_MAX * 95 // 2000))} · 7월 인상분 {won(up)}")
    e = compute(150_000_000, 200_000, 3, 1)
    print(f"- 연봉 1억 5,000만원 가족 3명·자녀 1명: 과세 월급여 {won(e['월세전'] - 200_000)} · 소득세 {won(e['소득세'])} · 월 실수령 {won(e['월실수령'])}")
    for fam in (1, 2):
        s = compute(50_000_000, 200_000, fam, 0)
        print(f"- 연봉 5,000만원 가족 {fam}명 소득세 80% {won(fl10(s['소득세'] * 80 // 100))} · 120% {won(fl10(s['소득세'] * 120 // 100))}")
    k = compute(50_000_000, 200_000, 3, 1)
    print(f"- 자녀 공제 새 금액 1명 {won(CHILD_1)} · 2명 {won(CHILD_2)} · 3명부터 1명당 {won(CHILD_MORE)} 더함 · 국세청 안내 쪽 사례 {won(CHILD_OLD_1)}·{won(CHILD_OLD_2)} · 1명 차이 {won(CHILD_1 - CHILD_OLD_1)} · 연 {won((CHILD_1 - CHILD_OLD_1) * 12)}")
    print(f"- 연봉 5,000만원 가족 3명 자녀 1명 간이세액(자녀 공제 전) {won(table_tax(50_000_000 // 12 - 200_000, 3))} · 뒤 {won(k['소득세'])}")
    print()
    print("## 시험 입력 10개")
    for t in TESTS:
        print(f"- {t} → {compute(**t)}")


if __name__ == "__main__":
    main()
