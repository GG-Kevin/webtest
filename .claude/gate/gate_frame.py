#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""서치 틀 게이트 gate_frame.py — 0토큰, 표준 라이브러리만 (본사 원본, H-189 v3.1)

사용
  python3 gate_frame.py <편성표.md|설계.md|발행.html ...> [--repo <서치 레포 루트>]
          [--ledger <주제대장.tsv>] [--fp <지문_22.tsv>] [--self /N] [--recent 10] [-v]
  python3 gate_frame.py --build-fp <라이브 스냅숏 폴더>   # 지문_22.tsv를 다시 만든다

  --repo 가 없으면 이 파일 위치에서 ../../ 를 레포 루트로 본다(서치 사본 .claude/gate/ 기준).
  종료코드: 0 = 실패 0, 1 = 실패 1개 이상, 2 = 사용법 오류. 경고·기록은 종료코드에 들어가지 않는다.

판정 — 마크다운 표(편성표·설계: 칸 검색어·가제·골격·묶음, 있으면 게시일·사건키·유형·h2·원천)
  실패  검색어·가제 칸이 있는 표가 없음(틀 검사를 할 수 없으면 막는다)
  기록  골격(칸 없음·4종 밖·묶음 안 같은 골격·하루 같은 골격) — H-194(10/3 회장 「샘플은 참고, 틀로 만들지 않는다」)로 실패에서 기록으로 낮춤
  실패  쌍둥이 글 — 정규화한 질문(검색어)이 같거나 핵심 명사 집합 자카드 >= 0.6
        비교 대상: 같은 입력의 다른 줄 + 주제대장 전체(없으면 지문_22 제목·핵심어) + 원장.csv 진행분
        (승인·집필·완성·대기·라이브·보류). 숫자·연령·지역은 지우고 비교한다(본사 안 3-1).
        두 쪽 모두 사건키가 있고 서로 다르면(다른 날짜 사건) 쌍둥이로 보지 않는다(v2 B1).
  실패  번호만 다른 같은 제목(「…2」「(2)」「2편」「Part 2」) · 숫자만 바꾼 같은 제목(v3.1 반복 금지)
  h2 칸이 있으면: 번호형 h2(50% 이상)=경고(H-212로 낮춤) / 경고: 기존 글과 h2 순서가 숫자·지명만 바꾼 꼴(H-194로 실패→경고)
  실패  서브도메인 링크(moneyproducer.co.kr 의 www 밖 하위 도메인, v3.1 반복 금지)
  경고  주 일정형 11편 초과 · 하루 일정형 2편 초과 · 하루 네이버 합의 2편 미만 · 한 원천 하루 2편 초과
판정 — 발행 HTML(본문 영역: 티스토리 div.contents_style, 없으면 body, 없으면 조각 전체)
  경고  번호형 h2(「숫자.」「숫자)」로 시작하는 h2가 50% 이상 — H-212로 치명에서 낮춤)
  경고  라이브 22편 지문(지문_22.tsv)·대기 글·같이 넣은 HTML과 h2 순서가 같음(H-194로 실패→경고)
  실패  지문 0.8 이상 비슷한 글이 최근 10편 중 5편 이상(v2 B2 「4편 이하」, 추정 기준)
        최근 10편 = 같이 넣은 HTML + 발행/대기/*.html + 작업/*/발행.html(제목이 같은 사본은 한 편) + 라이브(글 번호 큰 순)
  실패  서브도메인 링크
  실패  제목이 기존 글·진행분과 쌍둥이 / 번호만 다른 같은 제목
  경고  h2 순서가 3분의 2 이상 같은 자리에서 같음
