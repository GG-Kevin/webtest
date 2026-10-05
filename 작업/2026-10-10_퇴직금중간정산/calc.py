#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""퇴직금 중간정산 — 사유 문턱·퇴직금·퇴직소득세 비교 (B1010-2/1) · 표준 라이브러리만 · 같은 입력이면 같은 출력.

입력(가정 — 원고 표 caption과 본문에 그대로 적는다):
  WAGE_TOTAL_LIST  본인 연간 임금총액 예시(원) — 의료비 사유 문턱 계산
  AVG30_EARLY      중간정산 시점(근속 5년)의 30일분 평균임금(원) = 400만원
  AVG30_LATE       퇴직 시점(근속 10년)의 30일분 평균임금(원) = 500만원
  YEARS_EARLY / YEARS_LATE  중간정산 전·후 근속연수 5년·5년(합 10년)
  비과세 퇴직소득 없음, 두 시점 모두 2026년 10월 현행 세법을 그대로 적용(가정)
공식:
  1) 의료비 사유 문턱 = 연간 임금총액 × 125 / 1000 (이 금액을 넘게 부담해야 사유)
     근로자퇴직급여 보장법 시행령 제3조 제1항 제3호(대통령령 제36220호, 시행 2026. 3. 24.)
     https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=284693&joNo=0003&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  2) 퇴직금 = 30일분 평균임금 × 계속근로연수 (법 제8조 제1항 「1년에 대하여 30일분 이상」 — 최저 기준으로 계산)
     중간정산 뒤 계속근로기간은 정산시점부터 새로 계산 (법 제8조 제2항 후단)
     https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=284455&joNo=0008&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  3) 퇴직소득세(소득세법 제48조·제55조, 국세청 계산방법 안내 표):
     근속연수공제 D(n) → 환산급여 C=(P−D)×12÷n → 환산급여공제 E(C) → 과세표준 C−E
     → 환산산출세액 = 과세표준×기본세율−누진공제 → ÷12×n (원 미만 버림) → 지방소득세 10%(원 미만 버림)
     https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280405&joNo=0048&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
     https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280405&joNo=0055&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
     https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?mi=6444&cntntsId=7880
  4) 중간정산(퇴직소득중간지급)은 지급받은 날 퇴직한 것으로 봄 — 소득세법 시행령 제43조 제2항
     근속연수는 퇴직소득중간지급일 다음 날부터 — 같은 시행령 제105조 제1항
  5) 퇴직 때 세액정산(퇴직자가 중간정산 원천징수영수증을 내는 경우):
     정산세액 = 퇴직소득누계액(중간정산분+최종분)에 대한 세액 − 이미 낸 세액
     근속연수 = 두 근속 월수 합 − 중복 월수 (1년 미만 끝수는 1년)
     소득세법 제148조 제1항, 시행령 제203조 제1항·제3항(대통령령 제36737호, 시행 2026. 10. 1.)
     https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280405&joNo=0148&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
     https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=290841&joNo=0203&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
