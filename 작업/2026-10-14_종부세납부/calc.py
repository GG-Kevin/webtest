#!/usr/bin/env python3
"""종부세 납부기간 · 분납 · 주택분 세액 흐름 계산 (B1014-1/1) — 표준 라이브러리만.

입력(표마다 고정 예시, 가정은 표 아래에 적는다):
  official_sum  주택 공시가격 합계(원) · one_house  1세대 1주택자 여부
  bill          고지서의 종합부동산세액(원, 농어촌특별세 제외)
공식:
  납부기간      = 해당 연도 12월 1일 ~ 12월 15일
                  종합부동산세법 제16조①③(법률 제21224호, 시행 2026. 1. 1.)
                  https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280417&joNo=0016&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  고지서 발급   = 납부기간 개시 5일 전까지(제16조②) → 12월 1일 − 5일
  분납          = 세액 250만원 초과일 때, 납부기한이 지난 날부터 6개월 이내(법 제20조)
                  https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280417&joNo=0020&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
                  분납 한도 = 250만 초과 500만 이하: 세액 − 250만 / 500만 초과: 세액 × 50/100 이하
                  종합부동산세법 시행령 제16조①(대통령령 제36739호, 시행 2026. 10. 1.)
                  https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=290557&joNo=0016&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  농어촌특별세  = 종부세액 × 20%, 분납은 종부세 분납 비율대로
                  국세청 종합부동산세 납부기한 https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?mi=2352&cntntsId=7734
  납부유예      = 1세대 1주택 · 60세 이상 또는 5년 이상 보유 · 총급여 7천만 이하 또는 종합소득금액 6천만 이하
                  · 주택분 세액 100만 초과 · 납부기한 만료 3일 전까지 신청(법 제20조의2①)
                  https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280417&joNo=0020&joBrNo=02&docCls=jo&urlMode=lsScJoRltInfoR
  기한 특례     = 기한이 토·일요일·공휴일이면 그 다음 날(국세기본법 제5조①)
                  https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=289999&joNo=0005&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  과세표준      = (공시가격 합계 − 공제 12억(1세대 1주택)·9억(그 밖)) × 공정시장가액비율 60%, 0보다 작으면 0
                  종합부동산세법 제8조① · 국세청 세액계산 흐름도
                  https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280417&joNo=0008&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
                  https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?mi=2353&cntntsId=7735
  세율(2주택 이하) = 과세표준 × 세율 − 누진공제(국세청 세액계산 흐름도 글자 표, 법 제9조①1호 표는 그림)
  미납 가산세   = 지정납부기한까지 미납액 × 100분의 3(국세기본법 제47조의4①3호, 시행 2026. 10. 2.)
                  https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=289999&joNo=0047&joBrNo=04&docCls=jo&urlMode=lsScJoRltInfoR
  아래 세액은 재산세 상당액 공제·1세대 1주택 세액공제·세부담상한 전 금액이다(그 셋은 사람마다 달라 빼지 않았다).
기준일: 2026-10-04 원문 기준. 같은 입력이면 같은 출력. 실행하면 원고에 넣을 표를 마크다운으로 찍는다.
"""
import datetime as dt

YEAR = 2026
PAY_START = dt.date(YEAR, 12, 1)            # 제16조①
PAY_END = dt.date(YEAR, 12, 15)             # 제16조①
NOTICE_DAYS = 5                             # 제16조② 개시 5일 전까지
SPLIT_MIN = 2_500_000                       # 제20조 250만원 초과
SPLIT_MID = 5_000_000                       # 시행령 제16조① 500만원
SPLIT_RATE = 50                             # 시행령 제16조①2호 100분의 50
SPLIT_MONTHS = 6                            # 제20조 6개월 이내
RURAL_RATE = 20                             # 농어촌특별세 20%
DEFER_AGE = 60                              # 제20조의2①2호
DEFER_HOLD = 5                              # 제20조의2①2호
DEFER_WAGE = 70_000_000                     # 제20조의2①3호 가목
DEFER_INCOME = 60_000_000                   # 제20조의2①3호 나목
DEFER_TAX = 1_000_000                       # 제20조의2①4호
DEFER_DAYS = 3                              # 제20조의2① 만료 3일 전
DED_ONE = 1_200_000_000                     # 제8조① 1세대 1주택 12억
DED_GEN = 900_000_000                       # 제8조① 그 밖 9억
FMV = 60                                    # 공정시장가액비율 주택분 60%
LATE_RATE = 3                               # 국세기본법 제47조의4①3호 100분의 3
# (과세표준 상한, 세율 ‰ 단위 ×10, 누진공제) — 2주택 이하
BANDS = [(300_000_000, 5, 0), (600_000_000, 7, 600_000), (1_200_000_000, 10, 2_400_000),
         (2_500_000_000, 13, 6_000_000), (5_000_000_000, 15, 11_000_000),
         (9_400_000_000, 20, 36_000_000), (None, 27, 101_800_000)]
