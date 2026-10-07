#!/usr/bin/env python3
"""그림 2장을 SVG로 그린다(표준 라이브러리만, 날짜·숫자는 calc.py에서). 실행: python3 draw.py"""
import os
import calc

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "그림")
os.makedirs(OUT, exist_ok=True)
FONT = "font-family=\"'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif\""
FOOT = "2026년 10월 4일 한국은행 통화정책방향 결정회의 일정·기준금리 원문 기준 · 머니프로듀서"


def svg(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{label}" {FONT}>\n<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
            + "\n".join(body) + "\n</svg>\n")


def xpos(d, x0=80, x1=1120):
    doy = d.timetuple().tm_yday
    return x0 + (x1 - x0) * (doy - 1) / 364


def fig1():
    W, H = 1200, 630
    b = [f'<rect x="0" y="0" width="{W}" height="64" fill="#13294b"/>',
         '<text x="60" y="42" font-size="24" font-weight="700" fill="#ffffff">금통위 일정 2026 · 기준금리 결정회의 8번</text>',
         f'<text x="60" y="128" font-size="40" font-weight="700" fill="#13294b">끝난 회의 {calc.N_DONE}번, 남은 회의 {calc.N_LEFT}번</text>',
         f'<text x="60" y="176" font-size="26" fill="#3b4a5c">지금 기준금리 연 {calc.CUR_RATE:.2f}% · 다음 결정 {calc.fmt(calc.LEFT[0])}</text>']
    y = 350
    b.append(f'<line x1="80" y1="{y}" x2="1120" y2="{y}" stroke="#c4ccd6" stroke-width="6" stroke-linecap="round"/>')
    for m in range(1, 13):
        import datetime as dt
        x = xpos(dt.date(2026, m, 1))
        b.append(f'<line x1="{x:.0f}" y1="{y - 12}" x2="{x:.0f}" y2="{y + 12}" stroke="#c4ccd6" stroke-width="2"/>')
        b.append(f'<text x="{x + 6:.0f}" y="{y + 44}" font-size="18" fill="#7a8796">{m}월</text>')
    tx = xpos(calc.BASE_DATE)
    b.append(f'<line x1="{tx:.0f}" y1="{y - 70}" x2="{tx:.0f}" y2="{y + 70}" stroke="#d1495b" stroke-width="3" stroke-dasharray="6 5"/>')
    b.append(f'<text x="{tx - 44:.0f}" y="{y + 96}" font-size="18" fill="#d1495b">10월 4일</text>')
    for i, d in enumerate(calc.MEETINGS):
        x = xpos(d)
        done = d < calc.BASE_DATE
        fill = "#13294b" if done else "#ffffff"
        stroke = "#13294b" if done else "#d1495b"
        b.append(f'<circle cx="{x:.0f}" cy="{y}" r="15" fill="{fill}" stroke="{stroke}" stroke-width="5"/>')
        up = i % 2 == 0
        ly = y - 40 if up else y - 70
        label = f"{d.month}/{d.day}"
        b.append(f'<text x="{x:.0f}" y="{ly}" font-size="20" font-weight="700" text-anchor="middle" fill="{stroke}">{label}</text>')
        if done:
            r = calc.rate_after(d)
            b.append(f'<text x="{x:.0f}" y="{y + 140 + (0 if up else 28)}" font-size="18" text-anchor="middle" fill="#3b4a5c">{r:.2f}%</text>')
    b.append(f'<text x="80" y="{y + 210}" font-size="18" fill="#3b4a5c">아래 숫자 = 그 회의 뒤 기준금리(연) · 속이 빈 점 = 남은 회의 · 12월 회의 없음</text>')
    b.append(f'<text x="60" y="{H - 24}" font-size="16" fill="#7a8796">{FOOT}</text>')
    lab = "2026년 금통위 기준금리 결정회의 8번을 달력 선 위에 찍은 그림, 남은 회의는 10월 22일과 11월 26일"
    open(os.path.join(OUT, "01_대표.svg"), "w", encoding="utf-8").write(svg(W, H, b, lab))


def fig2():
    W, H = 1200, 520
    b = [f'<text x="60" y="60" font-size="30" font-weight="700" fill="#13294b">회의 하나에 따라오는 공개 날짜</text>',
         '<text x="60" y="98" font-size="20" fill="#3b4a5c">한국은행 게시 규칙(이슈분석 D+7 · 의사록 2주 경과 후 첫 화요일)으로 계산</text>']
    rows = calc.LEFT
    y = 170
    for d in rows:
        a, m = calc.issue_day(d), calc.minutes_day(d)
        x0, x1 = 150, 1100
        span = (m - d).days
        def px(t):
            return x0 + (x1 - x0) * (t - d).days / span
        b.append(f'<text x="60" y="{y + 8}" font-size="22" font-weight="700" fill="#13294b">{d.month}월</text>')
        b.append(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="#c4ccd6" stroke-width="8" stroke-linecap="round"/>')
        for t, name, c in [(d, "결정회의", "#13294b"), (a, "이슈분석", "#2a7f62"), (m, "의사록", "#d1495b")]:
            x = px(t)
            b.append(f'<circle cx="{x:.0f}" cy="{y}" r="14" fill="{c}"/>')
            b.append(f'<text x="{x:.0f}" y="{y - 26}" font-size="20" font-weight="700" text-anchor="middle" fill="{c}">{name}</text>')
            b.append(f'<text x="{x:.0f}" y="{y + 44}" font-size="20" text-anchor="middle" fill="#3b4a5c">{calc.fmt(t)}</text>')
        b.append(f'<text x="{x1:.0f}" y="{y + 74}" font-size="17" text-anchor="end" fill="#7a8796">회의 뒤 {span}일</text>')
        y += 170
    b.append(f'<text x="60" y="{H - 20}" font-size="16" fill="#7a8796">{FOOT}</text>')
    lab = "10월과 11월 금통위 회의일, 이슈분석 게시일, 의사록 게시일을 한 줄씩 이은 그림"
    open(os.path.join(OUT, "02_공개일.svg"), "w", encoding="utf-8").write(svg(W, H, b, lab))


if __name__ == "__main__":
    fig1()
    fig2()
    print("그림 2장:", sorted(os.listdir(OUT)))
