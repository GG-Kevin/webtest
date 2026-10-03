#!/usr/bin/env python3
"""주택청약 해지 — 잃는 1순위 조건 · 다시 가입했을 때 1순위가 돌아오는 달 · 해지 시점별 원금·세전 이자(근사)·소득공제 추징세액
· 세율 구간별 실제 감면세액과 추징세액 (표준 라이브러리만)

원문(모두 2026-10-03에 직접 열어 읽음):
  - 주택공급에 관한 규칙 [시행 2026. 6. 15.] 국토교통부령 제1592호
      제27조(국민주택의 일반공급) ① 1호 가목 수도권 「1년이 지난 자로서 … 12회 이상」(시·도지사 24개월·24회까지 연장 가능)
        나목 수도권 외 「6개월 … 6회 이상」(12개월·12회까지 연장 가능) · 다목 투기과열지구·청약과열지역 「2년 … 24회 이상」+세대주
        라목 위축지역 「1개월이 지난 자」 · ② 40㎡ 초과 = 저축총액 많은 순, 40㎡ 이하 = 납입횟수 많은 순
        https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=286965&joNo=0027&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
      제28조(민영주택의 일반공급) ① 수도권 「1년이 지나고 별표 2의 예치기준금액」 · 수도권 외 6개월 · 투기과열 2년 · 위축 1개월
        ⑦ 가점이 같으면 「주택청약종합저축 가입기간이 긴 사람」
        https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=286965&joNo=0028&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
      제10조 ⑤ 1호 「월납입금이 25만원을 초과한 경우: 해당 월납입금을 25만원으로 산정」 · ④ 3호 옛 청약저축만 해지 즉시 옮기면 횟수 합산
        https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=286965&joNo=0010&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  - 조세특례제한법 [시행 2026. 9. 18.] 제87조 ② 총급여 7천만원 이하 무주택 세대주등, 연 300만원 한도 납입액의 100분의 40 소득공제(2028-12-31까지)
        ② 단서: 주택 당첨 등 외의 사유로 과세기간 중 중도해지하면 그해 납입액은 공제 안 함
        ⑦ 소득공제를 받은 사람이 가입일부터 5년 이내 해지 → 공제 적용 과세기간 이후 납입액(연 300만원 한도) 누계 × 100분의 6 추징
           단서: 실제 감면세액이 추징세액에 미달함을 증명하면 실제 감면세액만 추징 · 2호 국민주택규모 초과 주택 당첨도 추징
        https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=284389&joNo=0087&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  - 조세특례제한법 시행령 제81조 ⑪ 추징 제외 사유(국민주택규모 당첨, 해지 전 6개월 안의 퇴직·폐업·3개월 이상 입원 등) · ⑫ 특별해지사유신고서
        https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=288915&joNo=0081&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  - 주택도시기금 주택청약종합저축 상품안내(약정이율: 1개월 이내 무이자 · 1개월 초과~1년 미만 연 2.3% · 1년 이상~2년 미만 연 2.8%
        · 2년 이상~10년 이내 연 3.1%, 「가입일로부터 해지일까지 저축기간에 따라 적용」 · 별표 2 예치기준금액 표 · 추징 「누계액의 6%」)
        https://nhuf.molit.go.kr/FP/FP07/FP0701/FP07010101.jsp
  - 주택도시기금 청년 주택드림 청약통장 상품안내(2년 이상 연 4.5%, 2년 미만 해지 시 일반 이율, 상품기준일 2026.6.30)
        https://nhuf.molit.go.kr/FP/FP07/FP0701/FP07010301.jsp
  - 국세청 종합소득세 세율(2023~2025년 귀속): 1,400만원 이하 6% · 5,000만원 이하 15% · 8,800만원 이하 24%
        https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?mi=2227&cntntsId=7667
기준일: 2026-10-03 원문.

공식(정수 계산, 원 미만 버림은 마지막에 한 번):
  - 원금 = 월 납입액 × 납입 횟수
  - 세전 이자(근사) = Σ_{k=1..n} 월 납입액 × 이율 × (n-k+1)/12 = 월 납입액 × 이율 × n(n+1)/24
      가정: 매달 같은 날 넣고 n회째를 넣은 한 달 뒤 해지 · 이율은 저축기간(n개월) 구간 하나를 전 회차에 적용 · 월 단위 단리 근사
      (은행은 일 단위로 계산하므로 실제 이자와 몇백 원~몇천 원 다를 수 있다)
  - 추징세액 = 공제 적용 과세기간 이후 납입액 누계(연 300만원 한도) × 6/100, 가입일부터 5년이 지난 뒤 해지면 0
      가정: 1월에 가입해 해마다 공제를 받고, n회째를 넣은 해의 다음 해 1월에 해지(해지한 해 납입분 0)
  - 실제 감면세액(1년분) = min(연 납입액, 300만원) × 40/100 × 세율 (공제로 세율 구간이 바뀌지 않는다고 가정, 지방소득세 제외)
  - 1순위가 다시 생기는 달 = 다시 가입한 달 + 필요 개월 수(가입기간과 납입 횟수를 둘 다 채운 첫 달)
같은 입력이면 같은 출력이다. 원고 표의 숫자는 모두 이 출력에서 가져온다.
"""
from fractions import Fraction as F

