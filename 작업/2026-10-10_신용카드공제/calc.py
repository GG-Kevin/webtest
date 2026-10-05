#!/usr/bin/env python3
"""연말정산 신용카드 등 사용금액 소득공제 계산 (B1010-2/2) — 표준 라이브러리만.

입력(원 단위, 표마다 고정 예시 · 가정은 표 이름과 표 아래 문장에 적는다):
  wage            총급여액(비과세 소득을 뺀 근로소득)
  credit          신용카드 사용액(전통시장·대중교통·문화체육 사용분 제외)
  debit           체크카드·현금영수증·기명식 선불 사용액(위 세 가지 제외)
  market          전통시장 사용분(결제 수단 무관)
  transit         대중교통 이용분(결제 수단 무관)
  culture_credit  도서·신문·공연·박물관·미술관·영화·수영장·체력단련장 사용분 중 신용카드 결제
  culture_debit   같은 사용분 중 체크카드·현금영수증 결제
  kids            제10항 단서의 「자녀등」 수(20세 이하 직계비속 등, 시행령 제121조의2 제18항)

공식(조세특례제한법 제126조의2, 법률 제21467호 · 시행 2026. 9. 18. 판):
  최저사용금액 = 총급여 × 100분의 25(제1항, 국외 사용분 제외)
  총급여 7천만원 이하: 문화체육사용분을 따로 떼어 30% · 초과: 결제 수단 칸(신용/직불)에 그대로 둔다(제2항 제4호·제5호)
  공제 계산 전 금액 = 전통시장×40% + 대중교통×40% + 문화체육×30%(7천만 이하) + 직불등×30% + 신용×15%   (제2항 제1~5호)
  빼는 금액(제2항 제6호):
    가. 최저 ≤ 신용                         : 최저 × 15%
    나. 신용 < 최저 ≤ 신용+직불(+문화)      : 신용 × 15% + (최저 − 신용) × 30%
    다. 최저 > 신용+직불(+문화)             : 신용 × 15% + (직불+문화) × 30% + (최저 − 신용 − 직불 − 문화) × 40%
  공제 가능 금액 = max(0, 계산 전 − 빼는 금액) (사용액이 최저사용금액 이하면 0)
  기본 한도(제10항, 개정 2025. 12. 23.): 7천만 이하 300만원(자녀등 1명 350만원·2명 이상 400만원)
                                        7천만 초과 250만원(자녀등 1명 275만원·2명 이상 300만원)
  추가 공제(제11항, 신설 2025. 12. 23.): 한도 초과분과 [전통시장×40% + 대중교통×40% (+문화체육×30%, 7천만 이하)] 중
                                        작은 금액, 다만 200만원(7천만 이하 300만원)까지
  소득공제액 = min(공제 가능, 기본 한도) + 추가 공제
  https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=284389&joNo=0126&joBrNo=02&docCls=jo&urlMode=lsScJoRltInfoR
  자녀등 범위(시행령 제121조의2 제18항, 신설 2026. 2. 27.): 20세 이하(장애인은 나이 제한 없음)·소득금액 100만원 이하
  https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=288915&joNo=0121&joBrNo=02&docCls=jo&urlMode=lsScJoRltInfoR
  적용 시기: 부칙 <법률 제21223호, 2025. 12. 23.> 제1조(2026. 1. 1. 시행)·제47조(시행 전 사용분은 종전 규정)
  https://www.law.go.kr/LSW/lsInfoR.do?lsiSeq=284389&efYd=20260918&chrClsCd=010202&ancYnChk=0
세금 효과(가정): 과세표준이 1,400만원 초과 5,000만원 이하 구간(세율 15%)에 있다고 놓는다.
  소득세 감소 = 소득공제액 × 15%(국세청 종합소득세 세율 표)
  https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?mi=2227&cntntsId=7667
  지방소득세 = 원천징수 소득세의 100분의 10(지방세법 제103조의13 ①) — 원 미만 버림
  https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=282559&joNo=0103&joBrNo=13&docCls=jo&urlMode=lsScJoRltInfoR
검산 사례: 국세청 「2025년 원천징수의무자를 위한 연말정산 신고안내」 137쪽 사례1(총급여 6,800만원, 4,300만원 사용 → 530만원)
  https://www.nts.go.kr/comm/nttFileDownload.do?fileKey=88c482e8d69eb1653515871654a4ab42 (zip 안 PDF)
기준일: 2026-10-06 원문 기준. 정수 계산이라 같은 입력이면 같은 출력. 실행하면 원고에 넣을 표를 마크다운으로 찍는다.
"""
from fractions import Fraction as F

MIN_PCT = 25
R_CREDIT, R_DEBIT, R_CULTURE, R_MARKET, R_TRANSIT = 15, 30, 30, 40, 40
WAGE_LINE = 70_000_000
LIMIT = {True: {0: 3_000_000, 1: 3_500_000, 2: 4_000_000},     # 총급여 7천만원 이하
         False: {0: 2_500_000, 1: 2_750_000, 2: 3_000_000}}    # 7천만원 초과
