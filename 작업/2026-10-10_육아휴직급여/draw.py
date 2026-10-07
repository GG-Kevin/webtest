#!/usr/bin/env python3
"""대표 그림 1장(SVG, 폭 1,200px)을 표준 라이브러리로 그린다. 숫자는 calc.py 함수에서 가져온다."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calc  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "그림")
os.makedirs(OUT, exist_ok=True)
FONT = "font-family=\"'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif\""


def monthly_chart():
    W, H = 1200, 675
    left, right, top, bottom = 100, 40, 150, 100
    pw, ph = W - left - right, H - top - bottom
    ymax = 3_500_000
    wage = 3_000_000
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="{left}" y="52" font-size="32" font-weight="700" fill="#1f2937" {FONT}>월 통상임금 300만원, 달마다 받는 육아휴직급여</text>',
         f'<text x="{left}" y="88" font-size="19" fill="#4b5563" {FONT}>고용보험법 시행령 제95조·제95조의3 · 2026년 10월 6일 국가법령정보센터 조문 기준</text>',
         f'<rect x="{left}" y="108" width="22" height="16" fill="#94a3b8"/>',
         f'<text x="{left + 30}" y="122" font-size="18" fill="#111827" {FONT}>혼자 쓰는 일반 육아휴직</text>',
         f'<rect x="{left + 280}" y="108" width="22" height="16" fill="#0f766e"/>',
         f'<text x="{left + 310}" y="122" font-size="18" fill="#111827" {FONT}>부모가 각각 6개월 쓸 때(한 사람)</text>']
    for v in range(0, ymax + 1, 500_000):
        y = top + ph - ph * v / ymax
        s.append(f'<line x1="{left}" y1="{y:.1f}" x2="{W - right}" y2="{y:.1f}" stroke="#e5e7eb"/>')
        s.append(f'<text x="{left - 12}" y="{y + 6:.1f}" font-size="16" text-anchor="end" fill="#6b7280" {FONT}>{v // 10_000}만</text>')
    gw = pw / 12
    bw = gw * 0.36
    for i in range(12):
        k = i + 1
        vals = [(calc.month_pay(wage, k), "#94a3b8"), (calc.month_pay(wage, k, "부모"), "#0f766e")]
        x0 = left + gw * i + gw / 2 - bw
        for j, (v, col) in enumerate(vals):
            x = x0 + j * bw
            h = ph * v / ymax
            y = top + ph - h
            s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw - 4:.1f}" height="{h:.1f}" fill="{col}"/>')
            s.append(f'<text x="{x + (bw - 4) / 2:.1f}" y="{y - 7:.1f}" font-size="13" text-anchor="middle" fill="#111827" {FONT}>{v // 10_000}</text>')
        s.append(f'<text x="{left + gw * i + gw / 2:.1f}" y="{top + ph + 28}" font-size="17" text-anchor="middle" fill="#111827" {FONT}>{k}개월째</text>')
    t1, t2 = calc.total(wage, 12), calc.total(wage, 12, "부모")
    s.append(f'<text x="{left}" y="{H - 28}" font-size="20" fill="#1f2937" {FONT}>12개월 합계: 일반 {calc.man(t1)} · 부모 각 6개월 {calc.man(t2)} (막대 위 숫자 단위 만원)</text>')
    s.append('</svg>')
    open(os.path.join(OUT, "01_대표.svg"), "w", encoding="utf-8").write("\n".join(s))


if __name__ == "__main__":
    monthly_chart()
