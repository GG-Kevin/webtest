#!/usr/bin/env python3
"""종합소득세 중간예납 — 고지액·분납 가능액·추계액 30% 판정·납부지연가산세 계산 (표준 라이브러리만).

실행: python3 calc.py  → 원고에 넣을 표 3개를 마크다운 그대로 출력한다(같은 입력이면 같은 출력).

입력(가정, 독자 대입용)
  - BASES: 2025년 귀속 종합소득세 중간예납기준액(직전 과세기간에 납부했거나 납부할 세액) 몇 가지
  - EST_*: 추계 예시 — 중간예납기준액 1,000만원, 상반기 종합소득금액 네 경우, 종합소득공제 300만원,
           공제·감면세액·원천징수세액 0원(가정)
  - PEN_*: 가산세 예시 — 고지액 1,500만원·800만원·120만원을 11월 30일까지 한 푼도 내지 않은 경우

공식·근거(모두 2026-10-04 열어 읽음)
  1) 중간예납세액 = 중간예납기준액 × 1/2, 1천원 미만 버림 — 소득세법 제65조① (시행 2026. 1. 1. 법률 제21221호)
     https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280405&joNo=0065&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
     고지서 11월 1일~15일 발급, 11월 30일까지 징수 — 같은 항
  2) 중간예납세액 50만원 미만이면 징수하지 않음 — 소득세법 제86조 제4호
     https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280405&joNo=0086&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  3) 분할납부: 납부할 세액 1천만원 초과, 납부기한 지난 뒤 2개월 이내 — 소득세법 제77조
     https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280405&joNo=0077&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
     분납 가능액: 2천만원 이하 → 1천만원 초과분 / 2천만원 초과 → 세액의 100분의 50 이하 — 소득세법 시행령 제140조
     (시행 2026. 10. 1. 대통령령 제36737호)
     https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=290841&joNo=0140&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
     국세청 안내 분납 기한 2027.2.1.(월) · 납부기한 2026.11.30.(월)
     https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?mi=2237&cntntsId=7674
  4) 추계액 신고: 중간예납추계액 < 중간예납기준액 × 100분의 30 이면 11월 1일~30일 신고 가능 — 소득세법 제65조③
     과세표준 = 상반기 종합소득금액 × 2 − 이월결손금 − 종합소득공제 / 산출세액 = 과세표준 × 기본세율 — 제65조⑧
     추계액 = 산출세액 ÷ 2 − (6.30.까지 공제·감면세액·원천징수세액 등) — 국세청 추계액 신고 안내
     https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?mi=2238&cntntsId=7675
     기본세율·누진공제 — 국세청 종합소득세 세율 표
     https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?mi=2227&cntntsId=7667
  5) 납부지연가산세: 지정납부기한까지 안 낸 세액 × 100분의 3 (국세기본법 제47조의4① 제3호)
     + 지정납부기한 다음 날부터 지난 개월 수 × 월 1만분의 67 (제1호의2 · 국세기본법 시행령 제27조의4②)
     고지서별·세목별 세액 150만원 미만이면 월 가산세(제1호의2) 미적용 — 제47조의4⑧ (시행 2026. 10. 2.)
     https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=289999&joNo=0047&joBrNo=04&docCls=jo&urlMode=lsScJoRltInfoR
     https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=283623&joNo=0027&joBrNo=04&docCls=jo&urlMode=lsScJoRltInfoR
     11월 30일까지 안 낸 세액 중 분할납부할 수 있는 세액은 고지가 없었던 것으로 보고 다음 해 1월 1일~15일에
     다시 고지 — 소득세법 제65조② → 예시에서는 분납 가능액을 가산세 대상에서 뺐다.
기준일: 2026-10-04
"""
import datetime as dt

HALF_DIV = 2              # 제65조① 2분의 1
TRUNC = 1000              # 제65조① 1천원 미만 버림
MIN_COLLECT = 500_000     # 제86조 제4호 50만원 미만 부징수
INST_MIN = 10_000_000     # 제77조 1천만원 초과
INST_MID = 20_000_000     # 시행령 제140조 2천만원
INST_RATE = 50            # 시행령 제140조 100분의 50
EST_RATIO = 30            # 제65조③ 100분의 30
PEN_ONCE = 3              # 국세기본법 제47조의4① 3호 100분의 3
PEN_MONTH = 67            # 시행령 제27조의4② 월 1만분의 67
PEN_MONTH_MIN = 1_500_000 # 제47조의4⑧ 150만원 미만 미적용