# ---- 원문 숫자 ----
RANK1 = [  # (구분, 필요 개월, 국민주택 납입 횟수, 근거)
    ("수도권(투기과열·청약과열 아님)", 12, 12, "제27조①1가·제28조①1가"),
    ("수도권 외", 6, 6, "제27조①1나·제28조①1나"),
    ("투기과열지구·청약과열지역", 24, 24, "제27조①1다·제28조①1다"),
    ("위축지역", 1, 0, "제27조①1라·제28조①1라"),
]
MONTHLY_CAP = 250000          # 규칙 제10조⑤1 — 저축총액 산정 때 월 25만원까지
DEDUCT_LIMIT = 3000000        # 조특법 제87조② 연 300만원
DEDUCT_RATE = F(40, 100)      # 조특법 제87조② 100분의 40
CLAWBACK_RATE = F(6, 100)     # 조특법 제87조⑦ 100분의 6
CLAWBACK_YEARS = 5            # 조특법 제87조⑦1 가입일부터 5년 이내
YOUTH_RATE_2Y = F(45, 1000)   # 청년 주택드림 2년 이상
TAX_BRACKETS = [("1,400만원 이하", F(6, 100)), ("1,400만원 초과~5,000만원 이하", F(15, 100)), ("5,000만원 초과~8,800만원 이하", F(24, 100))]
REJOIN = (2026, 10)           # 다시 가입하는 달(가정): 2026년 10월


def rate_for(n):
    """저축기간 n개월(가입일~해지일)에 적용하는 이율"""
    if n <= 1:
        return F(0)
    if n < 12:
        return F(23, 1000)
    if n < 24:
        return F(28, 1000)
    return F(31, 1000)


def interest(monthly, n):
    r = rate_for(n)
    return int(monthly * r * n * (n + 1) / 24)  # 원 미만 버림


def clawback(monthly, n):
    years = (n + 11) // 12          # 납입한 해 수(1월 가입 가정) = 해지 때 가입 후 지난 햇수
    if years > CLAWBACK_YEARS:      # 가입일부터 5년이 지난 뒤 해지 → 추징 없음
        return 0
    base = sum(min(monthly * min(12, n - 12 * y), DEDUCT_LIMIT) for y in range(years))
    return int(base * CLAWBACK_RATE)


def add_months(ym, k):
    y, m = ym
    t = y * 12 + (m - 1) + k
    return t // 12, t % 12 + 1


def table_rank():
    out = ["| 지역 구분 | 1순위 가입기간 | 국민주택 납입 횟수 | 오늘 해지 뒤 2026년 10월에 다시 가입하면 1순위가 다시 생기는 달 | 근거(주택공급에 관한 규칙) |",
           "|---|---|---|---|---|"]
    for name, months, cnt, law in RANK1:
        y, m = add_months(REJOIN, months)
        cnt_s = f"{cnt}회 이상" if cnt else "조건 없음"
        out.append(f"| {name} | {months}개월 | {cnt_s} | {y}년 {m}월 | {law} |")
    return "\n".join(out)


CASES = [(100000, 12), (100000, 24), (100000, 48), (100000, 72), (250000, 12), (250000, 24), (250000, 48), (250000, 72)]


