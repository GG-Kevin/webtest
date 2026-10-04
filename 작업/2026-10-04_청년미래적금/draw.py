#!/usr/bin/env python3
"""그림 2장을 SVG로 그린다(표준 라이브러리만, 숫자는 calc.py에서 가져온다). 실행: python3 draw.py"""
import os
import calc

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "그림")
os.makedirs(OUT, exist_ok=True)
FONT = "font-family=\"'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif\""
FOOT = "2026년 10월 4일 금융위원회 보도자료(2026.9.16·9.30) 원문 기준 · 머니프로듀서"


def svg(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{label}" {FONT}>\n<rect width="{w}" height="{h}" fill="#ffffff"/>\n{body}\n</svg>\n')


def man(x):
    v = x / 10000
    return f"{v:,.0f}만원" if v == int(v) else f"{v:,.2f}만원".replace(".00", "")


def fig1():
    W, H = 1200, 675
    m = calc.MAX_M
    P = calc.principal(m)
    I = calc.interest(m, calc.BASE_R)
    kinds = [("기여금 미대상", calc.RATE["미대상"], "#9aa5b1"),
             ("일반형 6%", calc.RATE["일반형"], "#2f6fb0"),
             ("우대형 12%", calc.RATE["우대형"], "#0a6350")]
    b = [f'<text x="60" y="72" font-size="38" font-weight="700" fill="#16212e">청년미래적금 월 50만원 3년, 원금 위에 얹히는 돈</text>',
         f'<text x="60" y="114" font-size="23" fill="#3d4852">원금 {man(P)}(월 50만원 × 36개월) · 원금 이자는 기본금리 5% 가정, 비과세</text>']
    # 원금 상자
    b.append('<rect x="60" y="160" width="300" height="330" rx="8" fill="#e9edf1"/>')
    b.append('<text x="210" y="300" font-size="30" font-weight="700" fill="#16212e" text-anchor="middle">원금</text>')
    b.append(f'<text x="210" y="350" font-size="34" font-weight="700" fill="#16212e" text-anchor="middle">{man(P)}</text>')
    b.append('<text x="210" y="395" font-size="21" fill="#3d4852" text-anchor="middle">모든 유형 같음</text>')
    b.append('<text x="395" y="335" font-size="44" font-weight="700" fill="#3d4852" text-anchor="middle">+</text>')
    base, top = 490, 175
    vmax = 3_600_000
    bw, gap, x0 = 170, 70, 450
    for k, (name, rate, col) in enumerate(kinds):
        g = calc.contrib(m, rate)
        x = x0 + k * (bw + gap)
        hi = I / vmax * (base - top)
        hg = g / vmax * (base - top)
        b.append(f'<rect x="{x}" y="{base - hi:.1f}" width="{bw}" height="{hi:.1f}" fill="#c3cbd3"/>')
        b.append(f'<text x="{x + bw / 2}" y="{base - hi / 2 + 8:.1f}" font-size="20" fill="#16212e" text-anchor="middle">이자 {man(I)}</text>')
        if g:
            b.append(f'<rect x="{x}" y="{base - hi - hg:.1f}" width="{bw}" height="{hg:.1f}" fill="{col}"/>')
            b.append(f'<text x="{x + bw / 2}" y="{base - hi - hg / 2 + 9:.1f}" font-size="20" font-weight="700" fill="#ffffff" text-anchor="middle">기여금 {man(g)}</text>')
        b.append(f'<text x="{x + bw / 2}" y="{base - hi - hg - 14:.1f}" font-size="22" font-weight="700" fill="#16212e" text-anchor="middle">합 {man(g + I)}</text>')
        b.append(f'<text x="{x + bw / 2}" y="{base + 34}" font-size="23" font-weight="700" fill="{col}" text-anchor="middle">{name}</text>')
    b.append(f'<line x1="440" y1="{base}" x2="1150" y2="{base}" stroke="#16212e" stroke-width="2"/>')
    b.append('<rect x="0" y="560" width="1200" height="78" fill="#16212e"/>')
    b.append('<text x="600" y="610" font-size="28" font-weight="700" fill="#ffffff" text-anchor="middle">2차 신청 10월 7일~16일 · 계좌개설 11월 16일~27일</text>')
    b.append(f'<text x="60" y="662" font-size="17" fill="#5b6670">{FOOT}</text>')
    label = "청년미래적금 월 50만원 3년 납입 시 원금 1,800만원 위에 유형별로 얹히는 이자와 정부 기여금을 비교한 그림"
    open(os.path.join(OUT, "01_대표.svg"), "w", encoding="utf-8").write(svg(W, H, "\n".join(b), label))


def fig2():
    W, H = 1200, 520
    L, R = 80, 1140
    # 10/7 = 0일 … 11/27 = 51일
    d = lambda mo, dy: (dy - 7) if mo == 10 else (24 + dy)
    X = lambda v: L + v / 52 * (R - L)
    rows = [("가입신청", d(10, 7), d(10, 16), "#2f6fb0", "10.7~10.16"),
            ("심사", d(10, 19), d(11, 13), "#9aa5b1", "10.19~11.13"),
            ("사전심사 안내(잠정)", d(10, 30), d(11, 2), "#e0a526", "10.30~11.2"),
            ("이의신청(잠정)", d(11, 2), d(11, 5), "#c0392b", "11.2~11.5"),
            ("최종 결과", d(11, 12), d(11, 13), "#16212e", "11.12~11.13"),
            ("계좌개설", d(11, 16), d(11, 27), "#0a6350", "11.16~11.27")]
    b = ['<text x="80" y="62" font-size="34" font-weight="700" fill="#16212e">청년미래적금 2차, 신청에서 계좌개설까지 52일</text>',
         '<text x="80" y="100" font-size="21" fill="#3d4852">10월 7일 홀수·8일 짝수(출생연도 끝자리), 12일부터 누구나 · 토·일·공휴일 제외</text>']
    for i, (name, a, z, col, lab) in enumerate(rows):
        y = 140 + i * 52
        b.append(f'<rect x="{X(a):.1f}" y="{y}" width="{max(X(z + 1) - X(a), 8):.1f}" height="34" rx="4" fill="{col}"/>')
        if a > 8:
            b.append(f'<text x="{X(a) - 12:.1f}" y="{y + 24}" font-size="20" fill="#16212e" text-anchor="end">{name} <tspan font-size="17" fill="#5b6670">{lab}</tspan></text>')
        else:
            b.append(f'<text x="{X(z + 1) + 12:.1f}" y="{y + 24}" font-size="20" fill="#16212e">{name} <tspan font-size="17" fill="#5b6670">{lab}</tspan></text>')
    for v, t in ((0, "10월 7일"), (d(11, 1), "11월 1일"), (d(11, 27) + 1, "11월 27일")):
        b.append(f'<line x1="{X(v):.1f}" y1="130" x2="{X(v):.1f}" y2="455" stroke="#c3cbd3" stroke-dasharray="4 4"/>')
        b.append(f'<text x="{X(v):.1f}" y="478" font-size="18" fill="#3d4852" text-anchor="middle">{t}</text>')
    b.append(f'<text x="80" y="508" font-size="16" fill="#5b6670">{FOOT}</text>')
    label = "청년미래적금 2차 가입신청, 심사, 사전심사 안내, 이의신청, 최종 결과, 계좌개설 기간을 날짜 축에 나란히 놓은 일정 그림"
    open(os.path.join(OUT, "02_일정.svg"), "w", encoding="utf-8").write(svg(W, H, "\n".join(b), label))


if __name__ == "__main__":
    fig1()
    fig2()
    print("그림 2장:", sorted(os.listdir(OUT)))
