#!/usr/bin/env python3
"""국민연금 임의가입 — 보험료와 10년 납부 뒤 노령연금 가정 계산 (B1008-2/2) · 표준 라이브러리만.

입력(표마다 고정 예시):
  B      기준소득월액(원). 임의가입자는 「중위수 기준소득월액」 이상에서 본인이 고른다.
  years  가입기간(년). 노령연금은 10년 이상부터.
공식:
  월 보험료     = 기준소득월액 × 그 해 보험료율, 10원 미만 버림
                  (공단 예상연금월액표 금액과 같은 방식: 1,013,000원 × 9.5% = 96,235 → 96,230원)
                  보험료율: 2026년 9.5%, 해마다 0.5%p 올라 2033년부터 13%
                  국민연금공단 「연금보험료」 https://www.nps.or.kr/pnsinfo/ntpsklg/getOHAF0038M0.do?menuId=MN24001113
                  최종 요율 1천분의 130 = 국민연금법 제88조 ④
                  https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280269&joNo=0088&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  최저 기준소득월액(임의가입) = 지역가입자 중위수 기준소득월액, 2026년 4월분부터 101.3만원(직전 100만원)
                  국민연금공단 「임의계속가입자」 연도별 표 https://www.nps.or.kr/pnsinfo/ntpsklg/getOHAF0032M0.do?menuId=MN24001111
                  (임의가입자 쪽 https://www.nps.or.kr/pnsinfo/ntpsklg/getOHAF0029M0.do?menuId=MN24001110 의 표는 2025년 4월 100만원까지만 실림)
  상한액 6,590,000원 · 하한액 410,000원(2026.7.~2027.6.) — 공단 「연금보험료」 쪽
  기본연금액(연) = 1.29 × (A + B)  (가입 20년 이하, 모든 가입월이 2026년 이후라고 가정)
                  국민연금법 제51조 ① 「1천분의 1천290」
                  https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280269&joNo=0051&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
                  A = 3,193,511원(2026년 적용값) — 공단 「노령연금」 https://www.nps.or.kr/pnsinfo/ntpsklg/getOHAF0056M0.do?menuId=MN24001118
  월 노령연금   = 기본연금액 × 지급률 ÷ 12, 10원 미만 버림 · 지급률 10년 50%, 1년마다 5%p(20년 100%)
                  월 지급액은 B(가입기간 기준소득월액 평균)를 넘지 못한다(공단 같은 쪽 유의사항 5)
                  가입기간 10년 이상 = 국민연금법 제61조 ①
  가정: B는 가입 내내 같다 · A는 2026년 값 그대로 · 재평가율·물가 반영 없음 · 부양가족연금액 없음.
       공단 예상연금월액표(2026년 1월 첫 가입 가정)와 같은 가정이다.
기준일: 2026-10-05 원문 기준. 같은 입력이면 같은 출력. 실행하면 원고에 넣을 표를 마크다운으로 찍는다.
"""

A_2026 = 3_193_511          # 2026년 적용 A값
MEDIAN_2026 = 1_013_000     # 중위수 기준소득월액 2026.4.~2027.3.
MEDIAN_2025 = 1_000_000     # 직전(2020.4.~2026.3.) 100만원
LOWER = 410_000             # 기준소득월액 하한 2026.7.~2027.6.
UPPER = 6_590_000           # 기준소득월액 상한 2026.7.~2027.6.
BASE_MULT_PERMIL = 1290     # 제51조 ① 1천분의 1천290
FINAL_RATE_PERMIL = 130     # 제88조 ④ 1천분의 130


def rate_permil(year):
    """보험료율(천분율): 2025년까지 90, 2026년 95, 해마다 +5, 2033년부터 130."""
    if year <= 2025:
        return 90
    return min(95 + 5 * (year - 2026), FINAL_RATE_PERMIL)


