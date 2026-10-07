#!/usr/bin/env python3
"""상속세 공제 합산 순서와 상속세 계산 (B1011-1/2) — 표준 라이브러리만, 정수 계산.

입력(표마다 고정 예시, 가정은 원고 표 caption·본문에 적는다):
  estate     상속세 과세가액(원) — 이 글의 예시는 채무·장례비·사전증여·비과세 0이라 상속재산가액과 같다
  fin        순금융재산 가액(원, 예금 등 − 금융채무)
  spouse_got 배우자가 실제 상속받은 금액(원). None이면 배우자 없음
  kids       자녀 수 · minors 미성년 상속인의 나이 목록 · elders 65세 이상 동거가족 수
공식(순서):
  ① 기초공제 2억원                                     상증법 제18조
  ② 그 밖의 인적공제 = 자녀 1명 5천만원 + 미성년 1천만원×(19세까지 연수) + 65세 이상 5천만원
                                                      상증법 제20조 ①·③(1년 미만은 1년)
  ③ 일괄공제 = max(①+②, 5억원). 신고가 없으면 5억원. 배우자 단독 상속이면 ①+②만
                                                      상증법 제21조 ①·②
  ④ 배우자 상속공제 = 실제 상속분이 없거나 5억원 미만이면 5억원,
                     그 밖에는 min(실제 상속분, 과세가액 기준 금액×법정상속분 − 배우자 사전증여 과세표준, 30억원)
                                                      상증법 제19조 ①·④, 국세청 상속공제 항목별 설명(한도 산식)
     법정상속분: 배우자 1.5 : 자녀 각 1                민법 제1009조 ②
  ⑤ 금융재산 상속공제 = 순금융 2천만원 이하 전액, 초과면 max(20%, 2천만원), 2억원 한도
                                                      상증법 제22조 ①
  ⑥ 동거주택 상속공제 = 주택가액(담보채무 차감)의 100%, 6억원 한도 (이 글 예시는 해당 없음)
                                                      상증법 제23조의2 ①
  ⑦ 공제 합계 ≤ 공제적용 한도(과세가액 − 상속인 아닌 자 유증 − 후순위 상속분 − 가산 증여재산 과세표준)
                                                      상증법 제24조 (3호는 과세가액 5억원 초과 때만)
  ⑧ 과세표준 = 과세가액 − 공제(− 감정평가수수료 0)    상증법 제25조 ① · 50만원 미만 과세 없음 ②
  ⑨ 산출세액 = 제26조 세율(10/20/30/40/50%, 누진공제 0/1천만/6천만/1억6천만/4억6천만)
  ⑩ 신고세액공제 = 산출세액의 100분의 3              상증법 제69조 ①
  원 미만은 모두 버린다(배우자 법정상속분 금액·세액·세액공제).
  신고기한 = 상속개시일이 속하는 달의 말일부터 6개월(상증법 제67조 ①), 토·일이면 다음 날(공휴일은 따로 확인)
  배우자상속재산분할기한 = 신고기한 다음날부터 9개월이 되는 날(상증법 제19조 ②)
  사전증여재산 결정정보 제공 신청 = 신고기한 만료 14일 전까지(국세청 상속세 신고시 유의사항)
원문:
  상증법(시행 2025. 10. 1. 법률 제21065호) 조문 본문 주소
  https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=276123&joNo=0018&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR (joNo 0019·0020·0021·0022·0023-02·0024·0025·0026·0067·0069 같은 꼴)
  민법 제1009조 https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=284415&joNo=1009&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  국세청 상속공제 https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?mi=6528&cntntsId=7956
  국세청 세액계산흐름도 https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?mi=2326&cntntsId=7720
  국세청 신고시 유의사항 https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?mi=2328&cntntsId=7722
기준일: 2026-10-06 원문 기준. 같은 입력이면 같은 출력. 실행하면 원고에 넣을 표를 마크다운으로 찍는다.
"""
import calendar
import datetime as dt
from fractions import Fraction

