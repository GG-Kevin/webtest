#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""결혼 증여세 면제(혼인 증여재산 공제) 계산 — B1004-1 편 1 · 표준 라이브러리만.

입력
  amount      이번에 받은 금액(원)
  giver       "직계존속"(부모·조부모 등) | "인척"(배우자의 부모 등 3촌 이내 인척)
  prior_10y   같은 직계존속(부모는 아버지·어머니를 한 사람으로 본다)에게서 이번 증여 전 10년 안에 받은 금액(원)
  in_window   증여일이 혼인일(혼인관계증명서상 신고일) 앞뒤 2년 안인가(True/False)
  minor       받는 사람이 미성년자인가(이 글의 예시는 모두 성년)

공식
  과세가액   = amount + prior_10y                          (상증법 제47조 제2항: 10년 안 동일인 증여 1천만원 이상이면 더함)
  일반 공제  = 직계존속 5천만원(미성년 2천만원) · 인척 1천만원, 10년 누계 한도 (제53조 제2호·제4호)
  혼인 공제  = 직계존속 + 혼인일 앞뒤 2년 → 이번 증여분에서 최대 1억원, 평생 누계 1억원, 출산 공제와 합쳐 1억원 (제53조의2 제1항·제3항)
  과세표준   = 과세가액 − 일반 공제 − 혼인 공제(0 아래면 0)
  산출세액   = 과세표준 1억 이하 10% · 5억 이하 1천만원+1억 초과분 20% · 10억 이하 9천만원+5억 초과분 30%
               · 30억 이하 2억4천만원+10억 초과분 40% · 30억 초과 10억4천만원+30억 초과분 50% (제56조 → 제26조)
  신고세액공제 = 산출세액 × 3/100, 원 아래 버림 (제69조 제2항) — 이 글의 예시는 앞선 증여의 세액이 0원이라 기납부세액은 없다
  납부할 세액 = 산출세액 − 신고세액공제
  신고기한   = 증여받은 날이 속하는 달의 말일부터 3개월 이내 → 3개월 뒤 달의 말일, 토·일이면 다음 월요일 (제68조 제1항,
               국세청 「신고시 유의사항」: 공휴일·토요일이면 다음 날). 예시 날짜는 공휴일과 겹치지 않는 날로 골랐다.
  미혼 수정신고 기한(가산세 전부·일부 면제, 이자상당액 가산) = 첫 증여일부터 2년이 되는 날이 속하는 달의 말일부터 3개월이 되는 날 (제53조의2 제6항)

원문(조문 본문 주소) — 2026-10-03 열람, 상속세 및 증여세법 [시행 2025. 10. 1.] [법률 제21065호]
  제53조의2 https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=276123&joNo=0053&joBrNo=02&docCls=jo&urlMode=lsScJoRltInfoR
  제53조   https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=276123&joNo=0053&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  제47조   https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=276123&joNo=0047&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  제26조   https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=276123&joNo=0026&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  제56조   https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=276123&joNo=0056&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  제68조   https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=276123&joNo=0068&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  제69조   https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=276123&joNo=0069&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  국세청 증여세 신고시 유의사항 https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?mi=2342&cntntsId=7730
