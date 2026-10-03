#!/usr/bin/env python3
"""4대보험 계산 — 2026년 요율·상하한과 항목별 본인·사업주 부담 (B1006-2/2) · 표준 라이브러리만.

기준일: 2026-10-03 원문 기준(2026년 10월 보험료에 적용되는 숫자). 같은 입력이면 같은 출력.

입력(아래 상수)과 근거:
  국민연금 보험료율   2026년 9.5%(근로자·사업주 절반씩 4.75%), 2026년부터 해마다 0.5%p 올라 2033년 13%
                     국민연금공단 「보험료 납부」 https://www.nps.or.kr/pnsinfo/ntpsklg/getOHAF0038M0.do?menuId=MN24001113
                     국민연금법 제88조 제3항(최종 1천분의 65씩) — 조문 본문
                     https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280269&joNo=0088&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  기준소득월액 상·하한 2026.7.1.~2027.6.30. 하한 41만원·상한 659만원(그 전 1년 40만원·637만원), 천원 미만 버림
                     국민연금공단 「보험료 납부」(위 주소)
  건강보험료율       1만분의 719(7.19%) — 국민건강보험법 시행령 제44조 제1항(시행 2026. 10. 1. 판 조문)
                     https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=289701&joNo=0044&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
                     부담: 근로자·사업주 100분의 50씩 — 국민건강보험법 제76조 제1항
                     https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=276651&joNo=0076&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  장기요양보험료율    100만분의 9,448(소득 대비 0.9448%) — 노인장기요양보험법 시행령 제4조
                     https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=286011&joNo=0004&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
                     산정: 건강보험료 × (장기요양보험료율 ÷ 건강보험료율) — 노인장기요양보험법 제9조 제1항
                     https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=286217&joNo=0009&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
                     건강보험료 대비 13.14% — 보건복지부 보도자료(2025-11-04)
                     https://www.mohw.go.kr/board.es?mid=a10503000000&bid=0027&act=view&list_no=1487817
  고용보험료율       실업급여 1천분의 18(근로자·사업주 절반씩), 고용안정·직업능력개발 1만분의 25~85(사업주만)
                     고용산재보험료징수법 시행령 제12조 제1항
                     https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=280527&joNo=0012&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
                     근로자 = 보수총액 × 실업급여 요율의 2분의 1, 산재보험료는 사업주만 — 같은 법 제13조 제2항·제5항
                     https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=247481&joNo=0013&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR

공식(정수·분수로 계산, 끝수 순서를 먼저 정한다):
  1) 국민연금 기준소득월액 = 월 보수에서 천원 미만 버림 → 41만원~659만원 안으로 자른다
  2) 항목마다 「전체 보험료」를 먼저 구하고 원 미만을 버린다
       국민연금 = 기준소득월액 × 95/1000 · 건강보험 = 보수 × 719/10000
       장기요양 = (원 미만 버린) 건강보험료 × 9448/71900 · 고용(실업급여) = 보수 × 18/1000
  3) 근로자 몫 = 전체 ÷ 2, 원 미만 버림 · 사업주 몫 = 전체 − 근로자 몫
     사업주는 고용안정·직업능력개발(150명 미만 25/10000)과 산재보험료(업종별 고시 요율)를 더 낸다
  ※ 실제 고지액은 공단의 끝수 처리·정산에 따라 몇십 원 안에서 다를 수 있다(글에 적는다).
  ※ 월 보수 = 비과세 근로소득을 뺀 금액이라고 가정한다(국민건강보험법 시행령 제33조 제1항 제3호).
"""
from fractions import Fraction as F
import math

NPS_RATE = {2026: F(95, 1000), 2027: F(100, 1000), 2028: F(105, 1000), 2029: F(110, 1000),
            2030: F(115, 1000), 2031: F(120, 1000), 2032: F(125, 1000), 2033: F(130, 1000)}
