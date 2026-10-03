#!/usr/bin/env python3
"""보금자리론 신혼부부 소득 기준 · 우대금리 · 월 상환액 · 한도 계산 (B1006-1/1) — 표준 라이브러리만.

입력(아래 상수, 2026-10-03 원문 기준):
  소득 기준(부부 합산 연소득)  일반 7천만원 · 신혼가구 8천5백만원 · 미성년 1자녀 9천만원 · 다자녀 1억원
      한국주택금융공사 (일반) 상품소개  https://www.hf.go.kr/ko/sub01/sub01_01_01.do
      보금자리론 업무처리기준 제2장 1(소득요건, 「85백만원」) — 일부개정 2026. 07. 20.
      https://www.hf.go.kr/cms/etcResourceDown.do?site=$cms$NYeyA&key=$cms$AwRg+sBsHgTJwDsBmEA6ADgEwGZA
  신혼가구 정의   혼인신고일이 신청일로부터 7년 이내(결혼예정 3개월 이내 포함) — 업무처리기준 제1장 3
  우대금리       신혼가구 0.3%p · 저소득청년 0.1%p — 둘 다 「부부 합산 연소득 7천만원 이하」 조건, 합계 최대 1.0%p
      업무처리기준 제4장 5 · 금리안내 https://www.hf.go.kr/ko/sub01/sub01_01_04.do
  기준금리       2026년 10월 공시(2026-10-01) 아낌e보금자리론 30년 5.10%(40년 5.15%, 50년 5.20%) — 금리안내 화면
  대출한도       3.6억원(다자녀 4억원, 생애최초 4.2억원), 1백만원 단위 — 업무처리기준 제4장 1
  LTV           아파트 최대 70%, 생애최초 80%(수도권·규제지역 70%) — (특성별) 상품소개 https://www.hf.go.kr/ko/sub01/sub01_01_02.do
  DTI           60% 이내 — 업무처리기준 제5장 1 · DTI = 연간 원리금상환액 ÷ 연소득 × 100(제5장 2)
  2개년 소득     |최근년도 − 전년도| ÷ 최근년도 × 100% > 20%이면 2개년 평균, 20% 이하면 최근년도 — 제6장 2 3)
  2024년 개편    금융위원회 2024-01-25 보도자료(신혼 8,500만원 · 1자녀 8천만원 · 신혼 우대 20bp)
      https://www.fsc.go.kr/no010101/81571
공식:
  월 상환액(원리금 균등) = P × r ÷ (1 − (1 + r)^−n), r = 연 금리 ÷ 12, n = 개월 수. 분수(Fraction)로 계산하고 원 미만은 버린다.
  총이자 = 월 상환액 × n − P (마지막 회차 끝자리 조정은 무시)
  한도 = min(주택가격 × LTV, 상품 한도) → 1백만원 미만 버림
  DTI 60%를 맞추는 최소 연소득 = 월 상환액 × 12 ÷ 0.6 → 만원 미만 올림(다른 빚 0 가정)
  금액 단위: 소득은 만원, 대출은 원. 같은 입력이면 같은 출력.
기준일: 2026-10-03 원문 기준(금리는 2026-10-01 공시).
"""
from fractions import Fraction as F

# ── 원문 숫자 ──
INCOME_CAP = {"일반": 7000, "신혼가구": 8500, "1자녀": 9000, "다자녀": 10000}   # 만원
PREF_LINE = 7000            # 우대금리·실수요자 판정 소득선(만원)
PREF_NEWLYWED = F(3, 10)    # 0.3%p
PREF_YOUTH = F(1, 10)       # 0.1%p (만 40세 미만)
PREF_MAX = F(1)             # 1.0%p
RATE = {30: F(510, 100), 40: F(515, 100), 50: F(520, 100)}   # 아낌e 2026-10-01 공시, 연 %
CAP_LOAN = {"일반": 360_000_000, "생애최초": 420_000_000, "다자녀": 400_000_000}
LTV = {"일반(아파트)": F(70, 100), "생애최초(비수도권)": F(80, 100), "생애최초(수도권)": F(70, 100)}
DTI = F(60, 100)
TWO_YEAR_LIMIT = F(20, 100)


