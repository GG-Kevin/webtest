#!/usr/bin/env python3
"""전세보증보험(HUG 전세보증금반환보증) 가입 한도 · 보증료 · 반전세 환산 · 신청 기한 계산 (B1007-2/2)
표준 라이브러리만. 같은 입력이면 같은 출력. 실행하면 원고에 넣을 표 4개를 마크다운으로 찍는다.

입력(표마다 고정 예시 — 가정은 표 caption과 본문에 적는다):
  house_price   주택가격(원). 아파트는 KB·부동산원 시세, 연립·다세대·단독은 공시가격 × 140%
  public_price  공시가격(원) · senior  선순위채권(근저당 채권최고액 등, 원) · deposit  전세보증금(원)
  monthly_rent  월세(원) · days  전세계약기간(일, 2년 = 730일로 가정) · apt  아파트 여부
공식과 근거(2026-10-04 열람, 원고 기준일 2026-10-05):
  주택가액       = 주택가격 × 담보인정비율 90%
  보증 한도      = 주택가액 − 선순위채권 등  (가입 조건: 보증금 + 선순위 ≤ 주택가액)
  공시가격 환산  = 공시가격 × 140% (2022-12-31 이전 신청은 150%)
  선순위 제한    = 선순위채권 ≤ 주택가액 × 60% (단독·다중·다가구는 다른 세입자 보증금 포함 80%)
  보증금 상한    = 수도권 7억원 · 그 외 지역 5억원
  신청 기한      = 잔금일·전입신고일 중 늦은 날부터 전세계약기간의 1/2이 지나기 전(갱신은 갱신 계약기간의 1/2)
  보증료         = 보증금액 × 보증료율 × 전세계약기간/365, 원 미만 버림(버림은 이 글의 가정)
  부채비율       = (선순위채권 + 전세보증금) ÷ 주택가액 → 보증료율 표(보증금 구간 4 × 아파트/기타 × 70·80% 구간)
  할증           = 선순위채권 > 주택가액 50%이면 산출 보증료의 10%
  할인           = 연소득 5천만원 이하 60% · 신혼부부(합산 6천만원 이하·혼인 7년 이내) 40% (사회배려계층 중복 불가)
    HUG 전세보증금반환보증 상품안내 https://www.khug.or.kr/hug/web/ig/dr/igdr000001.jsp
  반전세 환산    = 전세보증금 + 월세 × 12 ÷ 전월세전환율 6.5% (2026-07-01 신청분부터, 종전 6.4%)
    HUG 공지 2026-06-24 https://khug.or.kr/hug/web/cs/no/csno000001.jsp?id=16&mode=S&currentPage=1&articleId=37801
  HF 일반전세지킴보증 = LTV (선순위 + 보증금) ÷ 주택가격 → 70% 이하 0.04% · 80% 이하 0.11% · 90% 이하 0.18%
                       보증료 = 보증금액 × 요율 ÷ 365 × 계약기간(윤년 366 — 이 글은 730일/365로 가정)
    한국주택금융공사 https://www.hf.go.kr/ko/sub02/sub02_05_01.do
  세액공제       = 보증료 × 12%, 보험료 합계 연 100만원 한도, 보증대상 임차보증금 3억원 이하
    소득세법 제59조의4① https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280405&joNo=0059&joBrNo=04&docCls=jo&urlMode=lsScJoRltInfoR
    소득세법 시행령 제118조의4②6 https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=290841&joNo=0118&joBrNo=04&docCls=jo&urlMode=lsScJoRltInfoR
"""
import datetime as dt
from fractions import Fraction as F

EOK = 100_000_000
MAN = 10_000

LTV = F(90, 100)                 # 담보인정비율 90%
PUBLIC_MULT = F(140, 100)        # 공시가격의 140%
SENIOR_CAP = F(60, 100)          # 선순위채권 ≤ 주택가액 60%
SURCHARGE_LINE = F(50, 100)      # 선순위 > 주택가액 50%면 할증
SURCHARGE = F(10, 100)           # 산출 보증료의 10%
CAP_METRO = 7 * EOK              # 수도권 7억원
CAP_OTHER = 5 * EOK              # 그 외 지역 5억원
CONV_RATE = F(65, 1000)          # 전월세전환율 6.5%
DISC_LOW_INCOME = F(60, 100)     # 기준소득 이하(연소득 5천만원 이하) 60%
DISC_NEWLYWED = F(40, 100)       # 신혼부부 40%
TAX_CREDIT = F(12, 100)          # 소득세법 제59조의4① 100분의 12
TAX_CAP = 100 * MAN              # 연 100만원
TAX_DEPOSIT_CAP = 3 * EOK        # 시행령 제118조의4②6 3억원
DAYS = 730                       # 2년 계약 가정

