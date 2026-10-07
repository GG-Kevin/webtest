#!/usr/bin/env python3
"""국민취업지원제도 조건 — 가구원 수별 소득선 · 구직촉진수당 합계 · 유형 판정 예시 (B1011-2/1)
표준 라이브러리만. 같은 입력이면 같은 출력. 실행하면 원고에 넣을 표를 마크다운으로 찍는다.

입력(고정 예시):
  n          가구원 수(1~6)
  income     가구단위 월평균 총소득(원) — 고시 제3조 방식으로 이미 산정된 값이라고 가정
  asset      가구원 재산 합계액(원) · work_days  신청일 이전 2년 안 취업한 날 수 · age  신청 당시 나이
공식:
  소득선(원)  = 기준 중위소득 × 비율 ÷ 100, 원 미만 반올림(고용24 안내 1,538,543원 표기와 같게)
                60% = 1유형 요건심사형·선발형(비경제활동)  법 제7조①2, 시행령 제3조①
                100% = 취업지원서비스 기본선·2유형 중장년    법 제6조①3 본문
                120% = 15~34세 취업지원서비스선·1유형 청년특례  법 제6조①3 단서
                https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=253641&joNo=0006&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
                https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=253641&joNo=0007&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
                https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=260081&joNo=0003&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  기준 중위소득 2026 = 보건복지부 2025-07-31 보도자료(list_no=1487098) · 2027 = 2026-07-28 보도자료(list_no=1491453)
  재산선      = 4억원(시행령 제3조③), 15~34세 5억원(국민취업지원제도 운영규정 제5조의2, 고용노동부고시 제2026-35호)
  취업경험    = 신청일 이전 2년 안 100일 또는 800시간(시행령 제3조④)
  구직촉진수당 = 월 60만원 × 6개월 + 부양가족(18세 이하·70세 이상·중증장애인) 1인당 월 10만원, 최대 월 40만원
                고용24 국민취업지원제도 안내(work24.go.kr/ua/z/z/1300/selectEmssRqutIntro.do, 2026-10-06 열람)
                연장 신청 시 최대 1년, 총지급액은 같음(법 제20조②) → 12개월로 나눈 월 금액 = 6개월 합계 ÷ 12
  취업성공수당 = 6개월 계속 근무 50만원 + 추가 6개월 100만원 = 150만원(고용24 같은 화면)
  본인 소득 제외선 = 1인 가구 기준 중위소득의 60%(시행령 제5조④)
기준일: 2026-10-06 원문 기준.
"""

MEDIAN_2026 = {1: 2_564_238, 2: 4_199_292, 3: 5_359_036, 4: 6_494_738, 5: 7_556_719, 6: 8_555_952}
MEDIAN_2027 = {1: 2_736_042, 2: 4_480_645, 3: 5_718_091, 4: 6_929_885, 5: 8_063_019, 6: 9_129_201}
ASSET_GENERAL = 400_000_000
ASSET_YOUTH = 500_000_000
WORK_DAYS = 100
WORK_HOURS = 800
BASE = 600_000
FAMILY_ADD = 100_000
FAMILY_CAP = 400_000
MONTHS = 6
EXTEND_MONTHS = 12
SUCCESS_6 = 500_000
SUCCESS_12_ADD = 1_000_000


def line(n, pct, table=None):
    """기준 중위소득 × pct%, 원 미만 반올림(정수 계산)."""
    m = (table or MEDIAN_2026)[n]
    return (m * pct + 50) // 100


def monthly(dependents):
    return BASE + min(FAMILY_ADD * dependents, FAMILY_CAP)


def total(dependents):
    return monthly(dependents) * MONTHS


def judge(age, n, income, asset, work_days):
    """유형 판정(나이·소득·재산·취업경험만. 구직급여 수급·생계급여 등 제외 사유는 보지 않는다)."""
    youth = 15 <= age <= 34
    l60, l100, l120 = line(n, 60), line(n, 100), line(n, 120)
    asset_cap = ASSET_YOUTH if youth else ASSET_GENERAL
    if income <= l60 and asset <= asset_cap and work_days >= WORK_DAYS:
        return "1유형 요건심사형", l60
    if income <= l60 and asset <= ASSET_GENERAL:
        return "1유형 선발형(비경제활동)", l60
    if youth and income <= l120 and asset <= ASSET_YOUTH:
        return "1유형 선발형(청년특례) 후보 · 아니면 2유형 청년", l120
    if youth:
        return "2유형 청년", l120
    if income <= l100:
        return "2유형 중장년", l100
    return "기본 소득선 밖(취업취약계층 특례만)", l100


def won(v):
    return f"{v:,}원"


CASES = [
    ("28세, 부모와 3인 가구, 취업경험 0일, 재산 3억원", 28, 3, 4_500_000, 300_000_000, 0),
    ("45세, 4인 가구, 최근 2년 200일 근무, 재산 2억원", 45, 4, 3_500_000, 200_000_000, 200),
    ("52세, 부부 2인 가구, 최근 2년 300일 근무, 재산 3억원", 52, 2, 4_000_000, 300_000_000, 300),
]


def main():
    print("표1 2026년 가구원 수별 소득선(월, 원 미만 반올림)")
    print("| 가구원 수 | 60% (1유형) | 100% (2유형 중장년) | 120% (청년) |")
    print("|---|---|---|---|")
    for n in range(1, 7):
        print(f"| {n}인 | {won(line(n, 60))} | {won(line(n, 100))} | {won(line(n, 120))} |")
    print()
    print("표2 구직촉진수당 합계(부양가족 수별)")
    print("| 부양가족 | 한 달 | 6개월 합계 | 1년으로 나누면 한 달 |")
    print("|---|---|---|---|")
    for d in range(0, 5):
        lab = f"{d}명" if d < 4 else "4명 이상"
        print(f"| {lab} | {won(monthly(d))} | {won(total(d))} | {won(total(d) // EXTEND_MONTHS)} |")
    print()
    print(f"취업성공수당 합계 {won(SUCCESS_6 + SUCCESS_12_ADD)} · 부양가족 0명 수당+취업성공수당 {won(total(0) + SUCCESS_6 + SUCCESS_12_ADD)}"
          f" · 4명 이상 {won(total(4) + SUCCESS_6 + SUCCESS_12_ADD)}")
    print(f"본인 소득 제외선(1인 60%) {won(line(1, 60))} · 연 {won(line(1, 60) * 12)}")
    print()
    print("표3 유형 판정 직접 대입(가구 월소득은 고시 방식으로 산정된 값이라고 가정)")
    print("| 가정 | 가구 월소득 | 맞대는 선 | 결과 |")
    print("|---|---|---|---|")
    for lab, age, n, inc, ast, wd in CASES:
        res, ln = judge(age, n, inc, ast, wd)
        print(f"| {lab} | {won(inc)} | {won(ln)} | {res} |")
    print()
    print("표4 1유형 60% 소득선 2026년과 2027년(월)")
    print("| 가구원 수 | 2026년 | 2027년 | 오르는 폭 |")
    print("|---|---|---|---|")
    for n in range(1, 7):
        a, b = line(n, 60), line(n, 60, MEDIAN_2027)
        print(f"| {n}인 | {won(a)} | {won(b)} | {won(b - a)} |")
    print()
    print(f"재산선 {ASSET_GENERAL:,}원 · 청년 {ASSET_YOUTH:,}원 · 취업경험 {WORK_DAYS}일 또는 {WORK_HOURS}시간")


if __name__ == "__main__":
    main()