def monthly(principal, rate_pct, years):
    """원리금 균등 월 상환액(원 미만 버림)."""
    r = F(rate_pct) / 100 / 12
    n = years * 12
    pay = F(principal) * r / (1 - (1 + r) ** (-n))
    return int(pay)  # 양수라 int = 버림


def judge(income, age_under_40=True):
    """신혼가구(자녀 없음), 무주택, 6억 이하 구입 가정."""
    ok = income <= INCOME_CAP["신혼가구"]
    pref = F(0)
    if ok and income <= PREF_LINE:
        pref += PREF_NEWLYWED
        if age_under_40:
            pref += PREF_YOUTH
    pref = min(pref, PREF_MAX)
    realdemand = ok and income <= PREF_LINE
    return ok, pref, realdemand


def fmt_pct(x):
    return f"{float(x):.2f}%"


def fmt_pp(x):
    return f"{float(x):.1f}%p"


def won(x):
    return f"{x:,}원"


def man(x):
    return f"{x:,}만원"


def eok(w):
    """원 → 「2억원」·「2억 8,000만원」(만원 미만은 없다고 가정)."""
    m = w // 10_000
    e, r = divmod(m, 10_000)
    if e and r:
        return f"{e}억 {r:,}만원"
    if e:
        return f"{e}억원"
    return f"{r:,}만원"


def table_income():
    rows = ["표1 부부 합산 연소득별 판정(신혼가구·자녀 없음·무주택·6억원 이하 구입, 아낌e 30년 기준금리 5.10%)",
            "| 부부 합산 연소득 | 소득 요건(8,500만원 이하) | 신혼가구 우대 | 저소득청년 우대(만 40세 미만) | 적용 금리 |",
            "|---|---|---|---|---|"]
    out = {}
    for inc in (5000, 7000, 7500, 8500, 9000):
        ok, pref, _ = judge(inc)
        if not ok:
            rows.append(f"| {man(inc)} | 넘음(신혼 기준으로는 불가) | - | - | - |")
            out[inc] = None
            continue
        nw = fmt_pp(PREF_NEWLYWED) if pref >= PREF_NEWLYWED else "없음(7,000만원 초과)"
        yo = fmt_pp(PREF_YOUTH) if pref > PREF_NEWLYWED else "없음"
        rate = RATE[30] - pref
        out[inc] = rate
        rows.append(f"| {man(inc)} | 충족 | {nw} | {yo} | {fmt_pct(rate)} |")
    return rows, out


def table_payment():
    rows = ["표2 우대금리 유무에 따른 월 상환액(30년 원리금 균등)",
            "| 대출 원금 | 금리 | 월 상환액 | 30년 총이자 | 5.10% 대비 월 차이 |",
            "|---|---|---|---|---|"]
    res = {}
    for P in (200_000_000, 300_000_000):
        base = monthly(P, RATE[30], 30)
        for label, pref in (("5.10%(우대 없음)", F(0)), ("4.80%(신혼 0.3%p)", PREF_NEWLYWED),
                            ("4.70%(신혼 0.3%p + 청년 0.1%p)", PREF_NEWLYWED + PREF_YOUTH)):
            rate = RATE[30] - pref
            assert fmt_pct(rate) == label.split("(")[0]
            m = monthly(P, rate, 30)
            interest = m * 360 - P
            diff = base - m
            res[(P, label)] = (m, interest, diff)
            rows.append(f"| {eok(P)} | {label} | {won(m)} | {won(interest)} | {won(diff) if diff else '-'} |")
    return rows, res


