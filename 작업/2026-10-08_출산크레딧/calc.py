#!/usr/bin/env python3
"""출산크레딧 — 자녀 수별 추가 가입기간과 늘어나는 노령연금 월액 (B1008-1/2) · 표준 라이브러리만.

입력(표마다 고정 예시):
  kids        자녀 수(1~5)
  months      추가로 인정되는 가입기간(개월)
  B           본인 가입기간 평균 기준소득월액(원, 재평가 뒤 값이라고 가정)
  years       본인 실제 가입기간(년)
공식:
  [추가 가입기간]
  - 첫째 자녀를 2026. 1. 1. 이후 얻은 경우(현행 제19조 ①):
      자녀 2명 이하 = 자녀 1명마다 12개월 · 3명 이상 = 24개월 + (자녀 수 − 2) × 18개월 · 상한 없음
      국민연금법 제19조 ①(법률 제21203호, 시행 2026. 1. 1. 판)
      https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280269&joNo=0019&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
      부칙(법률 제20903호, 2025. 4. 2.) 제3조 ① 「이 법 시행 이후 첫째 자녀를 얻은 사람부터 적용」
  - 첫째·둘째 … 모두 2008. 1. 1.~2025. 12. 31.에 얻은 경우(종전 규정):
      둘째 12개월 · 셋째부터 1명마다 18개월 · 합계 50개월 상한 (첫째는 0)
      국민연금공단 연금개혁 안내 https://www.nps.or.kr/pnsinfo/ntpsklg/getOHAF0104M0.do?menuId=MN25059919
  - 첫째는 2008~2025년, 그 뒤 자녀를 2026. 1. 1. 이후 얻은 경우:
      종전 개월 수(둘째 12 · 셋째부터 18), 50개월 상한은 적용하지 않음(부칙 제3조 ②, 공단 안내 「상한 제한은 없습니다」)
  [연금 증가]
  - 기본연금액(연) = 1,290/1,000 × (A + B) × 가입월수/240  (20년 초과분은 1년마다 1,000분의 50 가산과 같은 식)
      국민연금법 제51조 ① https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280269&joNo=0051&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  - 출산 추가 가입기간의 기준소득월액 = A값 전액(제51조 ①2호 다목) · 군 복무 추가 기간 = A값의 2분의 1(같은 호 나목)
  - 크레딧 c개월(소득 X)을 더하면 B가 (B×n + X×c)/(n+c)로 바뀌므로
      증가(연) = 1.29 × (A×c + X×c) / 240  → B와 n에 관계없다.  출산: X = A → 월 증가 = 1.29 × 2A × c / 2,880
  - A값 2026년 3,193,511원(국민연금공단 노령연금 안내, 「2026년 기준 3,193,511원」)
      https://www.nps.or.kr/pnsinfo/ntpsklg/getOHAF0056M0.do?menuId=MN24001118
  - 검산: 같은 안내의 「노령연금 예상연금월액표」(B 100만원·20년 = 450,800원, 30년 = 676,200원)를 이 식이 다시 만든다(10원 미만 버림).
가정: 1,290/1,000 비율을 전체 기간에 적용, 오늘(2026년 A값) 돈 기준, 제53조 최고한도·부양가족연금액·물가 조정 제외.
기준일: 2026-10-05 원문 기준. 같은 입력이면 같은 출력.
"""

A = 3_193_511           # 2026년 A값(원)
RATIO = 1290            # 1천분의 1천290
MONTH_EACH = 12         # 자녀 1명마다 12개월(2명 이하)
TWO_KIDS = 24           # 첫째·둘째 24개월
THIRD_ON = 18           # 셋째부터 1명마다 18개월
OLD_CAP = 50            # 종전 상한 50개월
MIL_MAX = 12            # 군 복무 추가 산입 최대 12개월
KIDS = [1, 2, 3, 4, 5]
RECEIVE_YEARS = 25      # 수령 기간 가정(년)


def months_new(k):
    """2026. 1. 1. 이후 첫째를 얻은 경우(현행 제19조 ①)."""
    if k <= 2:
        return MONTH_EACH * k
    return TWO_KIDS + THIRD_ON * (k - 2)


