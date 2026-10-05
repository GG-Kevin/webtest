#!/usr/bin/env python3
"""연말정산 의료비 세액공제 계산 (B1009-1/1) — 표준 라이브러리만.

입력(표마다 고정 예시, 가정은 표 아래 문장으로 적는다):
  wage      총급여액(원, 비과세 소득을 뺀 근로소득)
  general   제1호 의료비 — 아래 제2~4호에 들지 않는 기본공제대상자(예: 64세 이하 배우자·자녀 7세 이상)
  special   제2호 의료비 — 근로자 본인 · 과세기간 개시일 현재 6세 이하 · 종료일 현재 65세 이상 · 장애인 ·
            중증질환자·희귀난치성질환자·결핵환자
  preterm   제3호 의료비 — 미숙아·선천성이상아
  ivf       제4호 의료비 — 난임시술비(관련 처방 의약품 포함)
공식(소득세법 제59조의4 제2항, 법률 제21221호 · 시행 2026. 1. 1.):
  문턱 T = 총급여 × 100분의 3
  제1호 대상 = min(max(general − T, 0), 700만원)            미달액 s1 = max(T − general, 0)
  제2호 대상 = max(special − s1, 0)                          미달액 s2 = max(s1 − special, 0)
  제3호 대상 = max(preterm − s2, 0)                          미달액 s3 = max(s2 − preterm, 0)
  제4호 대상 = max(ivf − s3, 0)
  소득세 공제 = (제1호 + 제2호) × 15% + 제3호 × 20% + 제4호 × 30%   (원 미만 버림)
  https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280405&joNo=0059&joBrNo=04&docCls=jo&urlMode=lsScJoRltInfoR
  안경·콘택트렌즈 1명당 연 50만원 · 산후조리원 출산 1회당 200만원 · 실손의료보험금 제외
  = 소득세법 시행령 제118조의5 제1항(대통령령 제36737호 · 시행 2026. 10. 1.)
  https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=290841&joNo=0118&joBrNo=05&docCls=jo&urlMode=lsScJoRltInfoR
  지방소득세 = 원천징수 소득세의 100분의 10(지방세법 제103조의13 ①) → 소득세 공제액의 10%만큼 함께 줄어든다
  https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=282559&joNo=0103&joBrNo=13&docCls=jo&urlMode=lsScJoRltInfoR
  산출세액 한도 = 의료비 등 특별세액공제 합이 근로소득 산출세액을 넘으면 넘는 금액은 없는 것(소득세법 제61조 ①)
  https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280405&joNo=0061&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
가정: 표의 공제액은 산출세액이 공제액보다 크다고 놓은 값이다(제61조 한도에 걸리지 않는 경우).
기준일: 2026-10-05 원문 기준. 같은 입력이면 같은 출력. 실행하면 원고에 넣을 표를 마크다운으로 찍는다.
"""

THRESHOLD_PCT = 3            # 총급여액의 100분의 3
GENERAL_CAP = 7_000_000      # 제1호 연 700만원
RATE_BASE = 15               # 100분의 15
RATE_PRETERM = 20            # 100분의 20(미숙아·선천성이상아)
RATE_IVF = 30                # 100분의 30(난임시술)
GLASSES_CAP = 500_000        # 안경·콘택트렌즈 1명당 연 50만원
POSTNATAL_CAP = 2_000_000    # 산후조리원 출산 1회당 200만원
LOCAL_PCT = 10               # 지방소득세 100분의 10
AGE_YOUNG = 6                # 개시일 현재 6세 이하
AGE_OLD = 65                 # 종료일 현재 65세 이상


def won(v):
    return f"{int(v):,}원"


def man(v):
    """만원 단위 표기(소수 한 자리까지)."""
    if v == 0:
        return "0원"
    if v >= 100_000_000 and v % 100_000_000 == 0:
        return f"{int(v) // 100_000_000}억원"
    x = v / 10_000
    return f"{x:,.0f}만원" if abs(x - round(x)) < 1e-9 else f"{x:,.1f}만원"