def table_limit():
    rows = ["표3 주택가격별 대출한도와 DTI 60%를 맞추는 최소 연소득(아파트, 다른 빚 0, 30년 5.10%)",
            "| 주택가격 | 일반 LTV 70%(한도 3.6억원) | 생애최초 비수도권 LTV 80%(4.2억원) | 생애최초 수도권 LTV 70%(4.2억원) | 일반 한도의 월 상환액 | DTI 60% 최소 연소득 |",
            "|---|---|---|---|---|---|"]
    res = {}
    for price in (300_000_000, 400_000_000, 500_000_000, 600_000_000):
        a = min(price * LTV["일반(아파트)"], CAP_LOAN["일반"])
        b = min(price * LTV["생애최초(비수도권)"], CAP_LOAN["생애최초"])
        c = min(price * LTV["생애최초(수도권)"], CAP_LOAN["생애최초"])
        a, b, c = (int(x) // 1_000_000 * 1_000_000 for x in (a, b, c))
        m = monthly(a, RATE[30], 30)
        need = -(-F(m * 12) / DTI // 10_000)  # 만원 올림
        res[price] = (a, b, c, m, int(need))
        rows.append(f"| {eok(price)} | {eok(a)} | {eok(b)} | {eok(c)} | {won(m)} | {int(need):,}만원 |")
    return rows, res


def two_year(recent, prev):
    """2개년 증빙소득 → (변동률 %, 산정 연소득 만원, 방법). 상시소득 입증이 없는 경우."""
    change = abs(F(recent - prev)) / recent
    if change > TWO_YEAR_LIMIT:
        return change, F(recent + prev) / 2, "2개년 평균"
    return change, F(recent), "최근년도"


def table_twoyear():
    rows = ["표4 배우자 사업소득이 해마다 다를 때 부부 합산 연소득(본인 근로소득 4,200만원, 상시소득 입증 없음)",
            "| 배우자 2025년 | 배우자 2024년 | 변동률 | 배우자 산정 소득 | 부부 합산 | 7,000만원 우대선 |",
            "|---|---|---|---|---|---|"]
    res = {}
    me = 4200
    for recent, prev in ((3000, 2300), (2300, 3000), (3000, 2600)):
        ch, inc, how = two_year(recent, prev)
        tot = me + inc
        res[(recent, prev)] = (ch, inc, tot)
        side = "이하(우대 대상)" if tot <= PREF_LINE else "초과(우대 없음)"
        rows.append(f"| {man(recent)} | {man(prev)} | {float(ch) * 100:.1f}% | {man(int(inc))}({how}) | {man(int(tot))} | {side} |")
    return rows, res


def main():
    print("# 보금자리론 신혼부부 소득 — calc.py 출력 (2026-10-03 원문 기준, 금리 2026-10-01 공시)")
    print()
    print("원문 숫자: 소득 기준", ", ".join(f"{k} {eok(v * 10_000)}" for k, v in INCOME_CAP.items()),
          f"· 우대선 {man(PREF_LINE)} · 신혼 우대 {fmt_pp(PREF_NEWLYWED)} · 청년 우대 {fmt_pp(PREF_YOUTH)} · 우대 한도 {fmt_pp(PREF_MAX)}")
    print("기준금리(아낌e):", ", ".join(f"{y}년 {fmt_pct(r)}" for y, r in RATE.items()),
          "· 한도", ", ".join(f"{k} {eok(v)}" for k, v in CAP_LOAN.items()), f"· DTI {int(DTI * 100)}%")
    print("2024-01-25 금융위 발표: 신혼 8,500만원 · 1자녀 8,000만원 · 신혼 우대 20bp(0.2%p) · 주택가격 6억원 · 한도 3.6억원")
    print("만기 40년: 만 40세 미만(신혼가구 만 50세 미만) · 50년: 만 35세 미만(신혼가구 만 40세 미만) · 결혼예정 3개월 · 혼인 7년")
    print()
    for f in (table_income, table_payment, table_limit, table_twoyear):
        rows, _ = f()
        print("\n".join(rows))
        print()
    # 본문용 한 줄 숫자
    _, pay = table_payment()
    for P in (200_000_000, 300_000_000):
        m0 = pay[(P, "5.10%(우대 없음)")]
        m1 = pay[(P, "4.80%(신혼 0.3%p)")]
        m2 = pay[(P, "4.70%(신혼 0.3%p + 청년 0.1%p)")]
        print(f"원금 {eok(P)}: 월 차이 신혼 {won(m1[2])} · 신혼+청년 {won(m2[2])} · 30년 총이자 차이 신혼 {won(m0[1] - m1[1])} · 신혼+청년 {won(m0[1] - m2[1])}"
              f" · 연 환산 차이 신혼 {won(m1[2] * 12)} · 신혼+청년 {won(m2[2] * 12)}")
    gap = INCOME_CAP["신혼가구"] - PREF_LINE
    print(f"소득 요건은 충족하지만 우대가 없는 구간: {man(PREF_LINE)} 초과 ~ {man(INCOME_CAP['신혼가구'])} 이하(폭 {man(gap)})")


if __name__ == "__main__":
    main()
