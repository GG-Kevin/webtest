#!/usr/bin/env python3
"""신생아 특례대출(구입·전세) 조건표와 월 상환액 계산 (B1009-2/2) — 표준 라이브러리만.

원문(모두 2026-10-05 KST에 열어 읽음):
  [구입]  주택도시기금 신생아 특례 디딤돌대출 대출 안내
          https://nhuf.molit.go.kr/FP/FP05/FP0503/FP05030801.jsp
          금리표 칸은 화면이 스크립트로 채운다. 같은 칸 원자료(36칸, 9행 x 4열, 행 우선):
          https://nhuf.molit.go.kr/init/include/NewBabyGetInform.jsp?newBabyGetBuySelect=newMearryHouse&productgb=S
  [종료 뒤] 특례금리 적용 종료 후 적용 금리 화면 + 원자료(접수 월별, NEW_ = 수도권, JB_ = 지방)
          https://nhuf.molit.go.kr/FP/FP05/FP0503/FP05030808.jsp
          https://nhuf.molit.go.kr/init/include/NewBabyGetInform.jsp?StdGb=B
  [전세]  신생아 특례 버팀목대출 대출 안내 + 금리 원자료(9행 x 4열, 열 = 임차보증금 구간)
          https://nhuf.molit.go.kr/FP/FP05/FP0502/FP05021401.jsp
          https://nhuf.molit.go.kr/init/include/NewBabyGetInform.jsp?newBabyGetBuySelect=newMearryHouseRent&productgb=S
  [비교]  내집마련디딤돌대출(금리 원자료 productgb=F) · 신혼부부전용 구입자금(productgb=H, 최저 2.55%)
          · 신혼부부전용 전세자금(최저 1.9%)
          https://nhuf.molit.go.kr/FP/FP05/FP0503/FP05030101.jsp
          https://nhuf.molit.go.kr/FP/FP05/FP0503/FP05030601.jsp
          https://nhuf.molit.go.kr/FP/FP05/FP0502/FP05020401.jsp
  [한도 축소] 주택도시기금 공지 2025-06-27(25.6.28 계약분부터 신생아 구입 5억 -> 4억, 전세 3억 -> 2.4억)
          https://nhuf.molit.go.kr/FP/FP08/FP0804/FP080402.jsp?id=3&mode=S&currentPage=1&articleId=1289
  [순자산] 주택도시기금 공지 2025-12-15(구입 5.11억·전월세 3.45억, 2026-01-01 신규 접수분부터)
          https://nhuf.molit.go.kr/FP/FP08/FP0804/FP080402.jsp?id=3&mode=S&currentPage=1&articleId=1298

공식:
  한도(구입)   = min(4억, 평가액 x LTV)  (LTV 70%, 생애최초 80%, 수도권·규제지역 70%) — 선순위·보증금 차감 전
  한도(전세)   = min(2.4억, 보증금 x 80%)
  월 상환액    = P x r x (1+r)^n / ((1+r)^n - 1),  r = 연 금리 / 12  (원리금균등, 원 미만 버림)
  5년 뒤 잔액  = 위 상환을 60회 한 뒤 남은 원금. 6년차부터는 바뀐 금리로 남은 300개월에 다시 나눈다.
  특례 종료 뒤 금리(소득 8.5천만원 이하)
               = 특례금리 + (신혼부부 구입자금 최저 기본금리 - 신생아 특례 최저 기본금리)
                 대출접수일 기준 표로 셈: 2.55 - 1.80 = 0.75%p
  특례 종료 뒤 금리(소득 8.5천만원 초과) = 접수 월 표(2026년 10월 수도권 4.55% 등)
  전세 월 이자  = 대출금 x 연 금리 / 12 (원 미만 버림), 종료 뒤(소득 7.5천만원 이하) = 특례 + (1.9 - 1.3)
  우대금리     = 합계를 0.5%p까지만 빼고, 최종 금리 하한 1.2%(구입)·1.0%(전세)
가정(표 아래에 적는다): 금리는 2026-10-05 화면 금리표 그대로(가산·우대 없음), 거치 없음, 중간 상환 없음, 추가 출산 없음.
같은 입력이면 같은 출력. 실행하면 원고에 넣을 표를 마크다운으로 찍는다.
"""
import math

