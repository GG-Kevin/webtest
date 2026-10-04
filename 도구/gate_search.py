#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""서치 발행 게이트(0토큰, 표준 라이브러리만).
사용: python3 도구/gate_search.py <발행 HTML> [--keyword <검색어>] [--title <제목>] [--revision <이전 발행 HTML>] [--date YYYY-MM-DD]
CLAUDE.md 「애드센스 기준」(H-161)과 개편안 v3.1·v2 2-7 「시범」 줄을 센다. 치명이 1개 이상이면 종료코드 1, 없으면 0(경고는 0).
마지막 줄은 「치명 n · 경고 m」. 제목은 --title → 첫 줄 주석 <!-- 제목: ... --> → 티스토리 post-cover h1 → <title> → 첫 <h1>.
제목을 못 찾으면 치명이다(h1·검색어 판형을 잴 수 없음). 티스토리 쪽 전체(라이브 스냅숏)를 넣으면 본문 div.contents_style 안만 잰다.

바뀐 줄(H-189 v3.1 집행, 본사 2026-10-03 — 한 줄에 하나)
- v3.1 반영: 제목 길이 경고 15~45자 → h1 22~32자
- v3.1 반영: --keyword 검색어가 제목 앞 15자 밖이면 경고(제목에 없으면 경고)
- v3.1 반영: 첫 130자(본문 첫 문단부터 센 글자) 안에 숫자가 없으면 치명
- v3.1 반영: 공공 원문 딥링크(정부·법령·거래소·국세청·금융위·DART·go.kr·or.kr 등, PUBLIC) 0이면 치명. 딥링크 3개 이상 치명(H-161)은 그대로
- v3.1 반영: 저자 박스(저자 칸 + 소개 쪽 링크) 없으면 치명 — 옛 「글 끝 3문단 바이라인」 검사를 위치와 무관하게 바꿈
- v3.1 반영: 본문 2,400~4,300자(공백 제외) 밖 경고 · h2 5~9개 밖 경고 · 표 4개 초과 경고 · 이미지 1~3장 밖 경고 · 3,000자 넘는데 목차 없음 경고
- v3.1 반영: 옛 「목차가 있는데 h2 6개 미만 = 치명」 → 「3,000자 이하 글의 목차 = 경고」(v3.1 「3,000자를 넘으면 목차」)
- v2 2-7 반영: 「보장」 부정문 오탐 수정 — 「수익을 보장하지 않습니다」류 통과
- v2 2-7 반영: 면책은 허용 목록 문구 1종(ALLOWED_DISCLAIMER)만 — 그 밖의 면책 문장은 치명, 허용 문장 2번 이상은 경고
- v2 2-7 반영: 바이라인 href 가 소개 쪽 저자 앵커(#저자)가 아니면 치명(E1)
- v2 2-7 반영: 첫 3단락 안 기준일 문장 없으면 치명(E4) — 옛 「YYYY-MM-DD 기준 0회 = 치명」을 바꿈. 3회 미만 경고는 두 형식을 함께 센다
- v2 2-7 반영: 내부 직함(「전문가」「전문 작가」) 치명 · FAQPage 구조화 데이터 치명 · FAQ 소제목 경고(옛 「FAQ 정확히 3문항」 경고를 넓힘)
- v2 2-7 반영: 번호형 h2(50% 이상) 치명 · 조언 문장(가입하세요·갈아타세요류) 경고 · 표 2개 이상 치명(그대로)
- v2 2-7 반영: E5 수정 이력 — --revision <이전 HTML> 이 있을 때만 수정 이력 줄 +1·「최종 수정」 날짜 = --date(없으면 오늘 KST) 치명.
  새 글(--revision 없음)에 「수정 이력」·「최종 수정」이 있으면 경고(B3)
- v2 2-7 반영: 「확인 과정」 단락(확인·대조·검산 + 원문·조문·공고 낱말이 함께 든 문단)이 없으면 경고 · 고정 소제목 「확인 과정」 경고(B4)
- 검증 반영(10/3): 「보장」·「권유」 부정 판정은 같은 문장 안 바로 뒤 활용형(하지 않·되지 않·할 수 없·받지 못·이 아니)만 본다.
  마침표·물음표·느낌표·블록 경계를 넘지 않는다(옛 판은 앞 12자·뒤 14자 안의 아무 「없/않」에 풀렸음)
- 검증 반영(10/3): 「원금 보장」·「수익 보장」·「100% 보장」·「보장 수익」은 부정·예금자보호 문맥이 아니면 무조건 치명(옛 줄 복원).
  「보장합니다·보장됩니다·보장해 드립니다」는 같은 문장에 수익·원금·투자·상품·금리 같은 돈 낱말이 있으면 치명
- 검증 반영(10/3): 「확정 수익(률)」 치명(본사 규칙 4 「보장·확정 수익 표현 금지」)
- 검증 반영(10/3): H-119 문구를 넓힘 — 「AI의 도움」「AI로 작성」「AI 도구」「생성형 AI」「인공지능의 도움·활용」
- 검증 반영(10/3): 면책 판정은 블록(p·li·td·caption·h*)으로 먼저 나눈 뒤 문장으로 나눈다(표·소제목 뒤 허용 문장 오탐 수정).
  「참고용」「일반 정보」는 같은 문장에 책임·권유·투자 판단이 있을 때만 면책 표지로 본다
- 검증 반영(10/3): 저자 박스는 class/id 표지(author·byline·writer·저자) 블록, 또는 「글쓴이·저자·필명」으로 시작하는 300자 이하
  독립 블록만 인정한다. body·contents_style 자신과 본문 문단 속 소개 링크는 저자 박스가 아니다
- 검증 반영(10/3): E4 기준일 — 「기준」 바로 앞이 원문·공고·고시·열람·발표이거나 「기준으로·기준입니다」로 끝나는 구만 인정
  (「…부터 적용되는 선정기준액」 같은 낱말은 기준일 문장이 아니다). 「YYYY-MM-DD 기준」은 그대로 인정
- 검증 반영(10/3): 번호형 h2 는 NFKC 뒤 판정 — 「①」「１．」「⑴」「1단계」「Step 1」「첫째」도 번호, 소수(「3.3% …」)는 번호 아님(gate_frame 과 같은 규칙)
- 검증 반영(10/3): 깨진 구조(h1~h6 안에 p·h2·표·목록 같은 블록이 들어감 = 닫는 태그 빠짐) 치명
- 검증 반영(10/3): 깨진 링크 주소(urllib 가 못 읽는 href, 예 「http://[bad-ipv6/18」)는 치명으로 적는다(옛 판은 말없이 건너뜀)
- 검증 반영(10/3): 제목을 못 찾으면 치명(옛 판은 경고 하나만 내고 --keyword 검사를 건너뜀). --title 로 줄 수 있고 HTML 제목과 다르면 치명
- 버그 수정: 내부 링크는 우리 글 주소(/숫자·/entry/)만 센다(옛 판은 소개·바이라인 링크까지 세어 2개를 채웠음)
- 버그 수정: 링크 주소는 urllib 로 나눈다(옛 정규식은 「?」 붙은 주소의 호스트를 잘못 잘랐고, 서브도메인을 사이트 안으로 셌음)
- 버그 수정: 금지어·화살표·요약 장치·min-width·AI 흔적을 본문 안에서만 센다(옛 판은 script·사이드바 글자까지 셌음)
- 그대로: 금지어(권유·보장·AI 문구) 치명 · 표 min-width 400px 초과 치명 · caption 없는 표 경고 · 표 밖 화살표 치명 · 요약 장치 2개 이상 치명
           · 외부 딥링크 3개 미만 치명 · 사이트 안 글 링크 2개 미만 치명 · 그림 0장·alt 없음 치명 · AI 표시·메타데이터 흔적 치명
"""
import argparse
import datetime
import html
import re
import sys
import unicodedata
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote

SITE = "moneyproducer.co.kr"
ABOUT_SLUG = "머니프로듀서를-소개합니다"
AUTHOR_ANCHORS = {"저자", "author"}
# 면책 허용 목록(1종). 본문에 면책을 둘 때는 이 문장 하나만 쓴다(v2 2-7). 금지어(권유·보장)를 피한 문장이다.
# 본사 게이트 overlap21.py ALLOWED_DISCLAIMER 와 같은 문장 — 바꾸면 둘 다 고친다.
ALLOWED_DISCLAIMER = "이 글은 기준일의 공개 원문을 정리한 일반 정보이며, 개인의 사정에 따라 결과가 달라질 수 있습니다."
PUBLIC_SUFFIX = (".go.kr", ".or.kr", ".gov.kr", ".mil.kr", ".gov")
PUBLIC_HOST = {"gov.kr", "korea.kr", "krx.co.kr", "kosis.kr", "applyhome.co.kr", "kodit.co.kr", "kibo.or.kr",
               "law.go.kr", "nts.go.kr", "hometax.go.kr", "fsc.go.kr", "fss.or.kr", "dart.fss.or.kr", "moef.go.kr",
               "nps.or.kr", "nhis.or.kr", "bok.or.kr", "ksd.or.kr", "seibro.or.kr", "kofia.or.kr", "kdic.or.kr",
               "hf.go.kr", "lh.or.kr", "reb.or.kr", "kinfa.or.kr", "wetax.go.kr", "easylaw.go.kr", "data.go.kr",
               "sec.gov", "irs.gov"}

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
BLOCK = {"p", "div", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6", "table", "tr", "td", "th", "thead",
         "tbody", "blockquote", "section", "article", "aside", "header", "footer", "nav", "figure", "figcaption",
         "caption", "pre", "dl", "dt", "dd", "br", "hr"}
HEADINGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
SKIP = {"script", "style", "noscript", "template"}


class Node:
    __slots__ = ("tag", "attrs", "kids", "parent")

    def __init__(self, tag, attrs=None, parent=None):
        self.tag, self.kids, self.parent = tag, [], parent
        self.attrs = {k: (v if v is not None else "") for k, v in (attrs or {}).items()}

    def iter(self):
        yield self
        for k in self.kids:
            if isinstance(k, Node):
                yield from k.iter()

    def cls(self):
        return (self.attrs.get("class") or "").split()

    def inside(self, pred):
        x = self.parent
        while x is not None:
            if pred(x):
                return True
            x = x.parent
        return False


class TB(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root")
        self.cur = self.root

    def handle_starttag(self, t, a):
        n = Node(t, dict(a), self.cur)
        self.cur.kids.append(n)
        if t not in VOID:
            self.cur = n

    def handle_startendtag(self, t, a):
        self.cur.kids.append(Node(t, dict(a), self.cur))

    def handle_endtag(self, t):
        x = self.cur
        while x is not None and x.tag != t:
            x = x.parent
        if x is not None and x.parent is not None:
            self.cur = x.parent

    def handle_data(self, d):
        self.cur.kids.append(d)


def text_of(node, skip=None):
    out = []

    def rec(x):
        for k in x.kids:
            if isinstance(k, str):
                out.append(k)
            elif k.tag in SKIP or (skip and skip(k)):
                continue
            else:
                b = k.tag in BLOCK
                if b:
                    out.append(" ")
                rec(k)
                if b:
                    out.append(" ")
    rec(node)
    return re.sub(r"\s+", " ", "".join(out)).strip()


def block_texts(node):
    """블록(p·li·td·th·caption·h1~h6·figcaption …)마다 글자. <br>은 줄바꿈. 블록 안 블록은 따로 낸다."""
    out, buf = [], []

    def flush():
        t = re.sub(r"[ \t\r\f\v]+", " ", "".join(buf)).strip()
        buf.clear()
        if t:
            out.append(t)

    def rec(x):
        for k in x.kids:
            if isinstance(k, str):
                buf.append(k)
                continue
            if k.tag in SKIP:
                continue
            if k.tag == "br":
                buf.append("\n")
                continue
            blk = k.tag in BLOCK
            if blk:
                flush()
            rec(k)
            if blk:
                flush()
    rec(node)
    flush()
    return out


SENT_SPLIT = re.compile(r"(?<=[.!?。])\s+|\n+")


def sentences(node):
    """블록으로 먼저 나누고, 블록 안에서 마침표·물음표·느낌표·줄바꿈으로 문장을 나눈다."""
    return [s.strip() for b in block_texts(node) for s in SENT_SPLIT.split(b) if s.strip()]


def find_body(root):
    for n in root.iter():
        if n.tag == "div" and "contents_style" in n.cls():
            return n
    for n in root.iter():
        if n.tag == "body":
            return n
    return root


def body_raw(raw):
    """본문 HTML 문자열(바깥 div.contents_style 안). 없으면 전체."""
    m = re.search(r'(?is)<div[^>]*class="[^"]*\bcontents_style\b[^"]*"[^>]*>', raw)
    if not m:
        return raw
    depth = 1
    for t in re.finditer(r"(?is)<\s*(/?)div\b[^>]*>", raw[m.end():]):
        depth += -1 if t.group(1) else 1
        if depth == 0:
            return raw[m.end():m.end() + t.start()]
    return raw[m.end():]


def get_title(raw, root):
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
            return re.sub(r"\s*::\s*머니프로듀서\s*$", "", text_of(n))
    for n in root.iter():
        if n.tag == "h1":
            return text_of(n)
    return None


def host_of(href):
    h = (href or "").strip()
    if h.startswith("//"):
        h = "https:" + h
    try:
        p = urlparse(h)
        host = (p.hostname or "").lower()
    except ValueError:
        return None, None, None
    return host, p, h


def is_public(host):
    host = (host or "").lower()
    if host.startswith("www."):
        host = host[4:]
    if host in PUBLIC_HOST or any(host.endswith("." + x) for x in PUBLIC_HOST):
        return True
    return host.endswith(PUBLIC_SUFFIX)


def is_about(href):
    u = unquote(href or "")
    return bool(re.search(r"/pages?/[^#?]*" + re.escape(ABOUT_SLUG), u) or re.search(r"/pages?/[^#?]*(소개|about)", u, re.I))


def nf(s):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", s or "")).strip()


# 번호형 h2 — 본사 게이트 gate_frame.py 와 같은 규칙(바꾸면 둘 다 고친다)
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


AUTHOR_MARK = re.compile(r"author|byline|writer|저자", re.I)
BYLINE_HEAD = re.compile(r"^\s*(글쓴이|저자|필명)(\s|[:：·]|$)")
DISCLAIMER_STRONG = re.compile(
    r"투자\s*(자문|권유|판단의?\s*책임|결정의?\s*책임)|책임(은|이)?\s*(본인|이용자|투자자|독자)|책임지지\s*않|"
    r"정보\s*제공(을|의)?\s*목적|법적\s*효력|매수\s*[·ㆍ・]?\s*매도를?\s*(권|추천)|권유하(거나|지)")
DISCLAIMER_SOFT = re.compile(r"참고용|일반(적인)?\s*정보")
DISCLAIMER_CTX = re.compile(r"책임|권유|투자\s*판단|판단의?\s*근거|투자\s*결정")
TITLE_INTERNAL = re.compile(r"전문가|전문\s*작가|분야\s*전문|전문\s*에디터")
ADVICE = re.compile(r"(가입|담으|담아\s*두|갈아타|투자하|매수하|매도하|넣어\s*두|사\s*두)(세요|십시오|시길)")
BASIS_TAIL = r"(?:으로|입니다|이며|이고|이다)?(?![가-힣])"
BASIS_ISO = r"\d{4}[-.]\s?\d{1,2}[-.]\s?\d{1,2}\.?\s*기준" + BASIS_TAIL
BASIS_KO = (r"\d{4}\s*년\s*\d{1,2}\s*월\s*\d{1,2}\s*일[^.!?]{0,40}?"
            r"(?:(?:원문|공고|고시|열람|발표)\s*기준" + BASIS_TAIL + r"|(?<![가-힣])기준\s*(?:으로|입니다))")
SUMMARY = re.compile(r"핵심\s*요약|한눈에\s*(비교|보기)|3줄\s*(정리|요약)|세\s*줄\s*(정리|요약)|한\s*줄\s*요약|TL;?DR", re.I)
KO_NUM = re.compile(r"[일이삼사오육칠팔구십백천만억]\s*(원|만원|억|년|개월|세|퍼센트|%)")

# 금지어 — 늘 치명(H-161·H-119)
ALWAYS_BAD = re.compile(
    r"지금\s*(사라|사세요|사야|팔라|팔아)|(매수|매도)\s*하세요|무조건|100\s*%\s*수익|ChatGPT|챗\s*GPT|"
    r"(?<![A-Za-z])AI\s*(?:의|가|로|를|을|와|과|에게|한테)?\s*(?:도움|활용|작성|생성|도구|툴|이용|사용)|생성형\s*AI|"
    r"인공지능\s*(?:의|을|를|으로|이|가)?\s*(?:도움|활용|작성|생성|도구|이용|사용)", re.I)
# 같은 문장 안 바로 뒤 부정 활용형(검증 반영) — 「보장하지 않습니다」「보장되지 않는」「보장할 수 없습니다」「보장받지 못」
# 「보장이 아닙니다」「보장 안 됩니다」「보장은 없습니다」
NEG_AFTER = re.compile(
    r"^\s*(?:(?:을|를|은|는|이|가|까지|도|만)\s*)?(?:"
    r"(?:하|되|해\s*드리|해\s*주|받)지\s*(?:는|도)?\s*(?:않|못)"
    r"|(?:할|될|받을|해\s*드릴|해\s*줄)\s*수\s*(?:는|도)?\s*없"
    r"|(?:하는|되는|된|한|받는)\s*(?:것|게|건)\s*(?:은|이)?\s*(?:아니|아닙|아닌|아님)"
    r"|안\s*(?:되|됩|돼|된|하|합|해|함)"
    r"|아니|아닙|아닌|아님|없)")
GUAR_OBJ = re.compile(r"(원금|원리금|수익률?|수익금|고수익|이익|이자|배당)\s*(?:을|를|이|가|은|는|도|까지)?\s*(?:100\s*%\s*)?$")
GUAR_STRONG_BEFORE = re.compile(r"(100\s*%|확실히|반드시|완벽(?:하게|히)?|무조건)\s*$")
GUAR_NOUN_AFTER = re.compile(r"^\s*(형|수익률?|이자|금리|상품)")
GUAR_VERB_AFTER = re.compile(r"^\s*(?:합니다|됩니다|한다|된다|돼요|해요|해\s*(?:드립니다|드려요|줍니다|준다|드릴게요)|되는|하는)")
FIN_CTX = re.compile(r"수익|원금|이자|투자|상품|금리|배당|손실|원리금|이익|%|퍼센트|연\s*\d")
DEPOSIT_CTX = re.compile(r"예금자\s*보호|예금\s*보험|보호\s*한도")
SOLICIT_EXEMPT_BEFORE = re.compile(r"(부당|불초청|재|투자\s*권유\s*대행)\s*$")
SOLICIT_EXEMPT_AFTER = re.compile(r"^\s*(대행|준칙|규제|금지)")
CONFIRMED = re.compile(r"확정\s*(?:적인\s*)?수익(?:률)?")

# E5 수정 이력(B3) — 수정 HTML 만
DATE_ANY = re.compile(r"(20\d\d)\s*[-.년]\s*(\d{1,2})\s*[-.월]\s*(\d{1,2})")
REV_LABEL = re.compile(r"^\s*수정\s*이력")
LAST_MOD = re.compile(r"최종\s*수정(?:일)?\s*[:：]?\s*(20\d\d)\s*[-.년]\s*(\d{1,2})\s*[-.월]\s*(\d{1,2})")
# 확인 과정(B4)
CHECK_VERB = re.compile(r"확인(?:했|한|하고|해\s*보|에\s*쓴|해\s*둔)|대조(?:했|한|해)|검산|다시\s*(?:계산|옮겼|확인|열어|맞춰)|"
                        r"맞춰\s*(?:봤|보)|열람(?:했|한|본)|조회(?:했|한)|직접\s*(?:열어|계산)")
CHECK_SRC = re.compile(r"원문|조문|공고|고시|법령|홈택스|공시|자료|통계|산식")


def banned_phrases(sents):
    """문장 단위 금지어 판정 → 걸린 조각 목록."""
    bad = []
    for s in sents:
        for m in ALWAYS_BAD.finditer(s):
            bad.append(m.group(0))
        for m in CONFIRMED.finditer(s):
            if not NEG_AFTER.match(s[m.end():]):
                bad.append(m.group(0))
        for m in re.finditer(r"보장", s):
            before, after = s[:m.start()], s[m.end():]
            if NEG_AFTER.match(after):
                continue  # 「보장하지 않습니다」류(같은 문장, 바로 뒤)
            strong = GUAR_OBJ.search(before) or GUAR_STRONG_BEFORE.search(before) or GUAR_NOUN_AFTER.match(after)
            verb = GUAR_VERB_AFTER.match(after) and FIN_CTX.search(s)
            if not (strong or verb):
                continue  # 사회보장·기초생활보장·보장성 보험·권리 보장 같은 말은 약속이 아니다
            if DEPOSIT_CTX.search(before) and re.search(r"원금|원리금|예금", before):
                continue  # 「예금자보호 한도 안에서는 원금이 보장됩니다」는 제도 설명
            bad.append(s[max(0, m.start() - 10):m.end() + 8])
        for m in re.finditer(r"권유", s):
            before, after = s[:m.start()], s[m.end():]
            if NEG_AFTER.match(after) or SOLICIT_EXEMPT_BEFORE.search(before) or SOLICIT_EXEMPT_AFTER.match(after):
                continue
            bad.append(s[max(0, m.start() - 10):m.end() + 8])
    return bad


def count_revisions(body):
    """「수정 이력」 라벨 블록(또는 그 바로 다음 목록·문단) 안 날짜 수."""
    n = 0
    for node in body.iter():
        if node.tag not in ("p", "div", "li", "section", "aside", "ul", "ol", "dl", "h2", "h3", "h4", "strong", "b"):
            continue
        t = text_of(node)
        if not REV_LABEL.match(t):
            continue
        if node.parent is not None and REV_LABEL.match(text_of(node.parent)) and node.parent.tag != "#root":
            continue  # 바깥 라벨 블록에서 센다
        dates = DATE_ANY.findall(LAST_MOD.sub(" ", t))  # 「최종 수정 YYYY-MM-DD」 날짜는 이력 줄로 세지 않는다
        if not dates and node.parent is not None:
            sib = node.parent.kids
            i = sib.index(node)
            for k in sib[i + 1:]:
                if isinstance(k, Node):
                    dates = DATE_ANY.findall(LAST_MOD.sub(" ", text_of(k)))
                    break
        n += len(dates)
    return n


def check_revision(body, btext, prev_path, today, fatal, info):
    raw = open(prev_path, encoding="utf-8").read()
    root = TB()
    root.feed(raw)
    root.close()
    pbody = find_body(root.root)
    cur, prev = count_revisions(body), count_revisions(pbody)
    info.append(f"수정 이력 날짜 {cur}개(이전 판 {prev}개)")
    if cur != prev + 1:
        fatal.append(f"E5 수정 이력 줄 {cur}개 — 이전 판 {prev}개에서 하나 늘어야 함(수정 HTML)")
    m = LAST_MOD.search(btext)
    if not m:
        fatal.append("E5 「최종 수정 YYYY-MM-DD」 없음(수정 HTML)")
    else:
        d = "%04d-%02d-%02d" % tuple(int(x) for x in m.groups())
        if d != today:
            fatal.append(f"E5 최종 수정 {d} ≠ 넘기는 날 {today}")


def main():
    ap = argparse.ArgumentParser(description="서치 발행 게이트")
    ap.add_argument("html")
    ap.add_argument("--keyword", help="질문 검색어(자동완성 원문). 있으면 제목 앞 15자 검사")
    ap.add_argument("--title", help="글 제목(HTML 에 제목 주석·h1 이 없을 때). HTML 제목과 다르면 치명")
    ap.add_argument("--revision", help="실질 수정 HTML 일 때 이전 발행 HTML(E5 수정 이력 검사)")
    ap.add_argument("--date", help="넘기는 날 YYYY-MM-DD(E5 최종 수정 비교, 없으면 오늘 KST)")
    a = ap.parse_args()
    raw = open(a.html, encoding="utf-8").read()
    root = TB()
    root.feed(raw)
    root.close()
    root = root.root
    body = find_body(root)
    braw = body_raw(raw)
    btext = text_of(body)
    sents = sentences(body)
    fatal, warn, info = [], [], []

    # ── 제목(v3.1: h1 22~32자, 검색어 앞 15자) — 못 찾으면 치명(검증 반영) ──
    htitle = get_title(raw, root)
    if a.title and htitle and nf(a.title) != nf(htitle):
        fatal.append(f"제목 불일치 — --title 「{a.title}」 ≠ HTML 제목 「{htitle}」")
    title = a.title or htitle
    if title:
        n = len(title)
        info.append(f"제목 {n}자: {title}")
        if n < 22 or n > 32:
            warn.append(f"제목 h1 {n}자(22~32자 밖)")
        if a.keyword:
            t, k = nf(title).lower(), nf(a.keyword).lower()
            pos, end = t.find(k), -1
            if pos >= 0:
                end = pos + len(k)
            else:  # 띄어쓰기만 다르면 공백 뺀 글자로 찾고 원래 제목 위치로 되돌린다
                idx = [i for i, ch in enumerate(t) if ch != " "]
                t2, k2 = "".join(t[i] for i in idx), k.replace(" ", "")
                p2 = t2.find(k2) if k2 else -1
                if p2 >= 0:
                    pos, end = idx[p2], idx[p2 + len(k2) - 1] + 1
            if pos < 0:
                warn.append(f"검색어 「{a.keyword}」가 제목에 없음")
            elif end > max(15, len(k)):
                warn.append(f"검색어 「{a.keyword}」가 제목 앞 15자 밖({pos + 1}~{end}자째)")
    else:
        fatal.append("제목 없음(<!-- 제목: ... --> · h1 · <title> 이 없고 --title 도 없음 — h1 길이·검색어 위치를 잴 수 없음)")

    # ── 깨진 구조(검증 반영): 소제목 안에 블록이 들어감 = 닫는 태그 빠짐 ──
    broken = []
    for n in body.iter():
        if n.tag in HEADINGS:
            inner = [k.tag for k in n.iter() if k is not n and k.tag in BLOCK and k.tag not in ("br", "hr")]
            if inner:
                broken.append(f"<{n.tag}> 안 <{inner[0]}>")
    if broken:
        fatal.append(f"구조 깨짐 {len(broken)}곳(소제목 닫는 태그 빠짐 — 소제목이 문단을 삼킴): " + ", ".join(broken[:3]))

    # ── 금지어(권유·보장·확정 수익·AI 문구) — 같은 문장 안에서만 판정(검증 반영) ──
    bad = banned_phrases(sents)
    if bad:
        fatal.append("금지어(권유·보장·확정 수익·AI 문구) " + str(len(bad)) + "건: " + " / ".join(bad[:5]))

    # ── 면책: 허용 목록 1종만(v2 2-7) — 블록 → 문장 순으로 나눈다(검증 반영) ──
    allowed_n, other = 0, []
    for s in sents:
        if nf(s) == nf(ALLOWED_DISCLAIMER):
            allowed_n += 1
            continue
        if DISCLAIMER_STRONG.search(s) or (DISCLAIMER_SOFT.search(s) and DISCLAIMER_CTX.search(s)):
            other.append(s[:60])
    if other:
        fatal.append(f"허용 목록 밖 면책 문장 {len(other)}개(허용 1종: 「{ALLOWED_DISCLAIMER[:24]}…」): " + " / ".join(other[:3]))
    if allowed_n > 1:
        warn.append(f"허용 면책 문장이 {allowed_n}번(한 번만)")

    # ── 내부 직함(v2 2-7 G1) ──
    tt = TITLE_INTERNAL.findall(btext + " " + (title or ""))
    if tt:
        fatal.append(f"내부 직함 {len(tt)}건(「전문가」「전문 작가」 같은 말은 공개 문면에 쓰지 않음): " + ", ".join(sorted(set(tt))))

    # ── 조언 문장(v2 2-7 시범 = 경고) ──
    adv = [m.group(0) for m in ADVICE.finditer(btext)]
    if adv:
        warn.append(f"조언 문장 {len(adv)}건: " + ", ".join(adv[:4]))

    # ── 첫 문단·기준일(v3.1 첫 130자 숫자, v2 E4 첫 3단락 기준일) ──
    def in_box(n):
        return n.inside(lambda x: re.search(r"author|byline|writer|저자|toc|목차", " ".join(x.cls()) + " " + (x.attrs.get("id") or ""), re.I) is not None
                        or x.tag in ("table", "figure", "nav"))
    paras = [p for p in body.iter() if p.tag == "p" and len(text_of(p)) >= 10 and not in_box(p)]
    if paras:
        first = text_of(paras[0])
        idx = btext.find(first[:30])
        win = btext[idx: idx + 130] if idx >= 0 else first[:130]
        info.append(f"첫 130자: {win[:50]}…")
        if not (re.search(r"\d", win) or KO_NUM.search(win)):
            warn.append("첫 130자(본문 첫 문단부터) 안에 숫자·날짜·금액이 없음(참고 — 답을 맨 앞에 두면 독자에게 좋다, H-212)")
        first3 = " ".join(text_of(p) for p in paras[:3])
        if not (re.search(BASIS_ISO, first3) or re.search(BASIS_KO, first3)):
            fatal.append("첫 3단락 안에 기준일 문장 없음(「YYYY-MM-DD 기준」 또는 「YYYY년 M월 D일 … 원문·공고·고시·열람·발표 기준」·「… 기준으로/기준입니다」)")
    else:
        fatal.append("본문 문단(<p>)이 없음 — 첫 130자·기준일을 잴 수 없음")
    n_date = len(re.findall(BASIS_ISO, btext)) + len(re.findall(BASIS_KO, btext))
    info.append(f"기준일 문구 {n_date}회")
    if 0 < n_date < 3:
        warn.append(f"기준일 문구 {n_date}회뿐(숫자마다 기준일 확인)")

    # ── 분량·h2·표·이미지·목차(v3.1 경고) ──
    nchar = len(re.sub(r"\s", "", btext))
    h2s = [text_of(n) for n in body.iter() if n.tag == "h2"]
    tables = [n for n in body.iter() if n.tag == "table"]
    imgs = [n for n in body.iter() if n.tag == "img"]
    svgs = [n for n in body.iter() if n.tag == "svg" and (n.attrs.get("role") == "img" or n.attrs.get("aria-label"))]
    info.append(f"본문 {nchar}자(공백 제외) · h2 {len(h2s)}개 · 표 {len(tables)}개 · 이미지 {len(imgs) + len(svgs)}장")
    if nchar < 2400 or nchar > 4300:
        warn.append(f"본문 {nchar}자(2,400~4,300자 밖, 공백 제외)")
    if len(h2s) < 5 or len(h2s) > 9:
        warn.append(f"h2 {len(h2s)}개(5~9개 밖)")
    nnum = sum(1 for h in h2s if is_numbered(h))
    if h2s and nnum * 2 >= len(h2s):
        warn.append(f"번호형 h2 {nnum}/{len(h2s)}(참고 — 틀 아님, H-212)")
    if len(tables) < 2:
        warn.append(f"표 {len(tables)}개(참고 — 개수 틀 아님, H-212. 고유 자료는 직접 계산·원문 수치로 글마다 채운다)")
    elif len(tables) > 4:
        warn.append(f"표 {len(tables)}개(4개 초과)")
    nocap = sum(1 for t in tables if not any(k.tag == "caption" for k in t.iter()))
    if nocap:
        warn.append(f"caption 없는 표 {nocap}개(표 안내는 표 안 caption으로, 기준 6)")
    mins = [int(x) for x in re.findall(r"min-width\s*:\s*(\d+)\s*px", braw)]
    if mins and max(mins) > 400:
        fatal.append(f"표 min-width {max(mins)}px(400px 이하여야 모바일에서 안 깨짐)")
    nimg = len(imgs) + len(svgs)
    if nimg < 1 or nimg > 3:
        warn.append(f"이미지 {nimg}장(1~3장 밖)")
    has_toc = any(re.search(r"\btoc\b|목차", " ".join(n.cls()) + " " + (n.attrs.get("id") or ""), re.I) for n in body.iter()) \
        or re.search(r">\s*(목차|이 글의 차례|차례)\s*<", braw) is not None
    if nchar > 3000 and not has_toc:
        warn.append(f"본문 {nchar}자(3,000자 초과)인데 목차 없음")
    if has_toc and nchar <= 3000:
        warn.append(f"본문 {nchar}자(3,000자 이하)인데 목차 있음(3,000자 넘을 때만)")

    # ── 링크(H-161 딥링크 3·글 링크 2, v3.1 공공 1) ──
    ext, pub, intl, sub, bad_url = set(), set(), set(), set(), []
    links = [n for n in body.iter() if n.tag == "a" and (n.attrs.get("href") or "").strip()]
    for n in links:
        href = n.attrs.get("href").strip()
        if href.startswith("#") or href.startswith("mailto:"):
            continue
        host, p, full = host_of(href)
        if p is None:
            bad_url.append(href[:60])
            continue
        if not host:  # 상대 주소
            if re.match(r"^/(\d+|entry/.+)$", p.path or ""):
                intl.add(p.path)
            continue
        if host in (SITE, "www." + SITE):
            if re.match(r"^/(\d+|entry/.+)$", p.path or ""):
                intl.add(p.path)
            continue
        if host.endswith("." + SITE):
            sub.add(full)
            continue
        if (p.path or "").strip("/") == "" and not p.query:
            continue  # 기관 홈 링크는 출처로 안 침
        ext.add(full)
        if is_public(host):
            pub.add(full)
    info.append(f"외부 딥링크 {len(ext)}개(공공 {len(pub)}) · 우리 글 링크 {len(intl)}개")
    if bad_url:
        fatal.append(f"깨진 링크 주소 {len(bad_url)}개: " + ", ".join(bad_url[:3]))
    if len(ext) < 3:
        warn.append(f"원문 딥링크 {len(ext)}개(참고 — 개수 틀 아님. 공공 원문 1개 이상은 치명으로 유지, H-212)")
    if not pub:
        fatal.append("공공 원문 딥링크 0개(정부·법령·거래소·국세청·금융위·DART 등 1개 이상)")
    if len(intl) < 2:
        warn.append(f"우리 글 링크 {len(intl)}개(참고 — 독자가 다음에 찾을 글이 있을 때만, H-212)")
    if sub:
        warn.append(f"서브도메인 링크 {len(sub)}개(gate_frame 치명): " + ", ".join(sorted(sub)[:3]))

    # ── 그림(H-161) ──
    good = [i for i in imgs if (i.attrs.get("alt") or "").strip()]
    if not good and not svgs:
        warn.append("본문 그림 없음 또는 alt 없음(참고 — 그림 장수 틀 아님, H-212)")
    if len(imgs) - len(good):
        fatal.append(f"alt 없는 img {len(imgs) - len(good)}개")
    for i in good:
        if len(i.attrs["alt"].strip()) < 10:
            warn.append("alt가 너무 짧음(문장으로)")
            break
    alts = " ".join((i.attrs.get("alt") or "") + " " + (i.attrs.get("src") or "") for i in imgs)
    if re.search(r"AI\s*(생성|제작|이미지)|synthid|c2pa", braw + " " + alts, re.I):
        fatal.append("AI 표시·메타데이터 흔적")

    # ── 요약 장치·FAQ ──
    nsum = len(SUMMARY.findall(btext))
    info.append(f"요약 장치 {nsum}개")
    if nsum > 1:
        warn.append(f"요약 장치 {nsum}개(참고, H-212)")
    if re.search(r"FAQPage", raw):
        fatal.append("FAQPage 구조화 데이터(쓰지 않음, B5)")
    faq_h = [text_of(n) for n in body.iter() if n.tag in ("h2", "h3") and re.search(r"자주\s*묻는|FAQ|Q\s*&\s*A|묻고\s*답", text_of(n), re.I)]
    if faq_h:
        warn.append(f"FAQ 소제목 {len(faq_h)}개(FAQ 칸 대신 질문 h2로): " + ", ".join(faq_h[:2]))

    # ── 확인 과정(B4) ──
    def in_author(n):
        return n.inside(lambda x: AUTHOR_MARK.search(" ".join(x.cls()) + " " + (x.attrs.get("id") or "")) is not None)
    has_check = any(CHECK_VERB.search(t) and CHECK_SRC.search(t) and not BYLINE_HEAD.match(t)
                    for t in (text_of(p) for p in body.iter() if p.tag in ("p", "li", "blockquote") and not in_author(p)))
    if not has_check:
        warn.append("「확인 과정」 단락 없음(원문을 어떻게 확인·대조·검산했는지 한 문단, 위치·소제목은 글마다 다르게 — B4)")
    fixed_h = [text_of(n) for n in body.iter() if n.tag in HEADINGS and re.fullmatch(r"\s*확인\s*과정\s*", text_of(n))]
    if fixed_h:
        warn.append("고정 소제목 「확인 과정」(B4: 소제목 이름은 글마다 다르게)")

    # ── E5 수정 이력(B3): 수정 HTML 만 치명, 새 글에 있으면 경고 ──
    if a.revision:
        today = a.date or datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y-%m-%d")
        check_revision(body, btext, a.revision, today, fatal, info)
    # 새 글의 「게시일 · 최종 수정일 · 수정 이력」은 저자 박스에서 변환기가 넣는다(H-212 · 관문 5) — 경고하지 않는다.

    # ── 화살표(표 밖) ──
    outside = text_of(body, skip=lambda n: n.tag == "table")
    arr = re.findall(r"[→←↑↓▶▷►➜➔➡⇒]", outside)
    if arr:
        fatal.append(f"표 밖 화살표 기호 {len(arr)}개(기준 6)")

    # ── 저자 박스(v3.1) + 바이라인 앵커(v2 E1) — 검증 반영: 표지 블록 또는 「글쓴이」로 시작하는 짧은 독립 블록만 ──
    boxes = []
    for n in body.iter():
        if n is body or n.tag not in ("p", "div", "aside", "section", "footer", "address") or "contents_style" in n.cls():
            continue
        about = [k.attrs.get("href") for k in n.iter() if k.tag == "a" and is_about(k.attrs.get("href"))]
        if not about:
            continue
        marker = AUTHOR_MARK.search(" ".join(n.cls()) + " " + (n.attrs.get("id") or ""))
        t = text_of(n)
        if marker or (len(t) <= 300 and BYLINE_HEAD.match(t)):
            boxes.append((n, about))
    if not boxes:
        fatal.append("저자 박스 없음(class author·byline 블록, 또는 「글쓴이」로 시작하는 짧은 블록 + 소개 쪽 링크)")
    else:
        hrefs = [h for _, ab in boxes for h in ab]
        ok = []
        for h in hrefs:
            try:
                if unquote(urlparse(h).fragment or "") in AUTHOR_ANCHORS:
                    ok.append(h)
            except ValueError:
                pass
        info.append(f"저자 박스 {len(boxes)}개 · 소개 링크 {hrefs[0][:60]}")
        if not ok:
            fatal.append("바이라인 href가 소개 쪽 저자 앵커(#저자)가 아님(E1)")

    print(f"게이트: {a.html}  (본문 {nchar}자)")
    for x in info:
        print("  ·", x)
    for x in fatal:
        print("치명:", x)
    for x in warn:
        print("경고:", x)
    print(f"치명 {len(fatal)} · 경고 {len(warn)}")
    sys.exit(1 if fatal else 0)


if __name__ == "__main__":
    main()