# HUG 보증료율(연 %, 소수 셋째 자리) — (보증금 상한, {아파트: (70%이하, 80%이하, 80%초과), 기타: (...)})
RATES = [
    (1 * EOK, {True: ("0.097", "0.117", "0.137"), False: ("0.111", "0.142", "0.172")}),
    (2 * EOK, {True: ("0.102", "0.124", "0.146"), False: ("0.117", "0.151", "0.184")}),
    (5 * EOK, {True: ("0.107", "0.131", "0.154"), False: ("0.124", "0.161", "0.197")}),
    (None,    {True: ("0.113", "0.138", "0.164"), False: ("0.132", "0.172", "0.211")}),
]
HF_RATES = [(F(70, 100), "0.04"), (F(80, 100), "0.11"), (F(90, 100), "0.18")]


def won(x):
    return f"{int(x):,}원"


def eok(x):
    """1억 2,000만원 꼴(만원 미만 버림)."""
    x = int(x)
    e, r = divmod(x // MAN, 10_000)
    if e and r:
        return f"{e}억 {r:,}만원"
    if e:
        return f"{e}억원"
    return f"{r:,}만원"


def pct(fr, nd=1):
    return f"{float(fr * 100):.{nd}f}%"


def house_value(price):
    return price * LTV


def limit(price, senior=0):
    return house_value(price) - senior


def hug_rate(deposit, ratio, apt):
    for cap, tbl in RATES:
        if cap is None or deposit <= cap:
            row = tbl[apt]
            break
    if ratio <= F(70, 100):
        return row[0]
    if ratio <= F(80, 100):
        return row[1]
    return row[2]


def hug_fee(price, deposit, senior=0, apt=True, days=DAYS):
    hv = house_value(price)
    ratio = F(senior + deposit) / hv
    r = hug_rate(deposit, ratio, apt)
    fee = F(deposit) * F(r) / 100 * days / 365
    sur = senior > hv * SURCHARGE_LINE
    if sur:
        fee = fee * (1 + SURCHARGE)
    ok = senior + deposit <= hv and senior <= hv * SENIOR_CAP
    return {"hv": hv, "ratio": ratio, "rate": r, "fee": int(fee), "sur": sur, "ok": ok}


def hf_fee(price, deposit, senior=0, days=DAYS):
    ltv = F(senior + deposit) / price
    r = next((x for cap, x in HF_RATES if ltv <= cap), None)
    if r is None:
        return {"ltv": ltv, "rate": None, "fee": None}
    return {"ltv": ltv, "rate": r, "fee": int(F(deposit) * F(r) / 100 / 365 * days)}


def converted(deposit, rent):
    return int(deposit + F(rent * 12) / CONV_RATE)


def deadline(balance_day, move_in_day, months):
    """늦은 날 + 계약기간 절반(개월). 이 날이 되기 전까지 신청."""
    base = max(balance_day, move_in_day)
    half = months // 2
    y, m = divmod(base.month - 1 + half, 12)
    return base, dt.date(base.year + y, m + 1, base.day)


def tax_credit(fee, deposit):
    if deposit > TAX_DEPOSIT_CAP:
        return 0
    return int(F(min(fee, TAX_CAP)) * TAX_CREDIT)


def main():
    # 표 1 — 주택가격으로 보는 최대 보증금(선순위 0)
    print("표: 주택가격으로 본 전세보증금 최대치(선순위채권이 없을 때, 2026년 10월 5일 HUG 기준)")
    print("| 집 | 주택가격 | 주택가액(90%) | 보증금 최대 |")
    print("|---|---|---|---|")
    T1 = [("빌라 공시가격 1억5천만원", int(F(15000 * MAN) * PUBLIC_MULT)),
          ("빌라 공시가격 2억원", int(F(2 * EOK) * PUBLIC_MULT)),
          ("빌라 공시가격 2억5천만원", int(F(25000 * MAN) * PUBLIC_MULT)),
          ("아파트 시세 3억원", 3 * EOK),
          ("아파트 시세 4억5천만원", 45000 * MAN)]
    for name, price in T1:
        print(f"| {name} | {eok(price)} | {eok(house_value(price))} | {eok(limit(price))} |")
    print(f"\n공시가격 기준 배수 = {int(PUBLIC_MULT*100)}% × {int(LTV*100)}% = {int(PUBLIC_MULT*LTV*100)}%")

    # 표 2 — 반전세 환산
    print("\n표: 월세가 낀 계약의 환산 보증금(전월세전환율 6.5%, 2026년 7월 1일 신청분부터)")
    print("| 보증금 + 월세 | 월세 환산분 | 환산 보증금 | 상한(수도권 7억 · 그 외 5억) |")
    print("|---|---|---|---|")
    for d, r in [(2 * EOK, 100 * MAN), (3 * EOK, 120 * MAN), (4 * EOK, 150 * MAN)]:
        c = converted(d, r)
        part = c - d
        verdict = ("어디서나 상한 안" if c <= CAP_OTHER else ("수도권만 상한 안" if c <= CAP_METRO else "어디서나 상한 넘음"))
        print(f"| {eok(d)} + 월 {r // MAN}만원 | {eok(part)} | {eok(c)} | {verdict} |")

    # 표 3 — 보증료 직접 계산(2년)
    print("\n표: HUG 보증료 직접 계산(2년 = 730일, 할인 전, 보증금 전액 가입 가정)")
    print("| 경우 | 부채비율 · 요율 | 2년 보증료 | 한 달로 |")
    print("|---|---|---|---|")
    T3 = [
        ("A 아파트 시세 3억 · 보증금 2억", 3 * EOK, 2 * EOK, 0, True),
        ("B 아파트 시세 4억5천 · 보증금 3억", 45000 * MAN, 3 * EOK, 0, True),
        ("C 아파트 시세 4억5천 · 근저당 1억 · 보증금 2억5천", 45000 * MAN, 25000 * MAN, 1 * EOK, True),
        ("D 빌라 공시 2억5천 · 보증금 3억", int(F(25000 * MAN) * PUBLIC_MULT), 3 * EOK, 0, False),
        ("E 빌라 공시 2억 · 근저당 1억4천 · 보증금 1억", int(F(2 * EOK) * PUBLIC_MULT), 1 * EOK, 14000 * MAN, False),
    ]
    res = {}
    for name, price, dep, sen, apt in T3:
        f = hug_fee(price, dep, sen, apt)
        res[name[0]] = (price, dep, sen, apt, f)
        tag = " · 할증 10%" if f["sur"] else ""
        print(f"| {name} | {pct(f['ratio'])} · 연 {f['rate']}%{tag} | {won(f['fee'])} | 약 {won(f['fee'] // 24)} |")
    print(f"  B−C 보증료 차이 = {won(res['B'][4]['fee'] - res['C'][4]['fee'])} · 보증금 차이 = {eok(res['B'][1] - res['C'][1])}")
    hvE = res["E"][4]["hv"]
    print(f"  E: 주택가액 50% = {eok(hvE * SURCHARGE_LINE)} · 60% = {eok(hvE * SENIOR_CAP)} · 근저당 {eok(res['E'][2])}")
    print(f"  요율 범위 = 연 {RATES[0][1][True][0]}% ~ 연 {RATES[3][1][False][2]}% · 칸 수 {sum(6 for _ in RATES)}")
    print(f"  월세 1만원 환산 = {won(F(MAN * 12) / CONV_RATE)} · 월세 120만원 1년 = {eok(120 * MAN * 12)}")
    print(f"  원문 예시: 주택가격 1억 → 한도 {eok(limit(1 * EOK))} · 선순위 5,500만원 > 60%선 {eok(house_value(1 * EOK) * SENIOR_CAP)}")
    for k, (price, dep, sen, apt, f) in res.items():
        print(f"  {k}: 주택가액 {won(f['hv'])} · 가입 조건 충족 {f['ok']} · 1년분 {won(F(dep) * F(f['rate']) / 100)}")

    # 표 4 — 같은 보증금 2억(경우 A)에서 달라지는 금액
    fa = res["A"][4]["fee"]
    hf = hf_fee(3 * EOK, 2 * EOK, 0)
    print("\n표: 보증금 2억원 아파트(경우 A) 2년 보증료가 달라지는 경우")
    print("| 경우 | 2년 보증료 | 원문 조건 |")
    print("|---|---|---|")
    print(f"| HUG 할인 없음 | {won(fa)} | 연 0.124% |")
    print(f"| HUG 연소득 5천만원 이하 할인 60% | {won(F(fa) * (1 - DISC_LOW_INCOME))} | 배우자 포함 연소득 |")
    print(f"| HUG 신혼부부 할인 40% | {won(F(fa) * (1 - DISC_NEWLYWED))} | 합산 6천만원 이하 · 혼인 7년 이내 |")
    print(f"| HF 일반전세지킴보증 | {won(hf['fee'])} | LTV {pct(hf['ltv'])} → 연 {hf['rate']}% · HF 전세자금보증 이용자 |")
    print(f"\n세액공제(경우 A를 한 해에 냈다면) = {won(fa)} × 12% = {won(tax_credit(fa, 2 * EOK))}")
    print(f"HF ÷ HUG = {float(F(hf['fee'], fa)):.3f}")
    print(f"세액공제(신혼부부 할인 뒤) = {won(tax_credit(int(F(fa) * (1 - DISC_NEWLYWED)), 2 * EOK))}")

    # 신청 기한 예시
    b, end = deadline(dt.date(2026, 11, 13), dt.date(2026, 11, 16), 24)
    _, end1 = deadline(dt.date(2026, 11, 13), dt.date(2026, 11, 16), 12)
    print(f"\n신청 기한 예: 잔금 2026-11-13 · 전입 2026-11-16 → 늦은 날 {b} → 2년 계약이면 {end} 전 · 1년 계약이면 {end1} 전")


if __name__ == "__main__":
    main()
