#!/usr/bin/env python3
"""애드센스 재신청 관문 점검 — 0토큰 한 줄 (전략실 확정본 · 본사 H-197).
라이브 글 수 · 발행 공백 날짜 · 최근 10편 구성 분포(h2 수·표 수·첫 문단 꼴) · 수정 이력 유무.
서치 회차 첫 단계에서 돌린다: python3 도구/관문_점검.py [--no-net] — 한 줄을 운영/관문_일지.md 끝에 더한다.
모델을 부르지 않는다. 관문(재신청 규칙)은 회장 결정 전까지 CLAUDE.md에 넣지 않는다: 이 스크립트는 숫자만 센다."""
import csv, os, re, sys, datetime, urllib.request, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, "운영", "원장.csv")
LOG = os.path.join(ROOT, "운영", "관문_일지.md")
KST = datetime.timezone(datetime.timedelta(hours=9))


def live_count(net):
    n_ledger = 0
    rows = list(csv.DictReader(open(LEDGER, encoding="utf-8")))
    for r in rows:
        if r["상태"] == "라이브":
            n_ledger += 1
    site = None
    if net:
        try:
            req = urllib.request.Request("https://moneyproducer.co.kr/sitemap.xml", headers={"User-Agent": "Mozilla/5.0"})
            xml = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "ignore")
            site = len(set(re.findall(r"co\.kr/(\d+)</loc>", xml)))
        except Exception:
            site = None
    return rows, n_ledger, site


def shape(path):
    h = open(path, encoding="utf-8").read()
    h2 = len(re.findall(r"<h2\b", h))
    tb = len(re.findall(r"<table\b", h))
    body = re.sub(r"<!--.*?-->", "", h, flags=re.S)
    m = re.search(r"<p[^>]*>(.*?)</p>", body, re.S)
    p1 = re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else ""
    lead = "숫자" if re.match(r"\D{0,8}\d", p1[:12]) else "문장"
    ln = "짧음" if len(p1) < 90 else ("보통" if len(p1) <= 130 else "김")
    return (h2, tb, f"{lead}/{ln}"), ("수정 이력:" in h)


def main():
    net = "--no-net" not in sys.argv
    today = datetime.datetime.now(KST).date()
    rows, n_ledger, site = live_count(net)
    # 게시일(원장) — 라이브·대기 글의 게시일 집합
    dates = sorted({r["게시일"] for r in rows if r["상태"] in ("라이브", "대기") and re.match(r"\d{4}-\d{2}-\d{2}$", r["게시일"])})
    gaps = []
    if dates:
        d0 = max(datetime.date.fromisoformat(dates[0]), today - datetime.timedelta(days=13)); d1 = max(datetime.date.fromisoformat(dates[-1]), min(today, datetime.date.fromisoformat(dates[-1])))
        have = {datetime.date.fromisoformat(d) for d in dates}
        d = d0
        while d <= d1:
            if d not in have: gaps.append(d.isoformat()[5:])
            d += datetime.timedelta(days=1)
    # 최근 10편 = 대기 파일을 파일명(게시일) 순으로 뒤에서 10개
    qdir = os.path.join(ROOT, "발행", "대기")
    files = sorted(f for f in os.listdir(qdir) if f.endswith(".html")) if os.path.isdir(qdir) else []
    recent = files[-10:]
    shapes, hist = [], 0
    for f in recent:
        s, has = shape(os.path.join(qdir, f)); shapes.append(s); hist += has
    c = collections.Counter((s[0], s[1]) for s in shapes)
    top = c.most_common(1)[0] if c else ((0, 0), 0)
    c2 = collections.Counter(s[2] for s in shapes)
    top2 = c2.most_common(1)[0] if c2 else ("-", 0)
    flag = "경고(같은 구성 5편 이상)" if top[1] >= 5 else "통과"
    line = (f"| {today} | 라이브 원장 {n_ledger} · 사이트맵 {site if site is not None else '확인 못 함'} | 대기 {len(files)} | "
            f"최근 14일 발행 공백 {','.join(gaps) if gaps else '없음'} | 최근 {len(recent)}편 최다 구성 h2 {top[0][0]}·표 {top[0][1]} = {top[1]}편 ({flag}) | "
            f"첫 문단 꼴 최다 {top2[0]} = {top2[1]}편 | 수정 이력 {hist}/{len(recent)} |")
    if not os.path.exists(LOG):
        open(LOG, "w", encoding="utf-8").write("# 관문 점검 일지 (0토큰 — 도구/관문_점검.py)\n\n| 날짜 | 라이브 | 대기 | 공백 | 구성 분포 | 첫 문단 | 수정 이력 |\n|---|---|---|---|---|---|---|\n")
    open(LOG, "a", encoding="utf-8").write(line + "\n")
    print(line)


if __name__ == "__main__":
    main()