기준일: 2026-10-03(원문 연 날)
"""
import calendar
import datetime as dt

EOK = 100_000_000
MAN = 10_000

GEN_LIMIT = {"직계존속": 50_000_000, "인척": 10_000_000}  # 제53조 제2호·제4호
MINOR_LIMIT = 20_000_000                                   # 제53조 제2호 단서
MARRIAGE_LIMIT = 100_000_000                               # 제53조의2 제1항·제3항
BRACKETS = [  # (상한, 누진 기본액, 아래 경계, 세율) — 제26조
    (1 * EOK, 0, 0, 0.10),
    (5 * EOK, 10_000_000, 1 * EOK, 0.20),
    (10 * EOK, 90_000_000, 5 * EOK, 0.30),
    (30 * EOK, 240_000_000, 10 * EOK, 0.40),
    (None, 1_040_000_000, 30 * EOK, 0.50),
]
FILING_CREDIT = 3 / 100  # 제69조 제2항


def gift_tax(base):
    if base <= 0:
        return 0, "-"
    for cap, fixed, low, rate in BRACKETS:
        if cap is None or base <= cap:
            return int(fixed + (base - low) * rate), f"{int(rate * 100)}%"


def compute(amount, giver="직계존속", prior_10y=0, in_window=True, minor=False):
    taxable = amount + prior_10y
    gen_cap = MINOR_LIMIT if (minor and giver == "직계존속") else GEN_LIMIT[giver]
    gen = min(gen_cap, taxable)
    mar = min(MARRIAGE_LIMIT, amount) if (giver == "직계존속" and in_window) else 0
    mar = min(mar, max(0, taxable - gen))
    base = max(0, taxable - gen - mar)
    tax, rate = gift_tax(base)
    credit = int(tax * FILING_CREDIT)
    return {"과세가액": taxable, "일반공제": gen, "혼인공제": mar, "공제합계": gen + mar,
            "과세표준": base, "세율": rate, "산출세액": tax, "신고세액공제": credit, "납부세액": tax - credit}


def won(v):
    return f"{v:,}원"


def man(v):
    """1억 5,000만원 꼴"""
    if v == 0:
        return "0원"
    e, m = divmod(v // MAN, 10_000)
    if e and m:
        return f"{e}억 {m:,}만원"
    if e:
        return f"{e}억원"
    return f"{m:,}만원"


def month_end_plus(d, months):
    y, m = d.year, d.month + months
    y, m = y + (m - 1) // 12, (m - 1) % 12 + 1
    return dt.date(y, m, calendar.monthrange(y, m)[1])


def next_weekday(d):
    while d.weekday() >= 5:
        d += dt.timedelta(days=1)
    return d


WD = "월화수목금토일"


def ko(d):
    return f"{d.year}년 {d.month}월 {d.day}일({WD[d.weekday()]})"


def main():
    amounts = [5_000 * MAN, 1 * EOK, 15_000 * MAN, 2 * EOK, 3 * EOK]

    print("표: 부모에게 받은 금액별 증여세(혼인신고일 앞뒤 2년 안, 성년 자녀, 10년 안 다른 증여 없음)")
    print("| 받은 금액 | 공제 합계 | 과세표준 | 세율 구간 | 산출세액 | 신고세액공제 3% | 납부할 세액 |")
    print("|---|---|---|---|---|---|---|")
    for a in amounts:
        r = compute(a)
        print(f"| {man(a)} | {man(r['공제합계'])} | {man(r['과세표준'])} | {r['세율']} | {won(r['산출세액'])} | {won(r['신고세액공제'])} | {won(r['납부세액'])} |")
    print()

    print("표: 혼인 공제가 있을 때와 없을 때의 납부할 세액 차이(부모 증여, 성년 자녀)")
    print("| 받은 금액 | 혼인 공제 없음 | 혼인 공제 있음 | 줄어드는 세금 | 받은 금액 대비 |")
    print("|---|---|---|---|---|")
    for a in amounts:
        w = compute(a, in_window=False)["납부세액"]
        y = compute(a)["납부세액"]
        print(f"| {man(a)} | {won(w)} | {won(y)} | {won(w - y)} | {(w - y) / a * 100:.1f}% |")
    print()

    print("표: 누가, 언제 주느냐에 따른 납부할 세액(계산 예시)")
    print("| 경우 | 받는 사람별 과세가액 | 공제 합계 | 납부할 세액 |")
    print("|---|---|---|---|")
    cases = [
        ("신랑이 자기 부모에게 1억 5,000만원", dict(amount=15_000 * MAN)),
        ("신부도 자기 부모에게 1억 5,000만원(부부 합 3억원)", dict(amount=15_000 * MAN)),
        ("신랑이 배우자의 부모에게 1억원", dict(amount=1 * EOK, giver="인척")),
        ("10년 안 부모에게 3,000만원을 받은 뒤 1억 5,000만원", dict(amount=15_000 * MAN, prior_10y=3_000 * MAN)),
        ("혼인신고 3년 전 부모에게 1억 5,000만원", dict(amount=15_000 * MAN, in_window=False)),
    ]
    for name, kw in cases:
        r = compute(**kw)
        print(f"| {name} | {man(r['과세가액'])} | {man(r['공제합계'])} | {won(r['납부세액'])} |")
    r = compute(15_000 * MAN, prior_10y=3_000 * MAN)
    print()
    print(f"(10년 합산 예시 풀이: 과세가액 {won(r['과세가액'])} − 공제 {won(r['공제합계'])} = 과세표준 {won(r['과세표준'])}, "
          f"산출세액 {won(r['산출세액'])} − 신고세액공제 {won(r['신고세액공제'])} = {won(r['납부세액'])})")
    rp = compute(1 * EOK, giver="인척")
    print(f"(인척 예시 풀이: 과세표준 {won(rp['과세표준'])} × 10% = {won(rp['산출세액'])}, 신고세액공제 {won(rp['신고세액공제'])})")
    print()

    print("표: 날짜로 본 신고기한과 수정신고 기한(계산 예시)")
    print("| 증여받은 날 | 이 날 기준으로 정해지는 기한 | 날짜 | 근거 |")
    print("|---|---|---|---|")
    for s in ["2026-10-20", "2026-12-05"]:
        d = dt.date.fromisoformat(s)
        raw = month_end_plus(d, 3)
        fin = next_weekday(raw)
        note = "" if raw == fin else f" (말일 {raw.month}월 {raw.day}일이 {WD[raw.weekday()]}요일)"
        print(f"| {ko(d)} | 증여세 신고·납부 기한 | {ko(fin)}{note} | 제68조 제1항 |")
    d = dt.date(2026, 10, 20)
    two = dt.date(d.year + 2, d.month, d.day)
    fix = month_end_plus(two, 3)
    print(f"| {ko(d)} (혼인 전, 공제 받음) | 2년 안에 혼인하지 않았을 때 가산세 감면을 받는 수정신고 마지막 날(이자상당액은 붙음) | {ko(fix)} (2년 되는 날 {ko(two)}) | 제53조의2 제6항 |")
    print()

    # 본문에 쓰는 숫자
    w15 = compute(15_000 * MAN, in_window=False)["납부세액"]
    print(f"본문: 혼인 공제가 없을 때 1억 5,000만원의 세금 {won(w15)} ÷ 12개월 = 한 달 약 {w15 // 12:,}원")
    r2 = compute(2 * EOK)
    print(f"본문: 2억원을 받을 때 납부할 세액 {won(r2['납부세액'])} = 받은 금액의 {r2['납부세액'] / (2 * EOK) * 100:.1f}%")
    used = 6_000 * MAN
    print(f"본문: 혼인 공제로 {man(used)}을 쓰면 출산 공제로 남는 한도 {man(MARRIAGE_LIMIT - used)} (통합 한도 {man(MARRIAGE_LIMIT)})")
    print()

    # 그림용 숫자
    print("그림 숫자: 받은 금액(만원) · 혼인 공제 없음 · 있음")
    for a in amounts:
        print(f"{a // MAN} {compute(a, in_window=False)['납부세액']} {compute(a)['납부세액']}")


if __name__ == "__main__":
    main()
