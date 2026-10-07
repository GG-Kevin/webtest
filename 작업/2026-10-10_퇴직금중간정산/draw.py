#!/usr/bin/env python3
"""대표 그림 1장을 표준 라이브러리로 SVG로 그린다. 숫자는 calc.py에서 가져온다."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calc  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "그림")
os.makedirs(OUT, exist_ok=True)
FONT = "font-family=\"'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif\""


def panel(s, x0, y0, w, h, title, rows, vmax, fmt):
    s.append(f'<text x="{x0}" y="{y0}" font-size="24" font-weight="700" fill="#1f2937" {FONT}>{title}</text>')
    bh, gap, top = 64, 46, y0 + 40
    lw = 250
    for i, (label, v, col) in enumerate(rows):
        y = top + i * (bh + gap)
        s.append(f'<text x="{x0}" y="{y + 26}" font-size="18" fill="#111827" {FONT}>{label[0]}</text>')
        s.append(f'<text x="{x0}" y="{y + 52}" font-size="18" fill="#4b5563" {FONT}>{label[1]}</text>')
        bw = (w - lw - 120) * v / vmax
        s.append(f'<rect x="{x0 + lw}" y="{y + 8}" width="{bw:.1f}" height="{bh - 16}" fill="{col}" rx="4"/>')
        s.append(f'<text x="{x0 + lw + bw + 10:.1f}" y="{y + 40}" font-size="20" font-weight="700" fill="#111827" {FONT}>{fmt(v)}</text>')


def main():
    sc = calc.scenarios()
    W, H = 1200, 675
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="60" y="58" font-size="32" font-weight="700" fill="#1f2937" {FONT}>근속 10년, 5년차에 퇴직금을 중간정산하면</text>',
         f'<text x="60" y="94" font-size="19" fill="#4b5563" {FONT}>30일분 평균임금 5년차 400만원 · 10년차 500만원 가정 · 2026년 10월 6일 근로자퇴직급여 보장법·소득세법 원문 기준</text>']
    labels = [("중간정산 없음", "10년 뒤 한 번에"), ("5년차 중간정산", "퇴직 때 따로 계산"), ("5년차 중간정산", "퇴직 때 합산 정산")]
    b_pay = sc["b1_pay"] + sc["b2_pay"]
    pays = [sc["a_pay"], b_pay, b_pay]
    taxes = [sc["a"]["합계"], sc["b1"]["합계"] + sc["b2"]["합계"], sc["b1"]["합계"] + sc["c2_tax"] + sc["c2_local"]]
    cols = ["#0f766e", "#94a3b8", "#2563eb"]
    panel(s, 60, 160, 560, 440, "받는 퇴직금 합계", [(labels[i], pays[i], cols[i]) for i in range(3)], 5_000 * calc.MAN,
          lambda v: f"{v // calc.MAN:,}만원")
    panel(s, 640, 160, 560, 440, "퇴직소득세 + 지방소득세", [(labels[i], taxes[i], cols[i]) for i in range(3)], 900_000,
          lambda v: f"{v:,}원")
    s.append(f'<text x="60" y="{H - 30}" font-size="17" fill="#6b7280" {FONT}>퇴직금 = 30일분 평균임금 × 근속연수(법 최저 기준) · 비과세 퇴직소득 없음 · 두 시점 모두 2026년 현행 세법 적용</text>')
    s.append('</svg>')
    open(os.path.join(OUT, "01_대표.svg"), "w", encoding="utf-8").write("\n".join(s))


if __name__ == "__main__":
    main()
