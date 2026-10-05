# -*- coding: utf-8 -*-
"""국민연금 추납(연금보험료 추후 납부) 계산 — B1008-2/1 · 기준일 2026-10-05 · 표준 라이브러리만.

입력
  income  : 추납을 신청한 달의 기준소득월액(원). 천원 미만 버림, 41만~659만원으로 자른다(2026.7.~2027.6.).
  months  : 추납 개월 수(10년 미만 = 최대 119개월).
  year    : 납부기한이 속하는 해(보험료율 결정).
  voluntary: 임의가입자 여부(True면 월 보험료 상한 = A값 × 보험료율).

공식
  보험료율(year) = 9.0% + 0.5%p × (year − 2025), 2026~2033년(2033년 13%)
        — 국민연금공단 연금개혁 Q&A·보험료 납부 안내(2026년부터 매년 0.5%p, 2033년 13%)
  월 보험료     = 기준소득월액 × 보험료율 (임의가입자는 min(그 금액, A값 × 보험료율), 원 미만 버림 — 가정)
  추납보험료     = 월 보험료 × 추납 개월 수                         — 국민연금법 제92조 제3항
  늘어나는 연금(연액) = 1.29 × (A + B) × 0.05 × 개월 수 ÷ 12           — 국민연금법 제51조 제1항(1천분의 1천290,
        20년 초과 1년마다 1천분의 50), 제63조 제1항 제2호(10~20년 구간도 1년마다 기본연금액의 1천분의 50)
        가정: B(본인 평균소득) = 추납 기준소득월액, A = 2026년 A값 3,193,511원, 물가·재평가 반영 없음, 부양가족연금액 제외
  늘어나는 연금(월액) = 연액 ÷ 12, 원 미만 버림
  단순 회수 개월 = 추납보험료 ÷ 늘어나는 월 연금(올림)
  연금보험료공제 절세 = 추납보험료 × 한계세율 × 1.1(지방소득세 10% 포함)  — 소득세법 제51조의3, 공단 안내(2006년부터 추납 포함)
  카드 수수료 = 추납보험료 × 0.8%(신용) · 0.5%(체크)               — 공단 반납금·추납보험료 납부방법

원문(2026-10-05 열어 확인)
  국민연금법 제92조 https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280269&joNo=0092&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  국민연금법 제51조 https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280269&joNo=0051&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  국민연금법 제63조 https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280269&joNo=0063&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  국민연금법 시행령 제62조·제52조 https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=272577&joNo=0062&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  공단 추납 안내 https://www.nps.or.kr/pnsinfo/ntpsklg/getOHAF0047M0.do?menuId=MN24001116
  공단 보험료 납부 https://www.nps.or.kr/pnsinfo/ntpsklg/getOHAF0038M0.do?menuId=MN24001113
  공단 연금개혁 Q&A https://www.nps.or.kr/pnsinfo/ntpsklg/getOHAF0104M0.do?menuId=MN25059919
  공단 추납 납부방법 https://www.nps.or.kr/pnsinfo/ntpsklg/getOHAF0045M0.do?menuId=MN24001114
  소득세법 제51조의3 https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280405&joNo=0051&joBrNo=03&docCls=jo&urlMode=lsScJoRltInfoR
  국세청 종합소득세 세율 https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?mi=2227&cntntsId=7667
모든 금액은 정수(원)로 계산한다. 같은 입력이면 같은 출력.
"""
from fractions import Fraction as F

A_2026 = 3_193_511           # 2026년 A값(공단 추납 안내)
FLOOR, CEIL = 410_000, 6_590_000   # 2026.7.1.~2027.6.30. 기준소득월액 하한·상한
COEF = F(1290, 1000)         # 제51조① 1천분의 1천290
STEP = F(50, 1000)           # 1년마다 1천분의 50
MAX_MONTHS = 119             # 10년 미만


def rate(year):
    """보험료율(분수). 2026 = 95/1000 … 2033 이후 130/1000."""
    y = min(max(year, 2025), 2033)
    return F(90 + 5 * (y - 2025), 1000)


def base_income(income):
    v = income // 1000 * 1000
    return min(max(v, FLOOR), CEIL)


def monthly_premium(income, year, voluntary=False):
    p = base_income(income) * rate(year)
    if voluntary:
        p = min(p, A_2026 * rate(year))
    return int(p)  # 원 미만 버림(가정)


def lump(income, months, year, voluntary=False):
    return monthly_premium(income, year, voluntary) * min(months, MAX_MONTHS)


def pension_up_month(income, months, a=A_2026):
    b = base_income(income)
    yearly = COEF * (a + b) * STEP * F(min(months, MAX_MONTHS), 12)
    return int(yearly / 12)


