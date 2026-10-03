#!/usr/bin/env python3
"""wp_collect — 원천 3군(구글 쪽) 새 글 목록 수집(0토큰, 표준 라이브러리만). 제목·날짜·링크만 받는다.

사용:
  python3 도구/wp_collect.py [--date YYYY-MM-DD] [--repo <서치 레포>] [--per-page 20] [--hours 72] [--stdout]
산출: 작업/<날짜>/3군.md (사이트별 최근 글 표 + 「네이버 합의 묶음과 같은 닻」 표시)
대상(v3.1 「3군 원천」, 도메인은 조사실 R-004 부록 BC 2절):
  WP REST  — hometax-go.kr · wegotogether.co.kr · jiwonfund.kr · myinvestplan.com · blog.signalplanner.co.kr
             /wp-json/wp/v2/posts?per_page=20&_fields=date,link,title (머리글 X-WP-Total = 전체 글 수)
  사이트맵 — www.banksalad.com/articles/sitemap.xml 의 lastmod(수정일) 최근 20개. 제목은 주소(슬러그)에서 읽는다.
수집하지 않는 곳(질문마다 열어 보는 판형 기준): kbthink·tossbank·toss.im·help.3o3·ezb·계산기 3곳·bloklo·refininfo(키워드 자동 페이지).
규칙: 본문은 받지 않는다. WP가 아니거나 403·429·인증서 오류면 「못 열었다(이유)」로 적고 우회하지 않는다(TLS 확인을 끄지 않는다).
종료코드: 0 = 모두 받음 · 1 = 못 연 곳 있음
"""
import argparse
import datetime as dt
import html
import json
import os
import re
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True  # 도구/에 __pycache__를 남기지 않는다(커밋 대상 아님)
sys.path.insert(0, HERE)
from source_open import fetch  # noqa: E402

KST = dt.timezone(dt.timedelta(hours=9))
WP_SITES = [("hometax-go.kr", "개인 WP(세금)"), ("wegotogether.co.kr", "개인 WP"), ("jiwonfund.kr", "개인 WP(지원금·서식)"),
            ("myinvestplan.com", "개인 WP"), ("blog.signalplanner.co.kr", "기업 블로그(보험 앱)")]
BANKSALAD = "https://www.banksalad.com/articles/sitemap.xml"


def anchor_name(title):
    try:
        import scout  # 같은 폴더 — 묶기 닻 표를 그대로 쓴다
        p = {"title": title}
        a = scout.anchor_of(p)
        return a[0] if a else ""
    except Exception:  # noqa: BLE001
        return ""


def wp(domain, per_page):
    url = f"https://{domain}/wp-json/wp/v2/posts?per_page={per_page}&_fields=date,link,title"
    r = fetch(url, timeout=25)
    if r["reason"]:
        why = r["reason"]
        if "CERTIFICATE" in why.upper():
            why = "인증서 확인 실패 — 사이트 인증서 문제(10/3 curl: 인증서 이름이 도메인과 안 맞음), 확인을 끄지 않는다"
        return url, f"못 열었다({why})", [], None
    if "json" not in (r["ctype"] or "").lower():
        return url, "못 열었다(WP REST 아님 — JSON 아님)", [], None
    try:
        data = json.loads(r["text"])
    except ValueError:
        return url, "못 열었다(JSON 해석 실패)", [], None
    if not isinstance(data, list):
        return url, "못 열었다(WP REST 아님 — 목록 아님)", [], None
    rows = []
    for x in data:
        try:
            d = dt.datetime.fromisoformat(x["date"]).replace(tzinfo=KST)  # WP date = 사이트 현지 시각(한국 사이트 = KST 가정)
        except (KeyError, ValueError):
            continue
        t = html.unescape(re.sub(r"<[^>]+>", "", (x.get("title") or {}).get("rendered", ""))).strip()
        rows.append({"when": d, "title": t, "url": urllib.parse.unquote(x.get("link", ""))})
    total = r["headers"].get("X-WP-Total") or r["headers"].get("x-wp-total")
    return url, "받음", rows, total


