from fractions import Fraction
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""퇴직연금 수령 방법별 세금 비교 — B1005-2/1 (2026-10-05 게시 예정, 기준일 2026-10-03)

입력(가정)
  - 퇴직급여 1억·3억·5억원, 근속연수 20년, 비과세 소득 0원
  - 퇴직급여 전액을 IRP(개인형퇴직연금) 계좌로 받아 과세이연(소득세법 제146조 제2항)
  - 연금은 해마다 같은 금액을 나눠 받고, 계좌 운용수익은 0원으로 둔다(이연퇴직소득만 계산)

공식
  1) 퇴직소득세(일시금, 소득세법 제48조·제55조 — 공제표·세율표는 조문에 그림으로 실려 있어
     국세청 「퇴직소득세 계산방법 및 계산사례」 쪽의 글자 표로 읽었다)
     근속연수공제: 5년 이하 100만×n / 10년 이하 500만+(n-5)×200만 / 20년 이하 1,500만+(n-10)×250만 / 초과 4,000만+(n-20)×300만
     환산급여 = (퇴직소득금액 - 근속연수공제) × 12 ÷ 근속연수
     환산급여공제: 800만 이하 전액 / 7,000만 이하 800만+(초과)×60% / 1억 이하 4,520만+(초과)×55%
                   / 3억 이하 6,170만+(초과)×45% / 초과 1억5,170만+(초과)×35%
     과세표준 = 환산급여 - 환산급여공제 → 기본세율(과세표준 × 세율 - 누진공제) → ÷ 12 × 근속연수
     국세청 계산 사례(근속 20년·1억원 → 산출세액 1,120천원)와 맞는지 아래에서 검산한다.
  2) 연금으로 받을 때(소득세법 제129조 제1항 제5호의3, 시행 2026.1.1.)
     연금 실제 수령연차 10년 이하 70% · 10년 초과 20년 이하 60% · 20년 초과 50%
     해마다 원천징수 = 그해 연금 × (이연퇴직소득세 ÷ 이연퇴직소득) × 비율
  3) 지방소득세 = 소득세의 100분의 10(지방세법 제103조의13 제1항)
  4) 연금수령한도(소득세법 시행령 제40조의2 제3항 제3호 계산식 — 조문 본문에 수식 그림으로 실림)
     = 연금계좌 평가액 ÷ (11 - 연금수령연차) × 120/100, 연금수령연차 11년 이상은 한도 없음(같은 조 제4항)
     기산연차: 보통 1년차, 2013년 3월 1일 전 가입 계좌(그 전 DB 가입자가 퇴직해 전액을 새 계좌로 옮긴 경우 포함) 6년차
  5) 운용수익·세액공제분 연금수령 세율(제129조 제1항 제5호의2, 국세청 연금소득 원천징수 방법 쪽):
     70세 미만 5% · 70세 이상 80세 미만 4% · 80세 이상 3% · 종신계약 3%(2026.1.1. 이후 연금수령분)

원문 URL(2026-10-03 열어 확인)
  - 소득세법 제129조 본문: https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280405&joNo=0129&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  - 소득세법 제146조 본문: https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280405&joNo=0146&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  - 소득세법 시행령 제40조의2 본문: https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=290841&joNo=0040&joBrNo=02&docCls=jo&urlMode=lsScJoRltInfoR
  - 지방세법 제103조의13 본문: https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=282559&joNo=0103&joBrNo=13&docCls=jo&urlMode=lsScJoRltInfoR
  - 국세청 퇴직소득세 계산방법: https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?mi=6444&cntntsId=7880
  - 국세청 연금소득 원천징수 방법: https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?mi=6452&cntntsId=7888
