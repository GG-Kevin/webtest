#!/usr/bin/env python3
"""구직급여 상한액·하한액 계산 (B1005-1/2) — 표준 라이브러리만.

입력(아래 상수):
  기초일액 상한   113,500원  고용보험법 시행령 제68조 제1항(「11만3500원」, 2025. 12. 23. 개정, 2026. 1. 1. 시행 — 부칙 제1조·제4조)
                 https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=288717&joNo=0068&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  지급 비율       기초일액 × 100분의 60(일반) · 최저기초일액 × 100분의 80(최저구직급여일액)  고용보험법 제46조 제1항·제2항
                 https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=284449&joNo=0046&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  최저기초일액     이직 전 1일 소정근로시간 × 이직일 당시 최저임금 시간급  고용보험법 제45조 제4항
                 https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=284449&joNo=0045&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  최저임금 시간급   2026년 10,320원 · 2027년 10,700원  최저임금위원회 연도별 최저임금 결정현황
                 https://www.minimumwage.go.kr/minWage/policy/decisionMain.do
  소정급여일수     고용보험법 별표 1(제50조 제1항 관련) — 피보험기간 × 이직일 현재 연령
  평균임금        이직 전 3개월 임금 총액 ÷ 그 기간 총일수  근로기준법 제2조 제1항 제6호
공식:
  기초일액 = 월급 × 3 ÷ 92(7·8·9월처럼 31+31+30일인 3개월을 예시로 둔다)
  최저기초일액 = 최저시급 × 소정근로시간
  기초일액이 최저기초일액보다 낮으면 기초일액 = 최저기초일액 → 일액 = × 0.8 (제45조 ④·제46조 ①2)
  그 밖에는 min(기초일액, 113,500) × 0.6, 그 값이 최저구직급여일액보다 낮으면 최저구직급여일액(제46조 ②)
  원 미만은 버린다. 30일 환산 = 일액 × 30(생활 단위 환산, 실제 지급 주기와 다르다)
기준일: 2026-10-03 원문 기준. 같은 입력이면 같은 출력.
"""
import math

CAP_BASE = 113500           # 시행령 제68조 ① 기초일액 상한
RATE = 0.6                  # 법 제46조 ① 1호
MIN_RATE = 0.8              # 법 제46조 ① 2호
MINWAGE = {2026: 10320, 2027: 10700}
HOURS = 8
DAYS3M = 92                 # 예시 3개월 총일수(31+31+30)
SOJEONG = [                 # 별표 1: (피보험기간, 50세 미만, 50세 이상·장애인)
    ("1년 미만", 120, 120),
    ("1년 이상 3년 미만", 150, 180),
    ("3년 이상 5년 미만", 180, 210),
    ("5년 이상 10년 미만", 210, 240),
    ("10년 이상", 240, 270),
]


def won(x):
    return f"{int(x):,}원"


def min_base(year, hours=HOURS):
    return MINWAGE[year] * hours


def floor_daily(year, hours=HOURS):
    return math.floor(min_base(year, hours) * MIN_RATE)


def cap_daily():
    return math.floor(CAP_BASE * RATE)


def daily_from_monthly(monthly, year=2026, hours=HOURS):
    base = math.floor(monthly * 3 / DAYS3M)  # 기초일액도 원 미만 버림(표에 적힌 값으로 60%를 곱한다)
    mb = min_base(year, hours)
    fl = floor_daily(year, hours)
    if base < mb:
        return base, fl, "하한(기초일액이 최저기초일액보다 낮음)"
    capped = min(base, CAP_BASE)
    d = math.floor(capped * RATE)
    if d < fl:
        return base, fl, "하한(60%가 하한보다 낮음)"
    if base > CAP_BASE:
        return base, d, "상한(기초일액 113,500원으로 자름)"
    return base, d, "60% 그대로"


def main():
    cap, fl = cap_daily(), floor_daily(2026)
    print("## 표1 2026년 구직급여 상한액과 하한액")
    print("| 구분 | 하루(구직급여일액) | 30일로 환산 | 계산 |")
    print("|---|---|---|---|")
    print(f"| 상한액 | {won(cap)} | {won(cap * 30)} | 기초일액 상한 113,500원 × 60% |")
    print(f"| 하한액(하루 8시간) | {won(fl)} | {won(fl * 30)} | 최저임금 10,320원 × 8시간 × 80% |")
    print(f"| 차이 | {won(cap - fl)} | {won((cap - fl) * 30)} | 상한액 − 하한액 |")
    print()
    print(f"최저기초일액(8시간) = {won(min_base(2026))}")

    print()
    print("## 표2 월급별 구직급여일액(이직 전 3개월 92일 예시)")
    print("| 이직 전 월급 | 기초일액 | 60% 계산값 | 실제 일액 | 30일 환산 | 어느 쪽 |")
    print("|---|---|---|---|---|---|")
    for m in (2000000, 3000000, 3400000, 4000000, 5000000):
        base, d, why = daily_from_monthly(m)
        print(f"| {m // 10000:,}만원 | {won(base)} | {won(math.floor(base * RATE))} | {won(d)} | {won(d * 30)} | {why} |")
    lo = fl / RATE * DAYS3M / 3        # 60% 계산값이 하한과 같아지는 월급
    hi = CAP_BASE * DAYS3M / 3         # 기초일액이 상한에 닿는 월급
    print()
    print(f"60% 계산값이 하한을 넘기 시작하는 기초일액 = {won(math.ceil(fl / RATE))}")
    print(f"그때 월급(92일 기준) = {won(math.ceil(lo))}")
    print(f"상한에 닿는 월급(92일 기준) = {won(math.ceil(hi))}")
    print(f"두 경계 사이 폭 = {won(math.ceil(hi) - math.ceil(lo))}")

    print()
    print("## 표3 소정급여일수별 총액(상한액·하한액 기준)")
    print("| 피보험기간 | 50세 미만 | 상한액 총액 | 50세 이상·장애인 | 상한액 총액 |")
    print("|---|---|---|---|---|")
    for name, a, b in SOJEONG:
        print(f"| {name} | {a}일 | {won(cap * a)} | {b}일 | {won(cap * b)} |")
    print()
    for d in sorted({x for _, a, b in SOJEONG for x in (a, b)}):
        print(f"하한액 {d}일 총액 = {won(fl * d)}")
    print(f"270일 상한·하한 총액 차이 = {won((cap - fl) * 270)}")

    print()
    print("## 표4 하한액과 상한액 비교(소정근로시간·연도별)")
    print("| 경우 | 최저임금 시간급 | 최저기초일액 | 하한액(80%) | 상한액과 차이 |")
    print("|---|---|---|---|---|")
    for y, h in ((2026, 4), (2026, 6), (2026, 8), (2027, 8)):
        f = floor_daily(y, h)
        print(f"| {y}년 이직 · 하루 {h}시간 | {won(MINWAGE[y])} | {won(min_base(y, h))} | {won(f)} | {f - cap:+,}원 |")
    print()
    print(f"2027년 8시간 하한액 − 상한액 = {floor_daily(2027) - cap:,}원")
    print(f"2027년 하한액 30일 환산 = {won(floor_daily(2027) * 30)}")


if __name__ == "__main__":
    main()
