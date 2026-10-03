#!/usr/bin/env python3
"""counter_log — 우리 블로그 공개 카운터의 어제 값을 운영/방문기록.csv에 한 줄 적는다(0토큰, 표준 라이브러리만).

사용:
  python3 도구/counter_log.py [--url https://moneyproducer.co.kr/] [--repo <서치 레포>] [--dry-run]
읽는 곳(티스토리 스킨 HTML, 10/3 본사 확인): 사이드바 「전체 방문자」 상자
  <div class="count"> <h2>전체 방문자</h2> <p class="total">720</p> <p>Today : 1</p> <p>Yesterday : 13</p> </div>
칸(고정): 날짜,어제,오늘,전체,수집시각
  - 날짜 = 「어제」 값이 가리키는 한국 날짜(수집한 한국 날짜 − 1일). 오늘 = 수집 시각까지의 부분값.
  - 같은 날짜 줄이 이미 있으면 덮지 않는다(종료 0, 「이미 있음」).
쓰임: 월중 판정의 상한 값(v3 4-2 — 공개 카운터는 구글 클릭보다 크다). 판정 원천은 구글 클릭(회장 답 2).
종료코드: 0 = 적음 또는 이미 있음 · 1 = 못 열었다·카운터 못 찾음
"""
import argparse
import csv
import datetime as dt
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True  # 도구/에 __pycache__를 남기지 않는다(커밋 대상 아님)
sys.path.insert(0, HERE)
from source_open import fetch  # noqa: E402

KST = dt.timezone(dt.timedelta(hours=9))
COLS = ["날짜", "어제", "오늘", "전체", "수집시각"]


def read_counter(url):
    r = fetch(url, timeout=25)
    if r["reason"]:
        return None, f"못 열었다({r['reason']})"
    h = r["text"]
    m = re.search(r'<div class="count">(.*?)</div>', h, re.S)
    if not m:
        return None, "카운터 상자(div.count)를 못 찾음 — 스킨이 바뀌었는지 볼 것"
    box = m.group(1)
    tot = re.search(r'class="total"[^>]*>\s*([\d,]+)', box)
    tod = re.search(r"Today\s*:\s*([\d,]+)", box)
    yes = re.search(r"Yesterday\s*:\s*([\d,]+)", box)
    if not (tot and tod and yes):
        return None, "카운터 숫자(total·Today·Yesterday)를 못 읽음"
    n = lambda x: int(x.group(1).replace(",", ""))  # noqa: E731
    return {"전체": n(tot), "오늘": n(tod), "어제": n(yes)}, "읽음"


def main(argv=None):
    ap = argparse.ArgumentParser(description="공개 카운터 어제 값 기록(0토큰)")
    ap.add_argument("--url", default="https://moneyproducer.co.kr/")
    ap.add_argument("--repo", default=os.path.normpath(os.path.join(HERE, "..")))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    now = dt.datetime.now(KST)
    val, state = read_counter(a.url)
    if not val:
        print(f"카운터: {state} · {a.url}")
        return 1
    day = (now.date() - dt.timedelta(days=1)).isoformat()
    row = {"날짜": day, "어제": val["어제"], "오늘": val["오늘"], "전체": val["전체"], "수집시각": now.strftime("%Y-%m-%d %H:%M")}
    path = os.path.join(a.repo, "운영", "방문기록.csv")
    have = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8-sig", newline="") as f:
            have = {r.get("날짜") for r in csv.DictReader(f)}
    line = f"{row['날짜']} 어제 {row['어제']} · 오늘(부분) {row['오늘']} · 전체 {row['전체']} · 수집 {row['수집시각']} KST"
    if day in have:
        print(f"이미 있음(덮지 않음): {line}")
        return 0
    if a.dry_run:
        print(f"(dry-run) {line}")
        return 0
    new = not os.path.exists(path) or os.path.getsize(path) == 0
    with open(path, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        if new:
            w.writeheader()
        w.writerow(row)
    print(f"적었다: {line} → {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
