#!/usr/bin/env python3
"""그림 2장을 표준 라이브러리로 SVG로 그린다. 숫자는 calc.py 함수에서 가져온다."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calc  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "그림")
os.makedirs(OUT, exist_ok=True)
FONT = "font-family=\"'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif\""


def t(x, y, s, size=18, fill="#1f2937", anchor="start", weight="400"):
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}" {FONT}>{s}</text>')


def fig1():
    p = calc.DID_CAP_NEWLY
    nb = calc.BUY_RATES[calc.INCOME_BAND][3]
    gap = calc.rnd(calc.NEWLYWED_BUY_MIN - calc.BUY_MIN)
    a = calc.plan(p, nb, calc.rnd(nb + gap))
    did_base = calc.DID_RATES[calc.DID_BAND][3]
    b = calc.plan(p, calc.rnd(did_base - calc.DID_CHILD_PREF), did_base)
    W, H = 1200, 675
    left, right, top, bottom = 120, 60, 150, 110
    pw, ph = W - left - right, H - top - bottom
    ymax = 1_600_000
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         t(left, 58, "신생아 특례대출 3.2억원 30년, 달마다 내는 돈", 34, weight="700"),
         t(left, 98, "부부합산 연소득 6천만원 · 원리금균등 · 2026년 10월 5일 주택도시기금 금리표로 계산", 20, "#4b5563")]
    for v in range(0, ymax + 1, 400_000):
        y = top + ph - ph * v / ymax
        s.append(f'<line x1="{left}" y1="{y:.1f}" x2="{W - right}" y2="{y:.1f}" stroke="#e5e7eb"/>')
        s.append(t(left - 12, f"{y + 6:.1f}", f"{v // 10_000}만", 17, "#6b7280", "end"))
    groups = [("처음 5년", a["m1"], b["m1"]), ("6년차부터", a["m2"], b["m2"])]
    gw = pw / 2
    bw = 150
    for i, (lab, va, vb) in enumerate(groups):
        cx = left + gw * i + gw / 2
        for j, (v, col, name) in enumerate([(va, "#0a6350", "신생아 특례"), (vb, "#9aa5b1", "일반 디딤돌")]):
            x = cx - bw - 10 + j * (bw + 20)
            h = ph * v / ymax
            y = top + ph - h
            s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw}" height="{h:.1f}" fill="{col}" rx="4"/>')
            s.append(t(f"{x + bw / 2:.1f}", f"{y - 12:.1f}", f"{v:,}원", 22, "#111827", "middle", "700"))
            s.append(t(f"{x + bw / 2:.1f}", f"{top + ph + 30:.1f}", name, 18, "#374151", "middle"))
        s.append(t(f"{cx:.1f}", f"{top + ph + 66:.1f}", lab, 22, "#111827", "middle", "700"))
    s.append("</svg>")
    open(os.path.join(OUT, "01_대표.svg"), "w", encoding="utf-8").write("\n".join(s))


def fig2():
    W, H = 1200, 520
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         t(60, 56, "특례금리는 몇 년 가나 (구입자금)", 30, weight="700"),
         t(60, 92, "추가 출산 1명당 5년씩 늘고 최장 15년 · 그 뒤는 소득 구간별 종료 뒤 금리", 19, "#4b5563")]
    x0, x1 = 120, 1120
    unit = (x1 - x0) / 20
    rows = [("자녀 1명", 5), ("2년 내 추가 출산 1명", 10), ("추가 출산 2명", 15)]
    for i, (lab, yrs) in enumerate(rows):
        y = 150 + i * 95
        s.append(t(x0, y - 10, lab, 20, "#111827", weight="700"))
        s.append(f'<rect x="{x0}" y="{y}" width="{unit * yrs:.1f}" height="40" fill="#0a6350" rx="4"/>')
        s.append(t(f"{x0 + unit * yrs / 2:.1f}", y + 27, f"특례금리 {yrs}년", 19, "#ffffff", "middle", "700"))
        s.append(f'<rect x="{x0 + unit * yrs:.1f}" y="{y}" width="{unit * (20 - yrs):.1f}" height="40" fill="#e5e7eb" rx="4"/>')
        s.append(t(f"{x0 + unit * yrs + 14:.1f}", y + 27, "종료 뒤 금리", 18, "#374151"))
    for yr in range(0, 21, 5):
        x = x0 + unit * yr
        s.append(f'<line x1="{x:.1f}" y1="440" x2="{x:.1f}" y2="450" stroke="#6b7280"/>')
        s.append(t(f"{x:.1f}", 474, f"{yr}년", 17, "#6b7280", "middle"))
    s.append(t(x0, 505, "대출 실행일부터 센 햇수 · 2026년 10월 5일 신생아 특례 디딤돌대출 화면 기준", 16, "#6b7280"))
    s.append("</svg>")
    open(os.path.join(OUT, "02_기간.svg"), "w", encoding="utf-8").write("\n".join(s))


if __name__ == "__main__":
    fig1()
    fig2()
    print("그림 2장:", os.listdir(OUT))