WD = "월화수목금토일"
EOK, MAN = 100_000_000, 10_000


def kday(d):
    return f"{d.year}년 {d.month}월 {d.day}일({WD[d.weekday()]})"


def next_weekday(d):
    """국세기본법 제5조①: 토·일요일이면 그 다음 날(공휴일은 따로 확인)."""
    while d.weekday() >= 5:
        d += dt.timedelta(days=1)
    return d


def add_months(d, n):
    m = d.month - 1 + n
    return dt.date(d.year + m // 12, m % 12 + 1, d.day)


def schedule():
    notice = PAY_START - dt.timedelta(days=NOTICE_DAYS)
    defer = PAY_END - dt.timedelta(days=DEFER_DAYS)
    split_end = add_months(PAY_END, SPLIT_MONTHS)
    return {"notice": notice, "start": PAY_START, "end": next_weekday(PAY_END), "defer_raw": defer,
            "defer": next_weekday(defer), "split_end": next_weekday(split_end)}


def split_max(bill):
    """시행령 제16조①: 분납할 수 있는 최대 금액."""
    if bill <= SPLIT_MIN:
        return 0
    if bill <= SPLIT_MID:
        return bill - SPLIT_MIN
    return bill * SPLIT_RATE // 100


def split_plan(bill):
    s = split_max(bill)
    rural = bill * RURAL_RATE // 100
    rural_s = rural * s // bill if bill else 0
    return {"bill": bill, "split": s, "dec": bill - s, "rural": rural, "rural_split": rural_s,
            "rural_dec": rural - rural_s, "dec_total": bill - s + rural - rural_s, "jun_total": s + rural_s}


def tax_base(official_sum, one_house):
    ded = DED_ONE if one_house else DED_GEN
    return max(0, official_sum - ded) * FMV // 100


def gross_tax(base):
    for top, r10, cut in BANDS:
        if top is None or base <= top:
            return base * r10 // 1000 - cut, r10, cut
    raise ValueError


def compute(official_sum, one_house):
    base = tax_base(official_sum, one_house)
    tax, r10, cut = gross_tax(base)
    return {"base": base, "rate_x10": r10, "cut": cut, "tax": tax, "split": split_max(tax)}


def won(v):
    return f"{v:,}원"


def man(v):
    """원 → 「1억 8,000만원」·「276만원」 꼴(만원 미만은 원 그대로)."""
    if v % MAN:
        return won(v)
    e, m = divmod(v // MAN, EOK // MAN)
    if e and m:
        return f"{e}억 {m:,}만원"
    if e:
        return f"{e}억원"
    return f"{m:,}만원"


def pct(r10):
    return f"{r10 / 10:.1f}%"


CASES = [("1세대 1주택", 1_500_000_000, True), ("1세대 1주택", 2_000_000_000, True),
         ("1세대 1주택", 3_000_000_000, True), ("2주택(합계)", 1_500_000_000, False),
         ("2주택(합계)", 2_000_000_000, False)]
BILLS = [2_000_000, 2_760_000, 4_000_000, 5_000_000, 8_400_000, 12_000_000]


def main():
    s = schedule()
    print("표: 2026년 종합부동산세 날짜(원문 조문으로 센 날)")
    print("| 할 일 | 날짜 | 근거 |")
    print("|---|---|---|")
    print(f"| 고지서 발급 기한 | {kday(s['notice'])}까지 | 납부기간 개시 {NOTICE_DAYS}일 전 |")
    print(f"| 납부(고지분) | {kday(s['start'])} ~ {kday(s['end'])} | 해당 연도 12월 1일~15일 |")
    print(f"| 신고납부를 고른 경우 신고·납부 | {kday(s['start'])} ~ {kday(s['end'])} | 같은 기간 |")
    print(f"| 납부유예 신청 | 만료 {DEFER_DAYS}일 전 = {kday(s['defer_raw'])} → 기한 특례로 {kday(s['defer'])} | 토요일이면 다음 날 |")
    print(f"| 분납분 납부 | {kday(s['split_end'])}까지(수정 고지서 날짜) | 납부기한이 지난 날부터 {SPLIT_MONTHS}개월 이내 |")
    print()
    print("표: 고지 세액별 12월과 이듬해 6월에 나눠 내는 금액(농어촌특별세 포함)")
    print("| 고지 종부세 | 분납 가능 최대 | 12월 종부세 | 농특세(20%) | 농특세 중 분납 | 12월 합계 | 6월 합계 |")
    print("|---|---|---|---|---|---|---|")
    for b in BILLS:
        p = split_plan(b)
        print(f"| {won(b)} | {won(p['split'])} | {won(p['dec'])} | {won(p['rural'])} | {won(p['rural_split'])} "
              f"| {won(p['dec_total'])} | {won(p['jun_total'])} |")
    print()
    print("표: 공시가격 합계별 주택분 과세표준과 세율 적용 세액(재산세 공제·세액공제·세부담상한 전)")
    print("| 구분 | 공시가격 합계 | 공제 | 과세표준(60%) | 세율 | 누진공제 | 세율 적용 세액 | 분납 가능 최대 |")
    print("|---|---|---|---|---|---|---|---|")
    for name, amt, one in CASES:
        c = compute(amt, one)
        print(f"| {name} | {man(amt)} | {man(DED_ONE if one else DED_GEN)} | {man(c['base'])} | {pct(c['rate_x10'])} "
              f"| {man(c['cut']) if c['cut'] else '없음'} | {man(c['tax'])} | {man(c['split']) if c['split'] else '없음(250만원 이하)'} |")
    print()
    print("표: 분납과 납부유예 조건 나란히(종합부동산세법 제20조·제20조의2)")
    print("| 항목 | 분납 | 납부유예 |")
    print("|---|---|---|")
    print(f"| 세액 조건 | {man(SPLIT_MIN)} 초과 | 주택분 {man(DEFER_TAX)} 초과 |")
    print("| 사람 조건 | 없음 | 1세대 1주택자 |")
    print(f"| 나이·보유 | 없음 | 만 {DEFER_AGE}세 이상 또는 {DEFER_HOLD}년 이상 보유 |")
    print(f"| 소득 | 없음 | 총급여 {man(DEFER_WAGE)} 이하 또는 종합소득금액 {man(DEFER_INCOME)} 이하 |")
    print(f"| 담보 | 없음 | 유예 세액 상당 담보 제공 |")
    print(f"| 신청 기한 | 납부기한까지 신청서 | 납부기한 만료 {DEFER_DAYS}일 전까지 |")
    print(f"| 미루는 기간 | 납부기한 뒤 {SPLIT_MONTHS}개월 이내 | 양도·증여·상속 등 취소 사유가 생길 때까지 |")
    print()
    print("참고 숫자")
    one20 = compute(2_000_000_000, True)
    late = one20["tax"] * LATE_RATE // 100
    print(f"- 1세대 1주택 20억원 예시 세액 {won(one20['tax'])} · 분납 {won(one20['split'])} · 12월 {won(one20['tax'] - one20['split'])}")
    print(f"- 같은 세액을 기한까지 안 내면 {LATE_RATE}% 가산세 {won(late)}")
    p4 = split_plan(4_000_000)
    print(f"- 400만원 고지: 12월 {won(p4['dec_total'])} · 6월 {won(p4['jun_total'])} · 농특세 {won(p4['rural'])}")
    print(f"- 한 달로 풀면: 276만원 = 한 달 약 {round(one20['tax'] / 12 / MAN)}만원")


if __name__ == "__main__":
    main()