def banksalad(n):
    r = fetch(BANKSALAD, timeout=25)
    if r["reason"]:
        return BANKSALAD, f"못 열었다({r['reason']})", [], None
    urls = re.findall(r"<url>\s*<loc>([^<]+)</loc>\s*(?:<lastmod>([^<]+)</lastmod>)?", r["text"])
    rows = []
    for loc, lm in urls:
        if not lm or loc.rstrip("/").endswith("/articles/home"):
            continue
        try:
            d = dt.datetime.fromisoformat(lm.replace("Z", "+00:00")).astimezone(KST)
        except ValueError:
            continue
        slug = urllib.parse.unquote(loc.rstrip("/").rsplit("/", 1)[-1])
        rows.append({"when": d, "title": slug.replace("-", " ") + " (주소에서)", "url": urllib.parse.unquote(loc)})
    rows.sort(key=lambda x: x["when"], reverse=True)
    return BANKSALAD, "받음(사이트맵 수정일)", rows[:n], str(len(urls))


def main(argv=None):
    ap = argparse.ArgumentParser(description="3군 새 글 목록(0토큰)")
    ap.add_argument("--date")
    ap.add_argument("--repo", default=os.path.normpath(os.path.join(HERE, "..")))
    ap.add_argument("--per-page", type=int, default=20)
    ap.add_argument("--hours", type=int, default=72)
    ap.add_argument("--stdout", action="store_true")
    a = ap.parse_args(argv)
    now = dt.datetime.now(KST)
    day = dt.date.fromisoformat(a.date) if a.date else now.date()
    start = now - dt.timedelta(hours=a.hours)
    res = [(d, kind) + wp(d, a.per_page) for d, kind in WP_SITES]
    res.append(("www.banksalad.com", "기업 콘텐츠 허브(사이트맵)") + banksalad(a.per_page))
    L = [f"# 3군 새 글 {day.isoformat()} — 구글 쪽 원천(wp_collect.py)", "",
         f"- 수집 {now:%Y-%m-%d %H:%M} KST · 제목·날짜·링크만(본문 받지 않음) · 「{a.hours}시간 안」 = {start:%m-%d %H:%M} 이후",
         "- 쓰임: 네이버 합의 묶음의 질문이 구글 쪽에서도 지금 쓰이는지 맞대 보는 참고. 3군 글만으로 주제를 정하지 않는다(본사 안 1-2 ①).",
         "- 「닻」 칸 = scout.py 묶기 표(ANCHORS)에 맞은 묶음 이름. 원천표의 합의 묶음과 같은 이름이면 구글 쪽도 같은 주제를 쓰는 중이다.",
         "", "## 1. 사이트별 결과", "| 사이트 | 유형 | 결과 | 받은 글 | 72시간 안 | 전체 글(머리글·사이트맵) | 요청 주소 |",
         "|---|---|---|---:|---:|---|---|"]
    bad = 0
    for d, kind, url, state, rows, total in res:
        if not state.startswith("받음"):
            bad += 1
        n72 = sum(1 for x in rows if x["when"] >= start)
        L.append(f"| {d} | {kind} | {state} | {len(rows)} | {n72} | {total or '-'} | {url} |")
    L += ["", "## 2. 최근 글(사이트별, 새 글 먼저)"]
    for d, kind, url, state, rows, total in res:
        L += ["", f"### {d}", "| 날짜(KST) | 제목 | 닻 | 링크 |", "|---|---|---|---|"]
        if not rows:
            L.append(f"| - | ({state}) | | |")
        for x in rows:
            L.append(f"| {x['when']:%Y-%m-%d %H:%M} | {x['title'].replace('|', '/')} | {anchor_name(x['title']) or '-'} | {x['url']} |")
    text = "\n".join(L) + "\n"
    if a.stdout:
        print(text)
    else:
        wdir = os.path.join(a.repo, "작업", day.isoformat())
        os.makedirs(wdir, exist_ok=True)
        p = os.path.join(wdir, "3군.md")
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"썼다: {p}")
    for d, kind, url, state, rows, total in res:
        print(f"# {d}: {state} · {len(rows)}편")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
