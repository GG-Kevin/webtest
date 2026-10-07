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
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="{anchor}" fill="{fill}" {FONT}>{s}</text>')


def bars(fname, title, sub, note, items, ymax, colors):
    W, H = 1200, 675
    left, right, top, bottom = 130, 60, 160, 120
    pw, ph = W - left - right, H - top - bottom
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         t(left, 58, title, 28, weight="700"),
         t(left, 96, sub, 19, "#4b5563"),
         t(left, 126, "2026년 10월 6일 국민연금법 제51조·제63조, 국민연금공단 예상연금 산식 원문으로 계산", 17, "#6b7280")]
    for v in range(0, ymax + 1, 200_000):
        y = top + ph - ph * v / ymax
        s.append(f'<line x1="{left}" y1="{y:.1f}" x2="{W - right}" y2="{y:.1f}" stroke="#e5e7eb"/>')
        s.append(t(left - 12, y + 6, f"{v // 10_000:,}만원", 16, "#6b7280", "end"))
    gw = pw / len(items)
    bw = gw * 0.42
    for i, (label, val) in enumerate(items):
        x = left + gw * i + (gw - bw) / 2
        h = ph * val / ymax
        y = top + ph - h
        s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{h:.1f}" fill="{colors[i]}" rx="4"/>')
        s.append(t(x + bw / 2, y - 14, f"월 {calc.won(val)}원", 22, "#16212e", "middle", "700"))
        s.append(t(x + bw / 2, top + ph + 34, label, 20, "#1f2937", "middle", "700"))
    s.append(t(left, H - 34, note, 16, "#6b7280"))
    s.append("</svg>")
    with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
        f.write("\n".join(s))


def main():
    items = [(name.replace("1월~", "~").replace("12월", ""), calc.monthly(calc.B_EX, mby)) for name, mby in calc.CASES]
    bars("01_대표.svg", "국민연금 조회 예상액, 같은 20년이라도 가입 시기에 따라 다릅니다",
         "B값 300만원 · 가입 20년 · 2026년 A값 3,193,511원 · 연도별 비율만 바꾼 직접 계산",
         "B값은 가입 내내 같다고 가정했고 물가·재평가율 변동과 부양가족연금액은 넣지 않았습니다.",
         items, 1_000_000, ["#9aa5b1", "#5b7c99", "#0a6350"])
    bars("02_계속납부.svg", "60세 전 5년을 더 내면 월 노령연금이 이렇게 바뀝니다",
         "2007년 1월 첫 가입 · B값 300만원 · 20년에서 멈춤과 25년까지 계속을 나란히 계산",
         "더 내는 5년 보험료는 해마다 오르는 요율(2027년 10%~2031년 12%)로 계산했습니다.",
         [("20년(2026년까지)", calc.monthly(calc.B_EX, calc.STOP)),
          ("25년(2031년까지)", calc.monthly(calc.B_EX, calc.CONT))], 1_000_000, ["#9aa5b1", "#0a6350"])


if __name__ == "__main__":
    main()