def threshold(wage):
    return wage * THRESHOLD_PCT // 100


def credit(wage, general=0, special=0, preterm=0, ivf=0):
    """소득세법 제59조의4 ② 순서대로 계산한다. 결과 dict."""
    t = threshold(wage)
    b1 = min(max(general - t, 0), GENERAL_CAP)
    s1 = max(t - general, 0)
    b2 = max(special - s1, 0)
    s2 = max(s1 - special, 0)
    b3 = max(preterm - s2, 0)
    s3 = max(s2 - preterm, 0)
    b4 = max(ivf - s3, 0)
    tax = ((b1 + b2) * RATE_BASE + b3 * RATE_PRETERM + b4 * RATE_IVF) // 100
    local = tax * LOCAL_PCT // 100
    return {"문턱": t, "제1호": b1, "제2호": b2, "제3호": b3, "제4호": b4,
            "차감1": general - b1 if general else 0,
            "소득세": tax, "지방소득세": local, "합계": tax + local}


def table_rules():
    print("표: 의료비 구분별 공제율과 한도(2026년 10월 5일 현행 조문)")
    print("| 누구의 의료비 | 공제율 | 한도 |")
    print("|---|---|---|")
    print(f"| 아래 칸에 들지 않는 기본공제대상자(예: 12월 31일 현재 64세 이하 배우자, 1월 1일 현재 7세 이상 자녀) | {RATE_BASE}% | 연 {man(GENERAL_CAP)} |")
    print(f"| 근로자 본인, 1월 1일 현재 {AGE_YOUNG}세 이하, 12월 31일 현재 {AGE_OLD}세 이상, 장애인, 중증·희귀난치성질환자, 결핵환자 | {RATE_BASE}% | 없음 |")
    print(f"| 미숙아·선천성이상아 | {RATE_PRETERM}% | 없음 |")
    print(f"| 난임시술비(관련 처방 약값 포함) | {RATE_IVF}% | 없음 |")
    print(f"| 안경·콘택트렌즈(위 구분 안에서) | 그 사람의 공제율 | 1명당 연 {man(GLASSES_CAP)} |")
    print(f"| 산후조리원(위 구분 안에서) | 그 사람의 공제율 | 출산 1회당 {man(POSTNATAL_CAP)} |")
    print()


EXAMPLES = [(40_000_000, 3_000_000), (40_000_000, 5_000_000), (60_000_000, 3_000_000), (60_000_000, 5_000_000)]


def table_examples():
    print("표: 총급여·의료비별 공제액 직접 계산(실손보험금 없음, 산출세액이 공제액보다 큰 경우)")
    print("| 총급여 | 1년 의료비 | 3% 문턱 | 공제 대상 | 소득세 공제(15%) | 지방소득세 포함 |")
    print("|---|---|---|---|---|---|")
    for w, m in EXAMPLES:
        r = credit(w, general=m)
        print(f"| {man(w)} | {man(m)} | {man(r['문턱'])} | {man(r['제1호'])} | {won(r['소득세'])} | {won(r['합계'])} |")
    print()
    for w, m in EXAMPLES:
        r = credit(w, general=m)
        print(f"- 총급여 {man(w)} · 의료비 {man(m)}: 한 달로 나누면 약 {r['합계'] / 12 / 10_000:.1f}만원")
    print()


WAGES = [30_000_000, 40_000_000, 50_000_000, 60_000_000, 80_000_000, 100_000_000]


def table_lines():
    print("표: 총급여별 공제가 시작되는 의료비와 연 700만원 한도에 닿는 의료비")
    print("| 총급여 | 이 금액을 넘어야 공제 시작 | 한 달 평균으로 보면 | 일반 부양가족 의료비가 한도에 닿는 지출 |")
    print("|---|---|---|---|")
    for w in WAGES:
        t = threshold(w)
        print(f"| {man(w)} | {man(t)} | {man(t / 12)} | {man(t + GENERAL_CAP)} |")
    print()
    print(f"- 한도에 닿았을 때 일반 부양가족 몫 소득세 공제: {won(GENERAL_CAP * RATE_BASE // 100)}")
    print()


