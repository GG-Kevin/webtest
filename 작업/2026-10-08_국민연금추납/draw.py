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


def fig1():
    W, H = 1200, 675
    left, right, top, bottom = 120, 60, 150, 110
    pw, ph = W - left - right, H - top - bottom
    months = (12, 36, 60, 119)
    inc = 1_000_000
    ymax = 14_000_000
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         t(left, 56, "국민연금 추납, 내는 돈과 늘어나는 월 연금", 32, weight="700"),
         t(left, 92, "기준소득월액 100만원 · 2026년 보험료율 9.5% · 늘어나는 연금은 2026년 A값과 B = 100만원 가정", 19, "#4b5563"),
         t(left, 120, "2026년 10월 5일 국민연금법 제51조·제92조, 국민연금공단 추납 안내 원문으로 계산", 17, "#6b7280")]
    for v in range(0, ymax + 1, 2_000_000):
        y = top + ph - ph * v / ymax
        s.append(f'<line x1="{left}" y1="{y:.1f}" x2="{W - right}" y2="{y:.1f}" stroke="#e5e7eb"/>')
        s.append(t(left - 12, y + 6, f"{v // 10_000:,}만", 16, "#6b7280", "end"))
    gw = pw / len(months)
    bw = gw * 0.46
    for i, m in enumerate(months):
        tot = calc.lump(inc, m, 2026)
        up = calc.pension_up_month(inc, m)
        x = left + gw * i + (gw - bw) / 2
        h = ph * tot / ymax
        y = top + ph - h
        s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{h:.1f}" fill="#0a6350" rx="4"/>')
        s.append(t(x + bw / 2, y - 40, f"추납 {calc.won(tot)}원", 19, "#16212e", "middle", "700"))
        s.append(t(x + bw / 2, y - 14, f"월 연금 +{calc.won(up)}원", 19, "#b45309", "middle", "700"))
        s.append(t(x + bw / 2, top + ph + 34, f"{m}개월", 21, "#1f2937", "middle", "700"))
    s.append(t(left, H - 30, "늘어나는 월 연금은 물가·재평가를 넣지 않은 단순 계산입니다. 본인 가입 이력에 따라 달라집니다.", 16, "#6b7280"))
    s.append("</svg>")
    with open(os.path.join(OUT, "01_대표.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(s))


def fig2():
    W, H = 1200, 520
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         t(60, 56, "일시납 추납은 신청한 다음 달 말일이 납부기한입니다", 30, weight="700"),
         t(60, 92, "보험료율은 납부기한이 든 달 기준 · 기준소득월액 100만원, 36개월 일시납 예시", 19, "#4b5563")]
    y0 = 250
    s.append(f'<line x1="80" y1="{y0}" x2="1120" y2="{y0}" stroke="#9aa5b1" stroke-width="3"/>')
    # 해 경계
    xb = 640
    s.append(f'<line x1="{xb}" y1="{y0 - 110}" x2="{xb}" y2="{y0 + 150}" stroke="#b45309" stroke-width="2" stroke-dasharray="8 6"/>')
    s.append(t(xb - 10, y0 - 118, "2026년", 18, "#b45309", "end", "700"))
    s.append(t(xb + 10, y0 - 118, "2027년", 18, "#b45309", "start", "700"))
    s.append(f'<rect x="80" y="{y0 + 70}" width="{xb - 80}" height="54" fill="#e8f4f0"/>')
    s.append(t((80 + xb) / 2, y0 + 104, "보험료율 9.5%", 21, "#0a6350", "middle", "700"))
    s.append(f'<rect x="{xb}" y="{y0 + 70}" width="{1120 - xb}" height="54" fill="#fdf1e3"/>')
    s.append(t((xb + 1120) / 2, y0 + 104, "보험료율 10.0%", 21, "#b45309", "middle", "700"))
    pts = [(180, "11월 신청"), (420, "12월 31일 납부기한"), (520, "12월 신청"), (860, "1월 31일 납부기한")]
    for x, lab in pts:
        s.append(f'<circle cx="{x}" cy="{y0}" r="9" fill="#16212e"/>')
    nov = calc.lump(1_000_000, 36, 2026)
    dec = calc.lump(1_000_000, 36, 2027)
    s.append(t(180, y0 - 24, "11월 신청", 19, "#16212e", "middle", "700"))
    s.append(t(420, y0 - 24, "12월 31일 기한", 19, "#16212e", "middle", "700"))
    s.append(t(300, y0 - 60, f"{calc.won(nov)}원", 22, "#0a6350", "middle", "700"))
    s.append(t(520, y0 + 40, "12월 신청", 19, "#16212e", "middle", "700"))
    s.append(t(860, y0 + 40, "1월 31일 기한", 19, "#16212e", "middle", "700"))
    s.append(t(760, y0 - 60, f"{calc.won(dec)}원", 22, "#b45309", "middle", "700"))
    s.append(t(60, H - 40, f"같은 36개월, 같은 기준소득월액이어도 차이 {calc.won(dec - nov)}원 · 분할 납부의 기준 달은 원문에서 확인되지 않았습니다.", 17, "#4b5563"))
    s.append("</svg>")
    with open(os.path.join(OUT, "02_납부기한.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(s))


if __name__ == "__main__":
    fig1()
    fig2()
