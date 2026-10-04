#!/usr/bin/env python3
"""그림 2장을 SVG로 그린다(표준 라이브러리만, 숫자는 calc.py에서). 실행: python3 draw.py"""
import os
import calc

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "그림")
os.makedirs(OUT, exist_ok=True)
FONT = "font-family=\"'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif\""
FOOT = "2026년 10월 4일 국가법령정보센터·고용노동부·국회 의안 원문 기준 · 머니프로듀서"


def svg(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{label}" {FONT}>\n<rect width="{w}" height="{h}" fill="#ffffff"/>\n{body}\n</svg>\n')


def fig1():
    W, H = 1200, 630
    b = [f'<rect x="0" y="0" width="{W}" height="64" fill="#16212e"/>',
         '<text x="60" y="42" font-size="24" font-weight="700" fill="#ffffff">정년연장 법제화 · 2026년 10월 4일 원문 기준</text>',
         f'<text x="60" y="122" font-size="38" font-weight="700" fill="#16212e">지금 법정 정년은 {calc.LEGAL_MIN}세, {calc.BILL_TARGET}세 법안은 국회 심사 중</text>']
    cols = [(60, "#0a6350", "#e8f3ef", "원문에서 확인된 것",
             [f"법정 정년 {calc.LEGAL_MIN}세 이상(제19조)",
              "정부: 세대 상생형 정년연장 법제화 추진",
              f"의안 {calc.BILL_NO}: 정년 {calc.BILL_TARGET}세 안, 의결 전",
              f"공무원 정년 {calc.CIVIL_AGE}세는 국가공무원법"]),
            (620, "#9a5b00", "#fbf1e1", "확인되지 않은 것",
             ["시행 연도", "내 출생연도에 적용되는지", "정부가 국회에 낸 법안", "임금 조정·재고용 방식"])]
    for x, c, bg, head, items in cols:
        b.append(f'<rect x="{x}" y="160" width="520" height="390" rx="14" fill="{bg}" stroke="{c}" stroke-width="3"/>')
        b.append(f'<rect x="{x}" y="160" width="520" height="66" rx="14" fill="{c}"/>')
        b.append(f'<rect x="{x}" y="200" width="520" height="26" fill="{c}"/>')
        b.append(f'<text x="{x + 260}" y="205" font-size="30" font-weight="700" fill="#ffffff" text-anchor="middle">{head}</text>')
        for i, it in enumerate(items):
            y = 290 + i * 66
            b.append(f'<circle cx="{x + 34}" cy="{y - 9}" r="7" fill="{c}"/>')
            b.append(f'<text x="{x + 54}" y="{y}" font-size="23" fill="#16212e">{it}</text>')
    b.append(f'<text x="{W - 60}" y="{H - 30}" font-size="16" text-anchor="end" fill="#8a96a3">{FOOT}</text>')
    return svg(W, H, "\n".join(b), "원문에서 확인된 것과 확인되지 않은 것을 두 칸으로 나눈 정년연장 판정판")


def fig2():
    W, H = 1200, 600
    births = list(range(1964, 1973))
    L, T, B = 150, 150, 500
    step = (W - L - 60) / len(births)
    unit = (B - T) / 6
    b = ['<text x="60" y="62" font-size="32" font-weight="700" fill="#16212e">60세 정년이면 연금 개시까지 3~5년이 빕니다</text>',
         '<text x="60" y="102" font-size="21" fill="#3d4852">출생연도별 공백(연금 개시 연령 − 정년 60세, 단위 년) · 우리 계산</text>']
    for k in range(0, 7):
        y = B - k * unit
        b.append(f'<line x1="{L - 10}" y1="{y:.1f}" x2="{W - 60}" y2="{y:.1f}" stroke="#e3e7eb" stroke-width="1"/>')
        b.append(f'<text x="{L - 20}" y="{y + 7:.1f}" font-size="18" text-anchor="end" fill="#3d4852">{k}년</text>')
    for i, by in enumerate(births):
        r = calc.compute(by)
        g = r["gap_years"]
        x = L + i * step + step * 0.18
        w = step * 0.64
        c = "#0a6350" if r["pension_age"] == 65 else "#5f8f84"
        b.append(f'<rect x="{x:.1f}" y="{B - g * unit:.1f}" width="{w:.1f}" height="{g * unit:.1f}" fill="{c}"/>')
        b.append(f'<text x="{x + w / 2:.1f}" y="{B - g * unit - 12:.1f}" font-size="22" font-weight="700" text-anchor="middle" fill="#16212e">{g}년</text>')
        b.append(f'<text x="{x + w / 2:.1f}" y="{B + 32}" font-size="19" text-anchor="middle" fill="#16212e">{str(by)[2:]}년생</text>')
        b.append(f'<text x="{x + w / 2:.1f}" y="{B + 58}" font-size="16" text-anchor="middle" fill="#6b7682">연금 {r["pension_age"]}세</text>')
    b.append(f'<text x="{W - 60}" y="{H - 14}" font-size="16" text-anchor="end" fill="#8a96a3">고령자고용법 제19조 · 국민연금공단 출생연도별 지급개시연령 · 2026년 10월 4일 원문 기준</text>')
    return svg(W, H, "\n".join(b), "1964년생부터 1972년생까지 60세 정년과 연금 개시 연령 사이 공백을 견준 막대 그림")


if __name__ == "__main__":
    for name, s in (("01_대표.svg", fig1()), ("02_공백.svg", fig2())):
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(s)
        print(name)
