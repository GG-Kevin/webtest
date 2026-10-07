#!/usr/bin/env python3
"""주택연금 가입조건·월지급금 계산 (B1009-2/1) — 표준 라이브러리만.

입력(표마다 고정 예시, 가정은 원고 표 아래에 적는다):
  age        부부 중 나이가 적은 사람의 나이(세)
  price_eok  공사가 인정하는 시세(억원) — 월지급금 산정용
  notice_eok 공시가격 등(억원, 부부 합산) — 가입 가능 여부 판정용
공식:
  가입 가능   = (부부 중 1명이 55세 이상) and (부부 합산 공시가격 등 ≤ 12억원)
                한국주택금융공사법 시행령 제3조의2 ② (55세)
                https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=290577&joNo=0003&joBrNo=02&docCls=jo&urlMode=lsScJoRltInfoR
                한국주택금융공사법 시행령 제28조의9 (12억원, 2023. 10. 4. 신설)
                https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=290577&joNo=0028&joBrNo=09&docCls=jo&urlMode=lsScJoRltInfoR
  산정 가격   = min(시세, 12억원) — 시세가 12억원을 넘으면 12억원으로 본다
                한국주택금융공사법 제43조의11 ② · 공사 자주하는 질문 「주택가격은 어떻게 평가하나요?」
                https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=277275&joNo=0043&joBrNo=11&docCls=jo&urlMode=lsScJoRltInfoR
  월지급금    = 공사 월지급금 예시 표(종신지급방식·정액형·일반주택, 단위 천원)의 (연령, 산정 가격) 칸
                https://www.hf.go.kr/ko/sub03/sub03_01_01_02.do  (화면 표 머리 「2026.03.01. 기준」)
                같은 화면의 일람표 엑셀(「2026. 6. 1. 신청접수분부터 적용」) 같은 칸과 72칸 모두 같음(아래 EXCEL로 확인)
  1년·10년 합계 = 월지급금 × 12 × 년수 (정액형 — 가입 때 정한 금액이 바뀌지 않는다는 공사 안내, 이자·보증료 제외)
  초기보증료  = 주택가격 × 1.0% (최초 연금지급일, 현금이 아니라 대출잔액에 더해짐) · 연보증료 = 보증잔액 × 연 0.95%
                https://www.hf.go.kr/ko/sub03/sub03_01_01_06.do
  해지 환급(가정) = 초기보증료 × (60 − 이용 개월) ÷ 60 (최초 연금 실행일부터 5년 안 전액 상환 해지,
                「이용기간에 비례한 액수를 차감」을 월 단위 비례로 옮긴 가정) · 30일 안 철회 = 전액
                https://www.hf.go.kr/ko/sub03/sub03_02_05_04.do?mode=list&pagerLimit=50&pager.offset=0
기준일: 2026-10-05 원문 기준. 같은 입력이면 같은 출력. 실행하면 원고에 넣을 표를 마크다운으로 찍는다.
"""

AGE_MIN = 55            # 부부 중 1명 55세 이상
PRICE_CAP_EOK = 12      # 공시가격 등 12억원 이하 / 시세 12억원 초과는 12억원으로 봄
INIT_FEE_PCT = 1.0      # 초기보증료 주택가격의 1.0%
ANNUAL_FEE_PCT = 0.95   # 연보증료 보증잔액의 연 0.95%
REFUND_MONTHS = 60      # 5년 안 해지 때 초기보증료 일부 환급

