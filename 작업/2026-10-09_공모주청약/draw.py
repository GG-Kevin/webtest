#!/usr/bin/env python3
"""그림 01 — 2026년 10월 날짜별 공모주 청약 곳 수 달력(SVG, 표준 라이브러리만). calc.py의 IPO 표를 읽는다."""
import datetime as dt
import os
import runpy

HERE = os.path.dirname(os.path.abspath(__file__))
C = runpy.run_path(os.path.join(HERE, "calc.py"), run_name="calc")
IPO, HOL, Y = C["IPO"], C["HOLIDAYS"], C["Y"]

W, H = 1200, 860
X0, Y0, CW, CH = 40, 170, 160, 128
HOLNAME = {dt.date(Y, 10, 3): "개천절", dt.date(Y, 10, 5): "대체공휴일", dt.date(Y, 10, 9): "한글날"}


def count(day):
    return sum(1 for r in IPO if dt.date(Y, *r[3]) <= day <= dt.date(Y, *r[4]))


def refunds(day):
    return sum(1 for r in IPO if dt.date(Y, *r[5]) == day)


out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Noto Sans KR, Malgun Gothic, sans-serif">',
       f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
       '<text x="40" y="62" font-size="34" font-weight="700" fill="#1b2a41">2026년 10월 공모주 청약 달력</text>',
       '<text x="40" y="102" font-size="21" fill="#4a5568">날짜마다 청약을 받는 신규·이전상장 공모 수 · 초록 숫자는 그날 환불(납입)되는 곳 수</text>']
for i, w in enumerate("일월화수목금토"):
    col = "#c53030" if i == 0 else ("#2b6cb0" if i == 6 else "#2d3748")
    out.append(f'<text x="{X0 + i * CW + CW / 2}" y="{Y0 - 14}" font-size="20" font-weight="700" text-anchor="middle" fill="{col}">{w}</text>')
first = dt.date(Y, 10, 1)
start_col = (first.weekday() + 1) % 7  # 일요일 = 0
mx = max(count(dt.date(Y, 10, k)) for k in range(1, 32))
for k in range(1, 32):
    day = dt.date(Y, 10, k)
    pos = start_col + k - 1
    cx, cy = X0 + (pos % 7) * CW, Y0 + (pos // 7) * CH
    off = day in HOL or day.weekday() >= 5
    fill = "#fdecec" if day in HOL else ("#f4f5f7" if off else "#ffffff")
    out.append(f'<rect x="{cx + 3}" y="{cy + 3}" width="{CW - 6}" height="{CH - 6}" rx="10" fill="{fill}" stroke="#d5dbe3"/>')
    dcol = "#c53030" if (day in HOL or day.weekday() == 6) else "#2d3748"
    out.append(f'<text x="{cx + 16}" y="{cy + 32}" font-size="22" font-weight="700" fill="{dcol}">{k}</text>')
    if day in HOLNAME:
        out.append(f'<text x="{cx + CW - 14}" y="{cy + 31}" font-size="15" text-anchor="end" fill="#c53030">{HOLNAME[day]}</text>')
    n = count(day)
    if n:
        bw = (CW - 32) * n / mx
        out.append(f'<rect x="{cx + 16}" y="{cy + 50}" width="{bw:.1f}" height="26" rx="5" fill="#2b6cb0"/>')
        out.append(f'<text x="{cx + 16}" y="{cy + 104}" font-size="19" font-weight="700" fill="#1b2a41">청약 {n}곳</text>')
    rf = refunds(day)
    if rf:
        out.append(f'<text x="{cx + CW - 14}" y="{cy + 104}" font-size="17" text-anchor="end" fill="#2f855a">환불 {rf}</text>')
out.append(f'<text x="40" y="{H - 22}" font-size="17" fill="#4a5568">자료: 금융감독원 전자공시 청약 달력(지분증권)·각 증권신고서, 2026년 10월 5일 열람 · 유상증자·투자계약증권은 뺌</text>')
out.append("</svg>")
os.makedirs(os.path.join(HERE, "그림"), exist_ok=True)
open(os.path.join(HERE, "그림", "01_대표.svg"), "w", encoding="utf-8").write("\n".join(out))
print("그림/01_대표.svg", W, H, "최대", mx)
