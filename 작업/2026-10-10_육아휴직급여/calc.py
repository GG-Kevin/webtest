#!/usr/bin/env python3
"""육아휴직급여 계산 (B1010-1/2) — 표준 라이브러리만. 정수(원)로만 계산한다.

입력
  wage     육아휴직 시작일을 기준으로 한 월 통상임금(원)
  months   휴직 개월 수(1~18) · company  휴직 중 회사가 휴직을 이유로 준 월 금품(원)
공식
  일반(고용보험법 시행령 제95조 ①, 대통령령 제36588호 시행 2026. 9. 18. 판 — 조문 개정 2024. 12. 24.)
    1~3개월째  = 통상임금, 상한 250만원 · 하한 70만원
    4~6개월째  = 통상임금, 상한 200만원 · 하한 70만원
    7개월째~   = 통상임금 × 80/100, 상한 160만원 · 하한 70만원
    https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=288717&joNo=0095&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  부모 모두 육아휴직(자녀 출생 후 18개월까지, 같은 시행령 제95조의3 ①)
    1~6개월째  = 통상임금, 각자 그 달의 상한 250·250·300·350·400·450만원(사용한 개월 수까지) · 하한 70만원
    7개월째~   = 통상임금 × 80/100, 상한 160만원 · 하한 70만원
    https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=288717&joNo=0095&joBrNo=03&docCls=jo&urlMode=lsScJoRltInfoR
    (가정: 두 사람이 같은 개월 수를 쓴 경우만 계산한다 — 조문 문구가 「각각 n개월인 경우」다)
  한부모(같은 조 ③): 1~3개월째 상한 300만원, 그 뒤는 일반과 같다.
  감액(시행령 제98조): 그 달 회사 금품 + 급여 > 월 통상임금이면 넘는 만큼 급여에서 뺀다.
    https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=288717&joNo=0098&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  기간: 남녀고용평등법 제19조 ② 1년 이내, 부모 모두 같은 자녀로 각각 3개월 이상 쓰면 6개월 추가(최대 18개월)
    https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=284457&joNo=0019&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  신청: 고용보험법 제70조 ② 시작일 이후 1개월부터 끝난 날 이후 12개월 이내 ·
        시행규칙 제116조 ② 매월 단위, 그 달 분은 다음 달 말일까지
기준일: 2026-10-06 원문 기준. 같은 입력이면 같은 출력. 실행하면 원고에 넣을 표를 마크다운으로 찍는다.
"""

FLOOR = 700_000
CAP_1_3 = 2_500_000
CAP_4_6 = 2_000_000
CAP_7 = 1_600_000
RATE_7 = 80                     # 100분의 80
CAP_BOTH = [2_500_000, 2_500_000, 3_000_000, 3_500_000, 4_000_000, 4_500_000]
CAP_SINGLE_1_3 = 3_000_000
WAGES = [1_500_000, 2_000_000, 3_000_000, 5_000_000]


def clamp(v, cap):
    return max(FLOOR, min(v, cap))


def month_pay(wage, k, mode="일반"):
    """k = 휴직 몇 개월째(1부터). mode = 일반 · 부모 · 한부모"""
    if k >= 7:
        return clamp(wage * RATE_7 // 100, CAP_7)
    if mode == "부모":
        return clamp(wage, CAP_BOTH[k - 1])
    if k <= 3:
        return clamp(wage, CAP_SINGLE_1_3 if mode == "한부모" else CAP_1_3)
    return clamp(wage, CAP_4_6)


def total(wage, months, mode="일반"):
    return sum(month_pay(wage, k, mode) for k in range(1, months + 1))


def reduce_pay(wage, pay, company):
    """시행령 제98조: 금품 + 급여가 통상임금을 넘는 만큼 급여에서 뺀다."""
    over = max(0, company + pay - wage)
    return max(0, pay - over)


def man(x):
    v = x / 10_000
    return f"{v:,.0f}만원" if x % 10_000 == 0 else f"{v:,.1f}만원"


def table_general():
    print("표: 월 통상임금별 육아휴직급여 — 혼자 쓰는 일반 육아휴직, 2026년 10월 시행 기준")
    print("| 월 통상임금 | 1~3개월째 월액 | 4~6개월째 월액 | 7개월째부터 월액 | 6개월 합계 | 12개월 합계 |")
    print("|---|---|---|---|---|---|")
    for w in WAGES:
        print(f"| {man(w)} | {man(month_pay(w, 1))} | {man(month_pay(w, 4))} | {man(month_pay(w, 7))} "
              f"| {man(total(w, 6))} | {man(total(w, 12))} |")
    print()


def table_both():
    print("표: 부모가 각각 6개월 쓸 때 한 사람의 달별 금액 — 일반 육아휴직과 비교")
    print("| 월 통상임금 | 1·2개월째 | 3개월째 | 4개월째 | 5개월째 | 6개월째 | 6개월 합계 | 일반 6개월 합계 | 차이 |")
    print("|---|---|---|---|---|---|---|---|---|")
    for w in WAGES[1:]:
        p = [month_pay(w, k, "부모") for k in range(1, 7)]
        t, g = total(w, 6, "부모"), total(w, 6)
        print(f"| {man(w)} | {man(p[0])} | {man(p[2])} | {man(p[3])} | {man(p[4])} | {man(p[5])} "
              f"| {man(t)} | {man(g)} | {man(t - g)} |")
    print()


def table_cases():
    w = 3_000_000
    print("표: 통상임금 300만원 가정 — 18개월 연장·회사 지급·한부모 경우 직접 계산")
    print("| 경우 | 계산 | 결과 |")
    print("|---|---|---|")
    ext = total(w, 18) - total(w, 12)
    print(f"| 부모가 각각 3개월 이상 써서 13~18개월째를 더 쓸 때 | {man(month_pay(w, 13))} × 6개월 | {man(ext)} 추가, 18개월 합계 {man(total(w, 18))} |")
    pay = month_pay(w, 1)
    company = 1_000_000
    r = reduce_pay(w, pay, company)
    print(f"| 1개월째에 회사가 휴직을 이유로 {man(company)}을 줄 때 | {man(company)} + {man(pay)} − {man(w)} = {man(company + pay - w)} 초과 | 급여 {man(r)} |")
    s = total(w, 3, "한부모") - total(w, 3)
    print(f"| 한부모가 1~3개월째를 쓸 때 | 상한 {man(CAP_SINGLE_1_3)} × 3개월 | 일반보다 {man(s)} 많음, 12개월 합계 {man(total(w, 12, '한부모'))} |")
    print()


def figure_data():
    w = 3_000_000
    print("그림 자료(통상임금 300만원, 12개월): 일반 " + ", ".join(str(month_pay(w, k) // 10_000) for k in range(1, 13))
          + " / 부모 각 6개월 " + ", ".join(str(month_pay(w, k, "부모") // 10_000) for k in range(1, 13)))
    print(f"부모 각 6개월 + 이후 6개월 한 사람 12개월 합계: {man(total(w, 12, '부모'))}")
    print(f"통상임금 500만원 부부 두 사람 6개월 합계(부모 특례): {man(total(5_000_000, 6, '부모') * 2)}")


if __name__ == "__main__":
    table_general()
    table_both()
    table_cases()
    figure_data()
