#!/usr/bin/env python3
"""전세대출 한도 — 보증기관·상품별 상한 직접 계산 (B1012-9/4) · 표준 라이브러리만.

입력(표마다 고정 예시. 가정은 원고 표 아래에 적는다):
  deposit   전세보증금(원) · area  'metro'(수도권·규제지역) | 'local'(수도권 밖·규제지역 아님)
  loan      대출금(원) · rate  연 금리(%) — 가정값
공식과 근거(2026-10-05 원문 기준):
  버팀목 일반   대상 보증금 수도권 3억원·수도권외 2억원 이하, 한도 = min(수도권 1.2억원·수도권 외 8천만원, 보증금×70%)
                https://nhuf.molit.go.kr/FP/FP05/FP0502/FP05020101.jsp (대상주택 2·대출한도 1·2)
  청년 버팀목   대상 보증금 3억원 이하, 한도 = min(1.5억원, 보증금×80%)
                https://nhuf.molit.go.kr/FP/FP05/FP0502/FP05020301.jsp
  신혼 버팀목   대상 보증금 수도권 4억원·수도권 외 3억원 이하, 한도 = min(수도권 2.5억원·수도권 외 1.6억원, 보증금×80%)
                https://nhuf.molit.go.kr/FP/FP05/FP0502/FP05020401.jsp
  HF 일반전세자금보증  보증금 7억원(수도권 밖 5억원) 이하, 한도 = min(4억원, 보증금×80%, 상환능력별 한도)
                × 8/9(수도권·규제지역, 「산출결과의 8/9만 인정」) — 8/9가 대출금 기준인지 보증금액 기준인지
                원문에 없어 표2에는 넣지 않는다(hf_general은 참고용, 출력하지 않음)
                https://www.hf.go.kr/ko/sub02/sub02_01_02.do
  HUG 전세금안심대출보증  한도 = min(보증금×80%(신혼·청년 90%), 수도권 4억원·그 외 3.2억원(신혼·청년 4.5억원·3.6억원))
                · 1주택자 2억원 초과 불가 · 소득 조건: 연간 이자 ≤ 연간 인정소득×40%
                · 반환보증금액 = 보증금 전액, 주택가격·선순위 조건은 충족한다고 가정
                https://www.khug.or.kr/hug/web/ig/dl/igdl000001.jsp
  보증료(HUG)   반환보증 = 보증금×요율(아파트·부채비율 70% 이하, 2억 초과~5억 이하 0.107%) · 특약보증 = 대출×보증비율 80%×0.031%
  월 이자       = 대출금×연 금리÷12, 원 미만 버림 · HUG 소득 조건 최소 인정소득 = 대출금×연 금리÷40%, 만원 미만 올림
  DSR 몫        = 연 이자÷연소득(1주택자가 수도권·규제지역에서 받는 전세대출, 이자상환분만 반영 — 금융위 2025-10-15, 10.29일 시행)
                https://www.fsc.go.kr/no010101/85432
  한도 금액은 만원 미만 버림(이 글의 표시 규칙).
같은 입력이면 같은 출력. 실행하면 원고에 넣을 표와 본문 숫자를 마크다운으로 찍는다.
"""
from fractions import Fraction as F

EOK, MAN = 100_000_000, 10_000

# 주택도시기금 버팀목(2026-10-05 화면)
BT_GEN_DEP = {"metro": 3 * EOK, "local": 2 * EOK}
BT_GEN_CAP = {"metro": 12_000 * MAN, "local": 8_000 * MAN}
BT_GEN_LTV = 70
BT_YOUTH_DEP = 3 * EOK
BT_YOUTH_CAP = 15_000 * MAN
BT_NEWLY_DEP = {"metro": 4 * EOK, "local": 3 * EOK}
BT_NEWLY_CAP = {"metro": 25_000 * MAN, "local": 16_000 * MAN}
BT_LTV80 = 80
# HF 일반전세자금보증
HF_DEP = {"metro": 7 * EOK, "local": 5 * EOK}
HF_CAP = 4 * EOK
HF_LTV = 80
HF_METRO = F(8, 9)
# HUG 전세금안심대출보증
HUG_DEP = {"metro": 7 * EOK, "local": 5 * EOK}
HUG_CAP = {"metro": 4 * EOK, "local": 32_000 * MAN}
HUG_CAP_YN = {"metro": 45_000 * MAN, "local": 36_000 * MAN}
HUG_LTV, HUG_LTV_YN = 80, 90
HUG_ONE_HOUSE = 2 * EOK
HUG_INCOME_RATIO = 40
HUG_RET_RATE = F(107, 100_000)   # 0.107%
HUG_SP_RATE = F(31, 100_000)     # 0.031%
HUG_GUAR = {"metro": 80, "local": 90}
# 소득·자산 기준
INC_BT = 5_000 * MAN
INC_BT_KIDS = 6_000 * MAN
INC_NEWLY = 7_500 * MAN
NET_ASSET = 34_500 * MAN
INC_HF_YOUTH = 7_000 * MAN
HF_YOUTH_CAP = 2 * EOK
INC_HUG_NEWLY = 6_000 * MAN


