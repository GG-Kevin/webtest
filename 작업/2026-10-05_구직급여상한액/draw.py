#!/usr/bin/env python3
"""그림 2장을 SVG로 그린다(표준 라이브러리만, 숫자는 calc.py 함수에서). 실행: python3 draw.py"""
import os
import calc

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "그림")
os.makedirs(OUT, exist_ok=True)
FONT = "font-family=\"'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif\""


def svg(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{label}" {FONT}>\n<rect width="{w}" height="{h}" fill="#ffffff"/>\n{body}\n</svg>\n')


def fig1():
    W, H = 1200, 630
    L, R, T, B = 120, 1140, 150, 540
    xmin, xmax, ymin, ymax = 2000000, 5000000, 30000, 100000
    X = lambda v: L + (v - xmin) / (xmax - xmin) * (R - L)
    Y = lambda v: B - (v - ymin) / (ymax - ymin) * (B - T)
    cap, fl = calc.cap_daily(), calc.floor_daily(2026)
    b = [f'<text x="{L}" y="62" font-size="34" font-weight="700" fill="#16212e">월급이 달라도 구직급여일액은 66,048원~68,100원 사이</text>',
         f'<text x="{L}" y="104" font-size="22" fill="#3d4852">2026년 이직 · 하루 8시간 · 이직 전 3개월 92일 예시</text>']
    for v in range(30000, 100001, 10000):
        b.append(f'<line x1="{L}" y1="{Y(v):.1f}" x2="{R}" y2="{Y(v):.1f}" stroke="#e3e7eb"/>')
        b.append(f'<text x="{L - 12}" y="{Y(v) + 7:.1f}" font-size="18" text-anchor="end" fill="#5b6773">{v // 10000}만</text>')
    for m in range(2000000, 5000001, 500000):
        b.append(f'<text x="{X(m):.1f}" y="{B + 32}" font-size="18" text-anchor="middle" fill="#5b6773">월 {m // 10000}만원</text>')
    pts60, pts = [], []
    for m in range(2000000, 5000001, 10000):
        base, d, _ = calc.daily_from_monthly(m)
        pts60.append(f"{X(m):.1f},{Y(min(base * calc.RATE, ymax)):.1f}")
        pts.append(f"{X(m):.1f},{Y(d):.1f}")
    b.append(f'<polyline points="{" ".join(pts60)}" fill="none" stroke="#9aa5b1" stroke-width="3" stroke-dasharray="10 8"/>')
    b.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="#0a6350" stroke-width="6"/>')
    b.append(f'<text x="{X(4200000):.1f}" y="{Y(88000):.1f}" font-size="20" fill="#5b6773">평균임금의 60% 계산값(점선)</text>')
    b.append(f'<text x="{X(4300000):.1f}" y="{Y(cap) - 16:.1f}" font-size="22" font-weight="700" fill="#0a6350">상한 {cap:,}원</text>')
    b.append(f'<text x="{X(2050000):.1f}" y="{Y(fl) - 16:.1f}" font-size="22" font-weight="700" fill="#0a6350">하한 {fl:,}원</text>')
    lo, hi = 3375787, 3480667
    for v in (lo, hi):
        b.append(f'<line x1="{X(v):.1f}" y1="{T}" x2="{X(v):.1f}" y2="{B}" stroke="#c0392b" stroke-width="2" stroke-dasharray="4 5"/>')
    b.append(f'<text x="{X(hi) + 10:.1f}" y="{T + 24}" font-size="19" fill="#c0392b">60%가 그대로 쓰이는 구간: 월 약 338만~349만원</text>')
    b.append(f'<line x1="{L}" y1="{B}" x2="{R}" y2="{B}" stroke="#16212e" stroke-width="2"/>')
    b.append(f'<text x="{R}" y="{H - 22}" font-size="16" text-anchor="end" fill="#8a96a3">2026년 10월 3일 국가법령정보센터·최저임금위원회 원문 기준 · 머니프로듀서</text>')
    return svg(W, H, "\n".join(b), "월급 200만원에서 500만원까지 구직급여일액이 하한 66,048원과 상한 68,100원 사이에 머무는 선 그림")


def fig2():
    W, H = 1200, 560
    cap, f26, f27 = calc.cap_daily(), calc.floor_daily(2026), calc.floor_daily(2027)
    rows = [("2026년 하한액(8시간)", f26, "#7f8c99"), ("현행 상한액", cap, "#0a6350"), ("2027년 최저임금 대입 하한액", f27, "#c0392b")]
    L, R, T = 420, 1100, 150
    vmin, vmax = 64000, 69000
    X = lambda v: L + (v - vmin) / (vmax - vmin) * (R - L)
    b = [f'<text x="60" y="62" font-size="32" font-weight="700" fill="#16212e">2027년 최저임금을 넣으면 하한액이 상한액을 380원 넘습니다</text>',
         f'<text x="60" y="102" font-size="21" fill="#3d4852">하루 8시간 · 시행령 제68조가 그대로일 때 · 가로축은 64,000원부터</text>']
    for i, (name, v, c) in enumerate(rows):
        y = T + i * 120
        b.append(f'<text x="{L - 16}" y="{y + 50}" font-size="23" text-anchor="end" fill="#16212e">{name}</text>')
        b.append(f'<rect x="{L}" y="{y + 14}" width="{X(v) - L:.1f}" height="56" fill="{c}"/>')
        b.append(f'<text x="{X(v) + 12:.1f}" y="{y + 52}" font-size="24" font-weight="700" fill="{c}">{v:,}원</text>')
    b.append(f'<line x1="{X(cap):.1f}" y1="{T}" x2="{X(cap):.1f}" y2="{T + 360}" stroke="#0a6350" stroke-width="2" stroke-dasharray="6 6"/>')
    b.append(f'<text x="{W - 40}" y="{H - 22}" font-size="16" text-anchor="end" fill="#8a96a3">최저임금 2026년 10,320원 · 2027년 10,700원(최저임금위원회) × 8시간 × 80% · 머니프로듀서</text>')
    return svg(W, H, "\n".join(b), "2026년 하한액 66,048원, 현행 상한액 68,100원, 2027년 최저임금을 넣은 하한액 68,480원을 견준 막대 그림")


if __name__ == "__main__":
    open(os.path.join(OUT, "01_대표.svg"), "w", encoding="utf-8").write(fig1())
    open(os.path.join(OUT, "02_2027역전.svg"), "w", encoding="utf-8").write(fig2())
    print("그림 2장:", sorted(os.listdir(OUT)))
