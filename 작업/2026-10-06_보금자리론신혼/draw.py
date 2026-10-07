#!/usr/bin/env python3
"""그림 2장을 SVG로 그린다(표준 라이브러리만, 숫자는 calc.py에서). 실행: python3 draw.py"""
import os
import calc

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "그림")
os.makedirs(OUT, exist_ok=True)
FONT = "font-family=\"'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif\""
FOOT = "2026년 10월 3일 한국주택금융공사 보금자리론 안내·업무처리기준 원문 기준 · 머니프로듀서"


def svg(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{label}" {FONT}>\n<rect width="{w}" height="{h}" fill="#ffffff"/>\n{body}\n</svg>\n')


def fig1():
    W, H = 1200, 630
    L, R = 70, 1130
    vmax = 11000
    X = lambda v: L + v / vmax * (R - L)
    line, cap = calc.PREF_LINE, calc.INCOME_CAP
    zones = [(0, line, "#0a6350", "대출 가능 + 신혼 우대 0.3%p"),
             (line, cap["신혼가구"], "#e0a526", "대출 가능 · 우대 없음"),
             (cap["신혼가구"], cap["1자녀"], "#9aa5b1", "미성년 자녀 1명이면 가능"),
             (cap["1자녀"], cap["다자녀"], "#c3cbd3", "자녀 2명 이상이면 가능"),
             (cap["다자녀"], vmax, "#eef1f4", "")]
    b = [f'<text x="{L}" y="70" font-size="36" font-weight="700" fill="#16212e">신혼부부 소득 7천만원과 8,500만원 사이가 갈림길</text>',
         f'<text x="{L}" y="114" font-size="23" fill="#3d4852">부부 합산 연소득 · 혼인신고 7년 이내 · 무주택 · 6억원 이하 주택 구입 기준</text>']
    T, Hb = 230, 120
    for a, z, c, name in zones:
        b.append(f'<rect x="{X(a):.1f}" y="{T}" width="{X(z) - X(a):.1f}" height="{Hb}" fill="{c}"/>')
    b.append(f'<text x="{(X(0) + X(line)) / 2:.1f}" y="{T + 70}" font-size="26" font-weight="700" fill="#ffffff" text-anchor="middle">우대금리 받는 구간</text>')
    b.append(f'<text x="{(X(line) + X(cap["신혼가구"])) / 2:.1f}" y="{T + 62}" font-size="21" font-weight="700" fill="#16212e" text-anchor="middle">대출만</text>')
    for v in (0, line, cap["신혼가구"], cap["1자녀"], cap["다자녀"]):
        b.append(f'<line x1="{X(v):.1f}" y1="{T - 12}" x2="{X(v):.1f}" y2="{T + Hb + 12}" stroke="#16212e" stroke-width="2"/>')
        lab = "0" if v == 0 else (f"{v // 10000}억" if v % 10000 == 0 else f"{v:,}만")
        ty = T - 26 if v == cap["신혼가구"] else T + Hb + 44
        b.append(f'<text x="{X(v):.1f}" y="{ty}" font-size="22" text-anchor="middle" fill="#16212e">{lab}</text>')
    ly = 470
    for i, (a, z, c, name) in enumerate(zones[:4]):
        x = L + (i % 2) * 540
        y = ly + (i // 2) * 44
        b.append(f'<rect x="{x}" y="{y - 20}" width="26" height="26" fill="{c}" stroke="#9aa5b1"/>')
        b.append(f'<text x="{x + 38}" y="{y}" font-size="22" fill="#16212e">{name}</text>')
    b.append(f'<text x="{R}" y="{H - 22}" font-size="16" text-anchor="end" fill="#8a96a3">{FOOT}</text>')
    return svg(W, H, "\n".join(b), "부부 합산 연소득 7천만원 이하는 대출과 신혼 우대금리, 7천만원 초과 8,500만원 이하는 대출만 되는 구간을 나눈 띠 그림")


def fig2():
    W, H = 1200, 560
    _, res = calc.table_payment()
    P = 300_000_000
    rows = [("우대 없음 5.10%", res[(P, "5.10%(우대 없음)")][0], "#9aa5b1"),
            ("신혼 0.3%p 4.80%", res[(P, "4.80%(신혼 0.3%p)")][0], "#0a6350"),
            ("신혼+청년 0.4%p 4.70%", res[(P, "4.70%(신혼 0.3%p + 청년 0.1%p)")][0], "#0a6350")]
    L, R, T = 360, 1100, 160
    vmin, vmax = 1_500_000, 1_650_000
    X = lambda v: L + (v - vmin) / (vmax - vmin) * (R - L)
    b = [f'<text x="60" y="64" font-size="32" font-weight="700" fill="#16212e">3억원을 30년 빌리면 우대 0.3%p가 한 달 {rows[0][1] - rows[1][1]:,}원</text>',
         f'<text x="60" y="104" font-size="21" fill="#3d4852">아낌e보금자리론 30년 · 원리금 균등 · 2026년 10월 1일 공시 금리 · 가로축은 150만원부터</text>']
    for i, (name, v, c) in enumerate(rows):
        y = T + i * 110
        b.append(f'<text x="{L - 16}" y="{y + 48}" font-size="23" text-anchor="end" fill="#16212e">{name}</text>')
        b.append(f'<rect x="{L}" y="{y + 14}" width="{X(v) - L:.1f}" height="54" fill="{c}"/>')
        b.append(f'<text x="{X(v) + 12:.1f}" y="{y + 50}" font-size="23" font-weight="700" fill="#16212e">{v:,}원</text>')
    b.append(f'<text x="{R}" y="{H - 22}" font-size="16" text-anchor="end" fill="#8a96a3">{FOOT}</text>')
    return svg(W, H, "\n".join(b), "3억원 30년 대출의 월 상환액을 우대 없음, 신혼 우대, 신혼과 청년 우대로 견준 막대 그림")


if __name__ == "__main__":
    open(os.path.join(OUT, "01_대표.svg"), "w", encoding="utf-8").write(fig1())
    open(os.path.join(OUT, "02_월상환액.svg"), "w", encoding="utf-8").write(fig2())
    print("그림 2장")
