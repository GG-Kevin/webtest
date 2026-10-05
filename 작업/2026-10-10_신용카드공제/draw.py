#!/usr/bin/env python3
"""그림 2장을 표준 라이브러리로 SVG로 그린다. 숫자는 모두 calc.py 함수에서 가져온다."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calc  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "그림")
os.makedirs(OUT, exist_ok=True)
FONT = "font-family=\"'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif\""


def lines_chart():
    W, H = 1200, 675
    left, right, top, bottom = 120, 70, 140, 100
    pw, ph = W - left - right, H - top - bottom
    wage = 40_000_000
    xmax, ymax = 36_000_000, 3_500_000
    X = lambda v: left + pw * v / xmax  # noqa: E731
    Y = lambda v: top + ph - ph * v / ymax  # noqa: E731
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="{left}" y="56" font-size="32" font-weight="700" fill="#16212e" {FONT}>총급여 4천만원, 1년 카드 사용액과 소득공제액</text>',
         f'<text x="{left}" y="96" font-size="19" fill="#4b5563" {FONT}>문턱 1,000만원(총급여 25%) · 신용 15% / 체크·현금영수증 30% · 한도 300만원 · 2026년 10월 6일 조세특례제한법 제126조의2 기준</text>']
    for v in range(0, ymax + 1, 500_000):
        y = Y(v)
        s.append(f'<line x1="{left}" y1="{y:.1f}" x2="{W - right}" y2="{y:.1f}" stroke="#e5e7eb"/>')
        s.append(f'<text x="{left - 12}" y="{y + 6:.1f}" font-size="17" text-anchor="end" fill="#6b7280" {FONT}>{v // 10_000}만</text>')
    for v in range(0, xmax + 1, 4_000_000):
        x = X(v)
        s.append(f'<text x="{x:.1f}" y="{top + ph + 30}" font-size="17" text-anchor="middle" fill="#6b7280" {FONT}>{v // 10_000:,}만</text>')
    s.append(f'<text x="{left + pw / 2:.1f}" y="{H - 24}" font-size="18" text-anchor="middle" fill="#374151" {FONT}>1년 사용액(원)</text>')
    mn = calc.min_usage(wage)
    s.append(f'<line x1="{X(mn):.1f}" y1="{top}" x2="{X(mn):.1f}" y2="{top + ph}" stroke="#9ca3af" stroke-dasharray="6 6"/>')
    s.append(f'<text x="{X(mn) + 8:.1f}" y="{top + 24}" font-size="17" fill="#4b5563" {FONT}>여기까지는 0원</text>')
    lim = calc.LIMIT[True][0]
    s.append(f'<line x1="{left}" y1="{Y(lim):.1f}" x2="{W - right}" y2="{Y(lim):.1f}" stroke="#b91c1c" stroke-dasharray="4 4"/>')
    s.append(f'<text x="{W - right - 6}" y="{Y(lim) - 10:.1f}" font-size="17" text-anchor="end" fill="#b91c1c" {FONT}>한도 {lim // 10_000}만원</text>')
    series = [("신용카드만 쓴 경우", "#c2410c", "credit"), ("체크카드·현금영수증만 쓴 경우", "#0a6350", "debit")]
    for i, (lab, col, key) in enumerate(series):
        pts = []
        for v in range(0, xmax + 1, 250_000):
            pts.append(f"{X(v):.1f},{Y(calc.deduction(wage, **{key: v})['소득공제액']):.1f}")
        s.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{col}" stroke-width="4"/>')
        full = mn + lim * 100 // (calc.R_CREDIT if key == "credit" else calc.R_DEBIT)
        s.append(f'<circle cx="{X(full):.1f}" cy="{Y(lim):.1f}" r="7" fill="{col}"/>')
        s.append(f'<text x="{X(full):.1f}" y="{Y(lim) + 30:.1f}" font-size="17" text-anchor="middle" fill="{col}" {FONT}>{full // 10_000:,}만원에서 한도</text>')
        lx, ly = left + 30, top + 10 + 34 * i
        s.append(f'<rect x="{lx}" y="{ly}" width="26" height="8" fill="{col}"/>')
        s.append(f'<text x="{lx + 36}" y="{ly + 10}" font-size="19" fill="#1f2937" {FONT}>{lab}</text>')
    s.append('</svg>')
    open(os.path.join(OUT, "01_대표.svg"), "w", encoding="utf-8").write("\n".join(s))


def kids_bars():
    W, H = 1200, 520
    left, right, top = 230, 80, 130
    bar_h, gap = 70, 40
    xmax = 7_000_000
    pw = W - left - right
    X = lambda v: left + pw * v / xmax  # noqa: E731
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="60" y="56" font-size="30" font-weight="700" fill="#16212e" {FONT}>같은 사용액, 2026년 자녀 한도를 넣으면</text>',
         f'<text x="60" y="94" font-size="19" fill="#4b5563" {FONT}>국세청 2025년 연말정산 신고안내 사례1(총급여 6,800만원·4,300만원 사용)을 2026년 조문으로 다시 계산</text>']
    labels = ((0, "자녀등 없음"), (1, "자녀등 1명"), (2, "자녀등 2명 이상"))
    for i, (k, lab) in enumerate(labels):
        r = calc.deduction(kids=k, **calc.NTS_CASE)
        y = top + i * (bar_h + gap)
        base = min(r["공제가능"], r["한도"])
        s.append(f'<text x="{left - 16}" y="{y + bar_h / 2 + 7:.1f}" font-size="20" text-anchor="end" fill="#1f2937" {FONT}>{lab}</text>')
        s.append(f'<rect x="{left}" y="{y}" width="{X(base) - left:.1f}" height="{bar_h}" fill="#1e3a8a"/>')
        s.append(f'<rect x="{X(base):.1f}" y="{y}" width="{X(base + r["추가"]) - X(base):.1f}" height="{bar_h}" fill="#60a5fa"/>')
        s.append(f'<text x="{left + 12}" y="{y + bar_h / 2 + 7:.1f}" font-size="18" fill="#ffffff" {FONT}>기본 {base // 10_000}만</text>')
        s.append(f'<text x="{X(base) + 10:.1f}" y="{y + bar_h / 2 + 7:.1f}" font-size="18" fill="#0f172a" {FONT}>추가 {r["추가"] // 10_000}만</text>')
        s.append(f'<text x="{X(r["소득공제액"]) + 14:.1f}" y="{y + bar_h / 2 + 8:.1f}" font-size="22" font-weight="700" fill="#16212e" {FONT}>{r["소득공제액"] // 10_000}만원</text>')
    s.append('</svg>')
    open(os.path.join(OUT, "02_자녀한도.svg"), "w", encoding="utf-8").write("\n".join(s))


if __name__ == "__main__":
    lines_chart()
    kids_bars()
