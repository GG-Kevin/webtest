#!/usr/bin/env python3
"""대표 그림 1장(1,200px)을 표준 라이브러리로 SVG로 그린다. 숫자는 calc.py에서 가져온다."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calc  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "그림")
os.makedirs(OUT, exist_ok=True)
FONT = "font-family=\"'Noto Sans KR','Nanum Gothic','Malgun Gothic','Apple SD Gothic Neo',sans-serif\""


def lines_chart():
    W, H = 1200, 700
    left, right, top, bottom = 110, 40, 130, 120
    pw, ph = W - left - right, H - top - bottom
    ymax = 11_000_000
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="{left}" y="54" font-size="32" font-weight="700" fill="#1f2937" {FONT}>국민취업지원제도 가구 소득선 (2026년, 월)</text>',
         f'<text x="{left}" y="92" font-size="19" fill="#4b5563" {FONT}>2026년 기준 중위소득 × 60% · 100% · 120% · 원 미만 반올림 · 2026년 10월 6일 원문 기준</text>']
    for v in range(0, ymax + 1, 2_000_000):
        y = top + ph - ph * v / ymax
        s.append(f'<line x1="{left}" y1="{y:.1f}" x2="{W - right}" y2="{y:.1f}" stroke="#e5e7eb"/>')
        s.append(f'<text x="{left - 12}" y="{y + 6:.1f}" font-size="17" text-anchor="end" fill="#6b7280" {FONT}>{v // 10_000:,}만</text>')
    cols = [(60, "#0f766e"), (100, "#60a5fa"), (120, "#f59e0b")]
    gw = pw / 6
    bw = gw * 0.26
    for i, n in enumerate(range(1, 7)):
        x0 = left + gw * i + (gw - bw * 3) / 2
        for j, (pct, col) in enumerate(cols):
            v = calc.line(n, pct)
            h = ph * v / ymax
            x = x0 + j * bw
            y = top + ph - h
            s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw - 5:.1f}" height="{h:.1f}" fill="{col}"/>')
            s.append(f'<text x="{x + (bw - 5) / 2:.1f}" y="{y - 8:.1f}" font-size="14" text-anchor="middle" fill="#111827" {FONT}>{v / 10_000:,.0f}만</text>')
        s.append(f'<text x="{left + gw * i + gw / 2:.1f}" y="{top + ph + 34}" font-size="21" text-anchor="middle" fill="#111827" {FONT}>{n}인 가구</text>')
    ly = H - 40
    labels = ["60% 이하: 1유형(수당 월 60만원)", "100% 이하: 2유형 중장년", "120% 이하: 청년 특례선"]
    for j, ((pct, col), lab) in enumerate(zip(cols, labels)):
        x = left + j * 350
        s.append(f'<rect x="{x}" y="{ly - 17}" width="22" height="22" fill="{col}"/>')
        s.append(f'<text x="{x + 32}" y="{ly + 1}" font-size="19" fill="#111827" {FONT}>{lab}</text>')
    s.append('</svg>')
    open(os.path.join(OUT, "01_대표.svg"), "w", encoding="utf-8").write("\n".join(s))


if __name__ == "__main__":
    lines_chart()
