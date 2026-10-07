#!/usr/bin/env python3
"""그림 2장을 표준 라이브러리로 SVG로 그린다. 숫자는 calc.py 함수에서 가져온다."""
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calc  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "그림")
os.makedirs(OUT, exist_ok=True)
FONT = "font-family=\"'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif\""


def eok1(v):
    return f"{v / calc.EOK:.2f}억".replace(".00억", "억")


def waterfall():
    """15억원 예시: 과세가액에서 공제를 차례로 빼 과세표준까지."""
    W, H = 1200, 675
    e = calc.MAIN_ESTATE
    a = int(e * calc.spouse_share(2))
    r = calc.compute(e, calc.MAIN_FIN, a, 2)
    steps = [("상속세 과세가액", e, "total"),
             ("① 일괄공제", r["일괄공제"], "minus"),
             ("② 배우자공제", r["배우자공제"], "minus"),
             ("③ 금융재산공제", r["금융재산공제"], "minus"),
             ("과세표준", r["과세표준"], "total")]
    left, right, top, bottom = 90, 40, 130, 120
    pw, ph = W - left - right, H - top - bottom
    ymax = 16 * calc.EOK
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="{left}" y="54" font-size="32" font-weight="700" fill="#1f2937" {FONT}>상속재산 15억원, 공제를 빼는 순서</text>',
         f'<text x="{left}" y="92" font-size="20" fill="#4b5563" {FONT}>배우자 + 성인 자녀 2명 · 배우자가 법정상속분 3/7 상속 · 예금 3억원 · 2026년 10월 6일 상속세 및 증여세법 기준</text>']
    for v in range(0, 16 + 1, 4):
        y = top + ph - ph * v * calc.EOK / ymax
        s.append(f'<line x1="{left}" y1="{y:.1f}" x2="{W - right}" y2="{y:.1f}" stroke="#e5e7eb"/>')
        s.append(f'<text x="{left - 10}" y="{y + 6:.1f}" font-size="17" text-anchor="end" fill="#6b7280" {FONT}>{v}억</text>')
    n = len(steps)
    gw = pw / n
    bw = gw * 0.56
    level = 0
    for i, (name, v, kind) in enumerate(steps):
        if kind == "total":
            lo, hi, col = 0, v, ("#1e3a5f" if i == 0 else "#0a6350")
            level = v
        else:
            lo, hi, col = level - v, level, "#93c5fd"
            level -= v
        x = left + gw * i + (gw - bw) / 2
        y_hi = top + ph - ph * hi / ymax
        y_lo = top + ph - ph * lo / ymax
        s.append(f'<rect x="{x:.1f}" y="{y_hi:.1f}" width="{bw:.1f}" height="{y_lo - y_hi:.1f}" fill="{col}"/>')
        label = eok1(v) if kind == "total" else "− " + eok1(v)
        s.append(f'<text x="{x + bw / 2:.1f}" y="{y_hi - 10:.1f}" font-size="21" font-weight="700" text-anchor="middle" fill="#111827" {FONT}>{label}</text>')
        s.append(f'<text x="{left + gw * i + gw / 2:.1f}" y="{top + ph + 34}" font-size="20" text-anchor="middle" fill="#111827" {FONT}>{name}</text>')
        if i < n - 1:
            nx = left + gw * (i + 1) + (gw - bw) / 2
            yl = top + ph - ph * level / ymax
            s.append(f'<line x1="{x + bw:.1f}" y1="{yl:.1f}" x2="{nx:.1f}" y2="{yl:.1f}" stroke="#9ca3af" stroke-dasharray="5 5"/>')
    s.append(f'<text x="{left}" y="{H - 34}" font-size="20" fill="#111827" {FONT}>산출세액 {r["산출세액"]:,}원 − 신고세액공제 3% {r["신고세액공제"]:,}원 = 납부세액 {r["납부세액"]:,}원</text>')
    s.append('</svg>')
    open(os.path.join(OUT, "01_대표.svg"), "w", encoding="utf-8").write("\n".join(s))


def by_size():
    W, H = 1200, 640
    left, right, top, bottom = 120, 40, 130, 110
    pw, ph = W - left - right, H - top - bottom
    ymax = 18 * calc.EOK
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="{left}" y="54" font-size="32" font-weight="700" fill="#1f2937" {FONT}>상속재산 규모별 상속세(신고세액공제 뒤)</text>',
         f'<text x="{left}" y="92" font-size="20" fill="#4b5563" {FONT}>성인 자녀 2명 · 금융재산은 상속재산의 20% · 채무·장례비·사전증여 0 가정</text>']
    for v in range(0, 18 + 1, 3):
        y = top + ph - ph * v * calc.EOK / ymax
        s.append(f'<line x1="{left}" y1="{y:.1f}" x2="{W - right}" y2="{y:.1f}" stroke="#e5e7eb"/>')
        s.append(f'<text x="{left - 10}" y="{y + 6:.1f}" font-size="17" text-anchor="end" fill="#6b7280" {FONT}>{v}억</text>')
    cols = ["#0a6350", "#93c5fd", "#dc6b2f"]
    n = len(calc.ESTATES)
    gw = pw / n
    bw = gw * 0.26
    for i, e in enumerate(calc.ESTATES):
        f = e // 5
        vals = [calc.compute(e, f, int(e * calc.spouse_share(2)), 2)["납부세액"],
                calc.compute(e, f, 0, 2)["납부세액"],
                calc.compute(e, f, None, 2)["납부세액"]]
        x0 = left + gw * i + gw / 2 - bw * 1.5
        for j, v in enumerate(vals):
            h = ph * v / ymax
            x = x0 + j * bw
            y = top + ph - h
            s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw - 4:.1f}" height="{h:.1f}" fill="{cols[j]}"/>')
            s.append(f'<text x="{x + (bw - 4) / 2:.1f}" y="{y - 7:.1f}" font-size="14" text-anchor="middle" fill="#111827" {FONT}>{eok1(v) if v else "0"}</text>')
        s.append(f'<text x="{left + gw * i + gw / 2:.1f}" y="{top + ph + 32}" font-size="20" text-anchor="middle" fill="#111827" {FONT}>{e // calc.EOK}억원</text>')
    ly = H - 34
    labels = ["배우자가 법정상속분 상속", "배우자 상속분 0원(공제 5억원)", "배우자 없음"]
    x = left
    for j, lab in enumerate(labels):
        s.append(f'<rect x="{x}" y="{ly - 16}" width="22" height="22" fill="{cols[j]}"/>')
        s.append(f'<text x="{x + 30}" y="{ly + 2}" font-size="18" fill="#111827" {FONT}>{lab}</text>')
        x += 330
    s.append('</svg>')
    open(os.path.join(OUT, "02_규모별.svg"), "w", encoding="utf-8").write("\n".join(s))


if __name__ == "__main__":
    waterfall()
    by_size()