def table_cases():
    out = ["| 월 납입액 | 넣은 횟수 | 원금 | 적용 이율 | 세전 이자(근사) | 소득공제를 받았다면 추징세액 |",
           "|---|---|---|---|---|---|"]
    rows = []
    for monthly, n in CASES:
        r = rate_for(n)
        p = monthly * n
        it = interest(monthly, n)
        cb = clawback(monthly, n)
        rows.append((monthly, n, p, r, it, cb))
        cb_s = f"{cb:,}원" if cb else "0원(가입 5년 지남)"
        out.append(f"| {monthly // 10000}만원 | {n}회 | {p:,}원 | 연 {float(r * 100):.1f}% | {it:,}원 | {cb_s} |")
    return "\n".join(out), rows


def table_brackets(annual=DEDUCT_LIMIT):
    ded = min(annual, DEDUCT_LIMIT) * DEDUCT_RATE
    cb = int(min(annual, DEDUCT_LIMIT) * CLAWBACK_RATE)
    out = ["| 과세표준 구간 | 세율 | 소득공제 금액 | 실제로 줄어든 세금 | 5년 안 해지 때 추징세액(6%) | 증명하면 내는 금액 |",
           "|---|---|---|---|---|---|"]
    rows = []
    for name, r in TAX_BRACKETS:
        saved = int(ded * r)
        pay = min(saved, cb)
        rows.append((name, r, int(ded), saved, cb, pay))
        out.append(f"| {name} | {int(r * 100)}% | {int(ded):,}원 | {saved:,}원 | {cb:,}원 | {pay:,}원 |")
    return "\n".join(out), rows


def main():
    print("## 표 1 — 1순위 조건과 다시 가입했을 때 1순위가 생기는 달")
    print(table_rank())
    print()
    print("## 표 2 — 해지 시점별 원금·세전 이자(근사)·추징세액")
    t2, rows2 = table_cases()
    print(t2)
    print()
    print("## 표 3 — 연 300만원 넣고 소득공제 받은 1년분: 세율 구간별 실제 감면세액과 추징세액")
    t3, rows3 = table_brackets()
    print(t3)
    print()
    print("## 본문에 쓰는 숫자")
    print(f"소득공제 한도: 연 {DEDUCT_LIMIT:,}원 × {int(DEDUCT_RATE * 100)}% = {int(DEDUCT_LIMIT * DEDUCT_RATE):,}원")
    print(f"월 납입 인정 상한(국민주택 저축총액): {MONTHLY_CAP:,}원 × 12 = {MONTHLY_CAP * 12:,}원")
    print(f"추징 비율 {int(CLAWBACK_RATE * 100)}% ÷ 공제율 {int(DEDUCT_RATE * 100)}% = 세율 {float(CLAWBACK_RATE / DEDUCT_RATE * 100):.0f}%와 같은 효과")
    m10_12 = [r for r in rows2 if r[0] == 100000 and r[1] == 12][0]
    print(f"월 10만원 12회: 원금 {m10_12[2]:,}원 · 이자 {m10_12[4]:,}원 · 추징 {m10_12[5]:,}원 · 한 달로 약 {m10_12[5] // 12:,}원")
    m25_48 = [r for r in rows2 if r[0] == 250000 and r[1] == 48][0]
    print(f"월 25만원 48회: 원금 {m25_48[2]:,}원 · 이자 {m25_48[4]:,}원 · 추징 {m25_48[5]:,}원")
    youth_gap = F(45, 1000) - F(31, 1000)
    print(f"청년 주택드림 2년 이상 연 {float(YOUTH_RATE_2Y * 100):.1f}% vs 일반 연 3.1% → 차이 연 {float(youth_gap * 100):.1f}%p")
    gap6 = rows3[0][4] - rows3[0][3]
    print(f"6% 구간: 추징 {rows3[0][4]:,}원 - 실제 감면 {rows3[0][3]:,}원 = 증명하면 덜 내는 금액 {gap6:,}원")
    print(f"24% 구간: 실제 감면 {rows3[2][3]:,}원 - 추징 {rows3[2][4]:,}원 = {rows3[2][3] - rows3[2][4]:,}원은 남음")


if __name__ == "__main__":
    main()
