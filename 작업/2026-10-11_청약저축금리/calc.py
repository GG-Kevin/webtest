#!/usr/bin/env python3
"""주택청약종합저축 금리·이자 계산 (B1011-2/2) — 표준 라이브러리만, 분수(Fraction)로 계산한 뒤 원 미만 버림.

입력(표마다 고정 예시, 가정은 원고 표 이름과 본문에 적는다):
  m   매월 같은 날 넣는 금액(원) · n  가입일부터 해지일까지 개월 수(= 납입 횟수, 가입일에 1회차를 넣고 매월 1회)
공식:
  약정이율(저축기간 = 가입일부터 해지일까지):
      1개월 이내 무이자 · 1개월 초과 1년 미만 연 2.3% · 1년 이상 2년 미만 연 2.8% · 2년 이상 연 3.1%
      (2년 이상 ~ 10년 이내 3.1%, 10년 초과 시부터 3.1%) — 세금공제 전, 단리식
      주택도시기금 주택청약종합저축상품 안내  https://nhuf.molit.go.kr/FP/FP07/FP0701/FP07010101.jsp
      같은 상품 자주하는질문(해지 시 이율 적용)  https://nhuf.molit.go.kr/FP/FP07/FP0701/FP07010102.jsp
      청년 주택드림 청약통장 상품 안내(두 통장 이율 비교표, 「세금공제 전, 단리식」, 상품기준일 2026.6.30)
                                               https://nhuf.molit.go.kr/FP/FP07/FP0701/FP07010301.jsp
  이자(세전, 월 단위 근사) = m × 이율 × (n + (n−1) + … + 1) ÷ 12 = m × 이율 × n(n+1)/2 ÷ 12  (원 미만 버림)
      — k회차 돈은 해지일까지 (n−k+1)개월 머문다. 은행은 날짜(일) 단위로 계산하므로 몇십 원 차이가 날 수 있다.
  이자소득세 = 이자 × 14%(원 미만 버림)   소득세법 제129조 ①1호 라목(법률 제21221호, 시행 2026. 1. 1.)
      https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280405&joNo=0129&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  지방소득세 = 소득세 × 10%(원 미만 버림)  지방세법 제103조의13 ①(법률 제21308호, 시행 2026. 1. 1.)
      https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=282559&joNo=0103&joBrNo=13&docCls=jo&urlMode=lsScJoRltInfoR
  비과세종합저축(65세 이상 기초연금 수급자·등록 장애인 등, 원금 5천만원 이하) = 이자 소득세 없음
      조세특례제한법 제88조의2 ①
      https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=284389&joNo=0088&joBrNo=02&docCls=jo&urlMode=lsScJoRltInfoR
  국민주택 청약 저축총액 = Σ min(월납입금, 25만원)   주택공급에 관한 규칙 제10조 ⑤1호
      https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=286965&joNo=0010&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  청년 주택드림 청약통장 = 2년 이상이면 연 4.5%(가입일부터 10년 이내 무주택 기간, 원금 5,000만원 한도),
      요건을 갖추면 이자 500만원까지 비과세(원금 연 600만원 한도) — 같은 화면
기준일: 2026-10-06(KST) 원문 기준. 같은 입력이면 같은 출력. 실행하면 원고에 넣을 표를 마크다운으로 찍는다.
"""
from fractions import Fraction as F

R0 = F(0)
R1 = F(23, 1000)   # 1개월 초과 1년 미만
R2 = F(28, 1000)   # 1년 이상 2년 미만
R3 = F(31, 1000)   # 2년 이상
R_YOUTH = F(45, 1000)  # 청년 주택드림 2년 이상
TAX = F(14, 100)
LOCAL = F(10, 100)
CAP_RECOG = 250_000     # 국민주택 회차당 인정 상한
MONTH_MAX = 500_000     # 월 납입 상한(잔액 1,500만원 미만이면 초과 일시예치 가능)
LUMP_MAX = 15_000_000


def rate_for(n):
    """가입일부터 해지일까지 n개월 → 약정이율."""
    if n <= 1:
        return R0
    if n < 12:
        return R1
    if n < 24:
        return R2
    return R3


def interest(m, n, r=None):
    r = rate_for(n) if r is None else r
    return int(m * r * F(n * (n + 1), 2) / 12)


def taxes(i):
    inc = int(i * TAX)
    loc = int(inc * LOCAL)
    return inc, loc


def net(i):
    inc, loc = taxes(i)
    return i - inc - loc


def pct(r):
    return f"{float(r * 100):.1f}%"


def won(x):
    return f"{x:,}원"


