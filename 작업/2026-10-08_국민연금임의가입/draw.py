#!/usr/bin/env python3
"""그림 2장을 표준 라이브러리로 SVG로 그린다. 숫자는 calc.py 함수에서 가져온다."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import calc  # noqa: E402

OUT = os.path.join(HERE, "그림")
os.makedirs(OUT, exist_ok=True)
FONT = "font-family=\"'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif\""


def fmt_man(v):
    return f"{v / 10_000:,.1f}만"


def hero():
    W, H = 1200, 675
    left, right, top, bottom = 110, 40, 150, 120
    pw, ph = W - left - right, H - top - bottom
    ymax = 700_000
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="{left}" y="56" font-size="34" font-weight="700" fill="#1f2937" {FONT}>국민연금 임의가입: 내는 돈과 10년 뒤 받는 돈</text>',
         f'<text x="{left}" y="94" font-size="20" fill="#4b5563" {FONT}>2026년 월 보험료(9.5%)와 10년 납부 뒤 월 연금 · A값 3,193,511원 가정</text>',
         f'<rect x="{left}" y="112" width="18" height="18" fill="#94a3b8"/>',
         f'<text x="{left + 26}" y="127" font-size="18" fill="#374151" {FONT}>월 보험료</text>',
         f'<rect x="{left + 140}" y="112" width="18" height="18" fill="#0a6350"/>',
         f'<text x="{left + 166}" y="127" font-size="18" fill="#374151" {FONT}>10년 납부 월 연금</text>']
    for v in range(0, ymax + 1, 100_000):
        y = top + ph - ph * v / ymax
        s.append(f'<line x1="{left}" y1="{y:.1f}" x2="{W - right}" y2="{y:.1f}" stroke="#e5e7eb"/>')
        s.append(f'<text x="{left - 12}" y="{y + 6:.1f}" font-size="17" text-anchor="end" fill="#6b7280" {FONT}>{v // 10_000}만</text>')
    n = len(calc.TIERS)
    gw = pw / n
    bw = gw * 0.3
    for i, b in enumerate(calc.TIERS):
        p = calc.premium(b, 2026)
        pen = calc.monthly_pension(b, 10)
        x0 = left + gw * i + gw * 0.17
        for j, (v, col) in enumerate(((p, "#94a3b8"), (pen, "#0a6350"))):
            h = ph * min(v, ymax) / ymax
            x = x0 + j * (bw + 6)
            y = top + ph - h
            s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{h:.1f}" fill="{col}"/>')
            s.append(f'<text x="{x + bw / 2:.1f}" y="{y - 8:.1f}" font-size="16" text-anchor="middle" fill="#111827" {FONT}>{fmt_man(v)}</text>')
        label = f"{b / 10_000:,.1f}만원" if b % 10_000 else f"{b // 10_000:,}만원"
        s.append(f'<text x="{left + gw * i + gw / 2:.1f}" y="{top + ph + 32}" font-size="19" text-anchor="middle" fill="#1f2937" {FONT}>{label}</text>')
    s.append(f'<text x="{left + pw / 2:.1f}" y="{top + ph + 66}" font-size="18" text-anchor="middle" fill="#6b7280" {FONT}>기준소득월액 · 101.3만원이 최저선 · 2026년 10월 5일 원문 기준</text>')
    s.append('</svg>')
    open(os.path.join(OUT, "01_대표.svg"), "w", encoding="utf-8").write("\n".join(s))


def cumulative():
    W, H = 1200, 600
    left, right, top, bottom = 120, 50, 110, 90
    pw, ph = W - left - right, H - top - bottom
    rows = calc.ten_year_schedule()
    total = sum(r[3] for r in rows)
    pen = calc.monthly_pension(calc.MEDIAN_2026, 10)
    months = -(-total // pen)
    xmax = 84
    ymax = 20_000_000
    X = lambda m: left + pw * m / xmax  # noqa: E731
    Y = lambda v: top + ph - ph * v / ymax  # noqa: E731
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="{left}" y="50" font-size="30" font-weight="700" fill="#1f2937" {FONT}>연금 누적액이 10년 보험료 합계를 넘는 달</text>',
         f'<text x="{left}" y="84" font-size="19" fill="#4b5563" {FONT}>최저선으로 2027년부터 10년 납부 · 물가·재평가 없는 명목 계산</text>']
    for v in range(0, ymax + 1, 5_000_000):
        y = Y(v)
        s.append(f'<line x1="{left}" y1="{y:.1f}" x2="{W - right}" y2="{y:.1f}" stroke="#e5e7eb"/>')
        s.append(f'<text x="{left - 12}" y="{y + 6:.1f}" font-size="17" text-anchor="end" fill="#6b7280" {FONT}>{v // 10_000:,}만</text>')
    for m in range(0, xmax + 1, 12):
        s.append(f'<text x="{X(m):.1f}" y="{top + ph + 30}" font-size="17" text-anchor="middle" fill="#6b7280" {FONT}>{m}개월</text>')
    s.append(f'<line x1="{left}" y1="{Y(total):.1f}" x2="{W - right}" y2="{Y(total):.1f}" stroke="#94a3b8" stroke-width="3" stroke-dasharray="10 6"/>')
    s.append(f'<text x="{W - right}" y="{Y(total) - 12:.1f}" font-size="18" text-anchor="end" fill="#374151" {FONT}>10년 낸 보험료 합계 {total:,}원</text>')
    s.append(f'<line x1="{X(0):.1f}" y1="{Y(0):.1f}" x2="{X(xmax):.1f}" y2="{Y(pen * xmax):.1f}" stroke="#0a6350" stroke-width="4"/>')
    s.append(f'<text x="{X(20):.1f}" y="{Y(pen * 20) - 14:.1f}" font-size="18" fill="#0a6350" {FONT}>월 {pen:,}원씩 쌓이는 연금</text>')
    cx, cy = X(months), Y(pen * months)
    s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="9" fill="#b45309"/>')
    s.append(f'<text x="{cx + 14:.1f}" y="{cy + 40:.1f}" font-size="20" font-weight="700" fill="#b45309" {FONT}>{months}개월째</text>')
    s.append(f'<text x="{left + pw / 2:.1f}" y="{H - 20}" font-size="17" text-anchor="middle" fill="#6b7280" {FONT}>연금 받기 시작한 뒤 개월 수 · A값 3,193,511원 가정</text>')
    s.append('</svg>')
    open(os.path.join(OUT, "02_누적.svg"), "w", encoding="utf-8").write("\n".join(s))


if __name__ == "__main__":
    hero()
    cumulative()