BRACKETS = [  # (상한, 세율%, 누진공제) — 국세청 세율 표
    (14_000_000, 6, 0), (50_000_000, 15, 1_260_000), (88_000_000, 24, 5_760_000),
    (150_000_000, 35, 15_440_000), (300_000_000, 38, 19_940_000), (500_000_000, 40, 25_940_000),
    (1_000_000_000, 42, 35_940_000), (None, 45, 65_940_000)]

DUE = dt.date(2026, 11, 30)
INST_DUE = dt.date(2027, 2, 1)

BASES = [990_000, 1_000_000, 3_400_000, 9_000_000, 24_000_000, 30_000_000, 50_000_000, 80_000_000]
EST_BASE = 10_000_000
EST_DEDUCT = 3_000_000
EST_HALF_INCOMES = [10_000_000, 15_000_000, 25_000_000, 30_000_000]
PEN_CASES = [15_000_000, 8_000_000, 1_200_000]


def mid_tax(base):
    t = base // HALF_DIV // TRUNC * TRUNC
    return 0 if t < MIN_COLLECT else t


def installment(tax):
    if tax <= INST_MIN:
        return 0
    if tax <= INST_MID:
        return tax - INST_MIN
    return tax * INST_RATE // 100


def basic_tax(base):
    for top, rate, cut in BRACKETS:
        if top is None or base <= top:
            return max(0, base * rate // 100 - cut)


def estimate(half_income, deduct, credits=0, withheld=0):
    taxable = max(0, half_income * 2 - deduct)
    calc_tax = basic_tax(taxable)
    est = calc_tax // 2 - credits - withheld
    return taxable, calc_tax, max(0, est)


def penalty(tax):
    inst = installment(tax)
    late = tax - inst
    once = late * PEN_ONCE // 100
    month = late * PEN_MONTH // 10000 if late >= PEN_MONTH_MIN else 0
    return inst, late, once, month


def w(n):
    return f"{n:,}원"


def main():
    wd = "월화수목금토일"
    print(f"납부기한 {DUE.isoformat()}({wd[DUE.weekday()]}) · 분납 기한 {INST_DUE.isoformat()}({wd[INST_DUE.weekday()]})")
    for d in (dt.date(2027, 1, 30), dt.date(2027, 1, 31)):
        print(f"  {d.isoformat()}은 {wd[d.weekday()]}요일")
    print()
    print("표1")
    print("| 2025년 귀속 기준액 | 고지액(절반, 천원 미만 버림) | 상반기 한 달 몫 | 11월 30일까지 낼 몫 | 2027년 2월 1일까지 분납 가능 |")
    print("|---|---|---|---|---|")
    for b in BASES:
        t = mid_tax(b)
        if t == 0:
            print(f"| {w(b)} | 고지 없음({w(b // 2 // TRUNC * TRUNC)} → 50만원 미만) | - | - | - |")
            continue
        i = installment(t)
        print(f"| {w(b)} | {w(t)} | 약 {round(t / 6 / 10000):,}만원 | {w(t - i)} | {w(i) if i else '분납 없음'} |")
    print()
    print("표2")
    line = EST_BASE * EST_RATIO // 100
    print(f"고지액 {w(mid_tax(EST_BASE))} · 30% 선 {w(line)}")
    print("| 상반기 종합소득금액 | 과세표준(×2 − 공제 300만원) | 산출세액 | 추계액(÷2) | 30% 선 300만원과 비교 |")
    print("|---|---|---|---|---|")
    for h in EST_HALF_INCOMES:
        tx, ct, est = estimate(h, EST_DEDUCT)
        ok = "미달 — 신고 가능" if est < line else "미달 아님 — 고지액대로"
        print(f"| {w(h)} | {w(tx)} | {w(ct)} | {w(est)} | {ok} |")
    print()
    print("표3")
    print("| 고지액 | 1월에 다시 고지되는 분납 가능액 | 11월 30일 넘긴 금액 | 한 번 붙는 3% | 한 달 지날 때마다 0.67% |")
    print("|---|---|---|---|---|")
    for t in PEN_CASES:
        inst, late, once, month = penalty(t)
        print(f"| {w(t)} | {w(inst) if inst else '없음'} | {w(late)} | {w(once)} | {w(month) if month else '없음(150만원 미만)'} |")
    print()
    # 원고 문장 속 계산 숫자
    t34 = mid_tax(3_400_000)
    print(f"본문: 기준액 340만원 → 고지 {w(t34)} · 한 달 몫 {w(t34 // 6)}")
    print(f"본문: 30% 선 {w(line)} · 고지 {w(mid_tax(EST_BASE))}")
    tx, ct, est = estimate(15_000_000, EST_DEDUCT)
    print(f"본문: 상반기 1,500만원 → 추계 {w(est)} · 고지와 차이 {w(mid_tax(EST_BASE) - est)}")


if __name__ == "__main__":
    main()