ORDER_CASE = {"wage": 50_000_000, "general": 500_000, "special": 1_000_000, "ivf": 4_000_000}


def table_order():
    c = ORDER_CASE
    r = credit(c["wage"], general=c["general"], special=c["special"], ivf=c["ivf"])
    t = r["문턱"]
    s1 = max(t - c["general"], 0)
    s2 = max(s1 - c["special"], 0)
    print(f"표: 총급여 {man(c['wage'])}, 3% 문턱 {man(t)}이 빠지는 순서(법 조문 순서)")
    print("| 구분 | 지출 | 문턱에서 빠진 금액 | 공제 대상 | 공제액 |")
    print("|---|---|---|---|---|")
    print(f"| 배우자(일반) | {man(c['general'])} | {man(c['general'] - r['제1호'])} | {man(r['제1호'])} | {won(r['제1호'] * RATE_BASE // 100)} |")
    print(f"| 본인 | {man(c['special'])} | {man(s1 - s2)} | {man(r['제2호'])} | {won(r['제2호'] * RATE_BASE // 100)} |")
    print(f"| 난임시술비 | {man(c['ivf'])} | {man(c['ivf'] - r['제4호'])} | {man(r['제4호'])} | {won(r['제4호'] * RATE_IVF // 100)} |")
    print(f"| 합계 | {man(c['general'] + c['special'] + c['ivf'])} | {man(t)} | - | {won(r['소득세'])} |")
    print()
    # 비교: 문턱을 난임시술비에서 먼저 뺀다고 잘못 놓으면
    wrong_ivf = max(c["ivf"] - t, 0)
    wrong = (c["general"] + c["special"]) * RATE_BASE // 100 + wrong_ivf * RATE_IVF // 100
    print(f"- 문턱을 난임시술비에서 먼저 뺀다고 잘못 놓으면: {won(wrong)} (조문 순서보다 {won(r['소득세'] - wrong)} 적다)")
    print(f"- 지방소득세 포함: {won(r['합계'])}")
    print()


MIX_CASE = {"wage": 60_000_000, "general": 10_000_000, "special": 3_000_000}


def mixed():
    c = MIX_CASE
    r = credit(c["wage"], general=c["general"], special=c["special"])
    print(f"- 혼합 예: 총급여 {man(c['wage'])}, 배우자(일반) {man(c['general'])} + 70세 부모 {man(c['special'])}")
    print(f"  · 문턱 {man(r['문턱'])} → 배우자 몫 {man(c['general'] - r['문턱'])} 중 한도 {man(r['제1호'])}만 대상, 부모 몫 {man(r['제2호'])} 전부 대상")
    print(f"  · 소득세 공제 {won(r['소득세'])} · 지방소득세 포함 {won(r['합계'])}")
    print(f"  · 한도로 잘린 배우자 의료비 {man(c['general'] - r['문턱'] - r['제1호'])}")
    print()


INS_CASE = {"wage": 40_000_000, "paid": 3_000_000, "insurance": 1_000_000}


def insurance():
    c = INS_CASE
    r = calc_r = credit(c["wage"], general=c["paid"] - c["insurance"])
    print(f"- 실손 예: 총급여 {man(c['wage'])}, 의료비 {man(c['paid'])} 중 실손보험금 {man(c['insurance'])}")
    print(f"  · 계산에 넣는 의료비 {man(c['paid'] - c['insurance'])} → 공제 대상 {man(r['제1호'])} → 소득세 공제 {won(r['소득세'])} · 지방소득세 포함 {won(calc_r['합계'])}")
    print()


def main():
    table_rules()
    table_examples()
    table_lines()
    table_order()
    mixed()
    insurance()


if __name__ == "__main__":
    main()