자기 자신 빼기: HTML 의 canonical(/N) 또는 --self /N 은 지문·주제대장의 같은 글을 비교에서 뺀다.
원장 줄은 작업폴더·대기파일 경로가 입력 파일과 같으면, 마크다운 줄은 묶음+편 또는 (검색어·가제)가 같으면 같은 글로 본다.
"""
import argparse
import csv
import datetime
import glob
import html
import os
import re
import sys
import unicodedata
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote

sys.dont_write_bytecode = True  # 게이트 폴더에 __pycache__ 를 남기지 않는다
HERE = os.path.dirname(os.path.abspath(__file__))
SITE = "moneyproducer.co.kr"
SKELETONS = ["날짜형", "계산형", "비교형", "절차형"]
TWIN_J = 0.6
FP_SIM = 0.8
FP_MAX = 4
# 지문 0.8 유사(v2 B2)는 추정 기준이다. 첫 2주(10/4~10/17)는 경고로 두고, 대기·라이브 분포를 본 뒤 본사가 True(실패)로 고정한다.
FP_FATAL = False
LIVE_STATES = {"승인", "집필", "완성", "대기", "라이브", "보류"}
F_EVENT = "사건키.tsv"
F_SYN = "동의어.tsv"
# 편성표 파일(게시일 칸 필수): 작업/<D>/편성표.md · 작업/편성/주간_*.md · 이름에 「편성표」가 든 파일
SCHEDULE_NAME = re.compile(r"편성표|^주간_")

# ───────────────────────── HTML 트리(공용: overlap21.py 가 가져다 쓴다) ─────────────────────────
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param",
        "source", "track", "wbr"}
BLOCK = {"p", "div", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6", "table", "tr", "td", "th",
         "thead", "tbody", "blockquote", "section", "article", "aside", "header", "footer", "nav",
         "figure", "figcaption", "caption", "pre", "dl", "dt", "dd", "br", "hr"}
SKIP = {"script", "style", "noscript", "template"}


class Node:
    __slots__ = ("tag", "attrs", "kids", "parent")

    def __init__(self, tag, attrs=None, parent=None):
        self.tag = tag
        self.attrs = {k: (v if v is not None else "") for k, v in (attrs or {}).items()}
        self.kids = []
        self.parent = parent

    def iter(self):
        yield self
        for k in self.kids:
            if isinstance(k, Node):
                yield from k.iter()

    def cls(self):
        return (self.attrs.get("class") or "").split()

    def ancestors(self):
        x = self.parent
        while x is not None:
            yield x
            x = x.parent


class _TreeBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root")
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        n = Node(tag, dict(attrs), self.cur)
        self.cur.kids.append(n)
        if tag not in VOID:
            self.cur = n

    def handle_startendtag(self, tag, attrs):
        self.cur.kids.append(Node(tag, dict(attrs), self.cur))

    def handle_endtag(self, tag):
        x = self.cur
        while x is not None and x.tag != tag:
            x = x.parent
        if x is not None and x.parent is not None:
            self.cur = x.parent

    def handle_data(self, data):
        self.cur.kids.append(data)


def parse_html(raw):
    tb = _TreeBuilder()
    tb.feed(raw)
    tb.close()
    return tb.root


def find_body(root):
    """티스토리 본문(바깥 div.contents_style) → body → 조각 전체."""
    for n in root.iter():
        if n.tag == "div" and "contents_style" in n.cls():
            return n
    for n in root.iter():
        if n.tag == "body":
            return n
    return root


def text_of(node, skip=None):
    """노드의 보이는 글자. 블록 경계는 공백 하나. skip(노드) 가 참이면 그 노드는 뺀다."""
    out = []

    def rec(x):
        for k in x.kids:
            if isinstance(k, str):
                out.append(k)
                continue
            if k.tag in SKIP or (skip and skip(k)):
                continue
            blk = k.tag in BLOCK
            if blk:
                out.append(" ")
            rec(k)
            if blk:
                out.append(" ")

    if isinstance(node, Node):
        rec(node)
    return re.sub(r"\s+", " ", "".join(out)).strip()


def html_title(raw, root):
    m = re.search(r"<!--\s*제목\s*:\s*(.+?)\s*-->", raw)
    if m:
        return html.unescape(m.group(1)).strip()
    for n in root.iter():
        if n.tag == "div" and "post-cover" in n.cls():
            for k in n.iter():
                if k.tag == "h1":
                    return text_of(k)
    for n in root.iter():
        if n.tag == "title":
            t = text_of(n)
            return re.sub(r"\s*::\s*머니프로듀서\s*$", "", t)
    for n in root.iter():
        if n.tag == "h1":
            return text_of(n)
    return None


def safe_urlparse(h):
    """깨진 주소(「http://[bad-ipv6/18」 등)에 ValueError 를 내지 않고 None 을 돌려준다."""
    try:
        return urlparse(h)
    except ValueError:
        return None


def canonical_id(raw):
    m = re.search(r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"', raw) or \
        re.search(r'<meta[^>]+property="og:url"[^>]+content="([^"]+)"', raw)
    if not m:
        return None
    p = safe_urlparse(html.unescape(m.group(1)))
    if p is None:
        return None
    mm = re.match(r"^/(\d+)$", p.path or "")
    return "/" + mm.group(1) if mm and SITE in (p.netloc or "") else None


# 번호형 h2(v2 B2 + 검증 반영): NFKC 를 거친 뒤 판정한다. 「1.」「1)」「(1)」「１．」「①」「⑴」「❶」「Ⅰ」「1단계」「2번째」
# 「Step 1」「Part 2」「제1장」「첫째」「두 번째」를 번호로 본다. 소수(「3.3% 원천징수는…」)는 번호가 아니다.
# gate_search.py(서치 도구/)에 같은 규칙을 복사해 둔다 — 바꾸면 둘 다 고친다.
NUM_RAW = re.compile(r"^\s*[①-⓿❶-➓㉑-㉟㊱-㊿Ⅰ-ⅿ]")
NUM_H2 = re.compile(
    r"^\s*(?:\d{1,2}\s*[.)](?!\d)"
    r"|[(\[]\s*\d{1,2}\s*[)\]]"
    r"|\d{1,2}\s*(?:단계|번째)"
    r"|(?:step|part|chapter|no\.?)\s*\d{1,2}(?!\d)"
    r"|제\s*\d{1,2}\s*(?:장|부|절|편|단계)"
    r"|(?:첫|두|둘|세|셋|네|넷|다섯|여섯|일곱|여덟|아홉|열)\s*(?:째|번째)(?![가-힣]))", re.I)


def is_numbered(h):
    h = h or ""
    return bool(NUM_RAW.match(h) or NUM_H2.match(unicodedata.normalize("NFKC", h)))


def strip_number(h):
    h = h or ""
    m = NUM_RAW.match(h)
    if m:
        h = h[m.end():]
    h = unicodedata.normalize("NFKC", h)
    return NUM_H2.sub("", h, count=1)


def numbered_ratio(h2s):
    if not h2s:
        return 0, 0.0
    n = sum(1 for h in h2s if is_numbered(h))
    return n, n / len(h2s)


URL_RX = re.compile(r"(?i)(?:https?:)?//[^\s\"'<>)\]|]+")
# 스킴 없는 하위 도메인(「tax.moneyproducer.co.kr/18」 · 「[글](tax.moneyproducer.co.kr/20)」)도 찾는다(검증 반영)
SUBHOST_RX = re.compile(r"(?i)(?<![a-z0-9.\-@])((?:[a-z0-9-]+\.)+moneyproducer\.co\.kr)(/[^\s\"'<>)\]|]*)?")


def subdomain_links(text_or_hrefs):
    """moneyproducer.co.kr 의 www 밖 하위 도메인으로 가는 주소(스킴이 없어도 찾는다)."""
    bad, seen = [], set()

    def add(u, host):
        host = host.lower()
        if host.endswith("." + SITE) and host != "www." + SITE and u not in seen:
            seen.add(u)
            bad.append(u)

    if isinstance(text_or_hrefs, list):
        for h in text_or_hrefs:
            h = html.unescape(h or "").strip()
            if h.startswith("//"):
                h = "https:" + h
            p = safe_urlparse(h)
            if p is not None and p.hostname:
                add(h, p.hostname)
            else:
                m = SUBHOST_RX.match(h)
                if m:
                    add(h, m.group(1))
        return bad
    text = html.unescape(text_or_hrefs or "")
    spans = []
    for m in URL_RX.finditer(text):
        h = m.group(0)
        spans.append(m.span())
        full = "https:" + h if h.startswith("//") else h
        p = safe_urlparse(full)
        if p is not None and p.hostname:
            add(full, p.hostname)
    for m in SUBHOST_RX.finditer(text):
        if any(a <= m.start() < b for a, b in spans):
            continue
        add(m.group(0), m.group(1))
    return bad


# ───────────────────────── 낱말 정규화(쌍둥이) ─────────────────────────
REGIONS = {"서울", "서울시", "서울특별시", "부산", "부산시", "부산광역시", "대구", "대구시", "인천", "인천시",
           "광주", "광주시", "대전", "대전시", "울산", "울산시", "세종", "세종시", "경기도", "강원", "강원도",
           "충북", "충남", "충청북도", "충청남도", "전북", "전남", "전라북도", "전라남도", "경북", "경남",
           "경상북도", "경상남도", "제주", "제주도", "수도권", "비수도권", "광역시"}
STOP = {"방법", "정리", "총정리", "한눈에", "이유", "뜻", "의미", "언제", "얼마", "얼마나", "얼마까지", "어떻게",
        "무엇", "무엇이", "기준", "계산", "계산법", "계산기", "조건", "대상", "신청", "일정", "날짜", "기간",
        "가능", "정말", "완벽", "가이드", "확인", "꿀팁", "최신", "올해", "내년", "작년", "지금", "이번", "다음",
        "모든", "전부", "차이", "비교", "정보", "안내", "한표", "우리", "가장", "최대", "최소", "금액", "어디서",
        "누구", "vs", "및", "또는", "그리고", "the", "a", "of", "총", "알아보기", "알아보자", "체크", "핵심",
        "필수", "주의", "주의점", "요약", "표", "예시", "사례", "있나", "없나", "되나", "하나", "받는", "받을",
        "내는", "내야", "드는", "되는", "하는", "있는", "없는", "없이", "넘으면", "넘는", "바뀌나", "바뀌는",
        "달라지나", "달라지는", "몇", "얼만큼", "얼마큼", "왜", "뭐", "무슨", "어느", "어떤", "언제부터",
        "언제까지", "부터", "까지", "년", "월", "일", "원", "만원", "억", "억원", "기준일", "기준표"}
UNITS = re.compile(r"^(원|만원|천원|억|억원|천만원|조|세|살|대|년|년도|월|일|개|개월|편|배|회|명|건|주|분위|등급|위|"
                   r"퍼센트|프로|%|p|%p|차|호|일차|시|분)?$")
PROTECT_END = ("나이", "차이", "한도", "제도", "주가", "물가", "결과", "효과", "이자", "단가", "시가", "종가", "원가",
               "평가", "추가", "증가", "부가", "국가", "정도", "용도", "연도", "년도", "의도", "속도", "지도", "가이",
               "부과", "과세", "비과", "대가", "할인가", "공시가", "기준가", "매매가", "분양가", "정가", "호가", "상한가",
               "하한가", "체크카드", "카드", "회사", "보험료", "수수료", "세율", "소득세", "증여세", "상속세", "취득세",
               "재산세", "양도세", "주민세", "지방세", "부가세", "종부세", "인지세")
PARTICLES = sorted(["에서는", "으로는", "에게서", "에서도", "이라는", "이라고", "에서", "으로", "까지", "부터", "이란",
                    "에는", "에도", "와의", "과의", "이나", "보다", "처럼", "만큼", "에게", "한테", "이면", "라면",
                    "은", "는", "이", "가", "을", "를", "의", "에", "로", "와", "과", "도", "만", "란", "면"],
                   key=len, reverse=True)
VERBAL = re.compile(r"(습니다|입니다|합니다|됩니다|나요|까요|는지|을까|할까|인가|인지|으면|하면|되면|면서|는데|지만|"
                    r"했다면|한다면|된다면|했나|하나요|되나요|일까|일까요|이다|한다|된다|있다|없다|봤다|보니)$")


def nfkc(s):
    return unicodedata.normalize("NFKC", s or "").lower()


def _strip_particle(t):
    if any(t.endswith(p) for p in PROTECT_END):
        return t
    for p in PARTICLES:
        if t.endswith(p) and len(t) - len(p) >= 2:
            return t[: -len(p)]
    return t


def raw_tokens(s):
    s = nfkc(s)
    s = re.sub(r"[「」『』\"'“”‘’()\[\]{}<>|:;,.!?·・/\\~—–\-_=+*#@&^`]", " ", s)
    out = []
    for t in s.split():
        if VERBAL.search(t) and not any(t.endswith(p) for p in PROTECT_END):
            continue
        t = _strip_particle(t)
        if re.search(r"\d", t):
            rest = re.sub(r"[\d.,%]+", "", t)
            if UNITS.match(rest):
                continue
            # 「상위10%」→「상위」, 「30대」→ 버림(UNITS), 「2026년」→ 버림
            t = _strip_particle(rest)
        if t in REGIONS or t in STOP:
            continue
        if re.fullmatch(r"[가-힣]", t):
            continue
        if not t or re.fullmatch(r"[a-z]", t):
            continue
        out.append(t)
    return out


def build_vocab(texts):
    v = set()
    for s in texts:
        for t in raw_tokens(s):
            if 2 <= len(t) <= 6:
                v.add(t)
    return v


def _segment(t, vocab):
    """vocab 낱말(2자 이상)로 남김없이 쪼개지면 쪼갠다(「결혼증여세」→「결혼」「증여세」)."""
    n = len(t)
    if n < 4:
        return [t]
    best = [None] * (n + 1)
    best[0] = []
    for i in range(n):
        if best[i] is None:
            continue
        for j in range(i + 2, n + 1):
            w = t[i:j]
            if w in vocab and w != t and (best[j] is None or len(best[j]) > len(best[i]) + 1):
                best[j] = best[i] + [w]
    return best[n] if best[n] and len(best[n]) >= 2 else [t]


def nouns(s, vocab=None):
    out = set()
    for t in raw_tokens(s):
        for w in (_segment(t, vocab) if vocab else [t]):
            if w not in STOP and w not in REGIONS:
                out.add(w)
    return out


def qnorm(s):
    s = nfkc(s)
    s = re.sub(r"\d+", "", s)
    s = re.sub(r"[^0-9a-z가-힣]", "", s)
    for r in sorted(REGIONS, key=len, reverse=True):
        s = s.replace(r, "")
    return s


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


SERIES_TAIL = re.compile(r"(?i)\s*[\(\[]?\s*(?:part|pt|vol|ep|시즌|제)?\s*\.?\s*(?:\d{1,2}|[①-⑳]|[ⅰ-ⅻⅠ-Ⅻ])\s*"
                         r"(?:편|부|탄|회|화|장)?\s*[\)\]]?\s*$")
SERIES_HEAD = re.compile(r"^\s*[\(\[]?\s*(?:\d{1,2}|[①-⑳])\s*(?:편|부|탄)?\s*[\)\].]\s*")
SERIES_STRONG = re.compile(r"(?i)(\d{1,2}\s*(편|부|탄)\s*$|part\s*\d|vol\.?\s*\d|[\(\[]\s*\d{1,2}\s*[\)\]]\s*$|[①-⑳]\s*$|"
                           r"(상|하|중)편\s*$)")


def series_base(title):
    t = nfkc(title)
    t2 = SERIES_TAIL.sub("", t)
    t2 = SERIES_HEAD.sub("", t2)
    t2 = re.sub(r"(상|하|중)편\s*$", "", t2)
    return re.sub(r"[^0-9a-z가-힣]", "", t2), (t2 != t)


def digitless(title):
    return re.sub(r"[^a-z가-힣]", "", re.sub(r"\d+", "", nfkc(title)))


# ───────────────────────── h2 지문 ─────────────────────────
def h2_norm(h):
    h = nfkc(strip_number(h))
    toks = []
    for t in re.sub(r"[^0-9a-z가-힣\s]", " ", h).split():
        b = _strip_particle(t)
        if b in REGIONS or t in REGIONS:
            toks.append("@")
        else:
            toks.append(re.sub(r"\d+", "#", t))
    return "".join(toks)


# h2 끝맺음 유형(기록용·첫/끝 h2 유형에 씀). 물음 끝맺음: 인가요·가요·는가·세나·되나 … (검증 반영: 「…인가요」가 S, 「…세나」가 D 로 갈렸음)
Q_END = re.compile(r"(\?|나요|까요|가요|죠|[는은인던]가|[을를일할될볼]까|"
                   r"(?:되|하|있|없|맞|오|가|드|받|내|세|크|많|적|늘|줄|바뀌|달라지|나오|들어오|붙|빠지|남|쓰|걸리|생기|오르|내리|다르)나|"
                   r"[는인]지|얼마|언제|무엇|어떻게|왜|어디|누구|몇|얼마일까|얼마인가|다를까|뭔가|뭘까)\s*$")


def h2_type(h):
    """끝맺음 유형: N 번호 · Q 물음 · D 숫자 든 서술 · S 서술."""
    s = nfkc(h).strip()
    if is_numbered(h):
        return "N"
    if Q_END.search(s):
        return "Q"
    if re.search(r"\d", s):
        return "D"
    return "S"


WH_HEAD = ("왜", "언제", "어디", "얼마", "무엇", "무얼", "뭐", "뭘", "누구", "누가", "어떻게", "어떤", "몇", "어느", "무슨")
HEAD_PARTICLE = re.compile(r"(은|는|이|가|을|를|의|에|에서|으로|로|와|과|도|만|이면|면|이라면|라면)$")


def h2_head_type(h):
    """v2 B2 「h2 첫 어절 유형」: N 번호 · W 의문사로 시작 · D 숫자로 시작 · P 따옴표·괄호로 시작 · J 조사 붙은 낱말로 시작 · K 그 밖(명사 등)."""
    if is_numbered(h):
        return "N"
    s = nfkc(h).strip()
    first = s.split()[0] if s.split() else ""
    if not first:
        return "K"
    if re.match(r"[「『\"'“‘(\[<《〈]", first):
        return "P"
    if re.match(r"\d", first):
        return "D"
    if any(first.startswith(w) for w in WH_HEAD):
        return "W"
    if len(first) >= 2 and HEAD_PARTICLE.search(first) and not any(first.endswith(p) for p in PROTECT_END):
        return "J"
    return "K"


def h2_frames(h2s):
    """h2 틀(주제어만 바꾼 자동 생성형 찾기, 경고용): 글 안 h2 절반 이상이 같은 머리 낱말(1~2어절)로 시작하면
    그 머리를 「§」로 바꾸고 바로 뒤 조사를 하나로 모은다(은/는·이/가·을/를·와/과·으로/로)."""
    rows = [re.sub(r"[^0-9a-z가-힣\s]", " ", nfkc(strip_number(h))).split() for h in h2s]
    if len(rows) < 3:
        return None
    cand = {}
    for toks in rows:
        for n in (2, 1):
            if len(toks) >= n:
                head = " ".join(toks[:n - 1] + [_strip_particle(toks[n - 1])])
                cand[head] = cand.get(head, 0) + 1
    best = max(((c, len(k), k) for k, c in cand.items() if len(k) >= 2), default=None)
    if not best or best[0] * 2 < len(rows):
        return None
    head = best[2]
    out = []
    for toks in rows:
        t = " ".join(toks)
        if t.startswith(head):
            rest = t[len(head):]
            rest = re.sub(r"^(은|는)", "은", rest)
            rest = re.sub(r"^(이|가)(?=\s|$)", "이", rest)
            rest = re.sub(r"^(을|를)", "을", rest)
            rest = re.sub(r"^(와|과)", "와", rest)
            rest = re.sub(r"^(으로|로)", "로", rest)
            t = "§" + rest
        out.append(re.sub(r"\d+", "#", t.replace(" ", "")))
    return out


SUMMARY = re.compile(r"핵심\s*요약|한눈에\s*(비교|보기)|3줄\s*(정리|요약)|세\s*줄\s*(정리|요약)|한\s*줄\s*요약|tl;?dr", re.I)


def html_fingerprint(raw):
    root = parse_html(raw)
    body = find_body(root)
    h2s = [text_of(n) for n in body.iter() if n.tag == "h2"]
    # 표 위치: 몇 번째 h2 구간에 표가 있나(0 = 첫 h2 앞)
    pos, sec = set(), 0
    for n in body.iter():
        if n.tag == "h2":
            sec += 1
        elif n.tag == "table":
            pos.add(sec)
    ext, broken = set(), []
    for n in body.iter():
        if n.tag == "a":
            h = (n.attrs.get("href") or "").strip()
            p = safe_urlparse(h)
            if p is None:
                broken.append(h)
                continue
            if p.scheme in ("http", "https") and SITE not in (p.netloc or ""):
                ext.add(h)
    nnum, ratio = numbered_ratio(h2s)
    return {
        "root": root, "body": body, "h2": h2s, "nnum": nnum, "ratio": ratio,
        "types": "".join(h2_type(h) for h in h2s), "heads": "".join(h2_head_type(h) for h in h2s), "tables": pos,
        "summary": bool(SUMMARY.search(text_of(body))), "ext": ext, "broken": broken, "frames": h2_frames(h2s),
        "hrefs": [n.attrs.get("href") or "" for n in body.iter() if n.tag == "a"],
    }


def fp_similarity(a, b):
    """v2 B2 지문 유사도(추정, 검증 반영): h2 첫 어절 유형 순서 · 첫 h2 유형 · 끝 h2 유형 · 표 위치 · 요약 상자 5칸 평균.
    「h2 수 같음」 칸은 명세에 없어 뺐다. 첫/끝 h2 유형 = 첫 어절 유형 + 끝맺음 유형."""
    s = []
    la, lb = a["heads"], b["heads"]
    m = max(len(la), len(lb)) or 1
    s.append(sum(1 for x, y in zip(la, lb) if x == y) / m)
    fa = (la[:1], a["types"][:1])
    fb = (lb[:1], b["types"][:1])
    ea = (la[-1:], a["types"][-1:])
    eb = (lb[-1:], b["types"][-1:])
    s.append(1.0 if fa == fb else 0.0)
    s.append(1.0 if ea == eb else 0.0)
    ta, tb = set(a["tables"]), set(b["tables"])
    s.append(1.0 if not ta and not tb else len(ta & tb) / len(ta | tb))
    s.append(1.0 if a["summary"] == b["summary"] else 0.0)
    return sum(s) / len(s)


# ───────────────────────── 원천 읽기 ─────────────────────────
def read_tsv(path):
    rows = []
    if not path or not os.path.exists(path):
        return rows
    with open(path, encoding="utf-8") as f:
        lines = [ln.rstrip("\n") for ln in f if ln.strip() and not ln.startswith("#")]
    if not lines:
        return rows
    head = [h.strip() for h in lines[0].split("\t")]
    for i, ln in enumerate(lines[1:], 2):
        cells = ln.split("\t")
        rows.append({h: (cells[k].strip() if k < len(cells) else "") for k, h in enumerate(head)} | {"_line": i})
    return rows


def pick(d, *names):
    for n in names:
        for k in d:
            if k is None or k == "_line":
                continue
            if re.sub(r"[\s*`_]", "", nfkc(k)) == re.sub(r"[\s*`_]", "", nfkc(n)):
                v = d[k]
                if v not in (None, ""):
                    return str(v).strip()
    return ""


def load_fp(path):
    out = []
    for r in read_tsv(path):
        h2 = [x.strip() for x in r.get("h2목록", "").split(" ‖ ") if x.strip()]
        out.append({
            "id": r.get("글", ""), "title": r.get("제목", ""), "h2": h2,
            # 유형은 h2 목록에서 다시 잰다(규칙이 바뀌어도 tsv 를 다시 만들 필요가 없게)
            "types": "".join(h2_type(h) for h in h2), "heads": "".join(h2_head_type(h) for h in h2),
            "ratio": (int(r.get("번호h2수") or 0) / max(1, int(r.get("h2수") or 1))),
            "notice": [x.strip() for x in r.get("안내문장", "").split(" ‖ ") if x.strip()],
            "tables": {int(x) for x in r.get("표위치", "").split(",") if x.strip().isdigit()},
            "summary": r.get("요약", "") == "1", "key": r.get("핵심어", ""), "event": r.get("사건키", ""),
            "_line": r["_line"],
        })
    return out


def load_ledger(path, fp_rows):
    """주제대장: 다른 영역이 만든 tsv(칸 이름은 유연하게). 없으면 지문_22 제목·핵심어."""
    rows = []
    src = "주제대장"
    if path and os.path.exists(path):
        for r in read_tsv(path):
            pid = pick(r, "글", "번호", "글번호", "id", "url", "라이브url", "주소")
            m = re.search(r"/(\d+)\b", pid) or re.match(r"^(\d+)$", pid)
            rows.append({
                "id": "/" + m.group(1) if m else "",
                "title": pick(r, "제목", "최종제목", "가제", "글 제목"),
                "key": pick(r, "핵심어", "검색어", "질문", "주제", "낱말"),
                "event": pick(r, "다루는사건키", "사건키", "사건 키", "다루는사건", "다루는 사건", "사건"),
                "state": pick(r, "상태"), "_line": r["_line"],
            })
    if not rows:
        src = "지문_22"
        rows = [{"id": f["id"], "title": f["title"], "key": f["key"], "event": f["event"], "state": "라이브",
                 "_line": f["_line"]} for f in fp_rows]
    return rows, src


WONJANG_NEED = ("묶음", "편", "검색어", "가제", "최종제목", "사건키", "상태", "작업폴더", "대기파일", "게시일")


def load_wonjang(repo):
    """→ (진행분 줄들, 경로, 모든 줄). 원장이 없으면 (None, 경로, []) — 부르는 쪽이 종료 2로 막는다."""
    path = os.path.join(repo, "운영", "원장.csv")
    rows, allrows = [], []
    if not os.path.isfile(path):
        return None, path, allrows
    with open(path, encoding="utf-8-sig", newline="") as f:
        rd = csv.DictReader(f)
        miss = [c for c in WONJANG_NEED if c not in (rd.fieldnames or [])]
        if miss:
            raise ValueError(f"원장.csv 머리에 칸 없음: {miss}({path})")
        for i, r in enumerate(rd, 2):
            r["_line"] = i
            allrows.append(r)
            if (r.get("상태") or "").strip() in LIVE_STATES:
                rows.append(r)
    return rows, path, allrows


# ───────────────────────── 사건키(일정형 예외, gate_topic 과 같은 조건) ─────────────────────────
# 날짜 토큰 — gate_topic.py DATE_RE 와 같은 식(바꾸면 둘 다 고친다)
DATE_RE = re.compile(
    r"(?<!\d)202[4-9](?!\d)(?!\s*(?:만|억|원|천|명|개|건|세대))"
    r"|(?<!\d)(?:1[0-2]|0?[1-9])\s*월"
    r"|연말(?!\s*정산)"
    r"|(?<!\d)[1-4]\s*분기|(?:이번|다음|지난|올해|내년)\s*분기|분기\s*(?:말|초)"
    r"|상반기|하반기")
EV_SEP = re.compile(r"[\s·ㆍ‧∙•・\-&/]+")
NONE_KEYS = {"", "-", "—", "–", "없음", "none", "new", "새", "새사건", "신규"}


def _flex(key):
    body = "[\\s·ㆍ‧∙•・\\-&/]*".join(re.escape(c) for c in key)
    return re.compile(body)


def load_events(d):
    """사건키.tsv·동의어.tsv(gate_topic 과 같은 파일) → {"rx": {키: 정규식}, "syn": [(정규식, 표준말)], "ok": bool}.
    파일이 없거나 깨졌으면 ok=False — 그때는 사건키 예외를 하나도 열지 않는다(fail-closed)."""
    ev = {"rx": {}, "syn": [], "ok": False, "why": ""}
    p = os.path.join(d, F_EVENT)
    if not os.path.isfile(p):
        ev["why"] = f"{F_EVENT} 없음"
        return ev
    try:
        for r in read_tsv(p):
            k = (r.get("사건키") or "").strip()
            pat = (r.get("찾는 정규식") or "").strip()
            if not k or k.lower() in NONE_KEYS or not pat:
                continue
            ev["rx"][unicodedata.normalize("NFKC", k).lower()] = re.compile(pat)
        sp = os.path.join(d, F_SYN)
        if os.path.isfile(sp):
            syn = []
            for r in read_tsv(sp):
                v = EV_SEP.sub("", nfkc(r.get("다른말", "")))
                if v:
                    syn.append((len(v), _flex(v), nfkc(r.get("표준말", ""))))
            ev["syn"] = [(rx, canon) for _, rx, canon in sorted(syn, key=lambda x: -x[0])]
        ev["ok"] = bool(ev["rx"])
    except (re.error, OSError, ValueError) as e:
        ev["why"] = f"{F_EVENT} 읽기 실패: {e}"
        ev["rx"] = {}
    return ev


def ev_flat(text, ev):
    t = nfkc(text)
    for rx, canon in ev["syn"]:
        t = rx.sub(canon, t)
    return t, EV_SEP.sub("", t)


def event_keys(keystr):
    return {unicodedata.normalize("NFKC", x).strip().lower() for x in re.split(r"[,;/·，]", keystr or "")
            if x.strip() and x.strip().lower() not in NONE_KEYS}


def events_differ(e1, t1, e2, t2, ev):
    """일정형 예외(v2 B1 「날짜가 다르면 다른 사건」)를 gate_topic 과 같은 조건으로만 연다:
    두 쪽 모두 사건키가 있고 · 키가 모두 사건키.tsv 에 있고 · 그 키의 정규식이 그쪽 문구에 맞고 ·
    그쪽 문구에 날짜 토큰이 있고 · 두 키 집합이 겹치지 않을 때. 아무 문자열 키·미등록 키는 예외를 열지 못한다."""
    if not ev or not ev.get("ok"):
        return False
    s1, s2 = event_keys(e1), event_keys(e2)
    if not s1 or not s2 or (s1 & s2):
        return False
    for keys, text in ((s1, t1), (s2, t2)):
        spaced, flat = ev_flat(text or "", ev)
        if not DATE_RE.search(spaced):
            return False
        for k in keys:
            rx = ev["rx"].get(k)
            if rx is None or not rx.search(flat):
                return False
    return True


# ───────────────────────── 마크다운 표 ─────────────────────────
COLS = {
    "q": ["검색어", "질문", "질문원문", "검색어(질문)", "키워드", "주제"],
    "title": ["가제", "제목", "최종제목", "가제목", "제목안", "구글판제목"],
    "skel": ["골격", "골격유형", "틀"],
    "bundle": ["묶음", "묶음id", "묶음번호"],
    "no": ["편", "편번호", "번호", "#"],
    "date": ["게시일", "날짜", "일자", "발행일", "게시예정일", "게시 예정일"],
    "event": ["사건키", "사건 키"],
    "kind": ["유형", "종류", "상시/일정형", "구분", "판"],
    "h2": ["h2", "소제목", "h2질문", "h2(질문)", "h2 질문"],
    "src": ["원천", "원천블로그", "원천 블로그", "합의", "합의블로그", "출처군"],
}


def _hn(s):
    return re.sub(r"[\s*`_]", "", nfkc(s))


def md_tables(text):
    lines = text.split("\n")
    i, out = 0, []
    while i < len(lines):
        if lines[i].lstrip().startswith("|") and i + 1 < len(lines) and \
                re.match(r"^\s*\|?\s*:?-{2,}", lines[i + 1].strip().lstrip("|")):
            head = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
                rows.append((j + 1, cells))
                j += 1
            out.append((i + 1, head, rows))
            i = j
        else:
            i += 1
    return out


def md_items(path):
    text = open(path, encoding="utf-8").read()
    items, notes = [], []
    for hline, head, rows in md_tables(text):
        hn = [_hn(h) for h in head]
        col = {}
        for key, names in COLS.items():
            for nm in names:
                if _hn(nm) in hn:
                    col[key] = hn.index(_hn(nm))
                    break
        if "q" not in col and "title" not in col:
            continue
        for ln, cells in rows:
            def g(k):
                return re.sub(r"\*\*|`", "", cells[col[k]]).strip() if k in col and col[k] < len(cells) else ""
            it = {k: g(k) for k in COLS}
            if not (it["q"] or it["title"]):
                continue
            it["file"], it["line"], it["has"] = path, ln, set(col)
            it["cells"] = " | ".join(cells)
            items.append(it)
    return items, text


def date_key(s):
    s = nfkc(s)
    m = re.search(r"(20\d\d)[-./년\s]+(\d{1,2})[-./월\s]+(\d{1,2})", s)
    if m:
        return int(m.group(1)), int(m.group(2)), int(m.group(3))
    m = re.search(r"(\d{1,2})\s*[/.월-]\s*(\d{1,2})", s)
    if m:
        return 2026, int(m.group(1)), int(m.group(2))
    return None


def skel_name(s):
    s = re.sub(r"\s", "", s)
    for k in SKELETONS:
        if s == k or s == k[:-1]:
            return k
    return None


# ───────────────────────── 검사 ─────────────────────────
class Report:
    def __init__(self):
        self.fail, self.warn, self.note = [], [], []

    def f(self, what, ref):
        self.fail.append(f"실패: {what} ← {ref}")

    def w(self, what, ref):
        self.warn.append(f"경고: {what} ← {ref}")

    def n(self, what, ref=None):
        self.note.append(f"기록: {what}" + (f" ← {ref}" if ref else ""))


def ref_md(it):
    return f"{os.path.basename(it['file'])} 줄{it['line']}"


def tkey(s):
    """제목 같음 비교용: NFKC·소문자·글자와 숫자만."""
    return re.sub(r"[^0-9a-z가-힣]", "", nfkc(s or ""))


def same_item(a, b):
    """편성표와 설계를 같이 넣었을 때만 같은 글로 합친다: 다른 파일 · 같은 묶음+편(검증 반영 — 검색어·가제만 같은 줄은 합치지 않는다)."""
    return bool(a["file"] != b["file"] and a.get("bundle") and a.get("no")
                and a["bundle"] == b.get("bundle") and a["no"] == b.get("no"))


def item_text(it):
    return " ".join(x for x in (it.get("q", ""), it.get("title", "")) if x)


def twin_check(a_q, a_title, a_event, b_q, b_title, b_event, vocab, ev=None):
    """쌍둥이면 (이유 문자열) 아니면 None. 사건키 예외는 events_differ(gate_topic 과 같은 조건)일 때만."""
    if events_differ(a_event, f"{a_q} {a_title}", b_event, f"{b_q} {b_title}", ev):
        return None
    if a_q and b_q:
        qa, qb = qnorm(a_q), qnorm(b_q)
        if qa and qa == qb:
            return f"같은 질문 「{a_q}」=「{b_q}」"
        ja = jaccard(nouns(a_q, vocab), nouns(b_q, vocab))
        if ja >= TWIN_J:
            return f"검색어 핵심 명사 자카드 {ja:.2f} 「{a_q}」≈「{b_q}」"
    if a_title and b_title:
        if qnorm(a_title) and qnorm(a_title) == qnorm(b_title):
            return f"제목이 숫자·지역만 다름 「{a_title}」=「{b_title}」"
        jt = jaccard(nouns(a_title, vocab), nouns(b_title, vocab))
        if jt >= TWIN_J:
            return f"제목 핵심 명사 자카드 {jt:.2f} 「{a_title}」≈「{b_title}」"
    if a_q and b_title and not b_q:
        jx = jaccard(nouns(a_q, vocab), nouns(b_title, vocab))
        if jx >= TWIN_J:
            return f"검색어·제목 핵심 명사 자카드 {jx:.2f} 「{a_q}」≈「{b_title}」"
    return None


def title_series_check(t1, e1, t2, e2, ev=None):
    if not t1 or not t2:
        return None
    b1, m1 = series_base(t1)
    b2, m2 = series_base(t2)
    if (m1 or m2) and b1 and b1 == b2 and nfkc(t1) != nfkc(t2):
        return f"번호만 다른 같은 제목 「{t1}」·「{t2}」"
    d1, d2 = digitless(t1), digitless(t2)
    if d1 and d1 == d2 and nfkc(t1) != nfkc(t2):
        if re.findall(r"\d+", nfkc(t1)) == re.findall(r"\d+", nfkc(t2)):
            return f"띄어쓰기·기호만 다른 같은 제목 「{t1}」·「{t2}」"
        if not events_differ(e1, t1, e2, t2, ev):
            return f"숫자만 바꾼 같은 제목 「{t1}」·「{t2}」"
    if nfkc(t1).strip() == nfkc(t2).strip():
        return f"같은 제목 「{t1}」"
    return None


def is_schedule_file(path):
    base = os.path.basename(path)
    parts = os.path.realpath(path).replace("\\", "/").split("/")
    return bool(SCHEDULE_NAME.search(base) or ("편성" in parts[:-1] and base.startswith("주간_")))


def wonjang_self(it, W):
    """원장 자기 줄(검증 반영): 묶음+편이 같고 · 검색어 정규화 값이 같고 · 가제가 원장 가제나 최종제목과 같고 ·
    게시일이 둘 다 있으면 같을 때만. → (자기 줄인가, 묶음·편만 같은가)"""
    same_bn = bool(it.get("bundle") and it.get("no") and it["bundle"] == (W.get("묶음") or "").strip()
                   and it["no"] == (W.get("편") or "").strip())
    if not same_bn:
        return False, False
    ok = qnorm(it.get("q", "")) == qnorm(W.get("검색어", "")) and qnorm(it.get("q", "")) != ""
    if ok and it.get("title"):
        ok = tkey(it["title"]) in {tkey(W.get("가제", "")), tkey(W.get("최종제목", ""))} - {""}
    if ok and it.get("date") and (W.get("게시일") or "").strip():
        ok = date_key(it["date"]) == date_key(W.get("게시일", ""))
    return ok, not ok


def check_md(items, texts, ctx, rep):
    vocab, ev = ctx["vocab"], ctx["events"]
    # 같은 파일 안 같은 묶음+편 두 줄은 막는다(한 묶음·편 = 한 글)
    seen_bn = {}
    for it in items:
        if it.get("bundle") and it.get("no"):
            k = (it["file"], it["bundle"], it["no"])
            if k in seen_bn:
                rep.f(f"같은 묶음·편 두 줄 — 묶음 {it['bundle']} 편 {it['no']}(한 묶음·편은 한 글)",
                      f"{ref_md(seen_bn[k])} · {ref_md(it)}")
            else:
                seen_bn[k] = it
    # 편성표 + 설계를 같이 넣은 같은 글(다른 파일 · 같은 묶음+편)은 한 번만 센다. 검색어가 다르면 불일치로 막는다
    uniq = []
    for it in items:
        twin = next((u for u in uniq if same_item(it, u)), None)
        if twin is None:
            uniq.append(it)
            continue
        if it.get("q") and twin.get("q") and qnorm(it["q"]) != qnorm(twin["q"]):
            rep.f(f"편성표·설계 불일치 — 묶음 {it['bundle']} 편 {it['no']}의 검색어가 다름 「{twin['q']}」·「{it['q']}」",
                  f"{ref_md(twin)} · {ref_md(it)}")
        for k in ("skel", "date", "event", "kind", "h2", "src", "title", "q"):
            if not twin.get(k) and it.get(k):
                twin[k] = it[k]
        twin["has"] = twin["has"] | it["has"]

    # 골격
    for it in uniq:
        if "skel" not in it["has"]:
            rep.n(f"골격 칸 없음(참고 — 골격은 설계자·작가가 정한다, H-194) 「{it['q'] or it['title']}」", ref_md(it))
            continue
        k = skel_name(it["skel"])
        if not k:
            rep.n(f"골격 「{it['skel'] or '빈칸'}」 — 4종 밖(참고, H-194)", ref_md(it))
        it["sk"] = k
    # 묶음 안 같은 골격 0
    byb = {}
    for it in uniq:
        if it.get("sk") and it.get("bundle"):
            byb.setdefault(it["bundle"], []).append(it)
    for b, lst in byb.items():
        seen = {}
        for it in lst:
            seen.setdefault(it["sk"], []).append(it)
        for sk, xs in seen.items():
            if len(xs) > 1:
                rep.n(f"묶음 {b} 안 같은 골격 {sk} {len(xs)}편(참고, H-194 — " + ", ".join("줄" + str(x["line"]) for x in xs) + ")",
                      ref_md(xs[0]))
    # 편성표 파일은 게시일 칸이 있어야 한다(검증 반영 — 칸을 빼면 하루 골격 상한을 피할 수 있었음)
    for path in {it["file"] for it in items}:
        if not is_schedule_file(path):
            continue
        rows = [it for it in items if it["file"] == path]
        if not any("date" in it["has"] for it in rows):
            rep.f("편성표인데 게시일 칸 없음(승인 만료·일정형 비율을 셀 수 없음)", os.path.basename(path))
            continue
        for it in rows:
            if not date_key(it.get("date", "")):
                rep.f(f"편성표 게시일 빈칸·읽을 수 없음 「{it.get('date') or '빈칸'}」", ref_md(it))
    # 하루 같은 골격 2편 이하
    has_date = any(it.get("date") for it in uniq)
    if not has_date:
        rep.n("게시일 칸 없음 — 설계 파일이면 그대로 둔다")
    byd = {}
    for it in uniq:
        dk = date_key(it.get("date", ""))
        if dk:
            byd.setdefault(dk, []).append(it)
    for dk, lst in sorted(byd.items()):
        cnt = {}
        for it in lst:
            if it.get("sk"):
                cnt.setdefault(it["sk"], []).append(it)
        for sk, xs in cnt.items():
            if len(xs) > 2:
                rep.n(f"{dk[1]}/{dk[2]} 같은 골격 {sk} {len(xs)}편(참고, H-194)", ref_md(xs[0]))
        kinds = [it for it in lst if "일정" in it.get("kind", "")]
        if len(kinds) > 2:
            rep.w(f"{dk[1]}/{dk[2]} 일정형 {len(kinds)}편(기본 하루 1, 2편인 날은 주 합계 안에서만)", ref_md(kinds[0]))
        if any("src" in it["has"] for it in lst):
            nav = [it for it in lst if re.search(r"네이버|합의|\d+\s*곳", it.get("src", ""))]
            if len(lst) >= 4 and len(nav) < 2:
                rep.w(f"{dk[1]}/{dk[2]} 네이버 합의 질문 {len(nav)}편(하루 4편 중 2편 이상, 못 채우면 05:20 승인 줄에 이유)",
                      ref_md(lst[0]))
            per = {}
            for it in lst:
                for blog in re.findall(r"[A-Za-z0-9_\-]{3,}|[가-힣]{2,}", it.get("src", "")):
                    if blog in ("네이버", "합의", "구글", "자동완성", "달력"):
                        continue
                    per.setdefault(blog, []).append(it)
            for blog, xs in per.items():
                if len(xs) > 2:
                    rep.w(f"{dk[1]}/{dk[2]} 한 원천 「{blog}」에서 {len(xs)}편(하루 2편까지)", ref_md(xs[0]))
    # 주 일정형 11편 이하
    byw = {}
    for it in uniq:
        dk = date_key(it.get("date", ""))
        if dk and "일정" in it.get("kind", ""):
            try:
                wk = datetime.date(*dk).isocalendar()[:2]
            except ValueError:
                continue
            byw.setdefault(wk, []).append(it)
    for wk, xs in byw.items():
        if len(xs) > 11:
            rep.w(f"{wk[0]}년 {wk[1]}주 일정형 {len(xs)}편(주 28편 중 11편 이하)", ref_md(xs[0]))

    # 쌍둥이 — 입력 안(묶음·게시일이 달라도 검색어·가제가 같으면 「같은 질문」으로 실패)
    for i in range(len(uniq)):
        for j in range(i + 1, len(uniq)):
            a, b = uniq[i], uniq[j]
            r = twin_check(a["q"], a["title"], a["event"], b["q"], b["title"], b["event"], vocab, ev)
            if r:
                rep.f(f"쌍둥이 글 — {r}", f"{ref_md(a)} · {ref_md(b)}")
            r = title_series_check(a["title"], a["event"], b["title"], b["event"], ev)
            if r:
                rep.f(f"반복 금지 — {r}", f"{ref_md(a)} · {ref_md(b)}")
    # 쌍둥이 — 주제대장(핵심어는 「쉼표로 나눈 주제 문구 목록」이라 문구마다 따로 맞댄다 + 제목 대 제목)
    for it in uniq:
        for L in ctx["ledger"]:
            r = None
            if not events_differ(it["event"], item_text(it), L["event"], f"{L['key']} {L['title']}", ev):
                for kw in [k.strip() for k in re.split(r"[,，]", L["key"] or "") if k.strip()]:
                    r = twin_check(it["q"], "", "", kw, "", "", vocab)
                    if r:
                        break
                if not r:
                    r = twin_check("", it["title"], "", "", L["title"], "", vocab)
            if r:
                rep.f(f"쌍둥이 글 — {r}", f"{ctx['ledger_src']} {L['id'] or '줄' + str(L['_line'])} ({ref_md(it)})")
            r = title_series_check(it["title"], it["event"], L["title"], L["event"], ev)
            if r:
                rep.f(f"반복 금지 — {r}", f"{ctx['ledger_src']} {L['id'] or '줄' + str(L['_line'])} ({ref_md(it)})")
    # 쌍둥이 — 원장 진행분(자기 줄 = 묶음+편 · 검색어 · 가제 · 게시일이 모두 같은 줄)
    for it in uniq:
        for W in ctx["wonjang"]:
            wq, wt = W.get("검색어", ""), W.get("최종제목") or W.get("가제", "")
            mine, reused = wonjang_self(it, W)
            if mine:
                continue
            if reused:
                rep.f(f"원장 줄{W['_line']}과 묶음·편이 같은데 검색어·가제·게시일이 다름(묶음 ID 재사용 또는 원장 미갱신 — "
                      f"같은 글이면 원장을 고치고, 새 글이면 새 묶음 ID)", f"원장 줄{W['_line']} ({ref_md(it)})")
            r = twin_check(it["q"], it["title"], it["event"], wq, wt, W.get("사건키", ""), vocab, ev)
            if r:
                rep.f(f"쌍둥이 글 — {r}", f"원장 줄{W['_line']} ({ref_md(it)})")
            r = title_series_check(it["title"], it["event"], wt, W.get("사건키", ""), ev)
            if r:
                rep.f(f"반복 금지 — {r}", f"원장 줄{W['_line']} ({ref_md(it)})")
    # 연재 표시만 있고 짝이 없는 제목
    for it in uniq:
        if it["title"] and SERIES_STRONG.search(nfkc(it["title"])):
            rep.w(f"연재 번호 표시 「{it['title']}」(한 주제 한 편)", ref_md(it))
    # h2 칸
    for it in uniq:
        if it.get("h2"):
            hs = [x.strip() for x in re.split(r"\s+/\s+|<br\s*/?>|\s‖\s", it["h2"]) if x.strip()]
            n, ratio = numbered_ratio(hs)
            if hs and ratio >= 0.5:
                rep.w(f"번호형 h2 {n}/{len(hs)}(참고 — H-212로 치명에서 낮춤)", ref_md(it))
            seq = [h2_norm(h) for h in hs]
            for F in ctx["fp"]:
                if len(hs) >= 3 and seq == [h2_norm(h) for h in F["h2"]]:
                    rep.w("자동 생성형 — h2 순서가 기존 글과 같음(숫자·지명만 다름)", f"지문 {F['id']} ({ref_md(it)})")
            it["_seq"] = seq
    hs_items = [it for it in uniq if it.get("_seq") and len(it["_seq"]) >= 3]
    for i in range(len(hs_items)):
        for j in range(i + 1, len(hs_items)):
            if hs_items[i]["_seq"] == hs_items[j]["_seq"]:
                rep.w("자동 생성형 — 두 글의 h2 순서가 같음(숫자·지명만 다름)", f"{ref_md(hs_items[i])} · {ref_md(hs_items[j])}")
    # 서브도메인(스킴 없는 주소 포함)
    for path, text in texts:
        for u in subdomain_links(text):
            k = text.find(u)
            if k < 0:
                k = text.find(u.split("//", 1)[-1])
            ln = text[:k].count("\n") + 1 if k >= 0 else 0
            rep.f(f"서브도메인 링크 {u}", f"{os.path.basename(path)} 줄{ln}")


def wonjang_mine(path, ctx):
    """이 HTML 파일이 원장의 어느 줄(작업폴더·대기파일)인가 → 원장 줄 또는 None."""
    rp = os.path.realpath(path)
    for W in ctx.get("wonjang_all") or ctx["wonjang"]:
        for k in ("작업폴더", "대기파일"):
            v = (W.get(k) or "").strip()
            if v:
                full = os.path.realpath(os.path.join(ctx["repo"], v))
                if rp == full or rp.startswith(full.rstrip("/") + "/"):
                    return W
    return None


def resolve_title(path, raw, root, ctx, rep):
    """제목: --title → HTML(<!-- 제목: --> · post-cover h1 · <title> · 첫 h1) → 원장 줄(작업폴더·대기파일)의 최종제목·가제.
    셋 다 없으면 None(부르는 쪽이 실패로 둔다 — 제목 검사를 조용히 건너뛰지 않는다)."""
    name = os.path.basename(path)
    ht = html_title(raw, root)
    arg = ctx.get("title_arg")
    if arg and ht and tkey(arg) != tkey(ht):
        rep.f(f"제목 불일치 — --title 「{arg}」 ≠ HTML 제목 「{ht}」", name)
    if arg:
        return arg, "--title"
    if ht:
        return ht, "HTML"
    W = wonjang_mine(path, ctx)
    if W is not None:
        wt = (W.get("최종제목") or W.get("가제") or "").strip()
        if wt:
            return wt, f"원장 줄{W.get('_line', '?')}"
    return None, ""


def check_html(path, ctx, rep, others):
    raw = open(path, encoding="utf-8", errors="replace").read()
    fp = html_fingerprint(raw)
    name = os.path.basename(path)
    title, tsrc = resolve_title(path, raw, fp["root"], ctx, rep)
    mine = wonjang_mine(path, ctx)
    my_event = (mine.get("사건키") or "") if mine else ""
    self_id = ctx["self"] or canonical_id(raw)
    vocab, ev = ctx["vocab"], ctx["events"]
    h2s = fp["h2"]
    rep.n(f"{name}: 제목 「{title or '없음'}」({tsrc or '못 찾음'}) · h2 {len(h2s)} · 번호 h2 {fp['nnum']} · "
          f"외부 링크 {len(fp['ext'])}" + (f" · 자기 글 {self_id}" if self_id else ""))
    for b in fp["broken"]:
        rep.n(f"{name}: 깨진 주소 「{b[:60]}」(읽지 못해 건너뜀)")
    if not title:
        rep.f("제목 없음 — HTML 에 <!-- 제목: --> · h1 · <title> 이 없고 --title · 원장 작업폴더 줄도 없음"
              "(제목 쌍둥이·번호만 다른 제목 검사를 할 수 없음)", name)
    # 번호형
    if h2s and fp["ratio"] >= 0.5:
        rep.w(f"번호형 h2 {fp['nnum']}/{len(h2s)}(「숫자.」「숫자)」「①」「1단계」 등 50% 이상 — 참고, H-212로 치명에서 낮춤)", name)
    # 22편 지문과 h2 순서
    seq = [h2_norm(h) for h in h2s]
    for F in ctx["fp"]:
        if self_id and F["id"] == self_id:
            continue
        fs = [h2_norm(h) for h in F["h2"]]
        if len(seq) >= 3 and seq == fs:
            rep.w("h2 순서가 라이브 글과 같음(숫자·지명만 다름 — 참고, H-194)", f"지문 {F['id']} ({name})")
        elif fp["frames"] and fp["frames"] == h2_frames(F["h2"]):
            rep.w("h2 틀이 라이브 글과 같음(주제어만 바꾼 꼴 — 자동 생성형 의심)", f"지문 {F['id']} ({name})")
        elif len(seq) >= 3 and len(seq) == len(fs):
            same = sum(1 for x, y in zip(seq, fs) if x == y)
            if same * 3 >= len(seq) * 2:
                rep.w(f"h2 {same}/{len(seq)}자리가 라이브 글과 같음", f"지문 {F['id']} ({name})")

    # 대기·같이 넣은 HTML 과 h2 순서(제목이 같은 사본은 같은 글로 보고 뺀다)
    def same_post(op, ofp):
        return os.path.realpath(op) == os.path.realpath(path) or \
            bool(title and tkey(ofp.get("title", "")) == tkey(title))
    for op, ofp in others:
        if same_post(op, ofp):
            continue
        os_ = [h2_norm(h) for h in ofp["h2"]]
        if len(seq) >= 3 and seq == os_:
            rep.w("자동 생성형 — h2 순서가 다른 글과 같음(숫자·지명만 다름)", f"{os.path.relpath(op)} ({name})")
        elif fp["frames"] and fp["frames"] == ofp.get("frames"):
            rep.w("h2 틀이 다른 글과 같음(주제어만 바꾼 꼴 — 자동 생성형 의심)", f"{os.path.relpath(op)} ({name})")
    # 지문 유사(최근 10편) — v2 B2 추정 기준. FP_FATAL 이 False 면 경고(첫 2주)
    pool = []
    for op, ofp in others:
        if not same_post(op, ofp):
            pool.append((os.path.relpath(op), ofp))
    live = sorted([F for F in ctx["fp"] if F["id"] != self_id],
                  key=lambda F: int(re.sub(r"\D", "", F["id"]) or 0), reverse=True)
    for F in live:
        pool.append((F["id"], F))
    recent = pool[: ctx["recent"]]
    sims = [(nm, fp_similarity(fp, F)) for nm, F in recent]
    close = [(nm, s) for nm, s in sims if s >= FP_SIM]
    rep.n(f"{name}: 지문 0.8 이상 비슷한 글 {len(close)}/{len(recent)}편(최근 {ctx['recent']}편, {FP_MAX}편 이하) "
          + ", ".join(f"{nm} {s:.2f}" for nm, s in close))
    if len(close) > FP_MAX:
        msg = f"지문 0.8 이상 비슷한 글 {len(close)}편(최근 {ctx['recent']}편 중 {FP_MAX}편 이하, v2 B2 추정 기준)"
        if FP_FATAL:
            rep.f(msg, name)
        else:
            rep.w(msg + " — 첫 2주는 경고, 분포를 본 뒤 본사가 고정", name)
    # 서브도메인
    for u in sorted(set(subdomain_links(fp["hrefs"]) + subdomain_links(raw))):
        rep.f(f"서브도메인 링크 {u}", name)
    # 제목 쌍둥이·번호 중복
    if title:
        for L in ctx["ledger"]:
            if self_id and L["id"] == self_id:
                continue
            if not L["id"] and tkey(L["title"]) == tkey(title) and mine is not None:
                rep.n(f"{name}: 주제대장 줄{L['_line']} 진행분과 제목이 같고 원장 작업폴더 줄이 이 파일이라 같은 글로 봄")
                continue
            # 제목 대 제목만 본다(핵심어 낱말 겹침은 gate_topic 제목 모드 몫)
            lref = f"{ctx['ledger_src']} {L['id'] or '줄' + str(L['_line'])} ({name})"
            r = twin_check("", title, my_event, "", L["title"], L["event"], vocab, ev)
            if r:
                rep.f(f"쌍둥이 글 — {r}", lref)
            r = title_series_check(title, my_event, L["title"], L["event"], ev)
            if r:
                rep.f(f"반복 금지 — {r}", lref)
        for W in ctx["wonjang"]:
            if mine is not None and W is mine:
                continue
            wt = W.get("최종제목") or W.get("가제", "")
            r = twin_check("", title, my_event, "", wt, W.get("사건키", ""), vocab, ev)
            if r:
                rep.f(f"쌍둥이 글 — {r}" + ("" if mine is not None else " (이 파일과 같은 작업폴더·대기파일 원장 줄이 없음)"),
                      f"원장 줄{W['_line']} ({name})")
            r = title_series_check(title, my_event, wt, W.get("사건키", ""), ev)
            if r:
                rep.f(f"반복 금지 — {r}", f"원장 줄{W['_line']} ({name})")


# ───────────────────────── 지문_22 만들기 ─────────────────────────
KEYS22 = {  # 초안 2-3 「라이브 22편 제목 핵심어」에서 글마다 하나(쌍둥이 비교용)
    "/2": ("동전주 상장폐지", ""), "/5": ("관리종목 지정", ""), "/6": ("정리매매", ""),
    "/7": ("주식병합", ""), "/8": ("근로장려금 반기신청", ""), "/10": ("거래정지 이유", ""),
    "/11": ("VI 변동성완화장치", ""), "/12": ("단기과열종목 지정", ""), "/13": ("상장폐지 사유", ""),
    "/16": ("생산적금융 ISA", ""), "/17": ("엔화 원엔 환율", ""), "/18": ("연금저축 세액공제", "연금저축세액공제"),
    "/19": ("해외주식 양도소득세", ""), "/20": ("국민연금 조기수령", ""), "/21": ("애프터마켓 가격제한폭", ""),
    "/22": ("추석 휴장", "추석휴장"), "/23": ("관리종목 시가총액 기준", ""), "/24": ("환율 상승", ""),
    "/25": ("유상증자 자금 용도", ""), "/27": ("10월 5일 증시 휴장", "10월5일휴장,한글날휴장,연말휴장"),
    "/28": ("대주주 기준일", "대주주기준일12월"), "/30": ("QQQ SPY 비교", ""),
}


NOTICE_LABEL = re.compile(r"^\s*(안내|알림|면책|유의\s*사항|일러두기)(\s|[:：]|$)")
NOTICE_SPLIT = re.compile(r"(?<=[.!?。])\s+|\n+")
REVISION_LINE = re.compile(r"수정\s*이력|최종\s*수정|수정일\s*[:：]|업데이트\s*[:：]")


def _external_href(href):
    h = (href or "").strip()
    if h.startswith("//"):
        h = "https:" + h
    p = safe_urlparse(h)
    return p is not None and p.scheme in ("http", "https") and SITE not in (p.netloc or "").lower()


def plain_text(n, drop_external=False):
    """노드 글자(<br>·블록 경계 = 줄바꿈). drop_external 이면 외부 링크 글자를 뺀다(overlap21 이 보는 글자와 맞춤)."""
    out = []

    def rec(x):
        for k in x.kids:
            if isinstance(k, str):
                out.append(k)
            elif k.tag == "br":
                out.append("\n")
            elif drop_external and k.tag == "a" and _external_href(k.attrs.get("href")):
                out.append(" ")
            elif k.tag not in SKIP:
                blk = k.tag in BLOCK
                if blk:
                    out.append("\n")
                rec(k)
                if blk:
                    out.append("\n")
    rec(n)
    return re.sub(r"[ \t\r\f\v]+", " ", "".join(out)).strip()


def notice_sentences(body):
    """라이브 글 끝 「안내」 상자(라벨로 시작하는 1,500자 이하 블록)의 문장들 — overlap21 의 고정 문구 목록(정확히 같을 때만 뺀다)."""
    out = []
    for n in body.iter():
        if n.tag not in ("p", "div", "blockquote", "aside", "section"):
            continue
        t = plain_text(n, drop_external=True)
        m = NOTICE_LABEL.match(t)
        if not m or len(t) > 1500:
            continue
        for sline in NOTICE_SPLIT.split(t[m.end():]):
            sline = sline.strip()
            if len(sline) >= 10 and not REVISION_LINE.search(sline) and sline not in out:
                out.append(sline)
    return out


def build_fp(live_dir, out):
    """라이브 스냅숏에서 지문을 잰다. 핵심어·사건키는 같은 폴더 주제대장.tsv(gate_topic 과 같은 낱말)에서,
    없으면 KEYS22(초안 2-3)에서 가져온다."""
    led = {}
    for r in read_tsv(os.path.join(HERE, "주제대장.tsv")):
        pid = pick(r, "글", "번호")
        if pid:
            led[pid] = (pick(r, "핵심어"), pick(r, "다루는사건키", "사건키"))
    rows = []
    for p in sorted(glob.glob(os.path.join(live_dir, "*.html")),
                    key=lambda x: int(re.sub(r"\D", "", os.path.basename(x)) or 0)):
        if not re.fullmatch(r"\d+\.html", os.path.basename(p)):
            continue
        raw = open(p, encoding="utf-8", errors="replace").read()
        if "contents_style" not in raw:
            continue
        fp = html_fingerprint(raw)
        pid = canonical_id(raw) or "/" + os.path.basename(p)[:-5]
        pub = re.search(r'article:published_time"\s+content="([^"]+)"', raw)
        mod = re.search(r'article:modified_time"\s+content="([^"]+)"', raw)
        key, ev = led.get(pid) or KEYS22.get(pid, ("", ""))
        ev = "" if ev == "-" else ev
        rows.append([pid, html_title(raw, fp["root"]) or "", pub.group(1) if pub else "", mod.group(1) if mod else "",
                     str(len(fp["h2"])), str(fp["nnum"]), "번호형" if fp["h2"] and fp["ratio"] >= 0.5 else "아님",
                     str(len(fp["ext"])), fp["h2"][-1] if fp["h2"] else "", " ‖ ".join(fp["h2"]), fp["types"],
                     fp["heads"], ",".join(str(x) for x in sorted(fp["tables"])), "1" if fp["summary"] else "0", key, ev,
                     " ‖ ".join(notice_sentences(fp["body"]))])
    head = ["글", "제목", "게시", "수정", "h2수", "번호h2수", "판정", "외부링크수", "마지막h2", "h2목록", "h2유형", "첫어절유형",
            "표위치", "요약", "핵심어", "사건키", "안내문장"]
    with open(out, "w", encoding="utf-8") as f:
        f.write("# 라이브 22편 지문 — gate_frame.py --build-fp 로 만듦(10/3 01:14Z 스냅숏, 본문 div.contents_style 안 h2만)\n")
        f.write("# 외부링크수 = 본문 안 서로 다른 외부 URL 수(기관 홈 포함). h2유형(끝맺음) N=번호 Q=물음 D=숫자 S=서술. "
                "첫어절유형 N=번호 W=의문사 D=숫자 P=따옴표 J=조사 붙은 낱말 K=그 밖. "
                "표위치 = 표가 놓인 h2 구간(0=첫 h2 앞). 핵심어·사건키 = 주제대장.tsv 와 같은 값(주제대장이 없을 때 쌍둥이 비교용). "
                "안내문장 = 글 끝 「안내」 상자 문장(우리 글, 외부 링크 글자를 뺀 꼴 — overlap21 이 정확히 같은 문장만 뺀다). 유형 칸은 기록용 — gate_frame 은 h2목록에서 다시 잰다\n")
        f.write("\t".join(head) + "\n")
        for r in rows:
            f.write("\t".join(x.replace("\t", " ").replace("\n", " ") for x in r) + "\n")
    return rows


# ───────────────────────── main ─────────────────────────
def find_repo(arg):
    """→ (레포 경로, 오류 문자열). --repo 가 없으면 자기 위치 ../../ — 서치 레포(도구/gate_search.py)가 아니면 오류."""
    if arg:
        return os.path.realpath(arg), ""
    cand = os.path.realpath(os.path.join(HERE, "..", ".."))
    if not os.path.isfile(os.path.join(cand, "도구", "gate_search.py")):
        return cand, (f"서치 레포 아님: 자동 인식한 {cand} 에 도구/gate_search.py 가 없다 — "
                      f"--repo <서치 레포 루트> 를 준다(본사 원본에서 돌릴 때)")
    return cand, ""


def main():
    ap = argparse.ArgumentParser(description="서치 틀 게이트(gate_frame)")
    ap.add_argument("files", nargs="*")
    ap.add_argument("--repo")
    ap.add_argument("--ledger")
    ap.add_argument("--fp")
    ap.add_argument("--self", dest="selfid")
    ap.add_argument("--title", help="HTML 의 글 제목(변환기 출력처럼 HTML 에 제목이 없을 때). HTML 1개일 때만")
    ap.add_argument("--no-ledger", action="store_true", help="원장(운영/원장.csv) 대조를 건너뜀 — 명시할 때만")
    ap.add_argument("--recent", type=int, default=10)
    ap.add_argument("--build-fp", dest="build")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args()
    if a.build:
        out = a.fp or os.path.join(HERE, "지문_22.tsv")
        rows = build_fp(a.build, out)
        print(f"지문 {len(rows)}편 → {out} (번호형 {sum(1 for r in rows if r[6] == '번호형')}편)")
        return 0
    if not a.files:
        ap.print_usage()
        return 2
    missing = [p for p in a.files if not os.path.isfile(p)]
    if missing:
        print("오류: 입력 파일 없음 " + ", ".join(missing))
        return 2
    repo, err = find_repo(a.repo)
    if err:
        print("오류: " + err)
        return 2
    md_files = [p for p in a.files if not p.lower().endswith((".html", ".htm"))]
    html_files = [p for p in a.files if p.lower().endswith((".html", ".htm"))]
    if a.title and len(html_files) != 1:
        print("오류: --title 은 HTML 1개를 넣을 때만 쓴다")
        return 2
    fp_rows = load_fp(a.fp or os.path.join(HERE, "지문_22.tsv"))
    ledger, lsrc = load_ledger(a.ledger or os.path.join(HERE, "주제대장.tsv"), fp_rows)
    if a.no_ledger:
        wonjang, wpath, wall = [], os.path.join(repo, "운영", "원장.csv"), []
    else:
        wonjang, wpath, wall = load_wonjang(repo)
        if wonjang is None:
            print(f"오류: 원장 없음 {wpath} — 서치 레포 루트를 --repo 로 준다(원장 대조를 일부러 건너뛸 때만 --no-ledger)")
            return 2
    events = load_events(HERE)
    selfid = a.selfid if (a.selfid or "").startswith("/") else ("/" + a.selfid if a.selfid else None)
    rep = Report()
    if not fp_rows:
        rep.f("지문_22.tsv 없음(라이브 22편 지문 대조 불가)", a.fp or os.path.join(HERE, "지문_22.tsv"))
    rep.n(f"비교 원천: 지문 {len(fp_rows)}편 · {lsrc} {len(ledger)}줄 · 원장 진행분 {len(wonjang)}줄"
          + (" (--no-ledger: 원장 대조 건너뜀)" if a.no_ledger else f"({wpath})")
          + (f" · 사건키 {len(events['rx'])}개" if events["ok"] else f" · 사건키 없음({events['why']}) — 일정형 예외 닫힘"))

    items, texts = [], []
    for p in md_files:
        its, tx = md_items(p)
        items += its
        texts.append((p, tx))
        if not its:
            rep.f("검색어·가제 칸이 있는 마크다운 표가 없음(편성표·설계는 표로 쓴다 — 틀 검사를 할 수 없음)",
                  os.path.basename(p))
    corpus = [it["q"] for it in items] + [it["title"] for it in items] + [L["title"] for L in ledger] + \
        [L["key"] for L in ledger] + [W.get("검색어", "") for W in wonjang] + [W.get("가제", "") for W in wonjang]
    ctx = {"fp": fp_rows, "ledger": ledger, "ledger_src": lsrc, "wonjang": wonjang, "wonjang_all": wall, "repo": repo,
           "self": selfid, "recent": a.recent, "events": events, "title_arg": a.title}
    if html_files:
        titles = []
        for p in html_files:
            raw = open(p, encoding="utf-8", errors="replace").read()
            titles.append(html_title(raw, parse_html(raw)) or "")
        corpus += titles + ([a.title] if a.title else [])
    ctx["vocab"] = build_vocab(corpus)
    if md_files:
        check_md(items, texts, ctx, rep)
    if html_files:
        others = []
        pend = glob.glob(os.path.join(repo, "발행", "대기", "*.html")) + \
            glob.glob(os.path.join(repo, "작업", "*", "발행.html"))
        seen = set()
        seen_titles = set()
        for op in html_files + sorted(pend, reverse=True):
            rp = os.path.realpath(op)
            if rp in seen or not os.path.exists(op):
                continue
            seen.add(rp)
            try:
                oraw = open(op, encoding="utf-8", errors="replace").read()
                ofp = html_fingerprint(oraw)
            except Exception as e:  # noqa: BLE001
                rep.n(f"{op} 읽기 실패: {e}")
                continue
            ofp["title"] = html_title(oraw, ofp["root"]) or ""
            if op in html_files and a.title:
                ofp["title"] = a.title
            tk = tkey(ofp["title"])
            if tk and tk in seen_titles and op not in html_files:
                continue  # 작업/…/발행.html 과 발행/대기/… 사본은 한 글로 센다
            seen_titles.add(tk)
            others.append((op, ofp))
        for p in html_files:
            check_html(p, ctx, rep, others)

    for x in rep.note if a.verbose or rep.fail else rep.note[:3]:
        print(x)
    for x in rep.warn:
        print(x)
    for x in rep.fail:
        print(x)
    nitems = len(items)
    print(f"결과: {'실패' if rep.fail else '통과'} — 실패 {len(rep.fail)} · 경고 {len(rep.warn)}"
          f" (표 줄 {nitems} · HTML {len(html_files)})")
    return 1 if rep.fail else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001 — 예상 못 한 오류는 종료 2(「실패 있음」 1 과 구분)
        print(f"오류: {type(e).__name__}: {e}")
        sys.exit(2)
