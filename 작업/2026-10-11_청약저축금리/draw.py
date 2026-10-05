#!/usr/bin/env python3
"""대표 그림 1장(SVG, 폭 1,200px)을 표준 라이브러리로 그린다. 숫자는 calc.py 함수에서 가져온다."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calc  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "그림")
os.makedirs(OUT, exist_ok=True)
FONT = "font-family=\"'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif\""
COL = {calc.R0: "#d1d5db", calc.R1: "#93c5fd", calc.R2: "#60a5fa", calc.R3: "#1d4ed8"}


def chart():
    W, H = 1200, 675
    left, right, top, bottom = 110, 40, 150, 100
    pw, ph = W - left - right, H - top - bottom
    N = 30
    ymax = 140_000
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="{left}" y="52" font-size="32" font-weight="700" fill="#1f2937" {FONT}>월 10만원 청약통장, 해지 시점별 세전 이자</text>',
         f'<text x="{left}" y="88" font-size="20" fill="#4b5563" {FONT}>매월 같은 날 납입 · 단리 월 단위 근사 · 2026년 10월 6일 주택도시기금 약정이율 기준</text>']
    # 범례
    legend = [(calc.R1, "1년 미만 2.3%"), (calc.R2, "1년 이상 2.8%"), (calc.R3, "2년 이상 3.1%")]
    for k, (r, t) in enumerate(legend):
        x = left + k * 230
        s.append(f'<rect x="{x}" y="108" width="22" height="22" fill="{COL[r]}"/>')
        s.append(f'<text x="{x + 30}" y="126" font-size="19" fill="#111827" {FONT}>{t}</text>')
    for v in range(0, ymax + 1, 20_000):
        y = top + ph - ph * v / ymax
        s.append(f'<line x1="{left}" y1="{y:.1f}" x2="{W - right}" y2="{y:.1f}" stroke="#e5e7eb"/>')
        s.append(f'<text x="{left - 12}" y="{y + 6:.1f}" font-size="17" text-anchor="end" fill="#6b7280" {FONT}>{v // 10_000}만</text>')
    gw = pw / N
    for n in range(1, N + 1):
        v = calc.interest(100_000, n)
        r = calc.rate_for(n)
        h = ph * v / ymax
        x = left + gw * (n - 1) + gw * 0.12
        y = top + ph - h
        s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{gw * 0.76:.1f}" height="{h:.1f}" fill="{COL[r]}"/>')
        if n in (11, 12, 23, 24, 30):
            s.append(f'<text x="{x + gw * 0.38:.1f}" y="{y - 10:.1f}" font-size="16" text-anchor="middle" fill="#111827" {FONT}>{v:,}</text>')
        if n % 3 == 0 or n == 1:
            s.append(f'<text x="{x + gw * 0.38:.1f}" y="{top + ph + 28}" font-size="17" text-anchor="middle" fill="#374151" {FONT}>{n}</text>')
    s.append(f'<text x="{left + pw / 2:.0f}" y="{top + ph + 62}" font-size="19" text-anchor="middle" fill="#374151" {FONT}>가입일부터 해지일까지 개월 수(= 넣은 횟수) · 막대 위 숫자는 원</text>')
    s.append('</svg>')
    with open(os.path.join(OUT, "01_대표.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(s))


if __name__ == "__main__":
    chart()
    print("그림/01_대표.svg")
