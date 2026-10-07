#!/usr/bin/env python3
"""그림 2장을 SVG로 그린다(표준 라이브러리만, 날짜·숫자는 calc.py에서). 실행: python3 draw.py"""
import os
import calc

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "그림")
os.makedirs(OUT, exist_ok=True)
FONT = "font-family=\"'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif\""
FOOT = "2026년 10월 4일 국가법령정보센터·국세청 원문 기준 · 머니프로듀서"


def svg(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{label}" {FONT}>\n<rect width="{w}" height="{h}" fill="#ffffff"/>\n{body}\n</svg>\n')


def md(d):
    return f"{d.month}월 {d.day}일({calc.WD[d.weekday()]})"


def fig1():
    s = calc.schedule()
    W, H = 1200, 630
    b = [f'<rect x="0" y="0" width="{W}" height="64" fill="#16212e"/>',
         '<text x="60" y="42" font-size="24" font-weight="700" fill="#ffffff">2026년 종합부동산세 날짜판 · 종합부동산세법 제16조·제20조·제20조의2</text>',
         f'<text x="60" y="126" font-size="40" font-weight="700" fill="#16212e">납부기간 {md(s["start"])} ~ {md(s["end"])}</text>',
         f'<text x="60" y="172" font-size="24" fill="#3d4852">세액이 {calc.SPLIT_MIN // calc.MAN}만원을 넘으면 일부를 납부기한 뒤 {calc.SPLIT_MONTHS}개월 안에 나눠 낼 수 있습니다</text>']
    # 시간선
    y = 330
    b.append(f'<line x1="80" y1="{y}" x2="1120" y2="{y}" stroke="#c9d1d9" stroke-width="6"/>')
    b.append(f'<rect x="330" y="{y - 22}" width="420" height="44" rx="10" fill="#0a6350"/>')
    b.append(f'<text x="540" y="{y + 9}" font-size="22" font-weight="700" fill="#ffffff" text-anchor="middle">납부기간 15일</text>')
    pts = [(150, "#5b6b7a", md(s["notice"]), "고지서 발급 기한", f"개시 {calc.NOTICE_DAYS}일 전까지"),
           (330, "#0a6350", md(s["start"]), "납부 시작", "고지분·신고납부 같은 날"),
           (640, "#9a5b00", md(s["defer"]), "납부유예 신청", f"만료 {calc.DEFER_DAYS}일 전(12일 토요일)"),
           (750, "#0a6350", md(s["end"]), "납부 마감", "분납 신청서도 이날까지"),
           (1050, "#16212e", f"2027년 {md(s['split_end'])}", "분납분 납부", f"{calc.SPLIT_MONTHS}개월 이내")]
    for i, (x, c, d, t1, t2) in enumerate(pts):
        up = i % 2 == 0
        ty = y - 70 if up else y + 80
        b.append(f'<circle cx="{x}" cy="{y}" r="13" fill="{c}" stroke="#ffffff" stroke-width="4"/>')
        b.append(f'<line x1="{x}" y1="{y + (-14 if up else 14)}" x2="{x}" y2="{ty + (8 if up else -30)}" stroke="{c}" stroke-width="2"/>')
        b.append(f'<text x="{x}" y="{ty - (54 if up else 0)}" font-size="24" font-weight="700" fill="{c}" text-anchor="middle">{d}</text>')
        b.append(f'<text x="{x}" y="{ty - (24 if up else -30)}" font-size="21" fill="#16212e" text-anchor="middle">{t1}</text>')
        b.append(f'<text x="{x}" y="{ty + (2 if up else 58)}" font-size="17" fill="#5b6b7a" text-anchor="middle">{t2}</text>')
    b.append(f'<text x="{W - 60}" y="{H - 30}" font-size="16" text-anchor="end" fill="#8a96a3">{FOOT}</text>')
    return svg(W, H, "\n".join(b), "2026년 종합부동산세 고지서 발급부터 납부기간, 납부유예 신청, 분납 기한까지 날짜를 한 줄에 놓은 그림")


def fig2():
    W, H = 1200, 560
    rows = [calc.split_plan(v) for v in calc.BILLS]
    mx = max(r["dec_total"] + r["jun_total"] for r in rows)
    b = [f'<text x="60" y="58" font-size="30" font-weight="700" fill="#16212e">고지 종부세별로 12월과 이듬해 6월에 내는 돈(농특세 포함, 최대 분납 기준)</text>',
         '<rect x="60" y="82" width="22" height="22" fill="#0a6350"/><text x="92" y="100" font-size="19" fill="#16212e">12월(납부기간 안)</text>',
         '<rect x="290" y="82" width="22" height="22" fill="#d9a441"/><text x="322" y="100" font-size="19" fill="#16212e">이듬해 6월(분납분)</text>']
    x0, scale = 260, 700 / mx
    for i, r in enumerate(rows):
        y = 140 + i * 62
        w1 = r["dec_total"] * scale
        w2 = r["jun_total"] * scale
        b.append(f'<text x="{x0 - 16}" y="{y + 28}" font-size="20" fill="#16212e" text-anchor="end">고지 {r["bill"] // calc.MAN:,}만원</text>')
        b.append(f'<rect x="{x0}" y="{y}" width="{w1:.1f}" height="40" fill="#0a6350"/>')
        b.append(f'<text x="{x0 + 10}" y="{y + 27}" font-size="18" font-weight="700" fill="#ffffff">{r["dec_total"] // calc.MAN:,}만원</text>' if w1 > 90 else "")
        if w2 > 0:
            b.append(f'<rect x="{x0 + w1:.1f}" y="{y}" width="{w2:.1f}" height="40" fill="#d9a441"/>')
            b.append(f'<text x="{x0 + w1 + w2 + 10:.1f}" y="{y + 27}" font-size="18" fill="#16212e">6월 {r["jun_total"]:,}원</text>')
        else:
            b.append(f'<text x="{x0 + w1 + 10:.1f}" y="{y + 27}" font-size="18" fill="#5b6b7a">250만원 이하라 분납 없음</text>')
    b.append(f'<text x="{W - 60}" y="{H - 24}" font-size="16" text-anchor="end" fill="#8a96a3">{FOOT}</text>')
    return svg(W, H, "\n".join(b), "고지 세액별로 12월에 내는 금액과 이듬해 6월로 미룰 수 있는 금액을 나눈 막대그림")


if __name__ == "__main__":
    open(os.path.join(OUT, "01_대표.svg"), "w", encoding="utf-8").write(fig1())
    open(os.path.join(OUT, "02_분납.svg"), "w", encoding="utf-8").write(fig2())
    print("그림 2장")
