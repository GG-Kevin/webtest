#!/usr/bin/env python3
"""그림 2장을 SVG로 그린다(표준 라이브러리만, 숫자는 calc.py 함수에서). 실행: python3 draw.py"""
import os
import calc

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "그림")
os.makedirs(OUT, exist_ok=True)
FONT = "font-family=\"'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif\""
COL = {"국민연금": "#1f5f8b", "건강보험": "#2e8b6e", "장기요양": "#8fbf6a", "고용보험": "#d99a3b"}


def svg(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{label}" {FONT}>\n<rect width="{w}" height="{h}" fill="#ffffff"/>\n{body}\n</svg>\n')


def fig1():
    W, H = 1200, 630
    L, R = 190, 1010
    rows = [calc.compute(p) for p in calc.CASES]
    mx = 720000
    X = lambda v: L + v / mx * (R - L)
    b = ['<text x="60" y="64" font-size="34" font-weight="700" fill="#16212e">4대보험 근로자 몫, 월 보수의 약 9.72%</text>',
         '<text x="60" y="104" font-size="21" fill="#3d4852">2026년 10월 요율 · 국민연금 4.75% + 건강 3.595% + 장기요양 0.4724% + 고용 0.9%</text>']
    lx = 60
    for k, c in COL.items():
        b.append(f'<rect x="{lx}" y="128" width="20" height="20" fill="{c}"/>')
        b.append(f'<text x="{lx + 28}" y="145" font-size="19" fill="#3d4852">{k}</text>')
        lx += 150
    y = 185
    for r in rows:
        b.append(f'<text x="{L - 16}" y="{y + 44}" font-size="22" text-anchor="end" fill="#16212e">월 {r["보수"] // 10000}만원</text>')
        x = L
        for k in COL:
            v = r[k + "_근로자"]
            w = X(v) - L
            b.append(f'<rect x="{x:.1f}" y="{y + 14}" width="{w:.1f}" height="44" fill="{COL[k]}"/>')
            x += w
        b.append(f'<text x="{x + 12:.1f}" y="{y + 45}" font-size="22" font-weight="700" fill="#16212e">{r["근로자합계"]:,}원</text>')
        y += 92
    b.append(f'<text x="60" y="{H - 34}" font-size="18" fill="#5b6773">800만원은 국민연금 기준소득월액 상한 659만원이 걸려 연금이 313,025원에서 멈춥니다 · 원 미만 버림</text>')
    return svg(W, H, "\n".join(b), "월 보수 200만·300만·500만·800만원의 4대보험 근로자 몫을 항목별로 쌓은 막대그림")


def fig2():
    W, H = 1200, 600
    L, R, T, B = 120, 1140, 150, 520
    years = list(range(2026, 2034))
    vals = [calc.compute(3000000, year=y)["국민연금_근로자"] for y in years]
    ymax = 220000
    Y = lambda v: B - v / ymax * (B - T)
    bw = (R - L) / len(years) * 0.6
    b = ['<text x="60" y="62" font-size="32" font-weight="700" fill="#16212e">국민연금 보험료율, 2026년 9.5%에서 2033년 13%로</text>',
         '<text x="60" y="102" font-size="21" fill="#3d4852">월 보수 300만원 근로자 몫(보수가 그대로라고 가정) · 해마다 0.5%p씩</text>']
    for v in range(0, ymax + 1, 50000):
        b.append(f'<line x1="{L}" y1="{Y(v):.1f}" x2="{R}" y2="{Y(v):.1f}" stroke="#e3e7eb"/>')
        b.append(f'<text x="{L - 12}" y="{Y(v) + 7:.1f}" font-size="18" text-anchor="end" fill="#5b6773">{v // 10000}만</text>')
    for i, (yr, v) in enumerate(zip(years, vals)):
        cx = L + (R - L) / len(years) * (i + 0.5)
        rate = calc.NPS_RATE[yr] * 100
        b.append(f'<rect x="{cx - bw / 2:.1f}" y="{Y(v):.1f}" width="{bw:.1f}" height="{B - Y(v):.1f}" fill="{"#1f5f8b" if i else "#d99a3b"}"/>')
        b.append(f'<text x="{cx:.1f}" y="{Y(v) - 10:.1f}" font-size="18" text-anchor="middle" fill="#16212e">{v:,}</text>')
        b.append(f'<text x="{cx:.1f}" y="{B + 30}" font-size="19" text-anchor="middle" fill="#3d4852">{yr}</text>')
        b.append(f'<text x="{cx:.1f}" y="{B + 56}" font-size="17" text-anchor="middle" fill="#5b6773">{float(rate):g}%</text>')
    return svg(W, H, "\n".join(b), "국민연금 보험료율 연도별 인상에 따른 월 보수 300만원 근로자 몫 막대그림")


if __name__ == "__main__":
    open(os.path.join(OUT, "01_대표.svg"), "w", encoding="utf-8").write(fig1())
    open(os.path.join(OUT, "02_연금요율.svg"), "w", encoding="utf-8").write(fig2())
    print("그림 2장")