AGES = [55, 60, 65, 70, 75, 80]
PRICES = list(range(1, 13))  # 1억~12억원
# 공사 「월지급금 예시」 화면 — 일반주택 종신지급방식 정액형(단위 천원)
WEB = {
    55: [156, 312, 468, 624, 780, 936, 1092, 1248, 1404, 1560, 1716, 1872],
    60: [210, 421, 632, 842, 1053, 1264, 1475, 1685, 1896, 2107, 2318, 2528],
    65: [252, 505, 758, 1011, 1264, 1517, 1770, 2023, 2276, 2529, 2782, 3035],
    70: [307, 615, 923, 1231, 1539, 1847, 2155, 2462, 2770, 3078, 3386, 3414],
    75: [381, 762, 1143, 1525, 1906, 2287, 2669, 3050, 3431, 3666, 3666, 3666],
    80: [483, 966, 1449, 1932, 2416, 2899, 3382, 3865, 4060, 4060, 4060, 4060],
}
# 같은 화면에서 내려받은 「월지급금 일람표_20260601기준.xlsx」 시트 「일반주택」 같은 칸(2026-10-05 열어 옮김)
EXCEL = {
    55: [156, 312, 468, 624, 780, 936, 1092, 1248, 1404, 1560, 1716, 1872],
    60: [210, 421, 632, 842, 1053, 1264, 1475, 1685, 1896, 2107, 2318, 2528],
    65: [252, 505, 758, 1011, 1264, 1517, 1770, 2023, 2276, 2529, 2782, 3035],
    70: [307, 615, 923, 1231, 1539, 1847, 2155, 2462, 2770, 3078, 3386, 3414],
    75: [381, 762, 1143, 1525, 1906, 2287, 2669, 3050, 3431, 3666, 3666, 3666],
    80: [483, 966, 1449, 1932, 2416, 2899, 3382, 3865, 4060, 4060, 4060, 4060],
}


def won(thousand):
    return thousand * 1000


def man(v_won):
    """원 → 「92.3만원」 꼴(만원 아래 한 자리, 반올림 없이 천원 단위 그대로)."""
    q, r = divmod(v_won, 10_000)
    if r == 0:
        return f"{q:,}만원"
    return f"{q:,}.{r // 1000}만원"


def eok_man(v_won):
    """원 → 「1억 5,168만원」 꼴(만원 미만 버림)."""
    m = v_won // 10_000
    e, rest = divmod(m, 10_000)
    if e and rest:
        return f"{e}억 {rest:,}만원"
    if e:
        return f"{e}억원"
    return f"{rest:,}만원"


def eligible(age, notice_eok):
    return age >= AGE_MIN and notice_eok <= PRICE_CAP_EOK


def basis_price(price_eok):
    return min(price_eok, PRICE_CAP_EOK)


def monthly(age, price_eok):
    """월지급금(원). 표의 나이·억 단위 칸만 쓴다."""
    p = basis_price(price_eok)
    return won(WEB[age][PRICES.index(p)])


def init_fee(price_eok):
    return price_eok * 100_000_000 * int(INIT_FEE_PCT * 10) // 1000


def refund(fee, months_used):
    if months_used >= REFUND_MONTHS:
        return 0
    return fee * (REFUND_MONTHS - months_used) // REFUND_MONTHS


def check_same():
    n = sum(1 for a in AGES for i in range(12) if WEB[a][i] == EXCEL[a][i])
    return n, len(AGES) * 12


def table1():
    cols = [3, 5, 7, 9, 12]
    print("표: 부부 중 젊은 사람 나이·주택 시세별 월지급금(종신지급방식 정액형, 일반주택)")
    print("| 나이 | " + " | ".join(f"{c}억원" for c in cols) + " |")
    print("|---|" + "---|" * len(cols))
    for a in AGES:
        print(f"| {a}세 | " + " | ".join(man(monthly(a, c)) for c in cols) + " |")
    print()


