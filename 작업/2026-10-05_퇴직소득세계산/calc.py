#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""퇴직소득세 계산(일반 글 · 계산형) — B1005-2/2 · 표준 라이브러리만 · 같은 입력이면 같은 출력.

입력: 근속연수 n(년, 1년 미만 끝수는 1년으로 올린 값) · 퇴직급여 P(원, 비과세 소득 없음 가정 → 퇴직소득금액 = P)
공식(순서):
  1) 근속연수공제 D(n)  = n≤5: 100만×n · n≤10: 500만+200만×(n-5) · n≤20: 1,500만+250만×(n-10) · n>20: 4,000만+300만×(n-20)
     퇴직소득금액이 D보다 작으면 D = 퇴직소득금액(제48조 제2항)
  2) 환산급여 C        = (P - D) × 12 ÷ n
  3) 환산급여공제 E(C) = C≤800만: C 전액 · ≤7,000만: 800만+(C-800만)×60% · ≤1억: 4,520만+(C-7,000만)×55%
                          · ≤3억: 6,170만+(C-1억)×45% · >3억: 1억5,170만+(C-3억)×35%
  4) 과세표준 B        = C - E
  5) 환산산출세액 T    = B × 기본세율(제55조 제1항) - 누진공제액
  6) 퇴직소득 산출세액 = T ÷ 12 × n (원 미만 버림 — 이 글의 계산 방식, 홈택스 모의계산과 원 단위 끝수가 다를 수 있음)
  7) 개인지방소득세    = 산출세액 × 10% (지방세법 제103조의13 제1항, 원 미만 버림)
근거 조항·원문(2026-10-03 열어 확인, 기준일 2026-10-03):
  - 소득세법 제48조(퇴직소득공제) 조문 본문 https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280405&joNo=0048&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
    (시행 2026. 1. 1. 법률 제21221호 · 공제 표는 그림 조문이라 본문 글자에 없음 → 숫자는 국세청 안내로 대조)
  - 소득세법 제55조(세율) 제1항 표·제2항 계산 순서 https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280405&joNo=0055&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  - 소득세법 시행령 제105조(근속연수) https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=290841&joNo=0105&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  - 국세청 퇴직소득세 계산방법 및 계산사례 https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?mi=6444&cntntsId=7880
  - 지방세법 제103조의13(특별징수의무) https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=282559&joNo=0103&joBrNo=13&docCls=jo&urlMode=lsScJoRltInfoR
