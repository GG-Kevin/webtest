#!/usr/bin/env python3
"""부가가치세 2026년 제2기 예정신고·예정고지 계산 (표준 라이브러리만, 같은 입력이면 같은 출력)

기준일: 2026-10-04 (아래 원문을 이날 열어 읽음)
원문:
- 부가가치세법 제48조(예정신고와 납부) ① 예정신고기간 끝난 후 25일 이내 신고 · ③ 개인사업자·소규모 법인은
  직전 과세기간 납부세액의 50퍼센트(1천원 미만 버림)를 고지·징수, 50만원 미만이면 징수하지 아니함 · ④ 사업 부진 등은 예정신고 가능
  본문 https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=276117&joNo=0048&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  (시행 2026. 1. 2. 법률 제21065호)
- 부가가치세법 시행령 제90조 ④ 고지 대상 법인 = 직전 과세기간 공급가액 합계 1억5천만원 미만 · ⑥ 1호 예정신고기간 공급가액 또는
  납부세액이 직전 과세기간의 3분의 1에 미달
  본문 https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=283641&joNo=0090&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  (시행 2026. 2. 27. 대통령령 제36133호)
- 국세청 세무일정 2026년 10월: 26일 「2026.2기 부가가치세 예정신고 납부」(국세기본법 제5조 — 토요일·공휴일이면 다음 날)
  https://www.nts.go.kr/nts/ad/taxSchdul/selectList.do?taxYear=2026&taxMonth=10&mi=135747
- 국세청 부가가치세 가산세: 일반 무신고 20%, 납부지연 1일 22/100,000
  https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?mi=2276&cntntsId=7697
- 국세기본법 제48조 ② 3호 라목: 예정신고를 하지 않았어도 확정신고기한까지 기한 후 신고하면 무신고가산세의 100분의 50 감면
  본문 https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=289999&joNo=0048&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  (시행 2026. 10. 2. 법률 제21987호)

공식:
- 기한: 9월 30일 + 25일 = 10월 25일 → 토·일이면 다음 월요일(공휴일 여부는 세무일정 원문으로 확인: 2026-10-26 월)
- 예정고지세액 = floor(직전 과세기간 납부세액 × 50 / 100 / 1,000) × 1,000, 결과가 500,000 미만이면 0(징수 안 함)
- 예정신고 선택 문턱 = 직전 과세기간(6개월) 공급가액 ÷ 3. 3개월 실적이 이보다 적으면 예정신고 가능
  → 월평균으로 바꾸면 직전 6개월 월평균의 2/3
- 가산세 예시(법인 일반과세자, 부정행위 아닌 무신고): 무신고 = 납부세액 × 20% → 확정신고기한까지 기한 후 신고면 50% 감면
  납부지연 = 납부세액 × 일수 × 22/100,000 (일수 = 기한 다음 날부터 납부일 전날까지), 원 미만 버림
"""
import datetime as dt

BASE_DATE = "2026-10-04"
PERIOD_END = dt.date(2026, 9, 30)      # 제2기 예정신고기간 7.1.~9.30.
DAYS_AFTER = 25                        # 제48조① 「25일 이내」
HALF_NUM, HALF_DEN = 50, 100           # 제48조③ 「50퍼센트」
CUT = 1000                             # 1천원 미만 버림
MIN_COLLECT = 500_000                  # 제48조③1 「50만원 미만」
CORP_LIMIT = 150_000_000               # 시행령 제90조④ 「1억5천만원 미만」
NONFILE_RATE = 20                      # 국세청 가산세: 일반 무신고 20%
LATE_NUM, LATE_DEN = 22, 100_000       # 1일 22/100,000
REDUCE_PCT = 50                        # 국기법 제48조②3라 100분의 50 감면


def deadline(period_end=PERIOD_END, days=DAYS_AFTER):
    d = period_end + dt.timedelta(days=days)
    raw = d
    while d.weekday() >= 5:            # 토(5)·일(6) → 다음 날
        d += dt.timedelta(days=1)
    return raw, d