기준일: 2026-10-06 원문 기준. 실행하면 원고에 넣을 표를 마크다운으로 찍는다.
"""

from fractions import Fraction as F

MAN = 10_000
EOK = 100_000_000

MED_NUM, MED_DEN = 125, 1000            # 1천분의 125
WAGE_TOTAL_LIST = [3_000 * MAN, 4_000 * MAN, 5_000 * MAN, 6_000 * MAN, 8_000 * MAN]
AVG30_EARLY = 400 * MAN
AVG30_LATE = 500 * MAN
YEARS_EARLY = 5
YEARS_LATE = 5


# 시행령 제3조 제1항 각 호의 숫자 조건(원문 그대로) · 제14조(DC 중도인출) 대조
CARE_MONTHS = 6          # 6개월 이상 요양
LOOKBACK_YEARS = 5       # 신청일부터 거꾸로 5년 이내
JEONSE_TIMES = 1         # 하나의 사업에서 1회
CUT_DAY_HOURS = 1        # 1일 1시간 이상 단축
CUT_WEEK_HOURS = 5       # 1주 5시간 이상 단축
CUT_KEEP_MONTHS = 3      # 3개월 이상 계속 근로
LAW_15513 = 15513        # 법률 제15513호 근로기준법 일부개정법률
REASONS = [
    ("1", "주택 구입", "무주택자, 본인 명의", "있음"),
    ("2", "전세금·임차보증금", f"무주택자, 주거 목적, 한 사업에서 {JEONSE_TIMES}회", "있음"),
    ("3", "요양 의료비", f"{CARE_MONTHS}개월 이상 요양, 연간 임금총액의 1천분의 {MED_NUM} 초과 부담", "있음"),
    ("4", "파산선고", f"신청일부터 거꾸로 {LOOKBACK_YEARS}년 안", "있음"),
    ("5", "개인회생절차 개시 결정", f"신청일부터 거꾸로 {LOOKBACK_YEARS}년 안", "있음"),
    ("6", "임금피크제", "정년 연장·보장 조건으로 임금을 줄이는 제도 시행", "없음"),
    ("6의2", "소정근로시간 단축", f"1일 {CUT_DAY_HOURS}시간 또는 1주 {CUT_WEEK_HOURS}시간 이상 단축, {CUT_KEEP_MONTHS}개월 이상 계속 근로", "없음"),
    ("6의3", "법정 근로시간 단축", f"근로기준법 개정(법률 제{LAW_15513}호) 시행으로 퇴직금이 줄어드는 경우", "없음"),
    ("7", "재난 피해", "고용노동부장관 고시 사유", "있음"),
]

SERVICE_STEPS = [(5, 0, 100 * MAN, 0), (10, 500 * MAN, 200 * MAN, 5), (20, 1_500 * MAN, 250 * MAN, 10), (None, 4_000 * MAN, 300 * MAN, 20)]
CONV_STEPS = [(800 * MAN, 0, F(100, 100), 0), (7_000 * MAN, 800 * MAN, F(60, 100), 800 * MAN), (1 * EOK, 4_520 * MAN, F(55, 100), 7_000 * MAN),
              (3 * EOK, 6_170 * MAN, F(45, 100), 1 * EOK), (None, 15_170 * MAN, F(35, 100), 3 * EOK)]
RATES = [(1_400 * MAN, F(6, 100), 0), (5_000 * MAN, F(15, 100), 1_260_000), (8_800 * MAN, F(24, 100), 5_760_000), (15_000 * MAN, F(35, 100), 15_440_000),
         (30_000 * MAN, F(38, 100), 19_940_000), (50_000 * MAN, F(40, 100), 25_940_000), (100_000 * MAN, F(42, 100), 35_940_000), (None, F(45, 100), 65_940_000)]


def years_from_months(m):
    """1년 미만 끝수는 1년으로 본다(소득세법 제48조 제1항)."""
    return -(-m // 12)


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
            return max(b * r - prog, 0), r


def retire_tax(years, pay):
    d = min(service_deduction(years), pay)
    c = F(pay - d) * 12 / years
    e = conv_deduction(c)
    b = max(c - e, 0)
    t, r = base_tax(b)
    tax = int(t / 12 * years)
    local = int(F(tax) * F(10, 100))
    return {"근속연수공제": d, "환산급여": c, "과세표준": b, "세율": r, "퇴직소득세": tax, "지방소득세": local, "합계": tax + local}


def medical_line(wage_total):
    return wage_total * MED_NUM // MED_DEN


def scenarios():
    n_all = YEARS_EARLY + YEARS_LATE
    # A: 중간정산 없음 — 퇴직 때 10년 전체를 마지막 평균임금으로
    a_pay = AVG30_LATE * n_all
    a = retire_tax(n_all, a_pay)
    # B: 5년차 중간정산 + 퇴직 때 따로 계산
    b1_pay = AVG30_EARLY * YEARS_EARLY
    b2_pay = AVG30_LATE * YEARS_LATE
    b1 = retire_tax(YEARS_EARLY, b1_pay)
    b2 = retire_tax(YEARS_LATE, b2_pay)
    # C: B와 같은 금액, 퇴직 때 세액정산(누계액·근속 월수 합산 − 중복 0)
    months = YEARS_EARLY * 12 + (YEARS_EARLY + YEARS_LATE) * 12 - YEARS_EARLY * 12
    c_years = years_from_months(months)
    c_all = retire_tax(c_years, b1_pay + b2_pay)
    c2_tax = c_all["퇴직소득세"] - b1["퇴직소득세"]
    c2_local = c_all["지방소득세"] - b1["지방소득세"]
    return {"n_all": n_all, "a_pay": a_pay, "a": a, "b1_pay": b1_pay, "b2_pay": b2_pay, "b1": b1, "b2": b2,
            "c_years": c_years, "c_all": c_all, "c2_tax": c2_tax, "c2_local": c2_local}


def won(v):
    return f"{int(v):,}원"


def man(v):
    v = int(v)
    if v % MAN == 0:
        v //= MAN
        if v >= 10_000:
            e, m = divmod(v, 10_000)
            return f"{e}억원" if m == 0 else f"{e}억 {m:,}만원"
        return f"{v:,}만원"
    return won(v)


def main():
    print("표: 퇴직금 중간정산 사유 9가지(시행령 제3조 제1항)와 퇴직연금(DC) 중도인출에도 있는지")
    print("| 호 | 사유 | 조건 | DC 중도인출 |")
    print("|---|---|---|---|")
    for r in REASONS:
        print("| " + " | ".join(r) + " |")
    print(f"- 호 수 {len(REASONS)}개 · 증명 서류 보존 퇴직 후 {LOOKBACK_YEARS}년 · 의료비 문턱 {MED_NUM / MED_DEN * 100}%")
    print()

    print("표: 연간 임금총액별 의료비 사유 문턱(1천분의 125 · 계산 예시)")
    print("| 본인 연간 임금총액 | 이 금액을 넘게 의료비를 부담해야 사유 | 한 달로 나누면 |")
    print("|---|---|---|")
    for w in WAGE_TOTAL_LIST:
        m = medical_line(w)
        print(f"| {man(w)} | {man(m)} | 약 {round(m / 12 / MAN, 1)}만원 |")
    print()

    s = scenarios()
    a, b1, b2, c = s["a"], s["b1"], s["b2"], s["c_all"]
    b_pay = s["b1_pay"] + s["b2_pay"]
    b_tax = b1["합계"] + b2["합계"]
    c_tax = b1["합계"] + s["c2_tax"] + s["c2_local"]
    print("표: 근속 10년, 5년차 중간정산 여부별 퇴직금과 세금(30일분 평균임금 5년차 400만원·10년차 500만원 가정, 지방소득세 포함 · 계산 예시)")
    print("| 경우 | 받는 퇴직금 합계 | 세금 계산 | 세금 합계 | 세금 뺀 금액 |")
    print("|---|---|---|---|---|")
    print(f"| 중간정산 없이 10년 뒤 한 번에 | {man(s['a_pay'])} | 10년·{man(s['a_pay'])} 한 번에 계산 | {won(a['합계'])} | {won(s['a_pay'] - a['합계'])} |")
    print(f"| 5년차 중간정산, 퇴직 때 따로 | {man(b_pay)} | 5년·{man(s['b1_pay'])} {won(b1['합계'])} + 5년·{man(s['b2_pay'])} {won(b2['합계'])} | {won(b_tax)} | {won(b_pay - b_tax)} |")
    print(f"| 5년차 중간정산, 퇴직 때 합산 정산 | {man(b_pay)} | {s['c_years']}년·{man(b_pay)} 합쳐 다시 계산 {won(c['합계'])} − 이미 낸 {won(b1['합계'])} | {won(c_tax)} | {won(b_pay - c_tax)} |")
    print()
    print(f"- 중간정산 없음 대비 퇴직금 차이 {won(s['a_pay'] - b_pay)} · 따로 계산과 합산 정산의 세금 차이 {won(b_tax - c_tax)}")
    print(f"- A 중간값: 근속연수공제 {won(a['근속연수공제'])} · 환산급여 {won(a['환산급여'])} · 과세표준 {won(a['과세표준'])} · 세율 {int(a['세율'] * 100)}% · 퇴직소득세 {won(a['퇴직소득세'])} · 지방 {won(a['지방소득세'])}")
    print(f"- B1 중간정산분: 근속연수공제 {won(b1['근속연수공제'])} · 환산급여 {won(b1['환산급여'])} · 과세표준 {won(b1['과세표준'])} · 세율 {int(b1['세율'] * 100)}% · 퇴직소득세 {won(b1['퇴직소득세'])} · 지방 {won(b1['지방소득세'])}")
    print(f"- B2 퇴직분: 근속연수공제 {won(b2['근속연수공제'])} · 환산급여 {won(b2['환산급여'])} · 과세표준 {won(b2['과세표준'])} · 퇴직소득세 {won(b2['퇴직소득세'])} · 지방 {won(b2['지방소득세'])}")
    print(f"- C 누계: 근속연수 {s['c_years']}년 · 근속연수공제 {won(c['근속연수공제'])} · 환산급여 {won(c['환산급여'])} · 과세표준 {won(c['과세표준'])} · 퇴직소득세 {won(c['퇴직소득세'])} · 지방 {won(c['지방소득세'])} · 퇴직 때 더 낼 퇴직소득세 {won(s['c2_tax'])} · 지방 {won(s['c2_local'])} · 합 {won(s['c2_tax'] + s['c2_local'])}")
    print(f"- 퇴직 때 손에 쥐는 몫: 따로 {won(s['b2_pay'] - b2['합계'])} · 합산 정산 {won(s['b2_pay'] - s['c2_tax'] - s['c2_local'])}")
    print()



if __name__ == "__main__":
    main()
