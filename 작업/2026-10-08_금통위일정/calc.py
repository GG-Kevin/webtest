#!/usr/bin/env python3
"""금통위 일정 2026 — 원고 표와 숫자를 만드는 계산(표준 라이브러리만).

입력(원문에서 옮긴 값, 2026-10-04 열어 확인)
- 2026년 통화정책방향 결정회의 날짜 8개
  https://www.bok.or.kr/portal/singl/crncyPolicyDrcMtg/listYear.do?mtgSe=A&menuNo=200755&pYear=2026
- 같은 화면 각주: 「금융·경제 이슈는 통화정책방향 결정회의 D+7일, 의사록은 회의일로부터 2주 경과 후 첫 화요일에 게시」
- 한국은행 기준금리 변경 목록(2025-05-29 2.50 · 2026-07-16 2.75 · 2026-08-27 3.00)
  https://www.bok.or.kr/portal/singl/baseRate/list.do?dataSeCd=01&menuNo=200643
- 「기준금리는 연 8회 금융통화위원회 '본회의'에서 결정」·「본회의는 통상 오전 9시」
  https://www.bok.or.kr/portal/main/contents.do?menuNo=200293

공식
- 회의 뒤 기준금리 = 변경 목록에서 회의일 이하인 가장 늦은 변경일의 금리
- 이슈분석 게시일 = 회의일 + 7일
- 의사록 게시일 = (회의일 + 14일) 다음 날부터 처음 오는 화요일 (「2주 경과 후 첫 화요일」)
- 이자 차이(연) = 대출(예금) 원금 × 금리 변동폭(%p) ÷ 100, 원 미만 버림
  월 = 연 ÷ 12, 원 미만 버림. 가정: 금리가 변동폭만큼 그대로 움직이고 1년 내내 원금이 같다.
같은 입력이면 같은 출력. 실행: python3 calc.py
"""
import datetime as dt

BASE_DATE = dt.date(2026, 10, 4)          # 원문을 연 날(기준일)
MEETINGS = [dt.date(2026, 1, 15), dt.date(2026, 2, 26), dt.date(2026, 4, 10), dt.date(2026, 5, 28),
            dt.date(2026, 7, 16), dt.date(2026, 8, 27), dt.date(2026, 10, 22), dt.date(2026, 11, 26)]
RATE_CHANGES = [(dt.date(2025, 5, 29), 2.50), (dt.date(2026, 7, 16), 2.75), (dt.date(2026, 8, 27), 3.00)]
MEETINGS_PER_YEAR = 8                       # 「연 8회」
MEETING_HOUR = 9                            # 「통상 오전 9시」
ISSUE_LAG = 7                               # 「D+7일」
MINUTES_LAG = 14                            # 「2주 경과 후」
WD = "월화수목금토일"

N_MEETINGS = len(MEETINGS)
DONE = [d for d in MEETINGS if d < BASE_DATE]
LEFT = [d for d in MEETINGS if d >= BASE_DATE]
N_DONE, N_LEFT = len(DONE), len(LEFT)
DAYS_TO_NEXT = (LEFT[0] - BASE_DATE).days
NOT_THURSDAY = [d for d in MEETINGS if d.weekday() != 3]
CUR_RATE = RATE_CHANGES[-1][1]
RISE_2026 = round(RATE_CHANGES[-1][1] - RATE_CHANGES[0][1], 2)   # 2.50 → 3.00


def fmt(d):
    return f"{d.month}월 {d.day}일({WD[d.weekday()]})"


def rate_after(d):
    r = None
    for day, v in RATE_CHANGES:
        if day <= d:
            r = v
    return r


def issue_day(d):
    return d + dt.timedelta(days=ISSUE_LAG)


def minutes_day(d):
    x = d + dt.timedelta(days=MINUTES_LAG + 1)
    while x.weekday() != 1:
        x += dt.timedelta(days=1)
    return x


def interest(principal, pp):
    year = int(principal * pp / 100)
    return year, year // 12


def table_meetings():
    rows = ["| 차례 | 회의일 | 결과(회의 뒤 기준금리) |", "|---|---|---|"]
    prev = rate_after(MEETINGS[0] - dt.timedelta(days=1))
    for i, d in enumerate(MEETINGS, 1):
        if d < BASE_DATE:
            r = rate_after(d)
            res = f"연 {r:.2f}% (변경 없음)" if r == prev else f"연 {r:.2f}% ({r - prev:+.2f}%p)"
            prev = r
        else:
            res = "남은 회의"
        rows.append(f"| {i} | {fmt(d)} | {res} |")
    return "\n".join(rows)


def table_minutes():
    rows = ["| 회의일 | 이슈분석 게시(D+7) | 의사록 게시(2주 뒤 첫 화요일) |", "|---|---|---|"]
    for d in MEETINGS[4:]:
        rows.append(f"| {fmt(d)} | {fmt(issue_day(d))} | {fmt(minutes_day(d))} |")
    return "\n".join(rows)


LOANS = [100_000_000, 200_000_000, 300_000_000]
DEPOSITS = [10_000_000, 30_000_000]
STEPS = [0.25, 0.50]


def won(p):
    return f"{p // 100_000_000}억원" if p >= 100_000_000 else f"{p // 10_000:,}만원"


def table_interest():
    rows = ["| 원금 | 0.25%p 차이(연) | 한 달로 | 0.50%p 차이(연) | 한 달로 |", "|---|---|---|---|---|"]
    for p in LOANS + DEPOSITS:
        kind = "대출" if p in LOANS else "예금"
        cells = []
        for s in STEPS:
            y, m = interest(p, s)
            cells += [f"{y:,}원", f"약 {m:,}원"]
        rows.append(f"| {kind} {won(p)} | " + " | ".join(cells) + " |")
    return "\n".join(rows)


if __name__ == "__main__":
    print(f"기준일 {BASE_DATE} · 회의 {N_MEETINGS}회(원문 연 {MEETINGS_PER_YEAR}회) · 끝난 회의 {N_DONE} · 남은 회의 {N_LEFT}")
    print(f"다음 회의 {fmt(LEFT[0])}까지 {DAYS_TO_NEXT}일 · 마지막 {fmt(LEFT[-1])}")
    print(f"목요일이 아닌 회의: {', '.join(fmt(d) for d in NOT_THURSDAY)}")
    print(f"지금 기준금리 연 {CUR_RATE:.2f}% · 2.50%에서 {RISE_2026:.2f}%p")
    print(f"회의 뒤 기준금리 1~6회: {[rate_after(d) for d in DONE]}")
    print()
    print("표: 2026년 기준금리 결정회의 8번과 결과")
    print(table_meetings())
    print()
    print("표: 남은 회의의 이슈분석·의사록 게시 예정일(게시 규칙으로 계산)")
    print(table_minutes())
    print()
    print("표: 금리가 0.25%p·0.50%p 달라질 때 1년 이자 차이(가정 계산)")
    print(table_interest())
