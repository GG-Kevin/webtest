#!/usr/bin/env python3
"""그림 2장(SVG, 표준 라이브러리). 숫자는 ../calc.py 함수에서 가져온다."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import calc as C  # noqa: E402

FONT = "font-family=\"'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif\""


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fig1():
    E = C.EOK
    items = [("1주택자(수도권·규제지역)", C.hug(4 * E, "metro", one_house=True), "#9aa5b1"),
             ("신혼부부 버팀목", C.bt_newly(4 * E, "metro"), "#5b6b7a"),
             ("HUG 안심대출(일반)", C.hug(4 * E, "metro"), "#0a6350"),
             ("HUG 안심대출(신혼·청년)", C.hug(4 * E, "metro", yn=True), "#0a6350")]
    alt = "수도권 전세보증금 4억원일 때 1주택자 2억원, 신혼부부 버팀목 2억 5,000만원, HUG 일반 3억 2,000만원, HUG 신혼·청년 3억 6,000만원으로 계산한 전세대출 한도 막대그림"
    W, H = 1200, 630
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(alt)}" {FONT}>',
           f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
           '<rect x="0" y="0" width="1200" height="64" fill="#16212e"/>',
           '<text x="60" y="42" font-size="24" font-weight="700" fill="#ffffff">전세대출 한도 · 수도권 전세보증금 4억원 기준 직접 계산</text>',
           '<text x="60" y="118" font-size="36" font-weight="700" fill="#16212e">같은 4억 전세라도 상품마다 2억~3억 6,000만원까지</text>',
           '<text x="60" y="160" font-size="22" fill="#3d4852">무주택·심사 통과 가정 · 2026년 10월 5일 주택도시기금·HF·HUG·금융위원회 원문 기준</text>']
    x0, bw, y, bh, gap = 400, 640, 215, 60, 32
    maxv = 4 * E
    # 보증금 4억 기준선
    out.append(f'<line x1="{x0 + bw}" y1="{y - 12}" x2="{x0 + bw}" y2="{y + 4 * (bh + gap)}" stroke="#c0392b" stroke-width="2" stroke-dasharray="6 6"/>')
    out.append(f'<text x="{x0 + bw}" y="{y - 20}" font-size="18" fill="#c0392b" text-anchor="middle">보증금 4억원</text>')
    for name, v, col in items:
        w = int(bw * v / maxv)
        out.append(f'<text x="{x0 - 16}" y="{y + 38}" font-size="22" fill="#16212e" text-anchor="end">{esc(name)}</text>')
        out.append(f'<rect x="{x0}" y="{y}" width="{w}" height="{bh}" rx="6" fill="{col}"/>')
        out.append(f'<text x="{x0 + w - 12}" y="{y + 38}" font-size="22" font-weight="700" fill="#ffffff" text-anchor="end">{esc(C.won(v))}</text>')
        y += bh + gap
    out.append('<text x="60" y="612" font-size="18" fill="#5b6b7a">한도 = 상품 상한과 보증금 × 비율 중 작은 값 · 1주택자는 보증기관과 관계없이 2억원 · HF는 원문 기준 확인 뒤 별도</text>')
    out.append('</svg>')
    open(os.path.join(HERE, "01_대표.svg"), "w", encoding="utf-8").write("\n".join(out) + "\n")


def fig2():
    loans = [12_000 * C.MAN, 15_000 * C.MAN, 2 * C.EOK, 25_000 * C.MAN, 32_000 * C.MAN]
    alt = "대출금 1억 2,000만원부터 3억 2,000만원까지 연 2.5%와 연 4.0%일 때 한 달 이자를 나란히 놓은 막대그림"
    W, H = 1200, 560
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(alt)}" {FONT}>',
           f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
           '<text x="60" y="56" font-size="30" font-weight="700" fill="#16212e">대출금별 한 달 이자(만기 일시상환, 원 미만 버림)</text>',
           '<rect x="760" y="80" width="22" height="22" fill="#9aa5b1"/><text x="790" y="98" font-size="20" fill="#16212e">연 2.5%(버팀목 금리 범위 하단)</text>',
           '<rect x="760" y="112" width="22" height="22" fill="#0a6350"/><text x="790" y="130" font-size="20" fill="#16212e">연 4.0%(가정)</text>']
    base, top, x = 470, 170, 110
    maxv = 1_100_000
    for L in loans:
        for i, (r, col) in enumerate(((2.5, "#9aa5b1"), (4.0, "#0a6350"))):
            v = C.monthly_interest(L, r)
            h = int((base - top) * v / maxv)
            bx = x + i * 80
            out.append(f'<rect x="{bx}" y="{base - h}" width="70" height="{h}" fill="{col}"/>')
            out.append(f'<text x="{bx + 35}" y="{base - h - 8}" font-size="16" fill="#16212e" text-anchor="middle">{v // 10000}만 {v % 10000:,}</text>' if v % 10000 else f'<text x="{bx + 35}" y="{base - h - 8}" font-size="16" fill="#16212e" text-anchor="middle">{v // 10000}만</text>')
        out.append(f'<text x="{x + 75}" y="{base + 34}" font-size="20" font-weight="700" fill="#16212e" text-anchor="middle">{esc(C.won(L))}</text>')
        x += 210
    out.append(f'<line x1="90" y1="{base}" x2="1150" y2="{base}" stroke="#16212e" stroke-width="2"/>')
    out.append('<text x="60" y="540" font-size="18" fill="#5b6b7a">단위: 원(막대 위 숫자는 「만」 단위로 줄여 적음) · 2026년 10월 5일 원문 기준 직접 계산</text>')
    out.append('</svg>')
    open(os.path.join(HERE, "02_월이자.svg"), "w", encoding="utf-8").write("\n".join(out) + "\n")


if __name__ == "__main__":
    fig1()
    fig2()
