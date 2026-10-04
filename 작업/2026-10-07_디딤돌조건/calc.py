#!/usr/bin/env python3
"""디딤돌대출 조건·한도·월 상환액 계산 (B1007-2/1) — 표준 라이브러리만.

입력(표마다 고정 예시, 가정은 원고 표 아래에 적는다):
  appraisal  담보주택 평가액(원) · kind  대상 구분(일반·생애최초·2자녀 이상·신혼가구·미혼 단독)
  capital_area  수도권·규제지역 여부(생애최초 LTV를 가른다)
  principal  대출금(원) · rate  연 금리(%) · years  대출기간(년)
공식:
  대상별 소득·주택가격·한도·LTV = 주택도시기금 내집마련디딤돌대출 상품안내(일반대출 안내)
      https://nhuf.molit.go.kr/FP/FP05/FP0503/FP05030101.jsp
      소득: 부부합산 6천만원 이하 · 생애최초·다자녀·2자녀 7천만원 이하 · 신혼가구 8.5천만원 이하
      순자산: 5.11억원 이하(2026년도 기준, 2026-01-01 신규 접수분부터 — 공지 articleId=1298)
      주택: 전용 85㎡(수도권 밖 읍·면 100㎡) 이하, 평가액 5억원(신혼·2자녀 이상 6억원) 이하
      한도: 일반 2억 · 생애최초 2.4억 · 신혼·2자녀 이상 3.2억(25.6.28 이후 계약분, 공지 articleId=1289)
      LTV 70%(생애최초 80%, 수도권·규제지역 70%) · DTI 60%
      만 30세 이상 미혼 단독세대주: 60㎡(읍·면 70㎡) 이하, 평가액 3억원 이하, 한도 1.5억(생애최초 2억)
  한도 = min(대상 상한, 평가액 × LTV)  (선순위채권·임대보증금·최우선변제 소액임차보증금 차감 전,
         매매가격 = 평가액 가정 — 상품안내 「대출한도」 1~3)
  금리 = 소득구간 × 기간 표(상품안내 페이지가 불러오는 금리 자료)
      https://nhuf.molit.go.kr/init/include/NewBabyGetInform.jsp?newBabyGetBuySelect=newMearryHouse&productgb=F
      우대금리 적용 상한 0.5%p(다자녀 0.7%p), 최종금리 하한 연 1.5%
  월 상환액(원리금균등, 비거치) = P × r × (1+r)^n / ((1+r)^n − 1), r = 연 금리/12, n = 기간×12, 원 미만 버림
  총이자 = 월 상환액 × n − P (마지막 회차 끝수 조정은 무시)
  DTI 60% 안에 드는 최소 연소득 = 월 상환액 × 12 ÷ 0.6 (다른 대출이 없다고 가정), 만원 미만 올림
기준일: 2026-10-05 원문 기준(한국 시각에 열어 확인). 같은 입력이면 같은 출력.
실행하면 원고에 넣을 표를 마크다운으로 찍는다.
"""
from decimal import Decimal, getcontext, ROUND_FLOOR, ROUND_CEILING

getcontext().prec = 50
MAN = 10_000
EOK = 100_000_000

INCOME_CAP = {"일반": 60_000_000, "생애최초": 70_000_000, "2자녀 이상": 70_000_000,
              "신혼가구": 85_000_000, "미혼 단독(만 30세 이상)": 60_000_000}
PRICE_CAP = {"일반": 5 * EOK, "생애최초": 5 * EOK, "2자녀 이상": 6 * EOK,
             "신혼가구": 6 * EOK, "미혼 단독(만 30세 이상)": 3 * EOK}
LOAN_CAP = {"일반": 2 * EOK, "생애최초": 240_000_000, "2자녀 이상": 320_000_000,
            "신혼가구": 320_000_000, "미혼 단독(만 30세 이상)": 150_000_000}
LOAN_CAP_SINGLE_FIRST = 2 * EOK          # 미혼 단독세대주가 생애최초면 2억
OLD_LOAN_CAP = {"일반": 250_000_000, "생애최초": 3 * EOK, "2자녀 이상·신혼가구": 4 * EOK}  # 25.6.27 이전 계약
NET_ASSET_CAP = 511_000_000              # 2026년도 기준 5.11억원
NET_ASSET_OLD = 488_000_000              # 2025년 기준 4.88억원(공지 1298)
LTV = 70
LTV_FIRST = 80
DTI = 60
AREA, AREA_RURAL, AREA_SINGLE = 85, 100, 60
PREF_CAP = Decimal("0.5")                # 우대금리 적용 상한
RATE_FLOOR = Decimal("1.5")