EXTRA_CAP = {True: 3_000_000, False: 2_000_000}
TAX_RATE = 15
LOCAL_PCT = 10


def pct(x, p):
    return F(x) * p / 100


def min_usage(wage):
    return wage * MIN_PCT // 100


def deduction(wage, credit=0, debit=0, market=0, transit=0, culture_credit=0, culture_debit=0, kids=0):
    low = wage <= WAGE_LINE
    if low:
        S, D, C = credit, debit, culture_credit + culture_debit
    else:
        S, D, C = credit + culture_credit, debit + culture_debit, 0
    M, T = market, transit
    total = S + D + C + M + T
    mn = min_usage(wage)
    gross = pct(M, R_MARKET) + pct(T, R_TRANSIT) + pct(C, R_CULTURE) + pct(D, R_DEBIT) + pct(S, R_CREDIT)
    if mn <= S:
        sub = pct(mn, R_CREDIT)
        case = "가"
    elif mn <= S + D + C:
        sub = pct(S, R_CREDIT) + pct(mn - S, R_DEBIT)
        case = "나"
    else:
        sub = pct(S, R_CREDIT) + pct(D + C, R_DEBIT) + pct(mn - S - D - C, R_MARKET)
        case = "다"
    able = max(F(0), gross - sub) if total > mn else F(0)
    lim = LIMIT[low][min(kids, 2)]
    special = pct(M, R_MARKET) + pct(T, R_TRANSIT) + (pct(C, R_CULTURE) if low else 0)
    extra = min(max(F(0), able - lim), special, F(EXTRA_CAP[low]))
    ded = min(able, F(lim)) + extra
    return {"최저사용금액": mn, "사용액": total, "계산전": int(gross), "빼는금액": int(sub), "구간": case,
            "공제가능": int(able), "한도": lim, "추가": int(extra), "소득공제액": int(ded)}


def compute(**inp):
    return deduction(**inp)


def tax_cut(ded):
    inc = ded * TAX_RATE // 100
    local = inc * LOCAL_PCT // 100
    return {"소득세": inc, "지방소득세": local, "합계": inc + local}


def man(v):
    """원 → 「1,500만원」 꼴(만원 단위로 나누어떨어지는 값만)."""
    if v % 10_000 == 0:
        return f"{v // 10_000:,}만원"
    return f"{v:,}원"


def month_man(v):
    """연 금액 → 한 달 몫을 만원 단위 소수 첫째 자리로(둘째 자리에서 반올림)."""
    t = (v * 10 + 60_000) // 120_000
    return f"{t // 10:,}" if t % 10 == 0 else f"{t // 10:,}.{t % 10}"


def won(v):
    return f"{v:,}원"


# 표에 쓰는 고정 예시
WAGES_T1 = [30_000_000, 40_000_000, 50_000_000, 60_000_000, 70_000_000, 80_000_000]
SPLIT_WAGE, SPLIT_TOTAL = 40_000_000, 18_000_000
SPLITS = [18_000_000, 10_000_000, 5_000_000, 0]          # 신용카드 몫, 나머지는 체크카드·현금영수증
EX_CREDIT, EX_CASH = 20_000_000, 5_000_000               # 설계도 예시: 카드 2천만원 + 현금영수증 5백만원
EX_WAGES = [40_000_000, 60_000_000, 80_000_000]
NTS_CASE = dict(wage=68_000_000, credit=30_000_000, transit=2_000_000, debit=7_000_000,
                market=3_000_000, culture_debit=1_000_000)   # 신용 3,200(대중교통 200 포함) · 현금영수증 800(전통시장 300 포함) · 체크 300(문화 100 포함)