NPS_FLOOR, NPS_CAP = 410000, 6590000          # 2026.7.1.~2027.6.30.
NPS_FLOOR_OLD, NPS_CAP_OLD = 400000, 6370000  # 2025.7.1.~2026.6.30.
HI_RATE = F(719, 10000)
LTC_RATE = F(9448, 1000000)
EI_UB = F(18, 1000)
EI_SAFETY = {"150명 미만": F(25, 10000), "150명 이상 우선지원대상기업": F(45, 10000),
             "150명 이상 1천명 미만": F(65, 10000), "1천명 이상·국가·지자체": F(85, 10000)}
CASES = [2000000, 3000000, 5000000, 8000000]


def fl(x):
    return math.floor(x)


def nps_base(pay, floor=NPS_FLOOR, cap=NPS_CAP):
    b = pay // 1000 * 1000
    return min(max(b, floor), cap)


def compute(pay, year=2026, cap=NPS_CAP, floor=NPS_FLOOR):
    """월 보수 → 항목별 전체·근로자·사업주(원)."""
    base = nps_base(pay, floor, cap)
    nps_t = fl(base * NPS_RATE[year])
    hi_t = fl(pay * HI_RATE)
    ltc_t = fl(hi_t * LTC_RATE / HI_RATE)
    ei_t = fl(pay * EI_UB)
    out = {"보수": pay, "기준소득월액": base}
    for k, t in (("국민연금", nps_t), ("건강보험", hi_t), ("장기요양", ltc_t), ("고용보험", ei_t)):
        me = fl(F(t, 2))
        out[k + "_전체"], out[k + "_근로자"], out[k + "_사업주"] = t, me, t - me
    out["근로자합계"] = sum(out[k + "_근로자"] for k in ("국민연금", "건강보험", "장기요양", "고용보험"))
    out["고용안정_사업주150미만"] = fl(pay * EI_SAFETY["150명 미만"])
    out["사업주합계_산재제외"] = sum(out[k + "_사업주"] for k in ("국민연금", "건강보험", "장기요양", "고용보험")) \
        + out["고용안정_사업주150미만"]
    return out


def pct(x, nd=4):
    s = f"{float(x) * 100:.{nd}f}".rstrip("0").rstrip(".")
    return s + "%"


def won(n):
    return f"{n:,}원"