EOK = 100_000_000
MAN = 10_000

BASIC = 2 * EOK              # 제18조 기초공제
CHILD = 5_000 * MAN          # 제20조①1 자녀 1명
MINOR_PER_YEAR = 1_000 * MAN  # 제20조①2 미성년 1년당
MINOR_AGE = 19
ELDER = 5_000 * MAN          # 제20조①3 65세 이상
LUMP = 5 * EOK               # 제21조 일괄공제
SPOUSE_MIN = 5 * EOK         # 제19조④
SPOUSE_CAP = 30 * EOK        # 제19조①2
FIN_FLOOR = 2_000 * MAN      # 제22조 2천만원
FIN_RATE = Fraction(20, 100)  # 100분의 20
FIN_CAP = 2 * EOK            # 2억원
HOUSE_CAP = 6 * EOK          # 제23조의2 6억원
FILE_CREDIT = Fraction(3, 100)  # 제69조 100분의 3
BRACKETS = [(1 * EOK, 10, 0), (5 * EOK, 20, 1_000 * MAN), (10 * EOK, 30, 6_000 * MAN),
            (30 * EOK, 40, 16_000 * MAN), (None, 50, 46_000 * MAN)]  # 제26조 · 국세청 흐름도 누진공제액


def personal(kids=0, minors=(), elders=0):
    """제20조 그 밖의 인적공제 — minors는 미성년 상속인의 만 나이(남은 기간 1년 미만은 1년)."""
    return kids * CHILD + sum(MINOR_PER_YEAR * max(1, MINOR_AGE - a) for a in minors) + elders * ELDER


def lump(kids=0, minors=(), elders=0, filed=True, spouse_alone=False):
    """제21조 — (기초 + 인적)과 5억원 중 큰 금액."""
    p = BASIC + personal(kids, minors, elders)
    if spouse_alone:
        return p
    if not filed:
        return LUMP
    return max(p, LUMP)


def spouse_share(kids):
    """민법 제1009조② — 배우자 1.5 : 자녀 각 1."""
    return Fraction(3, 2) / (Fraction(3, 2) + kids)


def spouse_ded(estate, got, kids, prior_gift_base=0):
    """제19조 — 5억원 ~ min(실제, 법정상속분 한도, 30억원)."""
    if got is None:
        return 0
    if got < SPOUSE_MIN:
        return SPOUSE_MIN
    limit = int(estate * spouse_share(kids)) - prior_gift_base
    return max(SPOUSE_MIN, min(got, limit, SPOUSE_CAP))


def fin_ded(fin):
    """제22조①."""
    if fin <= 0:
        return 0
    if fin <= FIN_FLOOR:
        return fin
    return min(max(int(fin * FIN_RATE), FIN_FLOOR), FIN_CAP)


def tax(base):
    """제26조 산출세액(원 미만 버림)."""
    if base < 50 * MAN:  # 제25조② 과세최저한
        return 0
    for top, rate, sub in BRACKETS:
        if top is None or base <= top:
            return base * rate // 100 - sub
    raise ValueError


def compute(estate, fin, spouse_got, kids, minors=(), elders=0):
    lp = lump(kids, minors, elders)
    sp = spouse_ded(estate, spouse_got, kids)
    fd = fin_ded(fin)
    total = min(lp + sp + fd, estate)  # 제24조 — 이 글 예시는 유증·후순위·사전증여 0이라 한도 = 과세가액
    base = estate - total
    t = tax(base)
    credit = int(t * FILE_CREDIT)
    return {"일괄공제": lp, "배우자공제": sp, "금융재산공제": fd, "공제합계": total,
            "과세표준": base, "산출세액": t, "신고세액공제": credit, "납부세액": t - credit}


def won(v):
    return f"{v:,}원"


