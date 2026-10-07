#!/usr/bin/env python3
"""그림 2장을 표준 라이브러리로 SVG로 그린다. 숫자는 calc.py 함수에서 가져온다."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calc  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "그림")
os.makedirs(OUT, exist_ok=True)
FONT = "font-family=\"'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif\""


def bar_chart():
    W, H = 1200, 675
    left, right, top, bottom = 110, 40, 120, 110
    pw, ph = W - left - right, H - top - bottom
    ymax = 1_800_000
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="{left}" y="52" font-size="32" font-weight="700" fill="#1f2937" {FONT}>월세별 1년 세액공제액</text>',
         f'<text x="{left}" y="88" font-size="20" fill="#4b5563" {FONT}>12개월 낸 경우 · 월세 합계 1,000만원까지만 계산 · 2026년 10월 5일 조세특례제한법 제95조의2 기준</text>']
    for v in range(0, ymax + 1, 300_000):
        y = top + ph - ph * v / ymax
        s.append(f'<line x1="{left}" y1="{y:.1f}" x2="{W - right}" y2="{y:.1f}" stroke="#e5e7eb"/>')
        s.append(f'<text x="{left - 12}" y="{y + 6:.1f}" font-size="17" text-anchor="end" fill="#6b7280" {FONT}>{v // 10_000}만</text>')
    n = len(calc.MONTHLY)
    gw = pw / n
    bw = gw * 0.38
    for i, m in enumerate(calc.MONTHLY):
        y12 = m * 12
        vals = [(calc.credit(y12, calc.RATE_LOW), "#2563eb"), (calc.credit(y12, calc.RATE_HIGH), "#93c5fd")]
        x0 = left + gw * i + gw / 2 - bw
        for j, (v, col) in enumerate(vals):
            x = x0 + j * bw
            h = ph * v / ymax
            y = top + ph - h
            s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw - 6:.1f}" height="{h:.1f}" fill="{col}"/>')
            s.append(f'<text x="{x + (bw - 6) / 2:.1f}" y="{y - 8:.1f}" font-size="14" text-anchor="middle" fill="#111827" {FONT}>{calc.manf(v)}</text>')
        s.append(f'<text x="{left + gw * i + gw / 2:.1f}" y="{top + ph + 32}" font-size="20" text-anchor="middle" fill="#111827" {FONT}>월 {m // 10_000}만원</text>')
    cap_y = top + ph - ph * calc.credit(calc.CAP, calc.RATE_LOW) / ymax
    s.append(f'<line x1="{left}" y1="{cap_y:.1f}" x2="{W - right}" y2="{cap_y:.1f}" stroke="#dc2626" stroke-dasharray="8 6"/>')
    s.append(f'<text x="{W - right}" y="{cap_y - 10:.1f}" font-size="17" text-anchor="end" fill="#dc2626" {FONT}>17% 상한 170만원(월세 1,000만원)</text>')
    ly = H - 36
    s.append(f'<rect x="{left}" y="{ly - 16}" width="22" height="22" fill="#2563eb"/>')
    s.append(f'<text x="{left + 32}" y="{ly + 2}" font-size="19" fill="#111827" {FONT}>총급여 5,500만원 이하 17%</text>')
    s.append(f'<rect x="{left + 330}" y="{ly - 16}" width="22" height="22" fill="#93c5fd"/>')
    s.append(f'<text x="{left + 362}" y="{ly + 2}" font-size="19" fill="#111827" {FONT}>총급여 5,500만원 초과 8,000만원 이하 15%</text>')
    s.append('</svg>')
    open(os.path.join(OUT, "01_대표.svg"), "w", encoding="utf-8").write("\n".join(s))


def spouse_chart():
    W, H = 1200, 420
    head, sp = 600_000 * 12, 500_000 * 12
    base = calc.spouse(head, sp)
    left, width = 80, 1040
    scale = width / (head + sp)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="{left}" y="50" font-size="28" font-weight="700" fill="#1f2937" {FONT}>부부가 따로 월세를 낼 때 1,000만원을 나누는 법</text>',
         f'<text x="{left}" y="84" font-size="19" fill="#4b5563" {FONT}>세대주 월 60만원 · 배우자 월 50만원 · 2026년 이후 지급분(조세특례제한법 제95조의2 제2항)</text>']
    y, h = 140, 90
    hw = head * scale
    s.append(f'<rect x="{left}" y="{y}" width="{hw:.1f}" height="{h}" fill="#2563eb"/>')
    s.append(f'<text x="{left + hw / 2:.1f}" y="{y + 55}" font-size="22" text-anchor="middle" fill="#ffffff" {FONT}>세대주 {calc.man(head)} 전부 대상</text>')
    bw = base * scale
    s.append(f'<rect x="{left + hw:.1f}" y="{y}" width="{bw:.1f}" height="{h}" fill="#60a5fa"/>')
    s.append(f'<text x="{left + hw + bw / 2:.1f}" y="{y + 55}" font-size="20" text-anchor="middle" fill="#ffffff" {FONT}>배우자 {calc.man(base)}</text>')
    rw = (sp - base) * scale
    s.append(f'<rect x="{left + hw + bw:.1f}" y="{y}" width="{rw:.1f}" height="{h}" fill="#e5e7eb" stroke="#9ca3af" stroke-dasharray="6 4"/>')
    s.append(f'<text x="{left + hw + bw + rw / 2:.1f}" y="{y + 55}" font-size="20" text-anchor="middle" fill="#374151" {FONT}>제외 {calc.man(sp - base)}</text>')
    cx = left + calc.CAP * scale
    s.append(f'<line x1="{cx:.1f}" y1="{y - 20}" x2="{cx:.1f}" y2="{y + h + 20}" stroke="#dc2626" stroke-width="3"/>')
    s.append(f'<text x="{cx:.1f}" y="{y + h + 48}" font-size="19" text-anchor="middle" fill="#dc2626" {FONT}>두 사람 합계 1,000만원 선</text>')
    s.append(f'<text x="{left}" y="{H - 60}" font-size="21" fill="#111827" {FONT}>세액공제(17%): 세대주 {calc.credit(head, calc.RATE_LOW):,}원 · 배우자 {calc.credit(base, calc.RATE_LOW):,}원</text>')
    s.append(f'<text x="{left}" y="{H - 28}" font-size="18" fill="#4b5563" {FONT}>배우자는 세대주와 주소지 시·군·구가 달라야 하고, 본인도 무주택·총급여 요건을 따로 갖춰야 합니다</text>')
    s.append('</svg>')
    open(os.path.join(OUT, "02_부부.svg"), "w", encoding="utf-8").write("\n".join(s))


if __name__ == "__main__":
    bar_chart()
    spouse_chart()
    print("그림 2장:", sorted(os.listdir(OUT)))
