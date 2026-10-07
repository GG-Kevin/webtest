#!/usr/bin/env python3
"""그림 2장을 SVG로 그린다(표준 라이브러리만). 숫자는 calc.py 함수에서 가져온다."""
import os
import calc

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "그림")
os.makedirs(OUT, exist_ok=True)
FONT = "font-family=\"'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif\""


def text(x, y, s, size=24, fill="#16212e", weight="normal", anchor="start"):
    return f'<text x="{x}" y="{y}" {FONT} font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{s}</text>'


def fig1():
    W, H = 1200, 630
    b = []
    b.append(f'<rect width="{W}" height="{H}" fill="#f7f8f9"/>')
    b.append(text(60, 90, "전세보증보험(HUG 전세보증금반환보증) 가입 기한", 40, weight="bold"))
    b.append(text(60, 140, "잔금일과 전입신고일 중 늦은 날부터, 전세계약기간의 절반이 지나기 전까지", 26, fill="#3d4852"))
    x0, x1, y = 90, 1110, 330
    mid = (x0 + x1) // 2
    b.append(f'<rect x="{x0}" y="{y-28}" width="{mid-x0}" height="56" rx="6" fill="#0a6350"/>')
    b.append(f'<rect x="{mid}" y="{y-28}" width="{x1-mid}" height="56" rx="6" fill="#c9d1d9"/>')
    b.append(text((x0 + mid) // 2, y + 10, "신청할 수 있는 구간 (2년 계약이면 12개월)", 26, fill="#ffffff", weight="bold", anchor="middle"))
    b.append(text((mid + x1) // 2, y + 10, "기한이 지난 구간", 26, fill="#16212e", anchor="middle"))
    base, end = calc.deadline(calc.dt.date(2026, 11, 13), calc.dt.date(2026, 11, 16), 24)
    for x, lab, sub in [(x0, "잔금·전입 중 늦은 날", f"예: {base.year}.{base.month}.{base.day}"),
                        (mid, "계약기간 절반", f"이날이 되기 전까지: {end.year}.{end.month}.{end.day}"),
                        (x1, "계약 만료", "2년 뒤")]:
        b.append(f'<line x1="{x}" y1="{y-60}" x2="{x}" y2="{y+60}" stroke="#16212e" stroke-width="3"/>')
        anc = "start" if x == x0 else ("end" if x == x1 else "middle")
        b.append(text(x, y + 100, lab, 24, weight="bold", anchor=anc))
        b.append(text(x, y + 135, sub, 22, fill="#3d4852", anchor=anc))
    b.append(text(60, 560, "갱신 계약은 갱신 계약기간의 절반 전까지 · 1년 계약이면 6개월", 24, fill="#3d4852"))
    b.append(text(60, 598, "2026년 10월 5일 주택도시보증공사 상품 안내 기준", 20, fill="#6b7785"))
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">' + "".join(b) + "</svg>"
    open(os.path.join(OUT, "01_대표.svg"), "w", encoding="utf-8").write(svg)


def fig2():
    W, H = 1200, 560
    pub = 2 * calc.EOK
    price = int(pub * calc.PUBLIC_MULT)
    hv = int(calc.house_value(price))
    rows = [("공시가격", pub, "#9aa5b1"), ("주택가격 (공시가격 × 140%)", price, "#3d6f9e"),
            ("주택가액 = 보증금 + 선순위 최대 (× 90%)", hv, "#0a6350")]
    b = [f'<rect width="{W}" height="{H}" fill="#ffffff"/>']
    b.append(text(60, 80, "빌라 공시가격 2억원이면 전세보증금은 어디까지 되나", 36, weight="bold"))
    b.append(text(60, 122, "공시가격 × 140% × 90% = 공시가격의 126%", 26, fill="#3d4852"))
    scale = 760 / price
    for i, (lab, v, col) in enumerate(rows):
        y = 180 + i * 110
        b.append(text(60, y, lab, 24, weight="bold"))
        b.append(f'<rect x="60" y="{y+14}" width="{int(v*scale)}" height="46" rx="4" fill="{col}"/>')
        b.append(text(60 + int(v * scale) + 16, y + 48, calc.eok(v), 26, weight="bold"))
    b.append(text(60, 520, "선순위채권(근저당 등)이 있으면 그만큼 보증금 자리가 줄어든다 · 2026년 10월 5일 HUG 원문 기준", 21, fill="#6b7785"))
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">' + "".join(b) + "</svg>"
    open(os.path.join(OUT, "02_한도.svg"), "w", encoding="utf-8").write(svg)


if __name__ == "__main__":
    fig1()
    fig2()
    print("그림 2장:", sorted(os.listdir(OUT)))
