#!/usr/bin/env python3
"""그림 2장을 SVG로 그린다(표준 라이브러리만, 숫자는 calc.py에서). 실행: python3 draw.py"""
import os
import calc

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "그림")
os.makedirs(OUT, exist_ok=True)
FONT = "font-family=\"'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif\""
FOOT = "2026년 10월 4일 소득세법·국세청 원문 기준 · 머니프로듀서"
NAVY, GREEN, AMBER, GRAY = "#16212e", "#0a6350", "#9a5b00", "#6b7682"


def svg(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{label}" {FONT}>\n<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
            + "\n".join(body) + "\n</svg>\n")


def fig1():
    W, H = 1200, 630
    b = [f'<rect x="0" y="0" width="{W}" height="64" fill="{NAVY}"/>',
         '<text x="60" y="42" font-size="24" font-weight="700" fill="#ffffff">종합소득세 중간예납 · 2026년 일정</text>',
         f'<text x="60" y="128" font-size="36" font-weight="800" fill="{NAVY}">납부기한 11월 30일(월), 분납은 2월 1일(월)까지</text>',
         f'<text x="60" y="176" font-size="24" fill="{GRAY}">고지액 = 2025년 귀속 소득세의 절반 · 50만원 미만이면 고지하지 않음</text>',
         f'<line x1="90" y1="330" x2="1110" y2="330" stroke="{NAVY}" stroke-width="4"/>']
    pts = [(150, "11월 1일~15일", "고지서 발급", GREEN),
           (420, "11월 30일(월)", "납부·추계액 신고 마감", NAVY),
           (690, "2027년 1월 1일~15일", "못 낸 분납 가능액 다시 고지", AMBER),
           (990, "2027년 2월 1일(월)", "분납 기한", GREEN)]
    for x, d, what, c in pts:
        b.append(f'<circle cx="{x}" cy="330" r="16" fill="{c}"/>')
        b.append(f'<text x="{x}" y="285" font-size="26" font-weight="700" fill="{c}" text-anchor="middle">{d}</text>')
        b.append(f'<text x="{x}" y="388" font-size="22" fill="{NAVY}" text-anchor="middle">{what}</text>')
    t = calc.mid_tax(30_000_000)
    i = calc.installment(t)
    b.append(f'<rect x="90" y="440" width="1020" height="110" rx="12" fill="#f7f8f9" stroke="#e6e8ea"/>')
    b.append(f'<text x="120" y="485" font-size="24" fill="{NAVY}">예: 2025년 귀속 세액 3,000만원 → 고지 {t:,}원</text>')
    b.append(f'<text x="120" y="525" font-size="24" fill="{NAVY}">11월 30일까지 {t - i:,}원 · 2월 1일까지 {i:,}원(1천만원 넘는 몫)</text>')
    b.append(f'<text x="60" y="600" font-size="18" fill="{GRAY}">{FOOT}</text>')
    open(os.path.join(OUT, "01_대표.svg"), "w", encoding="utf-8").write(
        svg(W, H, b, "중간예납 고지서 발급부터 분납 기한까지 네 날짜를 이은 일정 그림"))


def fig2():
    W, H = 1200, 640
    base = calc.EST_BASE
    notice = calc.mid_tax(base)
    line = base * calc.EST_RATIO // 100
    rows = [(f"상반기 {h // 10000:,}만원", calc.estimate(h, calc.EST_DEDUCT)[2]) for h in calc.EST_HALF_INCOMES]
    rows = [("고지액", notice)] + rows
    top, left, bw, gap, ch = 150, 140, 150, 50, 380
    scale = ch / notice
    b = [f'<text x="60" y="60" font-size="30" font-weight="800" fill="{NAVY}">기준액 1,000만원일 때 상반기 소득별 추계액</text>',
         f'<text x="60" y="100" font-size="22" fill="{GRAY}">종합소득공제 300만원·공제감면·원천징수 0원 가정 · 점선 = 기준액의 30%({line:,}원)</text>']
    for k, (lab, v) in enumerate(rows):
        x = left + k * (bw + gap)
        hgt = v * scale
        c = NAVY if k == 0 else (GREEN if v < line else AMBER)
        b.append(f'<rect x="{x}" y="{top + ch - hgt:.0f}" width="{bw}" height="{hgt:.0f}" fill="{c}"/>')
        b.append(f'<text x="{x + bw / 2}" y="{top + ch - hgt - 12:.0f}" font-size="22" font-weight="700" fill="{c}" text-anchor="middle">{v:,}원</text>')
        b.append(f'<text x="{x + bw / 2}" y="{top + ch + 34}" font-size="22" fill="{NAVY}" text-anchor="middle">{lab}</text>')
    ly = top + ch - line * scale
    b.append(f'<line x1="110" y1="{ly:.0f}" x2="1130" y2="{ly:.0f}" stroke="#c0392b" stroke-width="3" stroke-dasharray="10 8"/>')
    b.append(f'<line x1="110" y1="{top + ch}" x2="1130" y2="{top + ch}" stroke="{NAVY}" stroke-width="2"/>')
    b.append(f'<text x="60" y="615" font-size="18" fill="{GRAY}">{FOOT} · 계산: 머니프로듀서</text>')
    open(os.path.join(OUT, "02_추계.svg"), "w", encoding="utf-8").write(
        svg(W, H, b, "고지액 500만원과 상반기 소득별 추계액을 30% 선과 견준 막대 그림"))


if __name__ == "__main__":
    fig1()
    fig2()
    print("그림 2장:", sorted(os.listdir(OUT)))