def eok(v):
    """억·만원 표기(만원 미만 버림 표시용)."""
    e, r = divmod(v, EOK)
    m = r // MAN
    if e and m:
        return f"{e}억 {m:,}만원"
    if e:
        return f"{e}억원"
    return f"{m:,}만원"


def month_end_plus(d, months):
    y, m = d.year, d.month + months
    y += (m - 1) // 12
    m = (m - 1) % 12 + 1
    return dt.date(y, m, calendar.monthrange(y, m)[1])


def add_months_minus1(start, months):
    """민법 기간 계산: start부터 n개월이 되는 날 = n개월 뒤 같은 날의 전날."""
    y, m = start.year, start.month + months
    y += (m - 1) // 12
    m = (m - 1) % 12 + 1
    day = min(start.day, calendar.monthrange(y, m)[1])
    return dt.date(y, m, day) - dt.timedelta(days=1)


def next_weekday(d):
    while d.weekday() >= 5:
        d += dt.timedelta(days=1)
    return d


WD = "월화수목금토일"

# ── 표 1: 일괄공제 5억원 vs 기초 + 인적공제 ──
CASES1 = [
    ("성인 자녀 2명", dict(kids=2)),
    ("성인 자녀 1명 + 12세 자녀 1명", dict(kids=2, minors=(12,))),
    ("자녀 3명 + 65세 이상 동거 부모 1명", dict(kids=3, elders=1)),
    ("자녀 4명 중 5세·8세 미성년 2명", dict(kids=4, minors=(5, 8))),
]

# ── 표 2·3: 배우자 + 성인 자녀 2명, 금융재산은 상속재산의 20% ──
MAIN_ESTATE = 15 * EOK
MAIN_FIN = 3 * EOK
ESTATES = [10 * EOK, 15 * EOK, 20 * EOK, 30 * EOK, 50 * EOK]


