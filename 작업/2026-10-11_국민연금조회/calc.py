#!/usr/bin/env python3
"""국민연금 조회 — 조회 화면의 예상연금액을 원문 산식으로 다시 세어 보기 (B1011-3/1) · 표준 라이브러리만.

입력(표마다 고정 예시, 모두 가정):
  B      가입기간 중 기준소득월액 평균(재평가 뒤 금액으로 보고 가입 내내 같다고 둔다). 예시 3,000,000원.
  가입 시기  해마다 가입월수(1월~12월 12개월씩).
공식:
  기본연금액(연) = Σ(그 해 비율 × (A + B) × 그 해 가입월수 ÷ 전체 가입월수) × (1 + 0.05 × n ÷ 12)
      n = 20년(240개월)을 넘는 가입월수
      2026년 이후 비율 1천분의 1천290 — 국민연금법 제51조 ①
        https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280269&joNo=0051&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
      2025년 이전 연도별 비율('07년 1.8, '08년 1.5, … '25년 1.245, '26년 1.29) —
        국민연금공단 「예상연금 간단계산」 유족연금 유의사항 1의 산식
        https://www.nps.or.kr/comm/quick/getOHAH0011P0.do
        '08년 1.5에서 '25년 1.245까지는 해마다 0.015씩 내려간다(1.5 − 0.015 × 17 = 1.245, 산식의 양 끝과 맞음).
  노령연금(월) = 기본연금액 × 지급률 ÷ 12, 10원 미만 버림
      지급률: 20년 이상 100%, 10년 이상 20년 미만 50% + 10년 넘는 1년마다 5% — 국민연금법 제63조 ①
        https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280269&joNo=0063&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
      10년 이상이어야 노령연금 — 국민연금법 제61조 ①
        https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280269&joNo=0061&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
      월 지급액은 B(최종 5년 평균과 전체 평균 재평가액 중 많은 것)를 넘지 못한다 — 공단 노령연금 유의사항 5
  A = 3,193,511원(2026년 적용값) — 국민연금공단 「노령연금」
      https://www.nps.or.kr/pnsinfo/ntpsklg/getOHAF0056M0.do?menuId=MN24001118
  보험료율: 2025년까지 9%, 2026년부터 해마다 0.5%p 올려 2033년 13% — 국민연금공단 「연금보험료」
      https://www.nps.or.kr/pnsinfo/ntpsklg/getOHAF0038M0.do?menuId=MN24001113
      사업장가입자는 본인·사용자가 절반씩.
  가정: B는 가입 내내 같다 · A는 2026년 값 그대로 · 물가·재평가율 변동 없음 · 부양가족연금액 없음.
기준일: 2026-10-06 원문 기준(한국 시각). 같은 입력이면 같은 출력. 정수·분수로 계산한다.
"""
from fractions import Fraction as F

A_2026 = 3_193_511          # 2026년 적용 A값(공단 노령연금)
B_EX = 3_000_000            # 예시 B값
LOWER = 410_000             # 기준소득월액 하한 2026.7.~2027.6.
UPPER = 6_590_000           # 기준소득월액 상한 2026.7.~2027.6.
RATIO_2026_PERMIL = 1290    # 제51조 ① 1천분의 1천290
EXTRA_PERMIL = 50           # 제51조 ① 20년 초과 1년마다 1천분의 50
APP_SERVICES = 119          # 「내 곁에 국민연금」 앱 서비스 수('25.12월 말, 공단 FAQ)
APP_PERSONAL_INQ = 32       # 그중 개인 조회 32종
CALL = 1355                 # 공단 고객센터
GROWTH_MAX = 20             # 모의계산 예상소득상승률 입력 0~20%

# 공단 예상연금월액표(2026년 1월 첫 가입 가정, 노령연금 쪽) 검산용 값
NPS_TABLE = {(1_000_000, 20): 450_800, (3_000_000, 20): 665_800, (3_000_000, 10): 332_900,
             (410_000, 25): 410_000, (4_000_000, 30): 1_159_950}


def ratio_permil(year):
    """그 해 가입월에 곱하는 비율(천분율). 2007년 이전은 이 글에서 쓰지 않는다."""
    if year >= 2026:
        return RATIO_2026_PERMIL
    if year == 2007:
        return 1800
    if 2008 <= year <= 2025:
        return 1500 - 15 * (year - 2008)
    raise ValueError("2007년 이전 가입월은 계산하지 않는다")


