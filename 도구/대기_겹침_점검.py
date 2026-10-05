#!/usr/bin/env python3
"""후보 검색어가 원장의 진행·대기·라이브 글과 같은 주제인지 본다(gate_topic 보완, 서치 도구).
gate_topic은 .claude/gate의 대장만 읽어 발행/대기 글을 못 잡을 때가 있다(10/5 실업급여 수급기간).
사용: python3 도구/대기_겹침_점검.py "검색어" ["검색어" ...]   → 겹치면 줄을 찍고 종료 1
규칙: 핵심 낱말(첫 낱말)이 같거나 의미 낱말 둘 이상이 겹치면 같은 주제로 본다."""
import csv, re, sys

STOP = {"조건", "방법", "계산", "기준", "한도", "기간", "신청", "가입", "조회", "금액", "대상", "일정", "제도", "2026", "총정리"}
LIVE_STATES = {"집필", "완성", "대기", "라이브"}


def toks(s):
    return [t for t in re.findall(r"[가-힣A-Za-z0-9]+", s) if t not in STOP and not re.fullmatch(r"\d+(월|일|년|%)?", t)]


def main():
    cands = sys.argv[1:]
    if not cands:
        print(__doc__); return 2
    rows = [r for r in csv.DictReader(open("운영/원장.csv", encoding="utf-8")) if r["상태"] in LIVE_STATES]
    bad = 0
    for c in cands:
        ct = toks(c)
        for r in rows:
            for field in ("검색어", "최종제목", "가제"):
                rt = toks(r[field])
                if not ct or not rt:
                    continue
                shared = set(ct) & set(rt)
                if ct[0] == rt[0] or len(shared) >= 2:
                    print(f"겹침: 「{c}」 ← {r['묶음']}/{r['편']} {r['상태']} 「{r[field]}」 (낱말 {sorted(shared) or ct[0]})")
                    bad = 1
                    break
            else:
                continue
            break
    if not bad:
        print("겹침 없음")
    return bad


if __name__ == "__main__":
    sys.exit(main())