def notice_tax(prev_tax):
    """직전 과세기간 납부세액 → (반액, 천원 미만 버린 고지세액, 실제 징수액)"""
    half = prev_tax * HALF_NUM / HALF_DEN
    cut = int(half // CUT) * CUT
    collect = cut if cut >= MIN_COLLECT else 0
    return half, cut, collect


def slump_line(prev_supply_6m):
    """직전 과세기간(6개월) 공급가액 → 3개월 문턱, 직전 월평균, 문턱 월평균"""
    th = prev_supply_6m / 3
    return th, prev_supply_6m / 6, th / 3


def penalty(tax, days):
    nonfile = tax * NONFILE_RATE // 100
    reduced = nonfile * (100 - REDUCE_PCT) // 100
    late = tax * days * LATE_NUM // LATE_DEN
    return nonfile, reduced, late


def won(x):
    return f"{int(x):,}"


if __name__ == "__main__":
    raw, dl = deadline()
    WD = "월화수목금토일"
    print(f"# 기준일 {BASE_DATE}")
    print(f"법정 기한 계산: {raw.isoformat()}({WD[raw.weekday()]}) → 실제 기한 {dl.isoformat()}({WD[dl.weekday()]})")
    print()

    print("표: 직전 과세기간 납부세액별 10월 예정고지세액(개인 일반과세자, 우리 계산)")
    print("| 2026년 1기(1~6월) 납부세액 | 절반(50%) | 1천원 미만 버림 | 10월 고지 여부 | 고지세액 |")
    print("|---|---|---|---|---|")
    CASES = [800_000, 999_000, 1_000_000, 1_001_999, 2_345_678, 6_000_000]
    for p in CASES:
        half, cut, col = notice_tax(p)
        half_s = f"{half:,.1f}" if half != int(half) else won(half)
        print(f"| {won(p)}원 | {half_s}원 | {won(cut)}원 | {'고지' if col else '징수 안 함(50만원 미만)'} | {won(col)}원 |")
    print()

    print("표: 직전 6개월 매출별 예정신고 선택 문턱(사업 부진 1/3 기준, 우리 계산)")
    print("| 직전 과세기간(6개월) 공급가액 | 직전 월평균 | 7~9월 합계 문턱(1/3) | 문턱의 월평균 |")
    print("|---|---|---|---|")
    for s in (60_000_000, 120_000_000, 300_000_000):
        th, m_prev, m_th = slump_line(s)
        print(f"| {won(s)}원 | {won(m_prev)}원 | {won(th)}원 | {won(m_th)}원 |")
    print(f"문턱 월평균 ÷ 직전 월평균 = {slump_line(120_000_000)[2] / slump_line(120_000_000)[1]:.4f} (= 2/3)")
    print()

    TAX = 10_000_000
    pay = dt.date(2027, 1, 25)
    days =(pay - (dl + dt.timedelta(days=1))).days
    nonfile, reduced, late = penalty(TAX, days)
    print("표: 법인이 예정신고를 놓치고 2027년 1월 25일에 기한 후 신고·납부한 경우(가정, 우리 계산)")
    print("| 항목 | 계산 | 금액 |")
    print("|---|---|---|")
    print(f"| 예정신고 납부세액(가정) | - | {won(TAX)}원 |")
    print(f"| 무신고가산세 | {won(TAX)}원 × {NONFILE_RATE}% | {won(nonfile)}원 |")
    print(f"| 확정신고기한 안 기한 후 신고 감면 | {won(nonfile)}원 × {REDUCE_PCT}% | -{won(nonfile - reduced)}원 |")
    print(f"| 납부지연가산세 | {won(TAX)}원 × {days}일 × 22/100,000 | {won(late)}원 |")
    print(f"| 가산세 합계 | - | {won(reduced + late)}원 |")
    print(f"납부지연 일수 = {days}일 (2026-10-27 ~ 2027-01-24)")
    print(f"하루 납부지연가산세 = {won(TAX * LATE_NUM // LATE_DEN)}원")
    print(f"법인 고지 문턱 = {won(CORP_LIMIT)}원")