def table_rates():
    print("표: 저축기간별 약정이율과 100만원을 1년 두었을 때의 이자(세전, 단리)")
    print("| 가입일부터 해지일까지 | 약정이율(연) | 100만원 1년치 이자(세전) | 한 달로 나누면 |")
    print("|---|---|---|---|")
    rows = [("1개월 이내", R0), ("1개월 초과 1년 미만", R1), ("1년 이상 2년 미만", R2), ("2년 이상(10년 넘어도 같음)", R3)]
    for label, r in rows:
        y = int(1_000_000 * r)
        if r == 0:
            print(f"| {label} | 무이자 | 0원 | 0원 |")
        else:
            print(f"| {label} | {pct(r)} | {won(y)} | 약 {round(y / 12):,}원 |")
    print()


NS = [11, 12, 23, 24, 36, 60]


def table_monthly(m=100_000):
    print(f"표: 월 {m // 10_000}만원씩 넣고 해지할 때 이자 직접 계산(매월 같은 날 납입, 단리 월 단위 근사, 이자소득세 15.4%)")
    print("| 해지 시점(넣은 돈) | 적용 이율 | 세전 이자 | 세금 15.4% | 세후 이자 |")
    print("|---|---|---|---|---|")
    out = {}
    for n in NS:
        i = interest(m, n)
        inc, loc = taxes(i)
        out[n] = (i, inc + loc, i - inc - loc)
        print(f"| {n}개월({won(m * n)}) | {pct(rate_for(n))} | {won(i)} | {won(inc + loc)} | {won(i - inc - loc)} |")
    print()
    return out


AMTS = [20_000, 100_000, 250_000, 500_000]


def table_amounts(n=24):
    print(f"표: 월 납입액별 {n}개월 이자와 국민주택 청약에 인정되는 저축총액(매월 같은 날 납입, 단리 월 단위 근사, 세금 떼기 전)")
    print("| 월 납입액 | 넣은 돈 | 세전 이자(연 3.1%) | 국민주택 청약 인정 저축총액 |")
    print("|---|---|---|---|")
    out = {}
    for m in AMTS:
        i = interest(m, n)
        rec = min(m, CAP_RECOG) * n
        out[m] = (i, net(i), rec)
        print(f"| {won(m)} | {won(m * n)} | {won(i)} | {won(rec)} |")
    print()
    return out


def table_youth(m=100_000, n=24):
    print(f"표: 월 {m // 10_000}만원 {n}개월 — 통장 종류와 과세 여부에 따른 이자 비교(단리 월 단위 근사)")
    print("| 경우 | 적용 이율 | 세전 이자 | 세후 이자 |")
    print("|---|---|---|---|")
    g = interest(m, n)
    y = interest(m, n, R_YOUTH)
    rows = [("주택청약종합저축(일반 과세)", R3, g, net(g)),
            ("주택청약종합저축을 비과세종합저축으로(대상자만)", R3, g, g),
            ("청년 주택드림 청약통장(비과세 요건 충족)", R_YOUTH, y, y),
            ("청년 주택드림 청약통장(비과세 요건 미충족)", R_YOUTH, y, net(y))]
    for label, r, a, b in rows:
        print(f"| {label} | {pct(r)} | {won(a)} | {won(b)} |")
    print()
    return {"g": g, "g_net": net(g), "y": y, "y_net": net(y)}


def main():
    print("# 주택청약종합저축 금리·이자 계산 (2026-10-06 원문 기준)\n")
    table_rates()
    mon = table_monthly()
    table_amounts()
    yo = table_youth()
    print("본문 숫자")
    i23, _, n23 = mon[23]
    i24, t24, n24 = mon[24]
    print(f"- 23개월 해지 세전 {i23:,}원 · 24개월 해지 세전 {i24:,}원 · 차이 {i24 - i23:,}원(넣은 돈 차이 100,000원)")
    print(f"- 24개월 세후 {n24:,}원 · 세금 {t24:,}원 · 한 달 평균 세후 약 {n24 // 24:,}원")
    i60, t60, n60 = mon[60]
    print(f"- 60개월 세전 {i60:,}원 · 세후 {n60:,}원 · 원금 6,000,000원")
    # 23개월째 해지할 돈을 한 달 더 두면(추가 납입 없이): 23회 납입, 24개월째 해지
    hold = int(100_000 * R3 * F(sum(range(2, 25)), 1) / 12)
    print(f"- 23회 넣고 24개월째 해지(마지막 달 추가 납입 없음) 세전 {hold:,}원 · 23개월 해지보다 {hold - i23:,}원 많음")
    lump = int(LUMP_MAX * R3)
    print(f"- 1,500만원을 2년 넘게 둔 통장의 1년치 이자(세전) {lump:,}원 · 세후 {net(lump):,}원 · 한 달 약 {net(lump) // 12:,}원")
    print(f"- 청년 주택드림 비과세 세전=세후 {yo['y']:,}원 · 일반 세후 {yo['g_net']:,}원 · 차이 {yo['y'] - yo['g_net']:,}원")
    print(f"- 1개월 이내 해지 이자 {interest(100_000, 1):,}원")


if __name__ == "__main__":
    main()
