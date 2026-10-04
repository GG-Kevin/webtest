#!/usr/bin/env python3
"""대표 그림 1장을 SVG로 그린다(표준 라이브러리만, 숫자는 calc.py에서). 실행: python3 draw.py"""
import os
import calc

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "그림")
os.makedirs(OUT, exist_ok=True)
FONT = "font-family=\"'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif\""
FOOT = "2026년 10월 5일 주택도시기금 상품안내 금리로 계산 · 원리금균등·비거치 · 머니프로듀서"
ALT = "디딤돌대출 2억원을 10년부터 30년까지 원리금균등으로 갚을 때 한 달 상환액과 총이자를 기간별로 나란히 놓은 막대그림"


def fig1():
    W, H = 1200, 630
    rows = [(name, rate, calc.plan(p, rate, y)) for name, p, rate, y in calc.PAY_CASES]
    b = [f'<rect x="0" y="0" width="{W}" height="64" fill="#16212e"/>',
         '<text x="60" y="42" font-size="24" font-weight="700" fill="#ffffff">디딤돌대출 2억원, 기간별로 한 달에 갚는 돈과 총이자</text>',
         '<text x="60" y="108" font-size="20" fill="#3d4852">부부합산 연소득 4천만원 초과 7천만원 이하 금리 · 우대·지방 인하·금리 방식 가산 전</text>',
         '<rect x="60" y="128" width="22" height="22" fill="#0a6350"/><text x="92" y="146" font-size="19" fill="#16212e">월 상환액</text>',
         '<rect x="250" y="128" width="22" height="22" fill="#d9a441"/><text x="282" y="146" font-size="19" fill="#16212e">총이자</text>']
    mx_m = max(r["m"] for _, _, r in rows)
    mx_i = max(r["interest"] for _, _, r in rows)
    x0, wmax = 300, 520
    for i, (name, rate, r) in enumerate(rows):
        y = 190 + i * 98
        b.append(f'<text x="60" y="{y + 30}" font-size="26" font-weight="700" fill="#16212e">{name}</text>')
        b.append(f'<text x="60" y="{y + 60}" font-size="19" fill="#5b6b7a">연 {rate}%</text>')
        w1 = r["m"] / mx_m * wmax
        w2 = r["interest"] / mx_i * wmax
        b.append(f'<rect x="{x0}" y="{y + 4}" width="{w1:.0f}" height="32" rx="4" fill="#0a6350"/>')
        b.append(f'<text x="{x0 + w1 + 12:.0f}" y="{y + 28}" font-size="21" font-weight="700" fill="#0a6350">월 {r["m"]:,}원</text>')
        b.append(f'<rect x="{x0}" y="{y + 42}" width="{w2:.0f}" height="26" rx="4" fill="#d9a441"/>')
        b.append(f'<text x="{x0 + w2 + 12:.0f}" y="{y + 62}" font-size="19" fill="#7a5200">총이자 {r["interest"]:,}원</text>')
    b.append(f'<text x="{W - 40}" y="{H - 20}" font-size="15" text-anchor="end" fill="#8a96a3">{FOOT}</text>')
    body = "\n".join(b)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'role="img" aria-label="{ALT}" {FONT}>\n<rect width="{W}" height="{H}" fill="#ffffff"/>\n{body}\n</svg>\n')


if __name__ == "__main__":
    open(os.path.join(OUT, "01_대표.svg"), "w", encoding="utf-8").write(fig1())
    print("그림/01_대표.svg")
