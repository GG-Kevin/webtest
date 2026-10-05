#!/usr/bin/env python3
"""그림 2장을 표준 라이브러리로 SVG로 그린다. 숫자는 calc.py 함수에서 가져온다."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calc  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "그림")
os.makedirs(OUT, exist_ok=True)
FONT = "font-family=\"'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif\""


def credit_curve():
    W, H = 1200, 675
    left, right, top, bottom = 120, 60, 130, 100
    pw, ph = W - left - right, H - top - bottom
    xmax, ymax = 12_000_000, 1_200_000
    X = lambda v: left + pw * v / xmax  # noqa: E731
    Y = lambda v: top + ph - ph * v / ymax  # noqa: E731
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="{left}" y="54" font-size="32" font-weight="700" fill="#16212e" {FONT}>의료비가 늘 때 소득세 공제액은 이렇게 움직입니다</text>',
         f'<text x="{left}" y="92" font-size="19" fill="#4b5563" {FONT}>일반 부양가족 의료비 기준 · 총급여 3% 문턱 뒤 15% · 연 700만원 한도 · 2026년 10월 5일 소득세법 제59조의4 기준</text>']
    for v in range(0, ymax + 1, 200_000):
        y = Y(v)
        s.append(f'<line x1="{left}" y1="{y:.1f}" x2="{W - right}" y2="{y:.1f}" stroke="#e5e7eb"/>')
        s.append(f'<text x="{left - 12}" y="{y + 6:.1f}" font-size="17" text-anchor="end" fill="#6b7280" {FONT}>{v // 10_000}만</text>')
    for v in range(0, xmax + 1, 2_000_000):
        x = X(v)
        s.append(f'<text x="{x:.1f}" y="{top + ph + 30}" font-size="17" text-anchor="middle" fill="#6b7280" {FONT}>{v // 10_000:,}만</text>')
    s.append(f'<text x="{left + pw / 2:.1f}" y="{H - 24}" font-size="18" text-anchor="middle" fill="#374151" {FONT}>1년 의료비 지출(원)</text>')
    colors = {40_000_000: "#0a6350", 60_000_000: "#c2410c"}
    for i, (w, col) in enumerate(colors.items()):
        pts = []
        for v in range(0, xmax + 1, 100_000):
            pts.append(f"{X(v):.1f},{Y(calc.credit(w, general=v)['소득세']):.1f}")
        s.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{col}" stroke-width="4"/>')
        t = calc.threshold(w)
        cap_at = t + calc.GENERAL_CAP
        s.append(f'<circle cx="{X(t):.1f}" cy="{Y(0):.1f}" r="7" fill="{col}"/>')
        s.append(f'<circle cx="{X(cap_at):.1f}" cy="{Y(calc.GENERAL_CAP * calc.RATE_BASE // 100):.1f}" r="7" fill="{col}"/>')
        s.append(f'<text x="{X(t):.1f}" y="{Y(0) - 16 - 26 * i:.1f}" font-size="17" text-anchor="middle" fill="{col}" {FONT}>{t // 10_000}만부터</text>')
        s.append(f'<text x="{X(cap_at) + 10:.1f}" y="{Y(1_050_000) + 34 + 26 * i:.1f}" font-size="17" fill="{col}" {FONT}>{cap_at // 10_000}만에서 한도</text>')
        lx = left + 30
        ly = top + 10 + 34 * i
        s.append(f'<rect x="{lx}" y="{ly}" width="26" height="8" fill="{col}"/>')
        s.append(f'<text x="{lx + 36}" y="{ly + 10}" font-size="19" fill="#1f2937" {FONT}>총급여 {w // 10_000:,}만원</text>')
    s.append(f'<text x="{X(10_500_000):.1f}" y="{Y(1_050_000) - 14:.1f}" font-size="18" text-anchor="middle" fill="#374151" {FONT}>최대 105만원</text>')
    s.append('</svg>')
    open(os.path.join(OUT, "01_대표.svg"), "w", encoding="utf-8").write("\n".join(s))


def order_bar():
    c = calc.ORDER_CASE
    r = calc.credit(c["wage"], general=c["general"], special=c["special"], ivf=c["ivf"])
    W, H = 1200, 420
    left, right = 60, 60
    pw = W - left - right
    total = c["general"] + c["special"] + c["ivf"]
    X = lambda v: left + pw * v / total  # noqa: E731
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="{left}" y="50" font-size="28" font-weight="700" fill="#16212e" {FONT}>3% 문턱은 공제율이 낮은 의료비부터 채웁니다</text>',
         f'<text x="{left}" y="86" font-size="18" fill="#4b5563" {FONT}>총급여 5,000만원 · 문턱 150만원 · 배우자 50만 → 본인 100만 → 난임시술비 400만 순서</text>']
    segs = [("배우자 50만", c["general"], "#9ca3af"), ("본인 100만", c["special"], "#6b7280"), ("난임시술비 400만", c["ivf"], "#0a6350")]
    x0 = 0
    for name, v, col in segs:
        s.append(f'<rect x="{X(x0):.1f}" y="140" width="{X(x0 + v) - X(x0):.1f}" height="70" fill="{col}"/>')
        s.append(f'<text x="{(X(x0) + X(x0 + v)) / 2:.1f}" y="235" font-size="18" text-anchor="middle" fill="#1f2937" {FONT}>{name}</text>')
        x0 += v
    t = r["문턱"]
    s.append(f'<rect x="{X(0):.1f}" y="130" width="{X(t) - X(0):.1f}" height="90" fill="none" stroke="#c2410c" stroke-width="4" stroke-dasharray="10 6"/>')
    s.append(f'<text x="{X(0):.1f}" y="120" font-size="18" fill="#c2410c" {FONT}>문턱 {t // 10_000}만원이 여기서 빠짐</text>')
    s.append(f'<text x="{left}" y="300" font-size="22" fill="#1f2937" {FONT}>난임시술비 400만원 전부에 30% → 소득세 공제 {r["소득세"] // 10_000}만원</text>')
    s.append(f'<text x="{left}" y="340" font-size="18" fill="#4b5563" {FONT}>문턱을 난임시술비에서 먼저 뺀다고 놓으면 97.5만원 — 조문 순서가 22.5만원 더 큽니다</text>')
    s.append('</svg>')
    open(os.path.join(OUT, "02_순서.svg"), "w", encoding="utf-8").write("\n".join(s))


if __name__ == "__main__":
    credit_curve()
    order_bar()