# 소득구간 × 기간(10·15·20·30년) 금리(연 %, 2026-10-05 금리 자료)
TERMS = [10, 15, 20, 30]
RATE_TABLE = [
    ("2천만원 이하", ["2.85", "2.95", "3.05", "3.10"]),
    ("2천만원 초과 4천만원 이하", ["3.20", "3.30", "3.40", "3.45"]),
    ("4천만원 초과 7천만원 이하", ["3.55", "3.65", "3.75", "3.80"]),
    ("7천만원 초과 8.5천만원 이하", ["3.90", "4.00", "4.10", "4.15"]),
]


def won(v):
    return f"{int(v):,}원"


def eok(v):
    v = int(v)
    e, m = divmod(v, EOK)
    m //= MAN
    if e and m:
        return f"{e}억 {m:,}만원"
    if e:
        return f"{e}억원"
    return f"{m:,}만원"


def limit(kind, appraisal, capital_area):
    ltv = LTV
    if kind == "생애최초" and not capital_area:
        ltv = LTV_FIRST
    by_ltv = appraisal * ltv // 100
    cap = LOAN_CAP[kind]
    return {"ltv": ltv, "by_ltv": by_ltv, "cap": cap, "limit": min(cap, by_ltv)}


def monthly(principal, rate, years):
    p = Decimal(principal)
    r = Decimal(rate) / 100 / 12
    n = years * 12
    f = (1 + r) ** n
    m = (p * r * f / (f - 1)).to_integral_value(rounding=ROUND_FLOOR)
    return int(m)


def plan(principal, rate, years):
    m = monthly(principal, rate, years)
    n = years * 12
    interest = m * n - principal
    need = (Decimal(m * 12) * 100 / DTI / MAN).to_integral_value(rounding=ROUND_CEILING) * MAN
    return {"m": m, "interest": interest, "year": m * 12, "need": int(need)}


CASES = [  # (사례, 대상, 평가액, 수도권·규제지역)
    ("수도권 4억원 아파트 · 일반", "일반", 4 * EOK, True),
    ("지방 2억 5천만원 주택 · 일반", "일반", 250_000_000, False),
    ("지방 3억원 주택 · 생애최초", "생애최초", 3 * EOK, False),
    ("수도권 3억원 주택 · 생애최초", "생애최초", 3 * EOK, True),
    ("수도권 5억 5천만원 아파트 · 신혼가구", "신혼가구", 550_000_000, True),
    ("3억원 주택 · 만 30세 이상 미혼 단독", "미혼 단독(만 30세 이상)", 3 * EOK, True),
]

PAY_CASES = [  # (설명, 대출금, 금리 문자열, 기간)
    ("10년", 2 * EOK, "3.55", 10),
    ("15년", 2 * EOK, "3.65", 15),
    ("20년", 2 * EOK, "3.75", 20),
    ("30년", 2 * EOK, "3.80", 30),
]
PREF_YEARS = 5                           # 신혼·생애최초·청약 우대는 대출실행일부터 최대 5년
PREF_CASES = [  # (설명, 대출금, 기본 금리, 우대 합(%p), 기간)
    ("2억원 · 30년 · 신혼 0.2%p + 청약 5년 0.3%p", 2 * EOK, "3.80", "0.5", 30),
    ("3억 2,000만원 · 30년 · 신혼 소득 8천만원 · 신혼 0.2%p", 320_000_000, "4.15", "0.2", 30),
]


def balance_after(principal, rate, m, k):
    r = Decimal(rate) / 100 / 12
    f = (1 + r) ** k
    b = Decimal(principal) * f - Decimal(m) * (f - 1) / r
    return int(b.to_integral_value(rounding=ROUND_FLOOR))


def plan_pref(principal, base, pref, years):
    """처음 5년은 (기본 − 우대) 금리, 그 뒤 남은 원금을 기본 금리로 남은 기간에 다시 나눈다."""
    pref = min(Decimal(pref), PREF_CAP)
    low = max(Decimal(base) - pref, RATE_FLOOR)
    n, k = years * 12, PREF_YEARS * 12
    m1 = monthly(principal, low, years)
    bal = balance_after(principal, low, m1, k)
    m2 = monthly(bal, base, years - PREF_YEARS)
    total_int = m1 * k + m2 * (n - k) - principal
    return {"low": low, "m1": m1, "bal": bal, "m2": m2, "interest": total_int}


