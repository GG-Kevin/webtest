#!/usr/bin/env python3
"""연말정산 월세 세액공제 계산 (B1007-1/1) — 표준 라이브러리만.

입력(표마다 고정 예시, 가정은 표 아래에 적는다):
  monthly    월세(원, 관리비 제외 계약상 월세)
  wage       총급여액(원) · other_ok  종합소득금액 조건 충족 여부(기본 True)
공식:
  공제율      = 총급여 5,500만원 이하(종합소득금액 4,500만원 초과자 제외) → 100분의 17
                총급여 8,000만원 이하(종합소득금액 7,000만원 초과자 제외) → 100분의 15
                그 밖 → 0
  공제대상    = min(그 해 월세액, 1,000만원)
  세액공제    = 공제대상 × 공제율 (원 미만 버림)
                조세특례제한법 제95조의2 ①(법률 제21467호, 시행 2026. 9. 18. 판)
                https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=284389&joNo=0095&joBrNo=02&docCls=jo&urlMode=lsScJoRltInfoR
  배우자 추가 = 세대주 공제 뒤 배우자도 요건을 갖추면 추가. 세대주+배우자 월세 합이 1,000만원을 넘으면
                배우자 공제대상 = max(0, 배우자 월세 − (합계 − 1,000만원))  (같은 조 ②, 신설 2025. 12. 23.,
                부칙 법률 제21223호 제17조: 2026. 1. 1. 이후 지급하는 월세부터)
                배우자 요건(주소지 시·군·구가 다름 등) = 조세특례제한법 시행령 제95조 ⑤(신설 2026. 2. 27.)
                https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=288915&joNo=0095&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  해당 연도 월세액(계약이 해를 걸칠 때) = 계약기간 월세 합계 ÷ 계약기간 일수 × 그 해 임차일수
                조세특례제한법 시행령 제95조 ③
  지자체·국가 월세 지원금 상당액은 공제대상에서 뺀다
                국세청 「연말정산 주택자금·월세액 공제의 이해(2025년)」 해석사례 23(서면-2024-법규소득-0214, '25.1.31.)
                https://www.nts.go.kr/comm/nttFileDownload.do?fileKey=d68280b905b4d057a1b8ea26039cd832
  표준세액공제 = 근로자가 특별소득공제·특별세액공제·월세 세액공제를 하나도 신청하지 않으면 연 13만원
                소득세법 제59조의4 ⑨1호(법률 제21221호, 시행 2026. 1. 1.)
                https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280405&joNo=0059&joBrNo=04&docCls=jo&urlMode=lsScJoRltInfoR
  산출세액 한도 = 월세 세액공제 등이 근로소득 산출세액을 넘으면 넘는 금액은 없는 것(소득세법 제61조①)
기준일: 2026-10-05 원문 기준. 같은 입력이면 같은 출력. 실행하면 원고에 넣을 표를 마크다운으로 찍는다.
"""
import datetime as dt

WAGE_HIGH = 80_000_000      # 총급여 8천만원 이하
INCOME_HIGH = 70_000_000    # 종합소득금액 7천만원 초과 제외
WAGE_LOW = 55_000_000       # 총급여 5천500만원 이하
INCOME_LOW = 45_000_000     # 종합소득금액 4천500만원 초과 제외
RATE_HIGH = 15              # 100분의 15
RATE_LOW = 17               # 100분의 17
CAP = 10_000_000            # 월세액 1천만원 초과분 없음
STD_CREDIT = 130_000        # 표준세액공제 연 13만원


def rate(wage):
    if wage <= WAGE_LOW:
        return RATE_LOW
    if wage <= WAGE_HIGH:
        return RATE_HIGH
    return 0


def credit(annual_rent, r):
    base = min(annual_rent, CAP)
    return base * r // 100


def manf(x):
    """원 → 「○○.○만원」(공제액 표기, 천원 단위까지)."""
    v = x / 10_000
    return f"{v:,.0f}만원" if x % 10_000 == 0 else f"{v:,.1f}만원"


def man(x):
    """원 → 「○만원」(만 단위가 딱 떨어지지 않으면 원 단위)."""
    if x % 10_000 == 0:
        return f"{x // 10_000:,}만원"
    return f"{x:,}원"


def table_rates():
    print("표: 총급여 구간별 공제율과 1년 최대 공제액")
    print("| 총급여(종합소득금액 조건) | 공제율 | 1년 최대 공제액 | 한 달로 나누면 |")
    print("|---|---|---|---|")
    rows = [("5,500만원 이하(종합소득금액 4,500만원 이하)", RATE_LOW),
            ("5,500만원 초과 8,000만원 이하(종합소득금액 7,000만원 이하)", RATE_HIGH)]
    for label, r in rows:
        c = credit(CAP, r)
        print(f"| {label} | {r}% | {man(c)} | 약 {c / 12 / 10_000:.1f}만원 |")
    print("| 8,000만원 초과 | 대상 아님 | 0원 | - |")
    print()


