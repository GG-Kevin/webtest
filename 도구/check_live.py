#!/usr/bin/env python3
"""회장이 붙인 글이 잘렸는지 맞대 본다(0토큰). 사용: python3 도구/check_live.py <라이브 URL> <발행 HTML>
소제목(h2·h3) 수 · 표 수 · 마지막 문단 · 핵심 문장 5개를 대조해 「일치」 또는 「누락: …」을 낸다. 누락이면 종료코드 1."""
import re, sys, html, subprocess

def norm(s):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    return re.sub(r"[\s ]+", "", s)

def fetch(url):
    r = subprocess.run(["curl", "-sSL", "-m", "40", "-A", "Mozilla/5.0", url], capture_output=True, text=True)
    return r.stdout

def article(page):
    i = page.find('contents_style"')
    if i < 0:
        i = page.find("<article")
    j = page.find("</article>", i if i >= 0 else 0)
    return page[i:j] if i >= 0 and j > i else page

def parts(h):
    h = re.sub(r"(?s)<(script|style)[^>]*>.*?</\1>", "", h)
    heads = len(re.findall(r"<h[23][\s>]", h))
    tables = len(re.findall(r"<table[\s>]", h))
    paras = [norm(m) for m in re.findall(r"(?s)<p[\s>].*?</p>", h)]
    paras = [p for p in paras if p]
    return heads, tables, paras, norm(h)

def sentences(h):
    h = re.sub(r"(?s)<(script|style|table)[^>]*>.*?</\1>", "", h)
    out = []
    for m in re.findall(r"(?s)<p[\s>].*?</p>", h):
        t = html.unescape(re.sub(r"<[^>]+>", " ", m)); t = re.sub(r"\s+", " ", t).strip()
        for s in re.split(r"(?<=[.다요])\s+", t):
            if len(norm(s)) >= 25: out.append(s)
    return out

def main():
    if len(sys.argv) < 3: sys.exit("사용: python3 도구/check_live.py <라이브 URL> <발행 HTML>")
    url, path = sys.argv[1], sys.argv[2]
    loc = open(path, encoding="utf-8").read()
    live_page = fetch(url)
    if len(live_page) < 2000: sys.exit(f"라이브를 못 읽음({len(live_page)}바이트): {url}")
    live = article(live_page)
    lh, lt, lp, ltxt = parts(live)
    fh, ft, fp, ftxt = parts(loc)
    miss = []
    if lh < fh: miss.append(f"소제목 라이브 {lh}개 < 파일 {fh}개")
    if lt < ft: miss.append(f"표 라이브 {lt}개 < 파일 {ft}개")
    if fp and fp[-1][:60] not in ltxt: miss.append("마지막 문단 없음: " + fp[-1][:40] + "…")
    ss = sentences(loc)
    if ss:
        pick = [ss[round(i * (len(ss) - 1) / 4)] for i in range(5)] if len(ss) >= 5 else ss
        for s in pick:
            if norm(s)[:50] not in ltxt: miss.append("핵심 문장 없음: " + s[:40] + "…")
    print(f"라이브 {url}: 소제목 {lh} · 표 {lt}  /  파일 {path}: 소제목 {fh} · 표 {ft}")
    if miss:
        print("누락: " + " | ".join(miss))
        print(f"다시 붙여 주세요: {path}")
        sys.exit(1)
    print("일치")

if __name__ == "__main__":
    main()