def main():
    # 0) 요율 숫자
    me_rate = NPS_RATE[2026] / 2 + HI_RATE / 2 + LTC_RATE / 2 + EI_UB / 2
    print("## 요율 요약(2026년 10월 기준)")
    print(f"- 국민연금 {pct(NPS_RATE[2026])} → 근로자 {pct(NPS_RATE[2026] / 2)}")
    print(f"- 건강보험 {pct(HI_RATE)} → 근로자 {pct(HI_RATE / 2)}")
    print(f"- 장기요양 소득 대비 {pct(LTC_RATE)} → 근로자 {pct(LTC_RATE / 2)} · 건강보험료 대비 {pct(LTC_RATE / HI_RATE, 2)}")
    print(f"- 고용보험(실업급여) {pct(EI_UB)} → 근로자 {pct(EI_UB / 2)}")
    print(f"- 근로자 몫 합계 요율 {pct(me_rate)} (약 {float(me_rate) * 100:.2f}%)")
    print()

    # 표 1: 요율표
    print("표: 2026년 10월 적용 4대보험 요율과 부담 나눔")
    print("| 항목 | 전체 요율 | 근로자 | 사업주 | 근거 |")
    print("|---|---|---|---|---|")
    print(f"| 국민연금 | {pct(NPS_RATE[2026])} | {pct(NPS_RATE[2026] / 2)} | {pct(NPS_RATE[2026] / 2)} | 국민연금공단 보험료 안내 |")
    print(f"| 건강보험 | {pct(HI_RATE)} | {pct(HI_RATE / 2)} | {pct(HI_RATE / 2)} | 건강보험법 시행령 제44조 |")
    print(f"| 장기요양 | 소득의 {pct(LTC_RATE)} | {pct(LTC_RATE / 2)} | {pct(LTC_RATE / 2)} | 장기요양보험법 시행령 제4조 |")
    print(f"| 고용보험(실업급여) | {pct(EI_UB)} | {pct(EI_UB / 2)} | {pct(EI_UB / 2)} | 징수법 시행령 제12조 |")
    print(f"| 고용안정·직업능력개발 | {pct(EI_SAFETY['150명 미만'])}~{pct(EI_SAFETY['1천명 이상·국가·지자체'])} | 없음 | 전액 | 징수법 시행령 제12조 |")
    print("| 산재보험 | 업종별 고시 | 없음 | 전액 | 징수법 제13조 |")
    print()

    # 표 2: 월 보수별 근로자 몫
    rows = [compute(p) for p in CASES]
    print("표: 월 보수별 4대보험 근로자 부담 계산(2026년 10월 요율)")
    print("| 월 보수 | 국민연금 | 건강보험 | 장기요양 | 고용보험 | 근로자 합계 |")
    print("|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['보수'] // 10000:,}만원 | {won(r['국민연금_근로자'])} | {won(r['건강보험_근로자'])} | "
              f"{won(r['장기요양_근로자'])} | {won(r['고용보험_근로자'])} | {won(r['근로자합계'])} |")
    print()
    for r in rows:
        print(f"- {r['보수']:,}: 기준소득월액 {r['기준소득월액']:,} · 전체 연금 {r['국민연금_전체']:,} · 건보 {r['건강보험_전체']:,}"
              f" · 장기 {r['장기요양_전체']:,} · 고용 {r['고용보험_전체']:,} · 근로자 합계 {r['근로자합계']:,}"
              f" · 1년 {r['근로자합계'] * 12:,} · 보수 대비 {float(F(r['근로자합계'], r['보수'])) * 100:.2f}%")
    r8 = rows[3]
    nps_nocap = fl(F(r8['보수']) * NPS_RATE[2026] / 2)
    print(f"- 800만원 상한 효과: 상한이 없다면 연금 근로자 몫 {nps_nocap:,} → 실제 {r8['국민연금_근로자']:,}, 차이 {nps_nocap - r8['국민연금_근로자']:,}")
    old = compute(8000000, cap=NPS_CAP_OLD, floor=NPS_FLOOR_OLD)
    print(f"- 800만원 2026년 6월까지(상한 637만원): 연금 근로자 몫 {old['국민연금_근로자']:,} → 7월부터 {r8['국민연금_근로자']:,}, 늘어난 금액 {r8['국민연금_근로자'] - old['국민연금_근로자']:,}")
    print()

    # 표 3: 300만원 근로자 vs 사업주
    r3 = rows[1]
    print("표: 월 보수 300만원일 때 근로자와 사업주 몫(150명 미만 사업장)")
    print("| 항목 | 근로자 | 사업주 |")
    print("|---|---|---|")
    for k in ("국민연금", "건강보험", "장기요양", "고용보험"):
        name = "고용보험(실업급여)" if k == "고용보험" else k
        print(f"| {name} | {won(r3[k + '_근로자'])} | {won(r3[k + '_사업주'])} |")
    print(f"| 고용안정·직업능력개발 | 0원 | {won(r3['고용안정_사업주150미만'])} |")
    print("| 산재보험 | 0원 | 업종별 요율 × 보수 |")
    print(f"| 합계(산재 제외) | {won(r3['근로자합계'])} | {won(r3['사업주합계_산재제외'])} |")
    print()

    # 표 4: 국민연금 연도별(월 보수 300만원)
    print("표: 국민연금 보험료율 연도별 인상과 월 보수 300만원 근로자 몫")
    print("| 연도 | 보험료율 | 근로자 몫 | 2026년보다 |")
    print("|---|---|---|---|")
    base26 = None
    for y in range(2026, 2034):
        v = compute(3000000, year=y)['국민연금_근로자']
        base26 = v if base26 is None else base26
        print(f"| {y}년 | {pct(NPS_RATE[y])} | {won(v)} | {'—' if y == 2026 else '+' + won(v - base26)} |")
    print()
    print("- 2027년 300만원 근로자 몫:", compute(3000000, year=2027)['국민연금_근로자'])
    print("- 2033년 1년 차이(300만원):", (compute(3000000, year=2033)['국민연금_근로자'] - base26) * 12)


if __name__ == "__main__":
    main()
