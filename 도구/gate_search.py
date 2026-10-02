#!/usr/bin/env python3
"""서치 발행 게이트(0토큰). 사용: python3 도구/gate_search.py <발행 HTML>
CLAUDE.md 「애드센스 기준」 1~9와 글 규칙을 센다. 치명 위반이 있으면 종료코드 1, 없으면 0(경고는 0).
제목은 <title> → 첫 <h1> → 첫 줄 주석 <!-- 제목: ... --> 순으로 찾는다."""
import re, sys, html
from html.parser import HTMLParser

SITE = "moneyproducer.co.kr"

class P(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True)
        s.links = []; s.imgs = []; s.svgs = 0; s.tables = []; s.h = []
        s.in_table = 0; s.text_out = []; s.cur = None; s.stack = []
        s.title = None; s.h1 = None; s._t = None; s.paras = []; s._p = None
        s.table_caption = []; s.last_a_in_last_p = []
    def handle_starttag(s, t, a):
        a = dict(a)
        if t == "a" and a.get("href"): s.links.append(a["href"]);
        if t == "a" and s._p is not None: s._p["links"].append(a.get("href", ""))
        if t == "img": s.imgs.append(a)
        if t == "svg" and (a.get("role") == "img" or a.get("aria-label")): s.svgs += 1
        if t == "table":
            s.in_table += 1; s.tables.append({"style": a.get("style", ""), "caption": False, "html_min": None})
        if t == "caption" and s.tables: s.tables[-1]["caption"] = True
        if t in ("h1", "h2", "h3", "title"): s._t = [t, []]
        if t == "p": s._p = {"text": [], "links": []}
    def handle_endtag(s, t):
        if t == "table": s.in_table -= 1
        if s._t and s._t[0] == t:
            txt = "".join(s._t[1]).strip()
            if t == "title" and s.title is None: s.title = txt
            elif t == "h1" and s.h1 is None: s.h1 = txt
            elif t in ("h2", "h3"): s.h.append((t, txt))
            s._t = None
        if t == "p" and s._p is not None:
            s._p["text"] = "".join(s._p["text"]).strip(); s.paras.append(s._p); s._p = None
    def handle_data(s, d):
        if s._t: s._t[1].append(d)
        if s._p is not None: s._p["text"].append(d)
        if not s.in_table: s.text_out.append(d)