def main():
    print("표: 대상별 디딤돌대출 소득·주택가격·한도(2026년 10월 5일 상품안내)")
    print("| 대상 | 부부합산 연소득 | 주택 평가액 | 최대 한도 |")
    print("|---|---|---|---|")
    for k in INCOME_CAP:
        cap = eok(LOAN_CAP[k])
        if k.startswith("미혼"):
            cap += f"(생애최초 {eok(LOAN_CAP_SINGLE_FIRST)})"
        print(f"| {k} | {INCOME_CAP[k] // MAN:,}만원 이하 | {eok(PRICE_CAP[k])} 이하 | {cap} |")
    print()
    print(f"공통: 순자산 {eok(NET_ASSET_CAP)} 이하(전년 {eok(NET_ASSET_OLD)}) · 전용 {AREA}㎡(수도권 밖 읍·면 {AREA_RURAL}㎡) 이하 · "
          f"미혼 단독 {AREA_SINGLE}㎡ 이하 · LTV {LTV}%(생애최초 {LTV_FIRST}%) · DTI {DTI}%")
    print(f"순자산 기준 오른 폭: {eok(NET_ASSET_CAP - NET_ASSET_OLD)}")
    a = limit("생애최초", 3 * EOK, False)["limit"]
    b = limit("생애최초", 3 * EOK, True)["limit"]
    print(f"3억원 생애최초 지방 {eok(a)} − 수도권 {eok(b)} = {eok(a - b)}")
    print("25.6.27 이전 계약 한도: " + " · ".join(f"{k} {eok(v)}" for k, v in OLD_LOAN_CAP.items()))
    print()
    print("표: 집값과 대상으로 계산한 디딤돌대출 한도(방공제·선순위 차감 전)")
    print("| 사례 | 평가액 | LTV | LTV 금액 | 대상 상한 | 한도 |")
    print("|---|---|---|---|---|---|")
    for name, kind, ap, cap_area in CASES:
        r = limit(kind, ap, cap_area)
        print(f"| {name} | {eok(ap)} | {r['ltv']}% | {eok(r['by_ltv'])} | {eok(r['cap'])} | {eok(r['limit'])} |")
    print()
    print("표: 부부합산 연소득·대출기간별 디딤돌대출 기본 금리(연 %)")
    print("| 부부합산 연소득 | 10년 | 15년 | 20년 | 30년 |")
    print("|---|---|---|---|---|")
    for band, rates in RATE_TABLE:
        print(f"| {band} | " + " | ".join(f"{x}%" for x in rates) + " |")
    print()
    print(f"우대금리 적용 상한 {PREF_CAP}%p · 최종금리 하한 연 {RATE_FLOOR}%")
    print()
    print("표: 디딤돌대출 2억원을 원리금균등·비거치로 갚을 때(부부합산 연소득 4천만원 초과 7천만원 이하 금리)")
    print("| 기간 | 금리 | 월 상환액 | 총이자 | DTI 60% 최소 연소득 |")
    print("|---|---|---|---|---|")
    for name, p, rate, y in PAY_CASES:
        r = plan(p, rate, y)
        print(f"| {name} | {rate}% | {won(r['m'])} | {won(r['interest'])} | {eok(r['need'])} |")
    print()
    for name, p, rate, y in PAY_CASES:
        r = plan(p, rate, y)
        print(f"{eok(p)} {name}: 연 상환액 {won(r['year'])} · 한 달 약 {round(r['m'] / MAN)}만원 · 총이자 약 {eok(round(r['interest'] / MAN) * MAN)}")
    print()
    print("표: 우대금리가 처음 5년만 붙을 때 월 상환액(원리금균등·비거치)")
    print("| 가정 | 처음 5년 월 상환액 | 6년째부터 월 상환액 | 30년 총이자 |")
    print("|---|---|---|---|")
    for name, p, base, pref, y in PREF_CASES:
        r = plan_pref(p, base, pref, y)
        b0 = plan(p, base, y)
        print(f"| {name} | 연 {r['low']}% · {won(r['m1'])} | 연 {base}% · {won(r['m2'])} | {won(r['interest'])} |")
    print()
    for name, p, base, pref, y in PREF_CASES:
        r = plan_pref(p, base, pref, y)
        b0 = plan(p, base, y)
        print(f"{name}: 5년 뒤 남은 원금 {won(r['bal'])} · 우대 없을 때 월 {won(b0['m'])} · 총이자 {won(b0['interest'])} · "
              f"우대로 줄어드는 총이자 {won(b0['interest'] - r['interest'])} · 6년째부터 늘어나는 월 상환액 {won(r['m2'] - r['m1'])}")


if __name__ == "__main__":
    main()
