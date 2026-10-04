#!/usr/bin/env python3
"""정년연장 법제화 — 출생연도별 법정 정년 도달 해 · 연금 개시 해 · 공백 계산 (B1004-5/1) — 표준 라이브러리만.

입력:
  birth_year  출생연도(정수, 1953~1980)
  retire_age  정년 나이(정수, 기본 60 = 현행 법정 정년). 60 미만이면 60으로 본다.
공식:
  pension_age   = 61(1953~56년생) · 62(1957~60) · 63(1961~64) · 64(1965~68) · 65(1969~)
                  국민연금공단 노령연금 안내 「노령연금 지급연령 상향조정(법률 제8541호 부칙 제8조)」 표
                  https://www.nps.or.kr/pnsinfo/ntpsklg/getOHAF0056M0.do?menuId=MN24001118
  retire_age_eff = max(60, retire_age)   — 고령자고용법 제19조①②(법률 제18921호, 시행 2022. 6. 10.)
                  https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=243057&joNo=0019&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  retire_year   = birth_year + retire_age_eff  (정확한 퇴직일은 취업규칙, 공무원은 국가공무원법 제74조④ 6월 30일·12월 31일)
  pension_year  = birth_year + pension_age
  gap_years     = max(0, pension_age - retire_age_eff)
  노령연금 원칙: 국민연금법 제61조①(가입기간 10년 이상) — 법률 제21203호, 시행 2026. 1. 1.
                  https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280269&joNo=0061&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  의안 2213470 부칙 제2조(국회 심사 중, 통과 전): 시행일~2027년 63세 · 2028~2032년 64세 · 2033년~ 65세
                  bill_retire(b) = 60세가 되는 해부터 차례로 보며 (그해 − b) ≥ 그해의 의안 정년이 되는 첫 해
                  가정: 그 사람이 60세가 되는 해보다 먼저 시행된다(시행일은 부칙 제1조 「공포 후 6개월」, 공포 전)
                  https://pal.assembly.go.kr/napal/lgsltpa/lgsltpaDone/view.do?lgsltPaId=PRC_W2V5V0T9U2C4A1B0Z5A3Y2Z8O6O0N3
                  의안 원문 PDF https://likms.assembly.go.kr/filegate/servlet/FileGate?bookId=8F1ABFFC-8C00-4536-1846-97FC98E22BAE&type=1
기준일: 2026-10-04 원문 기준. 같은 입력이면 같은 출력. 실행하면 원고에 넣을 표를 마크다운으로 찍는다.
"""

LEGAL_MIN = 60                 # 고령자고용법 제19조①
BILL_NO = 2213470              # 국회 의안번호
LAW_NO = 18921                 # 고령자고용법 현행 법률 번호
BILL_TARGET = 65               # 의안 2213470 제19조 개정안
CIVIL_AGE = 60                 # 국가공무원법 제74조①
PENSION_BANDS = [(1953, 1956, 61), (1957, 1960, 62), (1961, 1964, 63), (1965, 1968, 64), (1969, 9999, 65)]


def pension_age(birth_year):
    for lo, hi, age in PENSION_BANDS:
        if lo <= birth_year <= hi:
            return age
    raise ValueError("1953년생 이후만 계산합니다")


def compute(birth_year, retire_age=LEGAL_MIN):
    eff = max(LEGAL_MIN, retire_age)
    pa = pension_age(birth_year)
    return {"pension_age": pa, "retire_age_eff": eff, "retire_year": birth_year + eff,
            "pension_year": birth_year + pa, "gap_years": max(0, pa - eff)}


def bill_age(year):
    """의안 2213470 부칙 제2조: 연도별 정년."""
    if year <= 2027:
        return 63
    if year <= 2032:
        return 64
    return 65


def bill_retire(birth_year):
    y = birth_year + LEGAL_MIN
    while y - birth_year < bill_age(y):
        y += 1
    return y, y - birth_year


