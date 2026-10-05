#!/usr/bin/env python3
"""그림 2장을 표준 라이브러리로 SVG로 그린다. 숫자는 calc.py에서 가져온다."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import calc  # noqa: E402

OUT = os.path.join(HERE, "그림")
os.makedirs(OUT, exist_ok=True)
FONT = "font-family=\"'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif\""
COLORS = {55: "#94a3b8", 65: "#0a6350", 75: "#c2410c", 80: "#1d4ed8"}


def lines():
    W, H = 1200, 675
    left, right, top, bottom = 110, 150, 125, 95
    pw, ph = W - left - right, H - top - bottom
    ymax = 450
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="{left}" y="52" font-size="32" font-weight="700" fill="#1f2937" {FONT}>주택연금 월지급금, 나이와 집값에 따라 이렇게 달라집니다</text>',
         f'<text x="{left}" y="90" font-size="19" fill="#4b5563" {FONT}>종신지급방식 정액형 · 일반주택 · 한국주택금융공사 월지급금 예시(2026년 10월 5일 열람 기준) · 단위 만원</text>']
    for v in range(0, ymax + 1, 50):
        y = top + ph - ph * v / ymax
        s.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + pw}" y2="{y:.1f}" stroke="#e5e7eb"/>')
        s.append(f'<text x="{left - 12}" y="{y + 6:.1f}" font-size="17" text-anchor="end" fill="#6b7280" {FONT}>{v}</text>')
    step = pw / 11
    for i, p in enumerate(calc.PRICES):
        x = left + step * i
        s.append(f'<text x="{x:.1f}" y="{top + ph + 30}" font-size="17" text-anchor="middle" fill="#374151" {FONT}>{p}억</text>')
    s.append(f'<text x="{left + pw / 2:.1f}" y="{top + ph + 64}" font-size="18" text-anchor="middle" fill="#374151" {FONT}>공사가 인정하는 주택 시세(12억원을 넘으면 12억원으로 봄)</text>')
    for age in [55, 65, 75, 80]:
        pts = []
        for i, p in enumerate(calc.PRICES):
            v = calc.monthly(age, p) / 10_000
            pts.append((left + step * i, top + ph - ph * v / ymax))
        path = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        c = COLORS[age]
        s.append(f'<polyline points="{path}" fill="none" stroke="{c}" stroke-width="4"/>')
        for x, y in pts:
            s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{c}"/>')
        lx, ly = pts[-1]
        s.append(f'<text x="{lx + 14:.1f}" y="{ly + 6:.1f}" font-size="19" font-weight="700" fill="{c}" {FONT}>{age}세 {calc.man(calc.monthly(age, 12))}</text>')
    # 평평해지는 구간 표시
    x9 = left + step * 8
    s.append(f'<rect x="{x9 - 10:.1f}" y="{top - 6}" width="{step * 3 + 20:.1f}" height="{ph * 0.26:.1f}" fill="none" stroke="#c2410c" stroke-dasharray="7 6" stroke-width="2"/>')
    s.append(f'<text x="{x9 - 18:.1f}" y="{top + 22}" font-size="17" text-anchor="end" fill="#c2410c" {FONT}>75세는 10억원, 80세는 9억원부터 금액이 같습니다</text>')
    s.append("</svg>")
    with open(os.path.join(OUT, "01_대표.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(s))


def steps():
    W, H = 1200, 520
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="60" y="56" font-size="30" font-weight="700" fill="#1f2937" {FONT}>가입 가능 여부는 네 가지를 차례로 봅니다</text>',
         f'<text x="60" y="92" font-size="18" fill="#4b5563" {FONT}>한국주택금융공사법 시행령 제3조의2·제28조의9, 공사 주택연금 안내(2026년 10월 5일 열람 기준)</text>']
    boxes = [
        ("① 나이", "부부 중 1명이", "55세 이상", "주택 등기 시점 기준"),
        ("② 집값", "부부 합산 공시가격 등", "12억원 이하", "넘는 2주택은 3년 안 처분"),
        ("③ 집 종류", "주택·분양 노인복지주택", "주거용 오피스텔", "상가·토지·분양권 제외"),
        ("④ 거주", "가입자나 배우자가", "실제로 전입·거주", "입원 등 예외는 1주택만"),
    ]
    bw, bh, gap, y0 = 250, 270, 36, 150
    x = 60
    for title, l1, l2, l3 in boxes:
        s.append(f'<rect x="{x}" y="{y0}" width="{bw}" height="{bh}" rx="14" fill="#f3f7f6" stroke="#0a6350" stroke-width="2"/>')
        s.append(f'<text x="{x + bw / 2}" y="{y0 + 52}" font-size="26" font-weight="700" text-anchor="middle" fill="#0a6350" {FONT}>{title}</text>')
        s.append(f'<text x="{x + bw / 2}" y="{y0 + 112}" font-size="19" text-anchor="middle" fill="#374151" {FONT}>{l1}</text>')
        s.append(f'<text x="{x + bw / 2}" y="{y0 + 158}" font-size="26" font-weight="700" text-anchor="middle" fill="#111827" {FONT}>{l2}</text>')
        s.append(f'<text x="{x + bw / 2}" y="{y0 + 222}" font-size="17" text-anchor="middle" fill="#6b7280" {FONT}>{l3}</text>')
        x += bw + gap
    s.append(f'<text x="60" y="{y0 + bh + 60}" font-size="18" fill="#374151" {FONT}>네 칸을 모두 통과해야 신청할 수 있고, 월지급금은 공시가격이 아니라 공사가 인정하는 시세로 정합니다.</text>')
    s.append("</svg>")
    with open(os.path.join(OUT, "02_조건.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(s))


if __name__ == "__main__":
    lines()
    steps()
    print("그림 2장:", sorted(os.listdir(OUT)))