MONTHLY = [400_000, 500_000, 600_000, 700_000, 800_000, 900_000]
WAGES = [55_000_000, 70_000_000]


def table_examples():
    print("표: 월세별 세액공제액 직접 계산(1년 12개월 낸 경우)")
    print("| 월세 | 1년 월세 | 총급여 5,500만원(17%) | 총급여 7,000만원(15%) | 17%에서 표준세액공제 13만원을 뺀 값 |")
    print("|---|---|---|---|---|")
    for m in MONTHLY:
        y = m * 12
        c_low = credit(y, rate(WAGES[0]))
        c_high = credit(y, rate(WAGES[1]))
        print(f"| {man(m)} | {man(y)} | {manf(c_low)} | {manf(c_high)} | {manf(c_low - STD_CREDIT)} |")
    print()


def days_between(a, b):
    return (b - a).days + 1


def prorate(monthly, months, start, end, year):
    """계약기간 월세 합계 ÷ 계약 일수 × 그 해 임차일수(원 미만 버림)."""
    total = monthly * months
    cdays = days_between(start, end)
    ystart = max(start, dt.date(year, 1, 1))
    yend = min(end, dt.date(year, 12, 31))
    ydays = max(0, days_between(ystart, yend))
    return total, cdays, ydays, total * ydays // cdays


def spouse(head_rent, sp_rent):
    total = head_rent + sp_rent
    over = max(0, total - CAP)
    return max(0, sp_rent - over)


def table_cases():
    print("표: 2026년에 자주 생기는 세 가지 경우 직접 계산(총급여 5,500만원 이하, 17%)")
    print("| 경우 | 공제대상 월세 | 세액공제 | 계산 |")
    print("|---|---|---|---|")
    # 1) 7월 1일 입주, 2년 계약, 월 50만원
    total, cdays, ydays, amt = prorate(500_000, 24, dt.date(2026, 7, 1), dt.date(2028, 6, 30), 2026)
    c1 = credit(amt, RATE_LOW)
    print(f"| 7월 1일 입주(2년 계약, 월 50만원) | {amt:,}원 | {c1:,}원 | {man(total)} ÷ {cdays}일 × {ydays}일 |")
    # 2) 지자체 월세 지원 월 20만원을 12개월 받은 경우, 월세 50만원
    own = (500_000 - 200_000) * 12
    c2 = credit(own, RATE_LOW)
    print(f"| 월세 50만원 중 월 20만원 지원받음(12개월) | {man(own)} | {man(c2)} | (50만원 − 20만원) × 12 |")
    # 3) 부부가 다른 시·군·구에 살며 각자 월세: 세대주 월 60만원, 배우자 월 50만원
    head = 600_000 * 12
    sp = 500_000 * 12
    sp_base = spouse(head, sp)
    c3h = credit(head, RATE_LOW)
    c3s = credit(sp_base, RATE_LOW)
    print(f"| 세대주 월 60만원 + 배우자 월 50만원(주소 시·군·구 다름) | 세대주 {man(head)} · 배우자 {man(sp_base)} | "
          f"세대주 {man(c3h)} · 배우자 {man(c3s)} | 합계 {man(head + sp)} − 1,000만원 = {man(head + sp - CAP)}을 배우자 몫에서 뺌 |")
    print()
    return {"c1": c1, "c2": c2, "c3h": c3h, "c3s": c3s, "sp_base": sp_base}


def main():
    print("# 연말정산 월세 세액공제 계산 (2026-10-05 원문 기준)\n")
    table_rates()
    table_examples()
    r = table_cases()
    # 본문 문장용 숫자
    m50_low = credit(500_000 * 12, RATE_LOW)
    m50_high = credit(500_000 * 12, RATE_HIGH)
    m60_low = credit(600_000 * 12, RATE_LOW)
    m60_high = credit(600_000 * 12, RATE_HIGH)
    print("본문 숫자")
    print(f"- 월 50만원: 17% {m50_low:,}원 · 15% {m50_high:,}원 · 한 달 약 {m50_low / 12:,.0f}원 / {m50_high / 12:,.0f}원")
    print(f"- 월 60만원: 17% {m60_low:,}원 · 15% {m60_high:,}원")
    print(f"- 표준세액공제 13만원 대비 순차이(월 50만원, 17%): {m50_low - STD_CREDIT:,}원")
    print(f"- 1천만원 한도에 닿는 월세: 월 {CAP / 12:,.0f}원(약 83만원)")
    print(f"- 경우별: 7월 입주 {r['c1']:,}원 · 지원금 {r['c2']:,}원 · 부부 세대주 {r['c3h']:,}원 / 배우자 {r['c3s']:,}원 (배우자 대상 {r['sp_base']:,}원)")
    print(f"- 지원금 없을 때 월 50만원 17%와의 차이: {m50_low - r['c2']:,}원")


if __name__ == "__main__":
    main()