TESTS = [
    {"birth_year": 1968, "retire_age": 60},
    {"birth_year": 1969, "retire_age": 60},
    {"birth_year": 1964, "retire_age": 60},
    {"birth_year": 1965, "retire_age": 60},
    {"birth_year": 1972, "retire_age": 65},
    {"birth_year": 1970, "retire_age": 58},
]
EXPECT = [(64, 2028, 2032, 4), (65, 2029, 2034, 5), (63, 2024, 2027, 3), (64, 2025, 2029, 4),
          (65, 2037, 2037, 0), (65, 2030, 2035, 5)]


def selftest():
    for t, e in zip(TESTS, EXPECT):
        r = compute(**t)
        got = (r["pension_age"], r["retire_year"], r["pension_year"], r["gap_years"])
        assert got == e, (t, got, e)


def table1():
    print("표: 정년연장, 원문에서 확인된 것과 확인되지 않은 것(2026년 10월 4일)")
    print("| 항목 | 지금 상태 | 확인한 원문 |")
    print("|---|---|---|")
    print(f"| 법정 정년 | {LEGAL_MIN}세 이상, {LEGAL_MIN}세 미만으로 정하면 {LEGAL_MIN}세로 봄(현행 법률 제{LAW_NO}호) | 고령자고용법 제19조 |")
    print("| 정부 방향 | 「세대 상생형 정년연장 법제화」 추진, 목표 나이·시행 연도 없음 | 고용노동부 2026. 8. 4. 보도자료 |")
    print(f"| 국회 법안 | 의안 {BILL_NO}: 정년 {BILL_TARGET}세, 부칙에 63세·64세·{BILL_TARGET}세 단계, 의결 전 | 국회 의안정보시스템·입법예고 |")
    print("| 정부가 낸 법안 | 확인되지 않음 | 국회 입법예고 목록 |")
    print("| 시행 연도 | 정해지지 않음(법 통과 전) | 확인된 원문 없음 |")
    print("| 내 출생연도 적용 | 정해지지 않음 | 확인된 원문 없음 |")
    print("| 임금 조정·재고용 | 현행 조문 그대로(임금체계 개편 조치·재고용 노력) | 고령자고용법 제19조의2·제21조 |")
    print(f"| 공무원 | {CIVIL_AGE}세, 다른 법(국가공무원법)이 정함 | 국가공무원법 제74조 |")
    print()


def table2():
    print(f"표: 출생연도별 지금 법 정년({LEGAL_MIN}세)과 연금 개시 연령 사이 공백(우리 계산)")
    print(f"| 출생연도 | {LEGAL_MIN}세 되는 해 | 연금 개시 연령 | 연금 개시 해 | 공백 |")
    print("|---|---|---|---|---|")
    for b in range(1964, 1973):
        r = compute(b)
        print(f"| {b}년생 | {r['retire_year']}년 | {r['pension_age']}세 | {r['pension_year']}년 | {r['gap_years']}년 |")
    print()


def table3():
    ages = list(range(60, 66))
    print("표: 정년이 몇 세라면 공백이 몇 년인가(가정 계산)")
    print("| 출생연도 | " + " | ".join(f"정년 {a}세" for a in ages) + " |")
    print("|---" * (len(ages) + 1) + "|")
    for b in (1965, 1968, 1969, 1972):
        print(f"| {b}년생 | " + " | ".join(f"{compute(b, a)['gap_years']}년" for a in ages) + " |")
    print()


def table4():
    print(f"표: 의안 {BILL_NO} 부칙대로 시행된다면 출생연도별 정년(가정 계산)")
    print("| 출생연도 | 지금 법 정년 해 | 의안대로라면 정년 해 | 그때 나이 | 연금 개시 해 | 공백 |")
    print("|---|---|---|---|---|---|")
    for b in range(1968, 1973):
        y, age = bill_retire(b)
        r = compute(b)
        gap = max(0, r["pension_year"] - y)
        print(f"| {b}년생 | {r['retire_year']}년 | {y}년 | {age}세 | {r['pension_year']}년 | {gap}년 |")
    print()


def tests_out():
    print("# 시험 입력")
    for t in TESTS:
        print(t, compute(**t))
    print("# 의안 부칙 연도별 정년:", {y: bill_age(y) for y in (2027, 2028, 2032, 2033)})


if __name__ == "__main__":
    selftest()
    table1()
    table2()
    table3()
    table4()
    tests_out()