def floor10(x):
    return int(x // 10) * 10


def base_annual(B, months_by_year):
    """기본연금액(연, 분수). months_by_year = {해: 가입월수}"""
    P = sum(months_by_year.values())
    s = sum(F(ratio_permil(y), 1000) * (A_2026 + B) * m for y, m in months_by_year.items()) / P
    n = max(0, P - 240)
    return s * (1 + F(EXTRA_PERMIL, 1000) * F(n, 12))


def pay_rate(P):
    """지급률(분수). P = 전체 가입월수"""
    if P >= 240:
        return F(1)
    if P < 120:
        return F(0)
    return F(500, 1000) + F(50, 1000) * F(P - 120, 12)


def monthly(B, months_by_year):
    P = sum(months_by_year.values())
    v = base_annual(B, months_by_year) * pay_rate(P) / 12
    return min(floor10(v), B)


def span(y0, y1):
    return {y: 12 for y in range(y0, y1 + 1)}


def premium_rate_permil(year):
    if year <= 2025:
        return 90
    return min(130, 95 + 5 * (year - 2026))


# ── 표 2: 같은 B·같은 20년, 가입 시기만 다를 때
CASES = [("2026년 1월~2045년 12월", span(2026, 2045)),
         ("2016년 1월~2035년 12월", span(2016, 2035)),
         ("2007년 1월~2026년 12월", span(2007, 2026))]


def avg_ratio(months_by_year):
    P = sum(months_by_year.values())
    return sum(F(ratio_permil(y), 1000) * m for y, m in months_by_year.items()) / P


# ── 표 3: 2007년부터 20년 낸 사람이 60세 전 5년을 더 내면
STOP = span(2007, 2026)
CONT = span(2007, 2031)


def extra_premium(B, y0, y1):
    """y0~y1년 매달 B를 기준으로 낸 보험료 합계(원). 각 달 10원 미만 버림."""
    tot = 0
    for y in range(y0, y1 + 1):
        tot += floor10(F(B * premium_rate_permil(y), 1000)) * 12
    return tot


def won(x):
    return f"{int(x):,}"


def check():
    for (B, yrs), v in NPS_TABLE.items():
        got = monthly(B, span(2026, 2026 + yrs - 1))
        assert got == v, (B, yrs, got, v)
    assert ratio_permil(2025) == 1245


def main():
    check()
    print("## 표 1: 국민연금 조회 경로")
    print("| 경로 | 로그인 | 보이는 것 | 숫자의 가정 |")
    print("|---|---|---|---|")
    print("| 공단 누리집 「국민연금 알아보기」 노령 예상연금액 조회 | 필요(간편·공동·금융·브라우저 인증서) | 만 60세 이후 받을 예상연금액 | 실제 가입이력 기준 |")
    print("| 같은 쪽 「가입·납부내역 조회」 | 필요 | 가입기간·납부 내역 | 납부 기록 그대로 |")
    print(f"| 「내 곁에 국민연금」 앱 | 필요(인증서·간편인증) | 예상노령연금·가입내역 등 개인 조회 {APP_PERSONAL_INQ}종(전체 {APP_SERVICES}종) | 누리집 조회와 같은 종류 |")
    print(f"| 예상연금 모의계산 | 없음 | 내가 넣은 소득·기간의 예상액 | 최장 만 60세까지 납부, 예상소득상승률 0~{GROWTH_MAX}% |")
    print(f"| 예상연금 간단계산 | 없음 | 10·15·20…40년 가입 예상액 | 조회하는 해 1월 1일 첫 가입 |")
    print(f"| 고객센터 {CALL} | 전화 상담 | 5년 단위 사이(예: 11년)의 예상액 상담 | 본인 확인 뒤 상담 |")
    print()
    print("## 검산: 공단 예상연금월액표(2026년 1월 첫 가입 가정)와 같은지")
    for (B, yrs), v in NPS_TABLE.items():
        print(f"- B {won(B)}원 · {yrs}년: 계산 {won(monthly(B, span(2026, 2026 + yrs - 1)))}원 = 공단 표 {won(v)}원")
    print()
    print(f"## 표 2: 같은 B {won(B_EX)}원·20년이라도 가입 시기에 따라 달라지는 월 노령연금")
    print("| 가입 시기(20년) | 평균 비율 | 월 노령연금 | 공단 월액표 대비 |")
    print("|---|---|---|---|")
    base = monthly(B_EX, CASES[0][1])
    out = {}
    for name, mby in CASES:
        m = monthly(B_EX, mby)
        r = avg_ratio(mby)
        out[name] = m
        diff = m - base
        print(f"| {name} | {float(r):.5f} | {won(m)}원 | {'같음(기준)' if diff == 0 else '+' + won(diff) + '원'} |")
    print()
    print(f"- CASE_2026 = {won(out[CASES[0][0]])}")
    print(f"- CASE_2016 = {won(out[CASES[1][0]])}")
    print(f"- CASE_2007 = {won(out[CASES[2][0]])}")
    print(f"- DIFF_2007 = {won(out[CASES[2][0]] - base)} (연 {won((out[CASES[2][0]] - base) * 12)})")
    print()
    m_stop = monthly(B_EX, STOP)
    m_cont = monthly(B_EX, CONT)
    prem = extra_premium(B_EX, 2027, 2031)
    print(f"## 표 3: 2007년부터 20년 낸 사람(B {won(B_EX)}원)이 60세 전 5년을 더 낼 때")
    print("| 경우 | 가입기간 | 월 노령연금 | 더 내는 보험료(5년 합계) |")
    print("|---|---|---|---|")
    print(f"| 2026년 12월에 멈춤 | 20년 | {won(m_stop)}원 | 0원 |")
    print(f"| 2031년 12월까지 계속 | 25년 | {won(m_cont)}원 | 전체 {won(prem)}원(사업장가입자 본인 몫 {won(prem // 2)}원) |")
    print()
    print(f"- STOP = {won(m_stop)} · CONT = {won(m_cont)} · UP = {won(m_cont - m_stop)} (연 {won((m_cont - m_stop) * 12)})")
    print(f"- PREM_TOTAL = {won(prem)} · PREM_HALF = {won(prem // 2)} · 해마다 요율 " +
          ", ".join(f"{y} {premium_rate_permil(y) / 10}%" for y in range(2027, 2032)))
    print(f"- 2027년 월 보험료(B 300만원) = {won(floor10(F(B_EX * premium_rate_permil(2027), 1000)))} · 2031년 = {won(floor10(F(B_EX * premium_rate_permil(2031), 1000)))}")
    print(f"- 25년 평균 비율 = {float(avg_ratio(CONT)):.5f} · 20년 초과 가산 = 1 + 0.05 × 60/12 = 1.25")
    print(f"- 2026년 이후 가정 20년, B 300만원 기본연금액(연) = {won(int(base_annual(B_EX, CASES[0][1])))}")


if __name__ == "__main__":
    main()