EOK = 100_000_000

# ── 신생아 특례 디딤돌(구입) 금리표: 원자료 LOANRATE~LOANRATE35, 행 = 소득 구간, 열 = 10·15·20·30년
BUY_ROWS = ["2천만원 이하", "2천만원 초과~4천만원 이하", "4천만원 초과~6천만원 이하",
            "6천만원 초과~8.5천만원 이하", "8.5천만원 초과~1억원 이하", "1억원 초과~1.3억원 이하",
            "(맞벌이) 1.3억원 초과~1.5억원 이하", "(맞벌이) 1.5억원 초과~1.7억원 이하",
            "(맞벌이) 1.7억원 초과~2억원 이하"]
BUY_RATES = [  # 단위 %, 2026-10-05
    [1.80, 1.90, 2.00, 2.05],
    [2.15, 2.25, 2.35, 2.40],
    [2.40, 2.50, 2.60, 2.65],
    [2.65, 2.75, 2.85, 2.90],
    [2.90, 3.00, 3.10, 3.20],
    [3.20, 3.30, 3.40, 3.50],
    [3.50, 3.60, 3.70, 3.80],
    [3.85, 3.95, 4.05, 4.15],
    [4.20, 4.30, 4.40, 4.50],
]
TERMS = [10, 15, 20, 30]

# ── 신생아 특례 버팀목(전세) 금리표: 열 = 임차보증금 5천만원 이하 / 5천~1억 / 1억~1.5억 / 1.5억 초과
RENT_RATES = [
    [1.30, 1.40, 1.50, 1.60],
    [1.60, 1.70, 1.80, 1.90],
    [1.90, 2.00, 2.10, 2.20],
    [2.20, 2.30, 2.40, 2.50],
    [2.55, 2.65, 2.75, 2.85],
    [2.90, 3.00, 3.10, 3.20],
    [3.25, 3.35, 3.45, 3.55],
    [3.60, 3.70, 3.80, 3.90],
    [4.00, 4.10, 4.20, 4.30],
]

# ── 일반 내집마련디딤돌 금리표(productgb=F): 행 = 2천 이하 / 2~4천 / 4~7천 / 7~8.5천
DID_RATES = [
    [2.85, 2.95, 3.05, 3.10],
    [3.20, 3.30, 3.40, 3.45],
    [3.55, 3.65, 3.75, 3.80],
    [3.90, 4.00, 4.10, 4.15],
]
NEWLYWED_BUY_MIN = 2.55   # 신혼부부전용 구입자금 최저(연 2.55% ~ 연 3.85%)
NEWLYWED_RENT_MIN = 1.90  # 신혼부부전용 전세자금 최저(연 1.9% ~ 연 3.3%)
BUY_MIN = BUY_RATES[0][0]   # 1.8
RENT_MIN = RENT_RATES[0][0]  # 1.3

# ── 특례금리 종료 뒤 금리(소득 8.5천만원 초과, 접수 월별, 수도권 NEW_ / 지방 JB_) — 원자료 StdGb=B
AFTER_ROWS = ["1억원 이하", "1.3억원 이하", "1.5억원 이하", "1.7억원 이하", "2억원 이하"]
AFTER_2026_10_CAPITAL = [
    [4.55, 4.55, 4.55, 4.55], [4.55, 4.55, 4.55, 4.55], [4.55, 4.55, 4.55, 4.55],
    [4.55, 4.55, 4.55, 4.55], [4.55, 4.55, 4.60, 4.70]]
AFTER_STDRATE = {"2026년 8월": 4.26, "2026년 9월": 4.40, "2026년 10월": 4.55}
AFTER_2026_10_LOCAL = 4.55  # 지방 20칸 모두 4.55