def payback_months(total, up):
    return -(-total // up)


def won(n):
    return f"{n:,}"


def main():
    print(f"보험료율 2026 = {float(rate(2026))*100:.1f}% · 2027 = {float(rate(2027))*100:.1f}% · 2033 = {float(rate(2033))*100:.1f}%")
    cap = A_2026 * rate(2026)
    print(f"임의가입자 월 보험료 상한(2026) = A값 {won(A_2026)} × 9.5% = {float(cap):,.3f} → {won(int(cap))}원")
    print()

    print("표: 기준소득월액별 추납보험료(2026년 납부기한, 보험료율 9.5%)")
    print("| 기준소득월액 | 월 보험료 | 12개월 | 36개월 | 60개월 | 119개월 |")
    print("|---|---|---|---|---|---|")
    for inc in (410_000, 1_000_000, 2_000_000, 3_000_000):
        mp = monthly_premium(inc, 2026)
        row = [won(lump(inc, m, 2026)) for m in (12, 36, 60, 119)]
        print(f"| {won(inc)}원 | {won(mp)}원 | " + " | ".join(r + "원" for r in row) + " |")
    print()

    print("표: 추납 개월 수별 늘어나는 월 연금과 단순 회수 기간(가정: B = 추납 기준소득월액, 2026년 A값, 물가 반영 없음)")
    print("| 기준소득월액 | 추납 개월 | 추납보험료 | 늘어나는 월 연금 | 단순 회수 기간 |")
    print("|---|---|---|---|---|")
    for inc in (1_000_000, 2_000_000):
        for m in (12, 36):
            tot = lump(inc, m, 2026)
            up = pension_up_month(inc, m)
            pb = payback_months(tot, up)
            print(f"| {won(inc)}원 | {m}개월 | {won(tot)}원 | {won(up)}원 | {pb}개월(약 {pb/12:.1f}년) |")
    print()

    # 신청 달에 따른 보험료율 차이(일시납: 신청 달의 다음 달 말일이 납부기한)
    inc, m = 1_000_000, 36
    nov = lump(inc, m, 2026)
    dec = lump(inc, m, 2027)
    print("표: 같은 36개월이라도 신청 달에 따라 달라지는 일시납 추납보험료(기준소득월액 100만원)")
    print("| 신청 달 | 납부기한 | 보험료율 | 추납보험료 |")
    print("|---|---|---|---|")
    print(f"| 2026년 11월 | 2026년 12월 31일 | 9.5% | {won(nov)}원 |")
    print(f"| 2026년 12월 | 2027년 1월 31일 | 10.0% | {won(dec)}원 |")
    print(f"차이 = {won(dec - nov)}원")
    print()

    # 임의가입자 상한 예시
    vol_400 = monthly_premium(4_000_000, 2026, voluntary=True)
    reg_400 = monthly_premium(4_000_000, 2026)
    print(f"기준소득월액 400만원: 지역가입자 월 {won(reg_400)}원 · 임의가입자 상한 적용 월 {won(vol_400)}원 · 36개월 차이 {won((reg_400 - vol_400) * 36)}원")

    # 연금보험료공제 절세(추납 342만원, 한계세율 가정)
    tot = lump(1_000_000, 36, 2026)
    for r in (6, 15, 24):
        tax = tot * r // 100
        local = tax // 10
        print(f"연금보험료공제: 추납 {won(tot)}원 × {r}% = {won(tax)}원 + 지방소득세 {won(local)}원 = {won(tax + local)}원")
    # 카드 수수료
    print(f"카드 수수료(추납 {won(tot)}원): 신용 0.8% = {won(tot * 8 // 1000)}원 · 체크 0.5% = {won(tot * 5 // 1000)}원")
    # 분할 예시: 119개월을 60회로
    q, r = divmod(119, 60)
    print(f"119개월 60회 분할: {60 - r}회는 {q}개월분, {r}회는 {q + 1}개월분 (개월 단위 산정)")
    # 그림 01용: 기준소득월액 100만원, 개월별 추납보험료와 늘어나는 월 연금
    for m in (12, 36, 60, 119):
        print(f"그림: 100만원·{m}개월 → 추납 {won(lump(1_000_000, m, 2026))}원 · 월 연금 +{won(pension_up_month(1_000_000, m))}원")
    # 1개월당 늘어나는 연금(연액) 기준
    for inc in (1_000_000, 2_000_000):
        yearly = COEF * (A_2026 + base_income(inc)) * STEP
        print(f"B={won(inc)}원: 추납 12개월당 연금 연액 증가 {float(yearly):,.2f}원 → 월 {won(int(yearly / 12))}원")


if __name__ == "__main__":
    main()