기준일: 2026-10-03. 같은 입력이면 같은 출력(난수·현재 시각 안 씀). 원 미만은 버린다.
"""
MAN = 10_000
EOK = 100_000_000
YEARS = 20                       # 근속연수(가정)
LOCAL = 0.10                     # 지방소득세 = 소득세의 10%
PAYS = [1 * EOK, 3 * EOK, 5 * EOK]
BRACKETS = [  # (상한, 세율, 누진공제) — 국세청 기본세율 표
    (14_000_000, 0.06, 0),
    (50_000_000, 0.15, 1_260_000),
    (88_000_000, 0.24, 5_760_000),
    (150_000_000, 0.35, 15_440_000),
    (300_000_000, 0.38, 19_940_000),
    (500_000_000, 0.40, 25_940_000),
    (1_000_000_000, 0.42, 35_940_000),
    (float("inf"), 0.45, 65_940_000),
]
PENSION_RATE = [(10, 0.70), (20, 0.60), (10**9, 0.50)]  # 실제 수령연차 상한, 비율


def service_ded(n):
    if n <= 5:
        return 1_000_000 * n
    if n <= 10:
        return 5_000_000 + (n - 5) * 2_000_000
    if n <= 20:
        return 15_000_000 + (n - 10) * 2_500_000
    return 40_000_000 + (n - 20) * 3_000_000


def conv_ded(c):
    if c <= 8_000_000:
        return c
    if c <= 70_000_000:
        return 8_000_000 + (c - 8_000_000) * 0.60
    if c <= 100_000_000:
        return 45_200_000 + (c - 70_000_000) * 0.55
    if c <= 300_000_000:
        return 61_700_000 + (c - 100_000_000) * 0.45
    return 151_700_000 + (c - 300_000_000) * 0.35


def basic_tax(base):
    for top, r, d in BRACKETS:
        if base <= top:
            return max(0.0, base * r - d)
    return 0.0


def retirement_tax(pay, n=YEARS):
    """퇴직소득세(소득세, 원 미만 버림)와 중간값"""
    sd = min(service_ded(n), pay)
    conv = (pay - sd) * 12 / n
    cd = conv_ded(conv)
    base = max(0.0, conv - cd)
    conv_tax = basic_tax(base)
    tax = int(conv_tax / 12 * n)
    return {"근속연수공제": int(sd), "환산급여": int(conv), "환산급여공제": int(cd),
            "과세표준": int(base), "환산산출세액": int(conv_tax), "퇴직소득세": tax}


def ratio_for_year(k):
    for top, r in PENSION_RATE:
        if k <= top:
            return r
    return PENSION_RATE[-1][1]


def pension_tax(pay, years, n=YEARS, local=False):
    """해마다 같은 금액을 받을 때 세금 합계(운용수익 0). 분수로 계산하고 합계에서 한 번만 원 미만 버림, local=True면 지방소득세(10%)를 더함"""
    t = retirement_tax(pay, n)["퇴직소득세"]
    per = Fraction(pay, years)
    total = Fraction(0)
    for k in range(1, years + 1):
        total += per * t / pay * Fraction(str(ratio_for_year(k)))
    if local:
        total += total * Fraction(str(LOCAL))
    return int(total)


def with_local(x):
    return int(x) + int(Fraction(int(x)) * Fraction(str(LOCAL)))


def limit(balance, year):
    """연금수령한도 — 연금수령연차 year(11 이상이면 None)"""
    if year >= 11:
        return None
    return int(balance / (11 - year) * 120 / 100)


def won(x):
    return f"{int(x):,}원"


def manwon(x):
    x = int(x)
    e, m = divmod(x, EOK)
    if e and m == 0:
        return f"{e}억원"
    if e:
        return f"{e}억 {m // MAN:,}만원"
    return f"{m // MAN:,}만원"


def main():
    # 검산: 국세청 계산 사례(근속 20년, 1억원 → 산출세액 1,120천원)
    chk = retirement_tax(1 * EOK)
    assert chk["퇴직소득세"] == 1_120_000, chk
    print("검산(국세청 사례 근속 20년·1억원): 산출세액", won(chk["퇴직소득세"]))
    print()

    print("표: 퇴직급여를 한 번에 받을 때의 퇴직소득세(근속 20년 가정 · 2026년 10월 3일 원문 기준 계산)")
    print("| 퇴직급여 | 근속연수공제 | 환산급여 | 과세표준 | 퇴직소득세 | 지방소득세 포함 | 받은 돈 대비 |")
    print("|---|---|---|---|---|---|---|")
    T = {}
    for p in PAYS:
        r = retirement_tax(p)
        T[p] = r["퇴직소득세"]
        tl = with_local(r["퇴직소득세"])
        print(f"| {manwon(p)} | {manwon(r['근속연수공제'])} | {won(r['환산급여'])} | {won(r['과세표준'])} | "
              f"{won(r['퇴직소득세'])} | {won(tl)} | {tl / p * 100:.2f}% |")
    print()

    print("표: 같은 퇴직급여를 일시금과 연금으로 받을 때 세금 합계(지방소득세 포함, 운용수익 0 · 계산 예시)")
    print("| 퇴직급여 | 일시금 | 10년 연금 | 20년 연금 | 30년 연금 | 10년 연금이 덜 내는 세금 |")
    print("|---|---|---|---|---|---|")
    P = {}
    for p in PAYS:
        lump = with_local(T[p])
        y10 = pension_tax(p, 10, local=True)
        y20 = pension_tax(p, 20, local=True)
        y30 = pension_tax(p, 30, local=True)
        P[p] = (lump, y10, y20, y30)
        print(f"| {manwon(p)} | {won(lump)} | {won(y10)} | {won(y20)} | {won(y30)} | {won(lump - y10)} |")
    print()

    print("일시금 세금 대비 비율(소득세 기준): 10년 연금",
          f"{pension_tax(3 * EOK, 10) / T[3 * EOK] * 100:.0f}%",
          "· 20년 연금", f"{pension_tax(3 * EOK, 20) / T[3 * EOK] * 100:.0f}%",
          "· 30년 연금", f"{pension_tax(3 * EOK, 30) / T[3 * EOK] * 100:.0f}%")
    print()

    # 한 달 단위로 풀기 — 3억원을 10년 연금으로
    p = 3 * EOK
    year_pay = p / 10
    eff = T[p] / p
    year_tax = with_local(int(year_pay * T[p] / p * 0.70))
    print("3억원 10년 연금: 해마다", manwon(year_pay), "· 한 달", manwon(year_pay / 12),
          "· 해마다 세금(지방소득세 포함)", won(year_tax), "· 한 달 약", won(year_tax / 12))
    print("3억원 실효세율(소득세, 일시금):", f"{eff * 100:.2f}%", "· 연금 1~10년차:", f"{eff * 0.7 * 100:.2f}%",
          "· 11~20년차:", f"{eff * 0.6 * 100:.2f}%", "· 21년차부터:", f"{eff * 0.5 * 100:.2f}%")
    print()

    print("표: 계좌 안 돈의 갈래별 세율(소득세 기준, 지방소득세는 그 10%가 더 붙음)")
    print("| 계좌 안 돈 | 연금으로 받을 때 | 한도 초과·55세 전 등 연금 밖으로 꺼낼 때 |")
    print("|---|---|---|")
    print("| 퇴직급여(이연퇴직소득), 실제 수령 1~10년차 | 퇴직소득세의 70% | 퇴직소득세 100% |")
    print("| 퇴직급여, 실제 수령 11~20년차 | 퇴직소득세의 60% | 퇴직소득세 100% |")
    print("| 퇴직급여, 실제 수령 21년차부터 | 퇴직소득세의 50% | 퇴직소득세 100% |")
    print("| 운용수익·세액공제 받은 납입금 | 70세 미만 5% · 70세 이상 80세 미만 4% · 80세 이상 3% | 기타소득 15% |")
    print()
    print("지방소득세 포함 연금소득세율:", " · ".join(f"{r}% → {r * (1 + LOCAL):.1f}%" for r in (5, 4, 3)))
    print()

    print("표: 연금수령한도 — 첫해와 한도가 사라지는 해(계좌 평가액 기준 · 계산 예시)")
    print("| 계좌 평가액 | 첫해 한도(기산 1년차) | 첫해 한도(기산 6년차) | 한도가 없어지는 해 |")
    print("|---|---|---|---|")
    for b in PAYS:
        print(f"| {manwon(b)} | {manwon(limit(b, 1))} | {manwon(limit(b, 6))} | 1년차 계좌 11년째 · 6년차 계좌 6년째 |")
    print()
    print("첫해 한도 비율: 기산 1년차", f"{limit(EOK, 1) / EOK * 100:.0f}%", "· 기산 6년차", f"{limit(EOK, 6) / EOK * 100:.0f}%")
    print("10년 균등 수령 첫해 금액 비율:", f"{1 / 10 * 100:.0f}%")


if __name__ == "__main__":
    main()