def premium(b, year):
    """월 보험료(원), 10원 미만 버림."""
    return (b * rate_permil(year) // 1000) // 10 * 10


def pay_rate_pct(years):
    """노령연금 지급률(%) — 10년 50%, 1년마다 5%p, 20년 이상 100%."""
    if years < 10:
        return 0
    return min(50 + 5 * (years - 10), 100)


def monthly_pension(b, years, a=A_2026):
    """월 노령연금(원) — 20년 이하만 다룬다. 10원 미만 버림, B 상한."""
    v = BASE_MULT_PERMIL * (a + b) * pay_rate_pct(years) // (1000 * 100 * 12)
    v = v // 10 * 10
    return min(v, b)


def won(n):
    return f"{n:,}원"


def man(n):
    return f"약 {n / 10_000:,.1f}만원"


TIERS = [MEDIAN_2026, 1_500_000, 2_000_000, 3_000_000, UPPER]
TIER_NAME = {MEDIAN_2026: "1,013,000원(최저)", UPPER: "6,590,000원(최고)"}


def table_premium():
    print("표: 2026년 임의가입 월 보험료(보험료율 9.5% · 10원 미만 버림 · 7월 이후 상한 기준)")
    print("| 기준소득월액 | 월 보험료 | 12개월 합계 |")
    print("|---|---|---|")
    for b in TIERS:
        p = premium(b, 2026)
        print(f"| {TIER_NAME.get(b, won(b))} | {won(p)} | {won(p * 12)} |")
    print()


def table_pension():
    print("표: 납부 기간별 월 노령연금 직접 계산(2026년 A값 3,193,511원 가정 · 같은 B값으로 계속 낸다고 가정 · 부양가족연금 제외)")
    print("| 기준소득월액 | 10년 | 15년 | 20년 |")
    print("|---|---|---|---|")
    for b in TIERS:
        cells = " | ".join(won(monthly_pension(b, y)) for y in (10, 15, 20))
        print(f"| {TIER_NAME.get(b, won(b))} | {cells} |")
    print()


def ten_year_schedule(b=MEDIAN_2026, start=2027):
    rows = []
    for y in range(start, start + 10):
        p = premium(b, y)
        rows.append((y, rate_permil(y), p, p * 12))
    return rows


def table_ten_year():
    rows = ten_year_schedule()
    total = sum(r[3] for r in rows)
    print("표: 최저 기준소득월액으로 2027년 1월부터 10년 낼 때의 보험료(요율 인상만 반영 · 기준소득월액 고정 가정)")
    print("| 연도 | 보험료율 | 월 보험료 | 그해 12개월 |")
    print("|---|---|---|---|")
    for y, r, p, t in rows:
        print(f"| {y}년 | {r / 10:.1f}% | {won(p)} | {won(t)} |")
    print(f"| 10년 합계 | - | - | {won(total)} |")
    print()
    return total


AGE_MIN, AGE_MAX, AGE_CONT_MAX = 18, 60, 65   # 제10조 ① · 제13조 ①


def table_compare():
    print("표: 임의가입과 임의계속가입, 나이와 조건 비교")
    print("| 칸 | 임의가입 | 임의계속가입 |")
    print("|---|---|---|")
    print(f"| 나이 | {AGE_MIN}세 이상 {AGE_MAX}세 미만 | {AGE_MAX}세부터 {AGE_CONT_MAX}세가 될 때까지 |")
    print("| 이전 납부 | 없어도 된다 | 낸 적이 있어야 한다 |")
    print("| 근거 조문 | 국민연금법 제10조 | 국민연금법 제13조 |")
    print()


def main():
    print(f"<!-- calc.py 출력 · 기준일 2026-10-05 -->")
    print(f"A_2026 = {A_2026:,} · 중위수 2026 = {MEDIAN_2026:,} (직전 {MEDIAN_2025:,}) · 하한 {LOWER:,} · 상한 {UPPER:,}")
    print(f"보험료율 2026 = {rate_permil(2026) / 10:.1f}% · 2033 = {rate_permil(2033) / 10:.1f}% · 기본연금액 계수 = {BASE_MULT_PERMIL / 1000:.2f}")
    p_min_26 = premium(MEDIAN_2026, 2026)
    p_min_25 = premium(MEDIAN_2025, 2026)
    p_max_26 = premium(UPPER, 2026)
    p_min_27 = premium(MEDIAN_2026, 2027)
    print(f"최저 월 보험료 2026(101.3만원) = {won(p_min_26)} · 100만원이었다면 = {won(p_min_25)} · 차이 = {won(p_min_26 - p_min_25)}")
    print(f"최고 월 보험료 2026 = {won(p_max_26)} · 2027년 1월부터 최저(요율 10.0%, 중위수 그대로 가정) = {won(p_min_27)}")
    print(f"하한 41만원 월 보험료 2026 = {won(premium(LOWER, 2026))}")
    print(f"하루로 나누면(30일) 최저 = 약 {p_min_26 / 30:,.0f}원")
    print()
    table_premium()
    table_pension()
    total = table_ten_year()
    table_compare()
    pen = monthly_pension(MEDIAN_2026, 10)
    months = -(-total // pen)
    print(f"10년 낸 보험료 합계 = {won(total)} ({man(total)})")
    print(f"10년 납부 월 노령연금(최저) = {won(pen)} · 1년 = {won(pen * 12)}")
    print(f"합계 ÷ 월 연금 = {total / pen:.1f}개월 → 받은 연금 합계가 낸 보험료를 넘는 달 = {months}개월째(약 {months / 12:.1f}년)")
    pen100 = monthly_pension(MEDIAN_2025, 10)
    print(f"검산: 공단 예상연금월액표 B 1,000,000원 10년 = {won(pen100)} · 20년 = {won(monthly_pension(MEDIAN_2025, 20))}")
    print(f"검산: B 6,590,000원 10년 = {won(monthly_pension(UPPER, 10))} · 공단 표 월 보험료 = {won(p_max_26)}")


if __name__ == "__main__":
    main()