def months_old_raw(k):
    """종전 규정 개월 수(첫째 0 · 둘째 12 · 셋째부터 18), 상한 전."""
    if k <= 1:
        return 0
    return MONTH_EACH + THIRD_ON * (k - 2)


def months_old(k):
    return min(months_old_raw(k), OLD_CAP)


def floor10(x):
    return int(x // 10 * 10)


def pension_month(B, n_months, extra=0, extra_income=None):
    """월 기본연금액(10원 미만 버림 전, 원). extra 개월은 소득 extra_income으로 더한다."""
    if extra_income is None:
        extra_income = A
    tot = n_months + extra
    Bp = (B * n_months + extra_income * extra) / tot
    return RATIO / 1000 * (A + Bp) * tot / 240 / 12


def gain_month(c, income=None):
    """크레딧 c개월이 늘리는 월 연금(원, 소수 그대로)."""
    if income is None:
        income = A
    return RATIO / 1000 * (A + income) * c / 2880


def won(x):
    return f"{int(x):,}원"


def man(x):
    return f"약 {x / 10_000:,.1f}만원"


def main():
    print("## 1. 자녀 수별 추가 가입기간(개월)\n")
    print("| 자녀 수 | 첫째를 2026년 이후 얻은 경우 | 모두 2008~2025년에 얻은 경우 | 첫째는 2025년 이전, 그 뒤 자녀는 2026년 이후 |")
    print("|---|---|---|---|")
    for k in KIDS:
        mix = "해당 없음" if k == 1 else f"{months_old_raw(k)}개월"
        print(f"| {k}명 | {months_new(k)}개월 | {months_old(k)}개월 | {mix} |")
    print()

    print("## 2. 추가 가입기간이 늘리는 월 연금(2026년 A값, 오늘 돈 기준)\n")
    per = gain_month(1)
    print(f"출산 1개월당 월 증가 = 1.29 × 2 × {A:,} ÷ 2,880 = {per:,.2f}원\n")
    print("| 자녀 수(2026년 이후 첫째) | 추가 가입기간 | 월 연금 증가 | 1년 | 25년 받으면 |")
    print("|---|---|---|---|---|")
    for k in KIDS:
        c = months_new(k)
        g = int(gain_month(c))
        print(f"| {k}명 | {c}개월 | {won(g)} | {won(g * 12)} | {man(g * 12 * RECEIVE_YEARS)} |")
    half = int(gain_month(6))
    print(f"| 1명(부모가 반씩) | 6개월씩 | 각 {won(half)} | 각 {won(half * 12)} | 각 {man(half * 12 * RECEIVE_YEARS)} |")
    mil = int(gain_month(MIL_MAX, A / 2))
    print(f"| (참고) 군 복무 12개월 | 12개월 | {won(mil)} | {won(mil * 12)} | {man(mil * 12 * RECEIVE_YEARS)} |")
    print()

    print("## 3. 소득이 달라도 늘어나는 금액은 같은가(자녀 1명, 12개월)\n")
    print("| 본인 평균소득(B) · 가입 20년 | 크레딧 전 월 연금 | 크레딧 후 월 연금 | 차이 |")
    print("|---|---|---|---|")
    for B in (2_000_000, 3_000_000, 4_000_000):
        before = pension_month(B, 240)
        after = pension_month(B, 240, 12)
        print(f"| {B // 10_000}만원 | {won(before)} | {won(after)} | {won(after - before)} |")
    print()

    print("## 4. 검산 — 공단 예상연금월액표 다시 만들기(B 100만원, 10원 미만 버림)\n")
    print("| 가입기간 | 식으로 계산 | 공단 표 |")
    print("|---|---|---|")
    for yrs, nps in ((20, 450_800), (30, 676_200)):
        print(f"| {yrs}년 | {floor10(pension_month(1_000_000, yrs * 12)):,}원 | {nps:,}원 |")
    print()
    print(f"변수: A={A} RATIO={RATIO} per_month={per:.4f} gain12={int(gain_month(12))} "
          f"gain24={int(gain_month(24))} gain42={int(gain_month(42))} mil12={mil}")


if __name__ == "__main__":
    main()