# ── 조건(화면 글자)
BUY_CAP = 4 * EOK            # 최대 4억원 이내(25.6.27 이전 계약 5억원)
BUY_CAP_OLD = 5 * EOK
RENT_CAP = 2.4 * EOK         # 2.4억원 이내(25.6.27 이전 계약 3억원)
RENT_CAP_OLD = 3 * EOK
LTV = 0.70
LTV_FIRST = 0.80
RENT_RATIO = 0.80
PREF_CAP = 0.5               # 우대금리 적용 상한 0.5%p
FLOOR_BUY = 1.2
FLOOR_RENT = 1.0


def rnd(x):
    return round(x + 1e-9, 2)


def monthly(p, rate, n):
    r = rate / 100 / 12
    return p * r * (1 + r) ** n / ((1 + r) ** n - 1)


def balance(p, rate, n, k):
    """원리금균등으로 k회 낸 뒤 남은 원금."""
    r = rate / 100 / 12
    m = monthly(p, rate, n)
    return p * (1 + r) ** k - m * ((1 + r) ** k - 1) / r


def plan(p, rate1, rate2, n=360, k=60):
    """처음 k개월 rate1, 그 뒤 rate2로 남은 기간에 다시 나눈다."""
    m1 = monthly(p, rate1, n)
    b = balance(p, rate1, n, k)
    int1 = m1 * k - (p - b)
    m2 = monthly(b, rate2, n - k)
    int2 = m2 * (n - k) - b
    return {"m1": math.floor(m1), "int5": math.floor(int1), "bal5": math.floor(b),
            "m2": math.floor(m2), "int_total": math.floor(int1 + int2)}


def pref(base, prefs, floor):
    return rnd(max(floor, base - min(sum(prefs), PREF_CAP)))


def calc_spread(row):
    return rnd(row[3] - row[0])


def won(x):
    return f"{int(x):,}원"


def man(x):
    if x >= EOK:
        return f"{x / EOK:g}억원"
    return f"{x / 10_000:,.0f}만원"


# ── 계산 예시 입력(표 아래에 가정으로 적는다)
APPRAISAL = 5 * EOK          # 수도권 아파트 평가액 5억원
INCOME_BAND = 2              # 부부합산 연소득 6천만원 → 「4천만원 초과~6천만원 이하」
DID_BAND = 2                 # 일반 디딤돌 「4천만원 초과~7천만원 이하」
DID_CHILD_PREF = 0.3         # 일반 디딤돌 1자녀가구 0.3%p(신혼 0.2%p와 중복 불가 → 큰 쪽)
DID_CAP_NEWLY = 3.2 * EOK    # 일반 디딤돌 신혼가구·2자녀 이상 3.2억원
DEPOSIT = 2 * EOK            # 전세 보증금 2억원(수도권)