def main():
    print("## 표 1 — 일괄공제와 기초+인적공제 비교")
    print("| 가족 구성 | 기초공제 | 그 밖의 인적공제 | 둘의 합 | 실제 공제(큰 쪽) |")
    print("|---|---|---|---|---|")
    for name, kw in CASES1:
        p = personal(**kw)
        print(f"| {name} | 2억원 | {eok(p)} | {eok(BASIC + p)} | {eok(lump(**kw))} |")
    print()
    print(f"미성년 12세 = {MINOR_AGE - 12}년 × 1천만원 = {eok(MINOR_PER_YEAR * 7)} · 5세 {MINOR_AGE - 5}년 = {eok(MINOR_PER_YEAR * 14)} · 8세 {MINOR_AGE - 8}년 = {eok(MINOR_PER_YEAR * 11)}")
    print()

    a = int(MAIN_ESTATE * spouse_share(2))
    A = compute(MAIN_ESTATE, MAIN_FIN, a, 2)
    B = compute(MAIN_ESTATE, MAIN_FIN, 0, 2)
    C = compute(MAIN_ESTATE, MAIN_FIN, None, 2)
    print("## 표 2 — 상속재산 15억원(아파트 12억원 + 예금 3억원), 성인 자녀 2명")
    print(f"배우자 법정상속분 = 3/7 → {won(a)} · 자녀 각 2/7 → {won(int(MAIN_ESTATE * Fraction(2, 7)))}")
    print("| 단계 | 배우자가 법정상속분 상속 | 배우자 상속분 0원 | 배우자 없음 |")
    print("|---|---|---|---|")
    print(f"| 상속세 과세가액 | {won(MAIN_ESTATE)} | {won(MAIN_ESTATE)} | {won(MAIN_ESTATE)} |")
    for k in ["일괄공제", "배우자공제", "금융재산공제", "공제합계", "과세표준", "산출세액", "신고세액공제", "납부세액"]:
        print(f"| {k} | {won(A[k])} | {won(B[k])} | {won(C[k])} |")
    print()
    print(f"A−B 차이 {won(B['납부세액'] - A['납부세액'])} · B−C 차이 {won(C['납부세액'] - B['납부세액'])}")
    print(f"A 납부세액 ÷ 15억 = {A['납부세액'] * 1000 // MAIN_ESTATE / 10}% · ÷ 3인 = {won(A['납부세액'] // 3)}")
    print(f"A 과세표준 2억원 구간 산식: {won(A['과세표준'])} × 20% − 1,000만원 = {won(A['산출세액'])}")
    print()

    print("## 표 3 — 상속재산 규모별 납부세액(신고세액공제 3% 뺀 뒤), 성인 자녀 2명, 금융재산 20%")
    print("| 상속재산 | 배우자가 법정상속분 상속 | 배우자 상속분 0원 | 배우자 없음 |")
    print("|---|---|---|---|")
    rows = []
    for e in ESTATES:
        f = e // 5
        sa = int(e * spouse_share(2))
        ra = compute(e, f, sa, 2)
        rb = compute(e, f, 0, 2)
        rc = compute(e, f, None, 2)
        rows.append((e, ra, rb, rc, sa))
        print(f"| {eok(e)} | {won(ra['납부세액'])} | {won(rb['납부세액'])} | {won(rc['납부세액'])} |")
    print()
    for e, ra, rb, rc, sa in rows:
        print(f"{eok(e)}: 배우자 법정분 {won(sa)} · 배우자공제 {won(ra['배우자공제'])} · 금융 {won(ra['금융재산공제'])} · 과표 A {won(ra['과세표준'])} B {won(rb['과세표준'])} C {won(rc['과세표준'])}")
    print()

    # 본문 보조 숫자
    print("## 본문 보조 숫자")
    print(f"배우자 법정분이 30억원 상한에 닿는 상속재산 = 30억 ÷ 3/7 = {eok(int(SPOUSE_CAP / spouse_share(2)))}")
    print(f"50억원의 배우자 법정분 약 {eok(int(50 * EOK * spouse_share(2)))}")
    print(f"신고 없을 때 덜 받는 공제(자녀 4명·미성년 2명) = {eok(lump(4, (5, 8)) - LUMP)}")
    gift, gift_ded, est = 5 * EOK, 5_000 * MAN, 8 * EOK
    lim = est - (gift - gift_ded)
    print(f"제24조 한도 예: 과세가액 {eok(est)} − (사전증여 {eok(gift)} − 증여공제 {eok(gift_ded)}) = {eok(lim)} · 일괄+배우자 {eok(LUMP + SPOUSE_MIN)} 중 {eok(lim)}만")
    print(f"순금융재산 1억원 공제 {eok(fin_ded(1 * EOK))} · 10억원 공제 {eok(fin_ded(10 * EOK))}")
    print(f"15억원 A안 1인당 = {eok(A['납부세액'] // 3)}(약) · B안 {eok(B['납부세액'])} · C안 {eok(C['납부세액'])} · C안 공제 {eok(C['공제합계'])}")
    print()

    # 기한 예시
    death = dt.date(2026, 11, 20)
    due = month_end_plus(death, 6)
    due2 = next_weekday(due)
    split = add_months_minus1(due + dt.timedelta(days=1), 9)
    split2 = next_weekday(split)
    req = due - dt.timedelta(days=14)
    old6 = add_months_minus1(due + dt.timedelta(days=1), 6)
    print("## 기한 예시 — 상속개시일 2026-11-20")
    print(f"신고기한 {due}({WD[due.weekday()]}) → {due2}")
    print(f"배우자상속재산분할기한(9개월) {split}({WD[split.weekday()]}) → {split2}")
    print(f"(옛 6개월로 셌다면 {old6}({WD[old6.weekday()]}))")
    print(f"사전증여재산 결정정보 제공 신청 마감(만료 14일 전) {req}({WD[req.weekday()]})")


if __name__ == "__main__":
    main()