def table2():
    cases = [
        ("A: 65세 · 시세 5억원 · 공시가격 3.5억원", 65, 5, 3.5),
        ("B: 70세 · 시세 3억원 · 공시가격 2.1억원", 70, 3, 2.1),
        ("C: 75세 · 시세 15억원 · 공시가격 10.5억원", 75, 15, 10.5),
        ("D: 62세 · 1주택 시세 18억원 · 공시가격 13억원", 62, 18, 13),
    ]
    print("표: 네 가구에 대입한 가입 가능 여부와 받는 돈(정액형, 이자·보증료 제외 단순 합계)")
    print("| 가구 | 가입 | 산정 가격 | 월지급금 | 1년 합계 | 10년 합계 |")
    print("|---|---|---|---|---|---|")
    for name, a, p, n in cases:
        ok = eligible(a, n)
        if not ok:
            print(f"| {name} | 안 됨(공시가격 12억원 초과) | - | - | - | - |")
            continue
        m = monthly(a, p)
        print(f"| {name} | 됨 | {basis_price(p)}억원 | {man(m)} | {man(m * 12)} | {eok_man(m * 120)} |")
    print()


def table3():
    cols = [8, 9, 10, 11, 12]
    print("표: 시세가 올라도 월지급금이 더 늘지 않는 칸(종신지급방식 정액형, 일반주택)")
    print("| 나이 | " + " | ".join(f"{c}억원" for c in cols) + " |")
    print("|---|" + "---|" * len(cols))
    for a in [70, 75, 80]:
        print(f"| {a}세 | " + " | ".join(man(monthly(a, c)) for c in cols) + " |")
    print()
    for a in [70, 75, 80]:
        row = WEB[a]
        first = next((i + 1 for i in range(11) if row[i] == row[-1]), None)
        print(f"- {a}세: 12억원 칸 {man(won(row[-1]))}, 같은 금액이 시작되는 칸 {first}억원" if first
              else f"- {a}세: 11억원 → 12억원 증가 {man(won(row[-1] - row[-2]))}")
    print()


def table4():
    p = 5
    fee = init_fee(p)
    print(f"표: 시세 5억원 주택 초기보증료 {man(fee)}을 낸 뒤 대출금을 모두 갚고 해지할 때 환급(월 단위 비례 가정)")
    print("| 해지 시점(최초 연금 실행일부터) | 돌려받는 초기보증료 | 못 돌려받는 몫 |")
    print("|---|---|---|")
    print(f"| 30일 안 보증약정 철회 | {man(fee)}(전액) | 0원 |")
    for mo in [12, 24, 36, 48, 60]:
        r = refund(fee, mo)
        print(f"| {mo // 12}년 | {man(r) if r else '0원'} | {man(fee - r)} |")
    print()


def main():
    n, tot = check_same()
    print(f"# 기준일 2026-10-05 · 화면 표와 엑셀 일람표 일치 {n}/{tot}칸")
    print(f"# 초기보증료 {INIT_FEE_PCT}% · 연보증료 {ANNUAL_FEE_PCT}% · 가입 {AGE_MIN}세 · {PRICE_CAP_EOK}억원")
    print()
    table1()
    table2()
    table3()
    table4()
    # 본문 문장에 쓰는 계산값
    print("본문 숫자:")
    print(f"- 70세 3억원 월지급금 {man(monthly(70, 3))} (원문 예시 문장과 같음)")
    print(f"- 65세 5억원 1년 {man(monthly(65, 5) * 12)} · 한 달 {man(monthly(65, 5))}")
    print(f"- 55세와 80세 12억원 차이 {man(monthly(80, 12) - monthly(55, 12))}")
    print(f"- 55세 → 60세 5억원 증가 {man(monthly(60, 5) - monthly(55, 5))}")
    print(f"- 70세 11억원 → 12억원 증가 {man(monthly(70, 12) - monthly(70, 11))}")
    print(f"- 75세 9억원 → 10억원 증가 {man(monthly(75, 10) - monthly(75, 9))}")
    print(f"- 초기보증료 3억원 {man(init_fee(3))} · 5억원 {man(init_fee(5))} · 12억원 {man(init_fee(12))}")
    print(f"- 연보증료 예: 보증잔액 1억원이면 1년 {man(100_000_000 * 95 // 10_000)}")


if __name__ == "__main__":
    main()