def floor_man(x):
    return int(x) // MAN * MAN


def won(x):
    """원 → 「2억 8,444만원」·「1억 2,000만원」·「8,000만원」·「416,666원」"""
    x = int(x)
    if x % MAN:
        return f"{x:,}원"
    e, m = divmod(x // MAN, 10_000)
    if e and m:
        return f"{e}억 {m:,}만원"
    if e:
        return f"{e}억원"
    return f"{m:,}만원"


def bt_general(dep, area):
    if dep > BT_GEN_DEP[area]:
        return None
    return min(BT_GEN_CAP[area], dep * BT_GEN_LTV // 100)


def bt_youth(dep, area):
    if dep > BT_YOUTH_DEP:
        return None
    return min(BT_YOUTH_CAP, dep * BT_LTV80 // 100)


def bt_newly(dep, area):
    if dep > BT_NEWLY_DEP[area]:
        return None
    return min(BT_NEWLY_CAP[area], dep * BT_LTV80 // 100)


def hf_general(dep, area):
    if dep > HF_DEP[area]:
        return None
    base = min(HF_CAP, dep * HF_LTV // 100)
    return floor_man(base * HF_METRO) if area == "metro" else base


def hug(dep, area, yn=False, one_house=False):
    if dep > HUG_DEP[area]:
        return None
    ltv = HUG_LTV_YN if yn else HUG_LTV
    cap = (HUG_CAP_YN if yn else HUG_CAP)[area]
    v = min(dep * ltv // 100, cap)
    return min(v, HUG_ONE_HOUSE) if one_house else v


def monthly_interest(loan, rate_pct):
    return int(F(loan) * F(str(rate_pct)) / 100 / 12)


def hug_min_income(loan, rate_pct):
    need = F(loan) * F(str(rate_pct)) / 100 / F(HUG_INCOME_RATIO, 100)
    return -(-need // MAN) * MAN


def cell(v):
    return "대상 아님" if v is None else won(v)


SCEN = [("수도권 2억 5,000만원", 25_000 * MAN, "metro"),
        ("수도권 4억원", 4 * EOK, "metro"),
        ("수도권 밖 2억 5,000만원", 25_000 * MAN, "local")]
ROWS = [("버팀목 일반(소득 5천만원 이하)", bt_general),
        ("청년 버팀목(만 34세 이하)", bt_youth),
        ("신혼부부 버팀목", bt_newly),
        ("HUG 안심대출(일반)", lambda d, a: hug(d, a)),
        ("HUG 안심대출(신혼·청년)", lambda d, a: hug(d, a, yn=True))]


def main():
    print("## 표1 — 상품별 한도 규칙(원문)")
    print("| 상품 | 한도 상한 | 보증금 대비 | 대상 보증금 |")
    print("|---|---|---|---|")
    print(f"| 버팀목 일반 | 수도권 {won(BT_GEN_CAP['metro'])} · 밖 {won(BT_GEN_CAP['local'])} | {BT_GEN_LTV}% | 수도권 {won(BT_GEN_DEP['metro'])} · 밖 {won(BT_GEN_DEP['local'])} 이하 |")
    print(f"| 청년 버팀목 | {won(BT_YOUTH_CAP)} | {BT_LTV80}% | {won(BT_YOUTH_DEP)} 이하 |")
    print(f"| 신혼부부 버팀목 | 수도권 {won(BT_NEWLY_CAP['metro'])} · 밖 {won(BT_NEWLY_CAP['local'])} | {BT_LTV80}% | 수도권 {won(BT_NEWLY_DEP['metro'])} · 밖 {won(BT_NEWLY_DEP['local'])} 이하 |")
    print(f"| HF 일반전세자금보증 | {won(HF_CAP)}, 수도권·규제지역은 계산값의 8/9 | {HF_LTV}% | 수도권 {won(HF_DEP['metro'])} · 밖 {won(HF_DEP['local'])} 이하 |")
    print(f"| HUG 안심대출(일반) | 수도권 {won(HUG_CAP['metro'])} · 그 외 {won(HUG_CAP['local'])} | {HUG_LTV}% | 수도권 {won(HUG_DEP['metro'])} · 그 외 {won(HUG_DEP['local'])} 이하 |")
    print(f"| HUG 안심대출(신혼·청년) | 수도권 {won(HUG_CAP_YN['metro'])} · 그 외 {won(HUG_CAP_YN['local'])} | {HUG_LTV_YN}% | 같음 |")
    print(f"| 1주택자(HF·HUG·SGI) | 수도권·규제지역 {won(HUG_ONE_HOUSE)} | - | - |")
    print()
    print("## 표2 — 보증금별 한도 직접 계산(무주택, 소득·신용 심사 통과 가정, HF는 8/9 적용 기준이 원문에 없어 뺌)")
    print("| 상품 | " + " | ".join(s[0] for s in SCEN) + " |")
    print("|---|---|---|---|")
    calc = {}
    for name, fn in ROWS:
        vals = [fn(d, a) for _, d, a in SCEN]
        calc[name] = vals
        print(f"| {name} | " + " | ".join(cell(v) for v in vals) + " |")
    print()
    print(f"- HUG 수도권 4억 일반: min(4억×80%={won(4 * EOK * 80 // 100)}, {won(HUG_CAP['metro'])}) = {won(hug(4 * EOK, 'metro'))}")
    print(f"- 1주택자 HUG 수도권 4억: {won(hug(4 * EOK, 'metro', one_house=True))}")
    print()

    print("## 표3 — 소득·나이·자산 기준(원문)")
    print("| 상품 | 소득 기준(부부 합산) | 그 밖의 조건 |")
    print("|---|---|---|")
    print(f"| 버팀목 일반 | {won(INC_BT)} 이하(2자녀 이상 {won(INC_BT_KIDS)}, 신혼 {won(INC_NEWLY)}) | 순자산 {won(NET_ASSET)} 이하, 무주택 세대주 |")
    print(f"| 청년 버팀목 | {won(INC_BT)} 이하(신혼 {won(INC_NEWLY)}) | 만 19~34세 세대주, 순자산 {won(NET_ASSET)} 이하 |")
    print(f"| 신혼부부 버팀목 | {won(INC_NEWLY)} 이하 | 혼인 7년 이내 또는 3개월 안 결혼 예정 |")
    print(f"| HF 청년 특례 | {won(INC_HF_YOUTH)} 이하 | 만 34세 이하 무주택, 최대 {won(HF_YOUTH_CAP)} |")
    print(f"| HF 일반 | 소득 상한 없음 | 소득·부채로 상환능력별 한도 |")
    print(f"| HUG 안심대출 | 신혼 {won(INC_HUG_NEWLY)}·청년 {won(INC_BT)} 이하면 90% 적용 | 연 이자 ≤ 인정소득의 {HUG_INCOME_RATIO}% |")
    print()

    print("## 표4 — 대출금별 월 이자와 HUG 소득 조건(가정 금리)")
    print("| 대출금 | 월 이자(연 2.5%) | 월 이자(연 4.0%) | HUG 최소 인정소득(연 4.0%) |")
    print("|---|---|---|---|")
    for loan in (12_000 * MAN, 15_000 * MAN, 2 * EOK, 25_000 * MAN, 32_000 * MAN):
        print(f"| {won(loan)} | {won(monthly_interest(loan, 2.5))} | {won(monthly_interest(loan, 4.0))} | {won(hug_min_income(loan, 4.0))} |")
    print()

    # 본문 숫자
    yearly = 2 * EOK * 4 // 100
    print("## 본문 숫자")
    print(f"- 1주택자 2억 × 연 4.0% = 연 이자 {won(yearly)}, 연봉 6,000만원이면 DSR {float(F(yearly, 6_000 * MAN) * 100):.1f}%p")
    ret = int(4 * EOK * HUG_RET_RATE)
    sp_base = 32_000 * MAN * HUG_GUAR['metro'] // 100
    sp = int(sp_base * HUG_SP_RATE)
    print(f"- HUG 보증료(수도권 4억 아파트, 부채비율 70% 이하, 1년): 반환보증 {won(ret)} + 특약보증({won(sp_base)}×0.031%) {won(sp)} = {won(ret + sp)}, 월 약 {won((ret + sp) // 12)}")
    print(f"- 청년 버팀목 1억 5,000만원 × 연 2.5% = 월 {won(monthly_interest(15_000 * MAN, 2.5))}")
    print(f"- HUG 3억 2,000만원 × 연 4.0% = 월 {won(monthly_interest(32_000 * MAN, 4.0))}, 소득 조건 {won(hug_min_income(32_000 * MAN, 4.0))}")
    print(f"- 신혼 버팀목 수도권 4억: {won(bt_newly(4 * EOK, 'metro'))}, 자기 돈 {won(4 * EOK - bt_newly(4 * EOK, 'metro'))}")
    print(f"- HUG 수도권 4억 일반 자기 돈 {won(4 * EOK - hug(4 * EOK, 'metro'))}")


if __name__ == "__main__":
    main()