def main():
    if len(sys.argv) < 2:
        sys.exit("사용: python3 도구/gate_search.py <발행 HTML>")
    raw = open(sys.argv[1], encoding="utf-8").read()
    p = P(); p.feed(raw)
    alltext = html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"(?s)<(script|style)[^>]*>.*?</\1>", "", raw)))
    alltext = re.sub(r"\s+", " ", alltext)
    outside = re.sub(r"\s+", " ", "".join(p.text_out))
    fatal, warn, info = [], [], []

    # 제목
    title = p.title or p.h1
    if not title:
        m = re.search(r"<!--\s*제목\s*:\s*(.+?)\s*-->", raw)
        title = m.group(1) if m else None
    if title:
        n = len(title); info.append(f"제목 {n}자: {title}")
        if n > 45 or n < 15: warn.append(f"제목 길이 {n}자(15~45자 권장)")
    else:
        warn.append("제목을 못 찾음(<title>·<h1>·첫 줄 주석 「<!-- 제목: ... -->」 없음)")

    # 글 규칙: 금지어
    bad = []
    for m in re.finditer(r"지금\s*(사라|사세요|사야|팔라|팔아)|(매수|매도|사|팔)\s*하세요|무조건|100%\s*수익|원금\s*보장|수익\s*(을\s*)?보장|AI\s*(활용|작성|가\s*작성|로\s*작성)|인공지능(으로|이)\s*작성|ChatGPT|챗GPT", alltext):
        bad.append(m.group(0))
    for m in re.finditer(r"(권유|보장|추천)", alltext):
        tail = alltext[m.end():m.end() + 12]
        head = alltext[max(0, m.start() - 12):m.start()]
        if m.group(1) == "추천": continue
        if not re.search(r"않|없|아니|못|불가|지\s*않", tail) and not re.search(r"않|없|아니|못", head):
            bad.append(alltext[max(0, m.start() - 10):m.end() + 8])
    if bad: fatal.append("금지어(권유·보장·AI 문구) " + str(len(bad)) + "건: " + " / ".join(bad[:5]))

    # 기준일
    n_date = len(re.findall(r"\d{4}[-.]\s?\d{1,2}[-.]\s?\d{1,2}\.?\s*기준", alltext))
    info.append(f"「YYYY-MM-DD 기준」 {n_date}회")
    if n_date == 0: fatal.append("「YYYY-MM-DD 기준」이 한 번도 없음")
    elif n_date < 3: warn.append(f"「YYYY-MM-DD 기준」 {n_date}회뿐(숫자마다 기준일 확인)")

    # 표
    nt = len(p.tables); info.append(f"표 {nt}개")
    if nt < 2: fatal.append(f"표 {nt}개(고유 재료 2개 이상 필요)")
    nocap = sum(1 for t in p.tables if not t["caption"])
    if nocap: warn.append(f"caption 없는 표 {nocap}개(표 안내는 표 안 caption으로, 기준 6)")
    for i, t in enumerate(p.tables, 1):
        m = re.search(r"min-width\s*:\s*(\d+)", t["style"])
        # min-width는 table이나 감싼 div 어느 쪽에도 올 수 있어 전체도 센다
    mins = [int(x) for x in re.findall(r"min-width\s*:\s*(\d+)\s*px", raw)]
    if mins and max(mins) > 400: fatal.append(f"표 min-width {max(mins)}px(400px 이하여야 모바일에서 안 깨짐)")

    # 링크
    ext, intl = [], []
    for h in p.links:
        if h.startswith("#") or h.startswith("mailto:"): continue
        m = re.match(r"https?://([^/]+)(/.*)?$", h)
        if m:
            host, path = m.group(1).lower(), (m.group(2) or "")
            if SITE in host: intl.append(h)
            elif path.strip("/") == "" : continue          # 기관 홈 링크는 출처로 안 침
            else: ext.append(h)
        elif h.startswith("/"): intl.append(h)
    info.append(f"외부 딥링크 {len(set(ext))}개 · 사이트 안 링크 {len(set(intl))}개")
    if len(set(ext)) < 3: fatal.append(f"원문 딥링크 {len(set(ext))}개(3개 이상, 기관 홈 제외)")
    if len(set(intl)) < 2: fatal.append(f"사이트 안 링크 {len(set(intl))}개(2개 이상)")

    # 그림
    good = [i for i in p.imgs if (i.get("alt") or "").strip()]
    noalt = len(p.imgs) - len(good)
    info.append(f"그림 img {len(p.imgs)}개(alt 있음 {len(good)}) · svg {p.svgs}개")
    if not good and not p.svgs: fatal.append("본문 그림 없음 또는 alt 없음(그림 1장 이상 + alt 문장)")
    if noalt: fatal.append(f"alt 없는 img {noalt}개")
    for i in good:
        if len(i["alt"].strip()) < 10: warn.append("alt가 너무 짧음(문장으로)")
    if re.search(r"AI\s*(생성|제작|이미지)|synthid|c2pa", raw, re.I): fatal.append("AI 표시·메타데이터 흔적")

    # 요약 장치·목차·FAQ
    nsum = len(re.findall(r"핵심\s*요약|한눈에\s*(비교|보기)|3줄\s*(정리|요약)|세\s*줄\s*(정리|요약)|한\s*줄\s*요약|TL;?DR", alltext, re.I))
    n_h2 = sum(1 for t, _ in p.h if t == "h2")
    info.append(f"요약 장치 {nsum}개 · 소제목(h2) {n_h2}개")
    if nsum > 1: fatal.append(f"요약 장치 {nsum}개(한 글에 하나까지)")
    if re.search(r"목\s*차", " ".join(x for _, x in p.h) + " ".join(q["text"][:6] for q in p.paras) ) or re.search(r'>\s*목차\s*<', raw):
        if n_h2 < 6: fatal.append(f"목차가 있는데 소제목 {n_h2}개(6개 이상일 때만)")
    # FAQ 정확히 3문항
    idx = [i for i, (t, x) in enumerate(p.h) if t == "h2" and re.search(r"자주\s*묻는|FAQ|Q&amp;A|Q&A", x, re.I)]
    if idx:
        i = idx[0]; q = 0
        for t, x in p.h[i + 1:]:
            if t == "h2": break
            q += 1
        info.append(f"FAQ 문항 {q}개")
        if q == 3: warn.append("FAQ가 정확히 3문항(개수 고정 의심, 실제 검색 질문만 넣기)")

    # 화살표
    arr = re.findall(r"[→←↑↓▶▷►➜➔➡⇒]|&rarr;|&larr;|&#8594;|&#x2192;", outside)
    if arr: fatal.append(f"표 밖 화살표 기호 {len(arr)}개(기준 6)")

    # 바이라인
    last = p.paras[-3:] if p.paras else []
    by = None
    for q in last:
        if re.search(r"글쓴이|저자|작성자|운영자|머니프로듀서|쓴\s*사람", q["text"]) and any(re.search(r"소개|about|profile|pages?|notice|/\d+$|^/", l or "", re.I) for l in q["links"]):
            by = q
    if not by:
        # 바이라인이 <div>·<span>일 수 있어 끝 800자도 본다
        tail = raw[-900:]
        if re.search(r"글쓴이|저자|작성자|머니프로듀서", tail) and re.search(r'<a [^>]*href="[^"]*(소개|about|profile|pages?/|notice)[^"]*"', tail, re.I): by = True
    if not by: fatal.append("글 끝 저자 바이라인 + 소개 페이지 링크 없음")

    print(f"게이트: {sys.argv[1]}  (글자 약 {len(alltext)}자)")
    for x in info: print("  ·", x)
    for x in warn: print("  경고:", x)
    for x in fatal: print("  치명:", x)
    print("결과:", "실패(치명 %d)" % len(fatal) if fatal else "통과(경고 %d)" % len(warn))
    sys.exit(1 if fatal else 0)

if __name__ == "__main__":
    main()
