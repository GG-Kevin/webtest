#!/usr/bin/env python3
"""그림 2장을 표준 라이브러리로 SVG로 그린다. 숫자는 calc.py 함수에서 가져온다."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calc  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "그림")
os.makedirs(OUT, exist_ok=True)
FONT = "font-family=\"'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif\""


def months_chart():
    W, H = 1200, 675
    left, right, top, bottom = 110, 40, 140, 100
    pw, ph = W - left - right, H - top - bottom
    ymax = 90
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="{left}" y="54" font-size="32" font-weight="700" fill="#1f2937" {FONT}>자녀 수별 국민연금 추가 가입기간</text>',
         f'<text x="{left}" y="92" font-size="20" fill="#4b5563" {FONT}>국민연금법 제19조 · 2026년 10월 5일 국가법령정보센터 원문 기준 · 단위 개월</text>']
    for v in range(0, ymax + 1, 15):
        y = top + ph - ph * v / ymax
        s.append(f'<line x1="{left}" y1="{y:.1f}" x2="{W - right}" y2="{y:.1f}" stroke="#e5e7eb"/>')
        s.append(f'<text x="{left - 12}" y="{y + 6:.1f}" font-size="17" text-anchor="end" fill="#6b7280" {FONT}>{v}</text>')
    capy = top + ph - ph * calc.OLD_CAP / ymax
    s.append(f'<line x1="{left}" y1="{capy:.1f}" x2="{W - right}" y2="{capy:.1f}" stroke="#b91c1c" stroke-dasharray="8 6" stroke-width="2"/>')
    s.append(f'<text x="{W - right - 6}" y="{capy - 8:.1f}" font-size="17" text-anchor="end" fill="#b91c1c" {FONT}>종전 상한 50개월(2026년부터 없어짐)</text>')
    n = len(calc.KIDS)
    gw = pw / n
    bw = gw * 0.32
    for i, k in enumerate(calc.KIDS):
        x0 = left + gw * i + gw * 0.16
        for j, (val, col) in enumerate(((calc.months_new(k), "#0a6350"), (calc.months_old(k), "#9aa5b1"))):
            h = ph * val / ymax
            x = x0 + j * bw
            y = top + ph - h
            s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw - 6:.1f}" height="{h:.1f}" fill="{col}"/>')
            s.append(f'<text x="{x + (bw - 6) / 2:.1f}" y="{y - 8:.1f}" font-size="18" font-weight="700" text-anchor="middle" fill="#1f2937" {FONT}>{val}</text>')
        s.append(f'<text x="{left + gw * i + gw / 2:.1f}" y="{top + ph + 34}" font-size="20" text-anchor="middle" fill="#1f2937" {FONT}>자녀 {k}명</text>')
    ly = H - 30
    s.append(f'<rect x="{left}" y="{ly - 16}" width="20" height="20" fill="#0a6350"/>')
    s.append(f'<text x="{left + 30}" y="{ly}" font-size="18" fill="#1f2937" {FONT}>첫째를 2026년 1월 1일 이후 얻은 경우</text>')
    s.append(f'<rect x="{left + 430}" y="{ly - 16}" width="20" height="20" fill="#9aa5b1"/>')
    s.append(f'<text x="{left + 460}" y="{ly}" font-size="18" fill="#1f2937" {FONT}>자녀를 모두 2008~2025년에 얻은 경우</text>')
    s.append('</svg>')
    with open(os.path.join(OUT, "01_대표.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(s))


def gain_chart():
    W, H = 1200, 600
    left, right, top, bottom = 260, 170, 130, 60
    pw = W - left - right
    rows = [(f"자녀 {k}명 · {calc.months_new(k)}개월", int(calc.gain_month(calc.months_new(k)))) for k in calc.KIDS]
    rows.append(("군 복무 12개월(참고)", int(calc.gain_month(calc.MIL_MAX, calc.A / 2))))
    vmax = 240_000
    rh = (H - top - bottom) / len(rows)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="40" y="54" font-size="30" font-weight="700" fill="#1f2937" {FONT}>추가 가입기간이 늘리는 월 연금(2026년 A값 기준)</text>',
         f'<text x="40" y="90" font-size="19" fill="#4b5563" {FONT}>월 증가 = 1.29 × (A값 + 크레딧 소득) × 개월 수 ÷ 2,880 · 본인 소득과 관계없음 · 오늘 돈 기준</text>']
    for i, (label, v) in enumerate(rows):
        y = top + rh * i + rh * 0.18
        h = rh * 0.64
        w = pw * v / vmax
        col = "#9aa5b1" if "군" in label else "#0a6350"
        s.append(f'<text x="{left - 14}" y="{y + h / 2 + 7:.1f}" font-size="19" text-anchor="end" fill="#1f2937" {FONT}>{label}</text>')
        s.append(f'<rect x="{left}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{col}"/>')
        s.append(f'<text x="{left + w + 10:.1f}" y="{y + h / 2 + 7:.1f}" font-size="19" font-weight="700" fill="#1f2937" {FONT}>월 {v:,}원</text>')
    s.append('</svg>')
    with open(os.path.join(OUT, "02_증가액.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(s))


if __name__ == "__main__":
    months_chart()
    gain_chart()
