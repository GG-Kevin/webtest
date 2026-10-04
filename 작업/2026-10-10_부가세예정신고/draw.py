#!/usr/bin/env python3
"""그림 2장을 SVG로 그린다(표준 라이브러리만, 숫자는 calc.py에서). 실행: python3 draw.py"""
import os
import calc

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "그림")
os.makedirs(OUT, exist_ok=True)
FONT = "font-family=\"'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif\""
FOOT = "2026년 10월 4일 국세청·국가법령정보센터 원문 기준 · 머니프로듀서"


def svg(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{label}" {FONT}>\n<rect width="{w}" height="{h}" fill="#ffffff"/>\n{body}\n</svg>\n')


def fig1():
    W, H = 1200, 630
    raw, dl = calc.deadline()
    b = [f'<rect x="0" y="0" width="{W}" height="64" fill="#16212e"/>',
         '<text x="60" y="42" font-size="24" font-weight="700" fill="#ffffff">2026년 제2기 부가가치세 예정신고 · 7월 1일~9월 30일 실적</text>',
         f'<text x="60" y="124" font-size="40" font-weight="700" fill="#16212e">기한은 {raw.month}월 {raw.day}일(일)이 아니라 {dl.month}월 {dl.day}일(월)</text>']
    cols = [(60, "#0a6350", "#e8f3ef", "신고하는 쪽",
             ["법인사업자", "직전 6개월 공급가액 1억5천만원 이상", "10월 1일부터 신고서 제출·납부", "홈택스 전자신고 또는 세무서"]),
            (620, "#1f4e8c", "#e7eef8", "고지서를 받는 쪽",
             ["개인 일반과세자", "소규모 법인(1억5천만원 미만)", "직전 과세기간 납부세액의 50%", "50만원 미만이면 고지 없음"])]
    for x, c, bg, head, items in cols:
        b.append(f'<rect x="{x}" y="160" width="520" height="380" rx="14" fill="{bg}" stroke="{c}" stroke-width="3"/>')
        b.append(f'<rect x="{x}" y="160" width="520" height="66" rx="14" fill="{c}"/>')
        b.append(f'<rect x="{x}" y="200" width="520" height="26" fill="{c}"/>')
        b.append(f'<text x="{x + 260}" y="205" font-size="30" font-weight="700" fill="#ffffff" text-anchor="middle">{head}</text>')
        for i, it in enumerate(items):
            y = 290 + i * 64
            b.append(f'<circle cx="{x + 34}" cy="{y - 9}" r="7" fill="{c}"/>')
            b.append(f'<text x="{x + 54}" y="{y}" font-size="22" fill="#16212e">{it}</text>')
    b.append('<text x="60" y="580" font-size="19" fill="#5b6773">간이과세자는 1년 과세기간이라 10월 예정신고 대상이 아닙니다.</text>')
    b.append(f'<text x="{W - 60}" y="{H - 22}" font-size="16" text-anchor="end" fill="#8a96a3">{FOOT}</text>')
    return svg(W, H, "\n".join(b), "법인은 10월 26일까지 신고하고 개인 일반과세자는 고지서를 받는다는 두 칸 그림")


def fig2():
    W, H = 1000, 520
    cases = [800_000, 999_000, 1_000_000, 2_345_678, 6_000_000]
    left, base, top = 230, 440, 90
    maxv = 3_000_000
    scale = (W - left - 120) / maxv
    b = ['<text x="40" y="48" font-size="26" font-weight="700" fill="#16212e">1기 납부세액별 10월 고지세액(우리 계산)</text>',
         '<text x="40" y="78" font-size="17" fill="#5b6773">절반을 1천원 단위로 버린 뒤 50만원에 못 미치면 고지하지 않습니다</text>']
    x50 = left + 500_000 * scale
    b.append(f'<line x1="{x50:.0f}" y1="{top}" x2="{x50:.0f}" y2="{base}" stroke="#b3261e" stroke-width="2" stroke-dasharray="6 5"/>')
    b.append(f'<text x="{x50 + 6:.0f}" y="{top + 16}" font-size="16" fill="#b3261e">50만원 선</text>')
    for i, p in enumerate(cases):
        half, cut, col = calc.notice_tax(p)
        y = top + 30 + i * 64
        w = max(cut * scale, 2)
        color = "#1f4e8c" if col else "#b9c3cd"
        b.append(f'<text x="{left - 14}" y="{y + 26}" font-size="18" text-anchor="end" fill="#16212e">1기 납부 {calc.won(p)}원</text>')
        b.append(f'<rect x="{left}" y="{y}" width="{w:.0f}" height="38" rx="4" fill="{color}"/>')
        lab = f"{calc.won(col)}원 고지" if col else f"{calc.won(cut)}원, 고지 없음"
        b.append(f'<text x="{left + w + 10:.0f}" y="{y + 26}" font-size="18" fill="#16212e">{lab}</text>')
    b.append(f'<text x="{W - 30}" y="{H - 16}" font-size="14" text-anchor="end" fill="#8a96a3">{FOOT}</text>')
    return svg(W, H, "\n".join(b), "1기 납부세액 다섯 경우의 10월 예정고지세액과 50만원 선을 견준 막대 그림")


if __name__ == "__main__":
    for name, s in (("01_대표.svg", fig1()), ("02_고지세액.svg", fig2())):
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(s)
        print("그림:", name)