def main():
    # 1) 조건 비교표
    print("표: 구입·전세 두 상품의 요건 나란히 보기(주택도시기금 화면, 10월 5일 열람)")
    print("| 항목 | 구입(디딤돌) | 전세(버팀목) |")
    print("|---|---|---|")
    print("| 출산 요건 | 대출접수일 기준 2년 내 출산·입양(2023년 1월 1일 이후 출생아) | 같음 |")
    print("| 부부합산 연소득 | 1.3억원 이하, 맞벌이 2억원 이하 | 같음 |")
    print("| 순자산 | 5.11억원 이하 | 3.45억원 이하 |")
    print("| 집 | 전용 85㎡ 이하, 평가액 9억원 이하 | 전용 85㎡ 이하, 보증금 수도권 5억원·그 외 4억원 이하 |")
    print(f"| 최대 한도 | {BUY_CAP / EOK:g}억원(LTV 70%, 생애최초 80%) | {RENT_CAP / EOK:g}억원(보증금의 80%) |")
    print(f"| 금리 | 연 {BUY_MIN}~{BUY_RATES[-1][-1]}% | 연 {RENT_MIN}~{RENT_RATES[-1][-1]}% |")
    print("| 특례금리 기간 | 5년, 추가 출산 1명당 5년 늘려 최장 15년 | 4년, 1명당 4년 늘려 최장 12년 |")
    print("| 우대 뒤 금리 하한 | 연 1.2% | 연 1.0% |")
    print()

    # 2) 구입 금리표
    print("표: 신생아 특례 디딤돌 금리(부부합산 연소득 × 대출기간, 2026년 10월 5일 원자료)")
    print("| 부부합산 연소득 | 10년 | 15년 | 20년 | 30년 |")
    print("|---|---|---|---|---|")
    for lab, row in zip(BUY_ROWS, BUY_RATES):
        print(f"| {lab} | " + " | ".join(f"{v:.2f}%" for v in row) + " |")
    spreads = sorted({calc_spread(r) for r in BUY_RATES})
    print(f"- 같은 소득 구간에서 10년 → 30년 금리 차이: {spreads[0]:.2f}~{spreads[-1]:.2f}%p")
    print()

    # 3) 직접 계산: 3.2억 30년, 특례 vs 일반 디딤돌
    p = DID_CAP_NEWLY
    nb_rate = BUY_RATES[INCOME_BAND][3]
    gap = rnd(NEWLYWED_BUY_MIN - BUY_MIN)
    nb_after = rnd(nb_rate + gap)
    did_base = DID_RATES[DID_BAND][3]
    did_rate = rnd(did_base - DID_CHILD_PREF)
    a = plan(p, nb_rate, nb_after)
    b = plan(p, did_rate, did_base)
    print(f"표: {p / EOK:g}억원·30년·원리금균등 직접 계산(부부합산 연소득 6천만원, 신혼가구 1자녀 가정)")
    print("| 항목 | 신생아 특례 디딤돌 | 일반 디딤돌(신혼가구) |")
    print("|---|---|---|")
    print(f"| 처음 5년 금리 | 연 {nb_rate:.2f}% | 연 {did_rate:.2f}%(표 {did_base:.2f}%에서 1자녀 우대 {DID_CHILD_PREF}%p) |")
    print(f"| 처음 5년 월 상환액 | {won(a['m1'])} | {won(b['m1'])} |")
    print(f"| 5년 동안 낸 이자 | {won(a['int5'])} | {won(b['int5'])} |")
    print(f"| 6년차부터 금리 | 연 {nb_after:.2f}%(특례 {nb_rate:.2f}% + {gap:.2f}%p) | 연 {did_base:.2f}%(우대 5년 끝) |")
    print(f"| 6년차부터 월 상환액 | {won(a['m2'])} | {won(b['m2'])} |")
    print(f"| 30년 이자 합계(6년차 금리가 끝까지 같다고 가정) | {won(a['int_total'])} | {won(b['int_total'])} |")
    print()
    d5 = b['int5'] - a['int5']
    dm1 = b['m1'] - a['m1']
    dm2 = b['m2'] - a['m2']
    dt = b['int_total'] - a['int_total']
    print(f"- 차이: 처음 5년 월 {won(dm1)} · 5년 이자 {won(d5)}({man(d5)}) · 6년차부터 월 {won(dm2)} · 30년 이자 {won(dt)}({man(dt)})")
    print(f"- 5년 뒤 남은 원금: 특례 {won(a['bal5'])} · 일반 {won(b['bal5'])}")
    lim_nb = min(BUY_CAP, APPRAISAL * LTV)
    lim_did = min(DID_CAP_NEWLY, APPRAISAL * LTV)
    m_full = math.floor(monthly(lim_nb, nb_rate, 360))
    print(f"- 평가액 {APPRAISAL / EOK:g}억원(수도권) 한도: 특례 min(4억, {APPRAISAL / EOK:g}억×70%) = {man(lim_nb)} · 일반 디딤돌 신혼 {man(lim_did)}")
    print(f"- 특례로 {man(lim_nb)}을 다 빌리면 처음 5년 월 상환액 {won(m_full)}")
    print()

    # 4) 특례 종료 뒤 금리
    print("표: 특례금리가 끝난 뒤 금리(2026년 10월 접수분, 30년 만기 예)")
    print("| 부부합산 연소득 | 특례금리(30년) | 끝난 뒤 금리 | 셈 |")
    print("|---|---|---|---|")
    for i in range(4):
        r = BUY_RATES[i][3]
        print(f"| {BUY_ROWS[i]} | {r:.2f}% | {rnd(r + gap):.2f}% | +{gap:.2f}%p |")
    for i in (4, 5):
        print(f"| {BUY_ROWS[i]} | {BUY_RATES[i][3]:.2f}% | 수도권 {AFTER_2026_10_CAPITAL[i - 4][3]:.2f}% · 지방 {AFTER_2026_10_LOCAL:.2f}% | 10월 접수 표 |")
    for i in (6, 7, 8):
        print(f"| {BUY_ROWS[i]} | {BUY_RATES[i][3]:.2f}% | 수도권 {AFTER_2026_10_CAPITAL[i - 4][3]:.2f}% · 지방 {AFTER_2026_10_LOCAL:.2f}% | 10월 접수 표 |")
    print()
    print("- 소득 8.5천만원 초과 칸 접수 월별 표 금리(수도권 1억원 이하 칸): "
          + " → ".join(f"{k} {v:.2f}%" for k, v in AFTER_STDRATE.items()))
    print(f"- 가산폭 셈: 신혼부부 구입자금 최저 {NEWLYWED_BUY_MIN:.2f}% - 신생아 특례 최저 {BUY_MIN:.2f}% = {gap:.2f}%p")
    print()

    # 5) 우대금리 예시
    pr = pref(nb_rate, [0.3, 0.1], FLOOR_BUY)
    pr2 = pref(nb_rate, [0.4, 0.1, 0.2], FLOOR_BUY)
    m_pr = math.floor(monthly(p, pr, 360))
    print(f"- 우대 예: 청약 5년·60회 0.3%p + 전자계약 0.1%p → {nb_rate:.2f} - 0.4 = 연 {pr:.2f}%, {p / EOK:g}억원 30년 월 {won(m_pr)}(특례 표 금리보다 월 {won(a['m1'] - m_pr)} 적음)")
    print(f"- 우대 합이 0.7%p(청약 0.4 + 전자계약 0.1 + 추가 출산 0.2)여도 상한 {PREF_CAP}%p → 연 {pr2:.2f}%")
    print()

    # 6) 전세 예시
    rent_loan = min(RENT_CAP, DEPOSIT * RENT_RATIO)
    rr = RENT_RATES[INCOME_BAND][3]
    rgap = rnd(NEWLYWED_RENT_MIN - RENT_MIN)
    rr_after = rnd(rr + rgap)
    mi = math.floor(rent_loan * rr / 100 / 12)
    mi_after = math.floor(rent_loan * rr_after / 100 / 12)
    print(f"- 전세 예: 보증금 {man(DEPOSIT)}(수도권) × 80% = {man(rent_loan)}, 소득 6천만원·보증금 1.5억원 초과 칸 연 {rr:.2f}% → 월 이자 {won(mi)}")
    print(f"- 전세 특례 4년 뒤(소득 7.5천만원 이하): {rr:.2f} + ({NEWLYWED_RENT_MIN:.2f} - {RENT_MIN:.2f} = {rgap:.2f}%p) = 연 {rr_after:.2f}% → 월 이자 {won(mi_after)}(월 {won(mi_after - mi)} 늘어남)")
    print(f"- 한도 축소 전(2025년 6월 27일 이전 계약): 구입 {BUY_CAP_OLD / EOK:g}억원 · 전세 {RENT_CAP_OLD / EOK:g}억원")


if __name__ == "__main__":
    main()
