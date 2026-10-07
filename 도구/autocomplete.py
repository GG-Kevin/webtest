#!/usr/bin/env python3
"""autocomplete — 구글·네이버 자동완성 원문(0토큰, 표준 라이브러리만).

사용:
  python3 도구/autocomplete.py <씨앗> [<씨앗> ...]           씨앗마다 구글·네이버 원문과 겹침
  python3 도구/autocomplete.py <씨앗> --expand                씨앗 × 접미어(어떻게·왜·얼마·언제·신청·조건·계산·기준·2026)도 함께
  python3 도구/autocomplete.py <씨앗> --suffix 얼마,언제       접미어를 직접 준다(--expand 포함)
  python3 도구/autocomplete.py --check "<질문>"               그 질문이 구글·네이버 자동완성에 원문 그대로 있는지(있으면 종료 0)
  옵션: --json · --out 파일(.json) · --sleep 초(호출 사이, 기본 0.35)

원천(10/3 본사 시험으로 동작 확인):
  구글   https://suggestqueries.google.com/complete/search?client=firefox&hl=ko&gl=kr&q=<q>   → JSON [q, [제안…]]
  네이버 https://ac.search.naver.com/nx/ac?q=<q>&con=1&frm=nv&ans=2&r_format=json&r_enc=UTF-8&r_unicode=0
         &t_koreng=1&run=2&rev=4&q_enc=UTF-8&st=100                                           → JSON items[0] = [[제안, "0"], …]
규칙:
  - 「원문」 = 자동완성이 돌려준 글자 그대로(띄어쓰기만 무시하고 맞댄다). 우리가 다듬은 말은 원문이 아니다.
  - 403·429·연결 실패는 None(=못 열었다)으로 돌려주고 다시 시도하지 않는다. 0개 결과(빈 목록)와 구별한다.
  - 수요 크기(검색량)는 재지 않는다. 개수(0~10)는 「꽉 찬 정도」 신호일 뿐이다.
다른 스크립트(scout·calendar_build·demand_google)가 google()·naver()·both()·same()을 가져다 쓴다.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.parse

sys.dont_write_bytecode = True  # 도구/에 __pycache__를 남기지 않는다(커밋 대상 아님)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from source_open import fetch  # noqa: E402

G_URL = "https://suggestqueries.google.com/complete/search?client=firefox&hl=ko&gl=kr&q="
N_URL = ("https://ac.search.naver.com/nx/ac?con=1&frm=nv&ans=2&r_format=json&r_enc=UTF-8&r_unicode=0"
         "&t_koreng=1&run=2&rev=4&q_enc=UTF-8&st=100&q=")
SUFFIXES = ["어떻게", "왜", "얼마", "언제", "신청", "조건", "계산", "기준", "2026"]
SLEEP = 0.35
_CACHE = {}
LAST_ERR = {}


def key(s):
    """띄어쓰기·대소문자를 무시한 맞대기 열쇠. 숫자 뒤 「프로·퍼센트·퍼」는 %로 본다(구글은 「10 프로」, 네이버는 「10%」로 돌려준다)."""
    t = re.sub(r"(\d)\s*(퍼센트|프로|퍼)(?![가-힣])", r"\1%", s or "")
    return re.sub(r"\s+", "", t).lower()


def same(a, b):
    return key(a) == key(b)


def _get(url, who, q):
    ck = (who, q)
    if ck in _CACHE:
        return _CACHE[ck]
    r = fetch(url + urllib.parse.quote(q), timeout=15, retries=0)
    time.sleep(SLEEP)
    if r["reason"]:
        LAST_ERR[who] = r["reason"]
        _CACHE[ck] = None
        return None
    try:
        data = json.loads(r["text"])
    except ValueError:
        LAST_ERR[who] = "응답이 JSON이 아님"
        _CACHE[ck] = None
        return None
    if who == "google":
        out = [s for s in (data[1] if isinstance(data, list) and len(data) > 1 else []) if isinstance(s, str)]
    else:
        items = data.get("items") or [[]]
        out = [it[0] for it in (items[0] if items else []) if isinstance(it, list) and it]
    _CACHE[ck] = out
    return out


def google(q):
    """구글 자동완성 원문 목록. 못 열면 None."""
    return _get(G_URL, "google", q)


def naver(q):
    """네이버 자동완성 원문 목록. 못 열면 None."""
    return _get(N_URL, "naver", q)


def both(q):
    """질문 하나 → {'q','google','naver','g_n','n_n','g_has','n_has'}
    g_has·n_has = 질문이 그 자동완성에 원문 그대로 있는가(질문 자체를 넣은 결과 기준)."""
    g = google(q)
    n = naver(q)
    return {"q": q, "google": g, "naver": n,
            "g_n": None if g is None else len(g), "n_n": None if n is None else len(n),
            "g_has": None if g is None else any(same(q, s) for s in g),
            "n_has": None if n is None else any(same(q, s) for s in n)}


def expand(seed, suffixes=None, with_suffix=False):
    """씨앗(+접미어) → {'seed', 'rows': [{'q','google','naver'}], 'google_all', 'naver_all', 'overlap'}"""
    qs = [seed] + ([f"{seed} {s}" for s in (suffixes or SUFFIXES)] if with_suffix else [])
    rows = []
    g_all, n_all = [], []
    for q in qs:
        g = google(q)
        n = naver(q)
        rows.append({"q": q, "google": g, "naver": n})
        for s in g or []:
            if key(s) not in {key(x) for x in g_all}:
                g_all.append(s)
        for s in n or []:
            if key(s) not in {key(x) for x in n_all}:
                n_all.append(s)
    nk = {key(x) for x in n_all}
    overlap = [s for s in g_all if key(s) in nk]
    return {"seed": seed, "rows": rows, "google_all": g_all, "naver_all": n_all, "overlap": overlap}


def _fmt_list(lst):
    if lst is None:
        return "못 열었다"
    return " | ".join(lst) if lst else "(0개)"


def main(argv=None):
    global SLEEP
    ap = argparse.ArgumentParser(description="구글·네이버 자동완성 원문(0토큰)")
    ap.add_argument("seeds", nargs="*")
    ap.add_argument("--expand", action="store_true", help="접미어 확장(어떻게·왜·얼마·언제·신청·조건·계산·기준·2026)")
    ap.add_argument("--suffix", help="쉼표로 준 접미어(주면 --expand로 본다)")
    ap.add_argument("--check", help="이 질문이 두 자동완성에 원문 그대로 있는지")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--sleep", type=float, default=SLEEP)
    a = ap.parse_args(argv)
    SLEEP = a.sleep
    if a.check:
        r = both(a.check)
        if a.json:
            print(json.dumps(r, ensure_ascii=False, indent=1))
        else:
            gl = "못 열었다" if r["g_has"] is None else ("있음" if r["g_has"] else "없음")
            nl = "못 열었다" if r["n_has"] is None else ("있음" if r["n_has"] else "없음")
            print(f"질문: {a.check}\n구글 원문 {gl}(제안 {r['g_n']}) · 네이버 원문 {nl}(제안 {r['n_n']})")
            print(f"  구글: {_fmt_list(r['google'])}\n  네이버: {_fmt_list(r['naver'])}")
        return 0 if (r["g_has"] and r["n_has"]) else 1
    if not a.seeds:
        ap.print_usage(sys.stderr)
        return 2
    sufs = [s.strip() for s in a.suffix.split(",") if s.strip()] if a.suffix else None
    res = [expand(s, sufs, a.expand or bool(sufs)) for s in a.seeds]
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=1)
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return 0
    for r in res:
        print(f"## {r['seed']} — 구글 {len(r['google_all'])} · 네이버 {len(r['naver_all'])} · 겹침 {len(r['overlap'])}")
        for row in r["rows"]:
            g, n = row["google"], row["naver"]
            print(f"- 「{row['q']}」 구글 {('못 열었다' if g is None else len(g))} · 네이버 {('못 열었다' if n is None else len(n))}")
        nk = {key(x) for x in r["naver_all"]}
        gk = {key(x) for x in r["google_all"]}
        print("  구글 원문: " + (" | ".join(f"{s}{' [N]' if key(s) in nk else ''}" for s in r["google_all"]) or "(0개)"))
        print("  네이버만: " + (" | ".join(s for s in r["naver_all"] if key(s) not in gk) or "(없음)"))
    if LAST_ERR:
        print("# 못 열었다: " + " · ".join(f"{k} {v}" for k, v in LAST_ERR.items()), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