def main():
    print("표: 총급여별 최저사용금액(총급여 × 25%) — 이 금액을 넘게 쓴 부분부터 공제")
    print("| 총급여 | 최저사용금액 | 한 달로 나누면 |")
    print("|---|---|---|")
    for w in WAGES_T1:
        m = min_usage(w)
        print(f"| {man(w)} | {man(m)} | 약 {month_man(m)}만원 |")
    print()

    print("표: 어디에 쓴 돈인지에 따른 공제율(조세특례제한법 제126조의2 제2항, 2026년 사용분)")
    print("| 사용처·결제 수단 | 공제율 | 총급여 7천만원 초과일 때 |")
    print("|---|---|---|")
    print(f"| 전통시장(카드·현금영수증 모두) | {R_MARKET}% | {R_MARKET}% |")
    print(f"| 대중교통(카드·현금영수증 모두) | {R_TRANSIT}% | {R_TRANSIT}% |")
    print(f"| 도서·신문·공연·박물관·미술관·영화·수영장·체력단련장 | {R_CULTURE}% | 따로 없음(결제 수단 칸으로) |")
    print(f"| 체크카드·현금영수증·기명식 선불 | {R_DEBIT}% | {R_DEBIT}% |")
    print(f"| 신용카드 | {R_CREDIT}% | {R_CREDIT}% |")
    print()

    print(f"표: 총급여 {man(SPLIT_WAGE)} · 1년 {man(SPLIT_TOTAL)} 사용 · 신용카드와 체크카드 비율만 바꾼 직접 계산")
    print("| 신용카드 | 체크카드·현금영수증 | 빼는 금액(문턱분) | 소득공제액 |")
    print("|---|---|---|---|")
    for c in SPLITS:
        r = deduction(SPLIT_WAGE, credit=c, debit=SPLIT_TOTAL - c)
        print(f"| {man(c) if c else '0원'} | {man(SPLIT_TOTAL - c) if SPLIT_TOTAL - c else '0원'} | {man(r['빼는금액'])} | {man(r['소득공제액'])} |")
    print()

    print(f"표: 신용카드 {man(EX_CREDIT)} + 현금영수증 {man(EX_CASH)}을 쓴 근로자의 공제액 직접 계산(자녀등 없음, 세금은 15% 구간 가정)")
    print("| 총급여 | 최저사용금액 | 한도 전 공제 가능액 | 한도 | 소득공제액 | 줄어드는 소득세+지방소득세 |")
    print("|---|---|---|---|---|---|")
    for w in EX_WAGES:
        r = deduction(w, credit=EX_CREDIT, debit=EX_CASH)
        t = tax_cut(r["소득공제액"])
        tx = f"{won(t['합계'])}(한 달 약 {month_man(t['합계'])}만원)" if w <= 60_000_000 else "구간 가정 안 함"
        print(f"| {man(w)} | {man(r['최저사용금액'])} | {man(r['공제가능'])} | {man(r['한도'])} | {man(r['소득공제액'])} | {tx} |")
    print()

    print("표: 2026년 사용분부터의 기본 한도와 추가 한도(제10항·제11항)")
    print("| 총급여 | 자녀등 없음 | 자녀등 1명 | 자녀등 2명 이상 | 전통시장·대중교통(·문화체육) 추가 한도 |")
    print("|---|---|---|---|---|")
    for low, label in ((True, "7천만원 이하"), (False, "7천만원 초과")):
        L = LIMIT[low]
        print(f"| {label} | {man(L[0])} | {man(L[1])} | {man(L[2])} | {man(EXTRA_CAP[low])} |")
    print()

    print("표: 국세청 2025년 책자 사례1(총급여 6,800만원·4,300만원 사용)을 2026년 한도로 다시 계산")
    print("| 자녀등 | 공제 가능액 | 기본 한도 | 추가 공제 | 소득공제액 |")
    print("|---|---|---|---|---|")
    for k, lab in ((0, "없음"), (1, "1명"), (2, "2명 이상")):
        r = deduction(kids=k, **NTS_CASE)
        print(f"| {lab} | {man(r['공제가능'])} | {man(r['한도'])} | {man(r['추가'])} | {man(r['소득공제액'])} |")
    print()

    # 본문 문장에 쓰는 숫자
    d1 = deduction(**NTS_CASE, kids=1)["소득공제액"] - deduction(**NTS_CASE)["소득공제액"]
    print(f"자녀 1명일 때 늘어난 공제액: {man(d1)} · 15% 구간이면 세금 {won(tax_cut(d1)['합계'])}")
    r = deduction(SPLIT_WAGE, credit=SPLIT_TOTAL)
    print(f"신용카드만 {man(SPLIT_TOTAL)}: 계산 전 {man(r['계산전'])} − 문턱분 {man(r['빼는금액'])} = {man(r['소득공제액'])}")
    r = deduction(SPLIT_WAGE, debit=SPLIT_TOTAL)
    print(f"체크카드만 {man(SPLIT_TOTAL)}: 계산 전 {man(r['계산전'])} − 문턱분 {man(r['빼는금액'])} = {man(r['소득공제액'])}")
    print(f"한도 300만원을 신용카드만으로 채우는 사용액(4천만원): {man(min_usage(40_000_000) + 3_000_000 * 100 // R_CREDIT)}")
    print(f"한도 300만원을 체크카드만으로 채우는 사용액(4천만원): {man(min_usage(40_000_000) + 3_000_000 * 100 // R_DEBIT)}")


TESTS = [
    dict(wage=40_000_000, credit=20_000_000, debit=5_000_000),
    dict(wage=60_000_000, credit=20_000_000, debit=5_000_000),
    dict(wage=80_000_000, credit=20_000_000, debit=5_000_000),
    dict(wage=40_000_000, credit=18_000_000),
    dict(wage=40_000_000, debit=18_000_000),
    dict(wage=40_000_000, credit=10_000_000, debit=8_000_000),
    dict(wage=40_000_000, credit=5_000_000, debit=13_000_000),
    dict(NTS_CASE),
    dict(NTS_CASE, kids=1),
    dict(NTS_CASE, kids=2),
]

if __name__ == "__main__":
    main()