"""

from fractions import Fraction as F

MAN = 10_000
EOK = 100_000_000

# 근속연수공제 구간: (상한 연수, 기본액, 연당 가산액, 기준 연수)
SERVICE_STEPS = [(5, 0, 100 * MAN, 0), (10, 500 * MAN, 200 * MAN, 5), (20, 1_500 * MAN, 250 * MAN, 10), (None, 4_000 * MAN, 300 * MAN, 20)]
# 환산급여공제 구간: (상한, 기본액, 초과분 비율, 초과 기준)
CONV_STEPS = [(800 * MAN, 0, F(100, 100), 0), (7_000 * MAN, 800 * MAN, F(60, 100), 800 * MAN), (1 * EOK, 4_520 * MAN, F(55, 100), 7_000 * MAN),
              (3 * EOK, 6_170 * MAN, F(45, 100), 1 * EOK), (None, 15_170 * MAN, F(35, 100), 3 * EOK)]
# 기본세율(제55조 제1항): (과세표준 상한, 세율, 누진공제액)
RATES = [(1_400 * MAN, F(6, 100), 0), (5_000 * MAN, F(15, 100), 1_260_000), (8_800 * MAN, F(24, 100), 5_760_000), (15_000 * MAN, F(35, 100), 15_440_000),
         (30_000 * MAN, F(38, 100), 19_940_000), (50_000 * MAN, F(40, 100), 25_940_000), (100_000 * MAN, F(42, 100), 35_940_000), (None, F(45, 100), 65_940_000)]


def service_deduction(n):
    for cap, base, per, start in SERVICE_STEPS:
        if cap is None or n <= cap:
            return base + per * (n - start)


def conv_deduction(c):
    for cap, base, r, over in CONV_STEPS:
        if cap is None or c <= cap:
            return base + (c - over) * r if over else c * r


def base_tax(b):
    for cap, r, prog in RATES:
        if cap is None or b <= cap:
            return b * r - prog, r


def compute(years, pay):
    """years = 근속연수(정수, 끝수 올림 뒤) · pay = 퇴직급여(원)"""
    d = min(service_deduction(years), pay)
    c = F(pay - d) * 12 / years
    e = conv_deduction(c)
    b = max(c - e, 0)
    t, r = base_tax(b)
    tax = int(t / 12 * years)  # Fraction → 원 미만 버림
    local = int(F(tax) * F(10, 100))
    return {"근속연수공제": d, "환산급여": c, "환산급여공제": e, "과세표준": b, "세율": r, "환산산출세액": t,
            "퇴직소득세": tax, "지방소득세": local, "합계": tax + local}


def zero_line(years):
    """퇴직소득세가 0원인 퇴직급여의 상한: 환산급여가 800만원 이하 → P ≤ D(n) + 800만 × n ÷ 12"""
    return service_deduction(years) + F(800 * MAN * years, 12)


def won(v):
    return f"{int(round(v)):,}원"


def man(v):
    """만원 단위 표기(1억 이상은 「1억 5,170만원」 꼴)"""
    v = int(round(v / MAN))
    if v >= 10_000:
        e, m = divmod(v, 10_000)
        return f"{e}억원" if m == 0 else f"{e}억 {m:,}만원"
    return f"{v:,}만원"


def main():
    print("## 기준 숫자(제48조·제55조, 국세청 계산방법 안내 · 2026-10-03)")
    print("근속연수공제:", " / ".join(f"{cap}년 이하 기본 {man(b) if b else '0원'} + 연 {man(p)}" if cap else f"20년 초과 {man(b)} + 연 {man(p)}"
                                    for cap, b, p, s in SERVICE_STEPS))
    print("환산급여공제:", " / ".join((f"{man(cap)} 이하" if cap else "3억원 초과") + f" 기본 {man(b) if b else '0원'} + {int(r * 100)}%" for cap, b, r, o in CONV_STEPS))
    print("기본세율:", " / ".join(f"{man(cap) if cap else '10억원 초과'} {int(round(r * 100))}% 누진공제 {won(p)}" for cap, r, p in RATES))
    print()

    print("표: 퇴직소득세에서 빼는 두 가지 공제(소득세법 제48조 · 2026년 10월 3일 원문 기준)")
    print("| 공제 | 구간 | 공제액 |")
    print("|---|---|---|")
    print("| 근속연수공제 | 5년 이하 | 100만원 × 근속연수 |")
    print("| 근속연수공제 | 5년 초과 10년 이하 | 500만원 + 200만원 × (근속연수 − 5년) |")
    print("| 근속연수공제 | 10년 초과 20년 이하 | 1,500만원 + 250만원 × (근속연수 − 10년) |")
    print("| 근속연수공제 | 20년 초과 | 4,000만원 + 300만원 × (근속연수 − 20년) |")
    print("| 환산급여공제 | 800만원 이하 | 환산급여 전액 |")
    print("| 환산급여공제 | 800만원 초과 7,000만원 이하 | 800만원 + 800만원 넘는 부분의 60% |")
    print("| 환산급여공제 | 7,000만원 초과 1억원 이하 | 4,520만원 + 7,000만원 넘는 부분의 55% |")
    print("| 환산급여공제 | 1억원 초과 3억원 이하 | 6,170만원 + 1억원 넘는 부분의 45% |")
    print("| 환산급여공제 | 3억원 초과 | 1억 5,170만원 + 3억원 넘는 부분의 35% |")
    print()

    n, p = 10, 1 * EOK
    r = compute(n, p)
    print(f"표: 근속 {n}년·퇴직급여 1억원일 때 계산 순서(계산 예시)")
    print("| 단계 | 계산 | 금액 |")
    print("|---|---|---|")
    print(f"| 퇴직소득금액 | 퇴직급여(비과세 없음) | {won(p)} |")
    print(f"| 근속연수공제 | 1,500만원 + 250만원 × (10 − 10) | {won(r['근속연수공제'])} |")
    print(f"| 환산급여 | ({won(p)} − {won(r['근속연수공제'])}) × 12 ÷ 10 | {won(r['환산급여'])} |")
    print(f"| 환산급여공제 | 6,170만원 + ({won(r['환산급여'])} − 1억원) × 45% | {won(r['환산급여공제'])} |")
    print(f"| 과세표준 | 환산급여 − 환산급여공제 | {won(r['과세표준'])} |")
    print(f"| 환산산출세액 | {won(r['과세표준'])} × {int(r['세율'] * 100)}% − 1,260,000원 | {won(r['환산산출세액'])} |")
    print(f"| 퇴직소득세 | {won(r['환산산출세액'])} ÷ 12 × 10 | {won(r['퇴직소득세'])} |")
    print(f"| 지방소득세 | 퇴직소득세 × 10% | {won(r['지방소득세'])} |")
    print(f"| 합계 | 퇴직소득세 + 지방소득세 | {won(r['합계'])} |")
    print(f"- 퇴직급여 대비 {r['합계'] / p * 100:.2f}% · 근속 1년당 {won(r['합계'] / n)} · 손에 쥐는 돈 {won(p - r['합계'])}")
    print()

    print("표: 근속연수·퇴직급여별 퇴직소득세(지방소득세 10% 포함, 비과세 소득 없음 · 계산 예시)")
    print("| 근속연수 | 퇴직급여 | 근속연수공제 | 과세표준 | 퇴직소득세 | 지방소득세 포함 합계 | 퇴직급여 대비 |")
    print("|---|---|---|---|---|---|---|")
    for n in (5, 10, 20):
        for p in (5_000 * MAN, 1 * EOK, 3 * EOK):
            r = compute(n, p)
            print(f"| {n}년 | {man(p)} | {won(r['근속연수공제'])} | {won(r['과세표준'])} | {won(r['퇴직소득세'])} | {won(r['합계'])} | {r['합계'] / p * 100:.2f}% |")
    print()
    # 본문에 쓰는 비교 숫자
    a, b = compute(5, 1 * EOK), compute(20, 1 * EOK)
    print(f"- 같은 1억원: 5년 합계 {won(a['합계'])} · 20년 합계 {won(b['합계'])} · 차이 {won(a['합계'] - b['합계'])} · 배수 {a['합계'] / b['합계']:.1f}배")
    c = compute(20, 1 * EOK)
    print(f"- 20년·1억원 중간값: 근속연수공제 {won(c['근속연수공제'])} · 환산급여 {won(c['환산급여'])} · 환산급여공제 {won(c['환산급여공제'])} · 과세표준 {won(c['과세표준'])} · 환산산출세액 {won(c['환산산출세액'])} · 퇴직소득세 {won(c['퇴직소득세'])}")
    d = compute(5, 3 * EOK)
    print(f"- 5년·3억원: 환산급여 {won(d['환산급여'])} · 세율 {int(round(d['세율'] * 100))}% · 합계 {won(d['합계'])}")
    print()

    print("표: 퇴직소득세가 0원인 퇴직급여 상한(환산급여 800만원 이하 · 계산 예시)")
    print("| 근속연수 | 근속연수공제 | 더해지는 몫(800만원 × 근속연수 ÷ 12) | 세금 0원 상한 |")
    print("|---|---|---|---|")
    for n in (1, 3, 5, 10, 15, 20, 30):
        z = zero_line(n)
        print(f"| {n}년 | {won(service_deduction(n))} | {won(F(800 * MAN * n, 12))} | {won(z)} |")
    z10 = zero_line(10)
    r = compute(10, 2_300 * MAN)
    print(f"- 10년 상한 {won(z10)} · 퇴직급여 {man(2_300 * MAN)}이면 퇴직소득세 {won(r['퇴직소득세'])} · 지방소득세 포함 {won(r['합계'])}")


if __name__ == "__main__":
    main()
