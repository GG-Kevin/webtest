#!/usr/bin/env python3
"""scout — 네이버 1군 RSS 72시간 합의 → 구글·네이버 질문 원문 → 원문 열림 → gate_topic (0토큰, 표준 라이브러리만).

사용:
  python3 도구/scout.py [--date YYYY-MM-DD] [--hours 72] [--repo <서치 레포>] [--max-q 3]
                        [--expand] [--no-ac] [--no-open] [--no-gate] [--gate <gate_topic.py>] [--force] [--dry-run]
산출:
  작업/<날짜>/원천표.md       — 묶음·합의 블로그·원천 URL·질문 원문·자동완성 수·사건키·열림·게이트
                               (그날 두 번째 회차부터는 원천표_<HHMM>.md, --force면 원천표.md를 덮는다)
  운영/질문은행.csv           — 줄 추가(칸 고정: 날짜,질문,구글자동완성,네이버자동완성,합의블로그,합의수,원천URL,사건키,사건일,원문URL,열림,gate_topic)
                               같은 날짜·같은 질문은 다시 넣지 않는다.
순서(본사 안 1-2): ① 네이버 합의 → ② 구글·네이버 질문 원문 → ③ 게이트 → ④ 원문 열림.
  - 1군 10곳은 매번 전부 받는다. 2군은 합의 집계에만 쓴다(2군만으로 된 묶음은 버린다).
  - 합의 = 1군 2곳 이상이 창(기본 72시간) 안에 같은 묶음을 썼다, 또는 1군 1곳 + 달력(운영/달력_*.md)의 오늘 이후 사건.
  - 서치 분야(세금·연금·지원금·정책·증시제도·생활금융)만 남긴다. 개별 종목 시황·상품 추천·공모주 한 종목은 뺀다.
    공모주 글이 있으면 「M월 공모주 청약 일정」 묶음 후보 한 줄만 낸다(월 1편, v2 B1).
  - 묶는 규칙은 README_정찰.md 「묶기」 절(주제 닻 표 ANCHORS → 없으면 핵심 명사 2개 겹침).
원천 본문은 받지 않는다(RSS의 제목·링크·시각·카테고리만 쓴다). 제목·URL만 원천표에 적는다.
종료코드: 0 = 끝까지 돎 · 1 = 1군 RSS를 하나도 못 받음 · 2 = 사용 오류
"""
import argparse
import csv
import datetime as dt
import email.utils
import html
import json
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True  # 도구/에 __pycache__를 남기지 않는다(커밋 대상 아님)
sys.path.insert(0, HERE)
from source_open import fetch, open_check  # noqa: E402
import autocomplete as ac  # noqa: E402
from calendar_build import EventIndex, gate_dir_default, read_calendar  # noqa: E402

KST = dt.timezone(dt.timedelta(hours=9))
HQ_GATE_PY = "/home/user/claude_ebook/본사/게이트/서치/gate_topic.py"
BANK_COLS = ["날짜", "질문", "구글자동완성", "네이버자동완성", "합의블로그", "합의수", "원천URL", "사건키", "사건일",
             "원문URL", "열림", "gate_topic"]

# ── 원천 3군 중 네이버 1·2군(본사 안 1-1, R-003 B-ⓐ-1) ─────────────────────────────
GROUP1 = [("ya_nt", "청년개미"), ("press02", "재미진 저널리스트"), ("secretbankbook", "비밀통장"),
          ("hermebook", "에르메"), ("8starstarstar8", "스크랩유미"), ("cs1487", "오쿤"), ("vipro", "지델롱"),
          ("meaning87", "은퇴연구소"), ("meyou27", "아임플래너"), ("msql", "아이언")]
GROUP2 = [("loonshots88", "비아이"), ("partner6766", "아이엠그레이트"), ("doomaker", "모아이형"),
          ("92happywoo", "꿈꾸는에릭"), ("xuenxu", "슈엔슈"), ("gjwlh", "한대디"), ("traderfeels", "트필"),
          ("ssibar1188", "킴찹(ID 추정)"), ("phpboy", "전선인간(ID 추정)")]
GROUP2_UNKNOWN = ["난그르타", "짠테커 루시"]  # R-003 B1에 ID가 없다 → README 「2군 ID 확인 안 됨」

# ── 서치 분야 거르기 ────────────────────────────────────────────────────────────
FIELD = [
    ("세금", r"세금|세액|공제|과세|비과세|절세|환급|증여|상속|양도세|양도소득|종소세|종합소득|부가세|부가가치세|종부세|종합부동산|"
             r"재산세|취득세|연말정산|원천징수|국세청|홈택스|금융소득|배당소득|소득세|세법|세제|금투세|증권거래세|중간예납"),
    ("연금", r"국민연금|기초연금|퇴직연금|퇴직금|연금저축|irp|개인연금|주택연금|노령연금|연금"),
    ("지원금·정책", r"지원금|장려금|수당|바우처|청년|정책|복지|기초생활|생계급여|소상공인|민생|소비쿠폰|지역화폐|고유가|"
                   r"부모급여|아동수당|육아휴직|출산|실업급여|구직급여|국민참여성장펀드|국민성장펀드|정부|신청"),
    ("증시제도", r"휴장|개장|폐장|공매도|대주주|상장폐지|관리종목|거래정지|배당기준일|배당락|분배금|자사주|서킷브레이커|사이드카|"
               r"동시만기|애프터마켓|프리마켓|넥스트레이드|isa|예탁금|반대매매|공모주|수요예측|청약|금통위|fomc|기준금리"),
    ("생활금융", r"대출|금리|예금|적금|주담대|주택담보|전세|월세|보금자리론|디딤돌|신생아특례|버팀목|dsr|ltv|신용점수|보험료|실손|"
               r"실비|건강보험|건보료|피부양자|연봉|실수령|월급|최저임금|주휴수당|순자산|소득분위|상위\d|계급표|계급도|중위소득|"
               r"생활비|파킹통장|cma|환율|통장|카드|캐시백"),
]
EXCLUDE = (r"주가|목표가|목표주가|전망|급등|급락|상한가|하한가|시황|손절|매수|매도|추천주|관련주|수혜주|테마주|대장주|"
           r"폭등|폭락|\d+배|실적|어닝|포트폴리오|종목|배당주|코스피|코스닥|나스닥|s&p|다우|비트코인|코인|리딩방|급반등|반등")
# 개별 종목 이름(배당금·주가를 다루는 개별 종목 글은 저널 몫 — 뺀다): 이름표 + 회사 이름 꼬리
STOCK_NAMES = (r"삼성전자|하이닉스|현대차|셀트리온|카카오|알테오젠|에코프로|고려아연|한미반도체|삼성바이오|포스코|두산|한화|"
               r"테슬라|엔비디아|애플|마이크론|팔란티어|스페이스x|브로드컴|아마존|마이크로소프트|tsmc|코인베이스|"
               r"리츠|맥쿼리|kb금융|신한지주|하나금융|우리금융|메리츠|삼성생명|삼성화재|sk텔레콤|kt&g|기업은행")
STOCK_TAIL = re.compile(r"[가-힣A-Za-z0-9]{1,8}(전자|하이닉스|바이오로직스|바이오|제약|증권|화학|중공업|조선|에너지솔루션|반도체|"
                        r"로보틱스|건설|자동차|생명|화재|해상|지주|홀딩스|엔터)(?=$|[^가-힣A-Za-z0-9])")
ETF_BRAND = r"kodex|tiger|ace|sol|rise|plus|kbstar|arirang|hanaro|kosef|timefolio|1q"
ETF_OK = r"분배금|지급일|세금|과세|배당기준일|절세|isa"
IPO_ANY = r"공모주|공모청약|수요예측|ipo|상장일|균등배정|비례배정|증거금"
IPO_SCHEDULE = r"(\d{1,2}월|이번주|다음주|이번 주|다음 주|주간|일정)"

# ── 묶기: 주제 닻(위에서부터 먼저 맞는 것 하나가 그 글의 묶음) ─────────────────────────
# (이름, 정규식(정규화한 제목: NFKC·소문자·공백 제거), 씨앗(자동완성), 분야, 대표 원문 URL)
NTS = "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?"
ANCHORS = [
    ("증여세(결혼·자녀·가족 간)", r"증여|(자녀|자식|부모|가족|부부|배우자).{0,10}(이체|송금).{0,10}세",
     ["결혼 증여세", "자녀 증여세", "가족 간 이체 증여세"], "세금", NTS + "mi=2338&cntntsId=7726"),
    ("상속세", r"상속", ["상속세"], "세금", NTS + "mi=2324&cntntsId=7718"),
    ("국민연금", r"국민연금", ["국민연금"], "연금", "https://www.nps.or.kr/"),
    ("기초연금", r"기초연금", ["기초연금"], "연금", "https://basicpension.mohw.go.kr/"),
    ("퇴직금·퇴직연금", r"퇴직금|퇴직연금|퇴직소득|퇴직급여", ["퇴직금"], "연금", "https://www.easylaw.go.kr/CSP/Main.laf"),
    ("연말정산", r"연말정산|13월의월급", ["연말정산"], "세금", NTS + "mi=2304&cntntsId=238938"),
    ("건강보험료·피부양자", r"건강보험료|건보료|피부양자|지역가입자|직장가입자", ["건강보험료"], "생활금융", "https://www.nhis.or.kr/nhis/index.do"),
    ("청년미래적금", r"청년미래적금", ["청년미래적금"], "지원금·정책", "https://www.fsc.go.kr/"),
    ("청년도약계좌", r"청년도약계좌", ["청년도약계좌"], "지원금·정책", "https://www.fsc.go.kr/"),
    ("보금자리론·정책대출", r"보금자리론|디딤돌|신생아특례|버팀목|정책대출|특례대출|정책모기지", ["보금자리론"], "생활금융", "https://www.hf.go.kr/"),
    ("주택청약", r"주택청약|청약통장|청약저축|주택드림|청약가점|무순위", ["주택청약"], "생활금융", "https://nhuf.molit.go.kr/"),
    ("근로·자녀장려금", r"근로장려금|자녀장려금", ["근로장려금"], "지원금·정책", NTS + "mi=2453&cntntsId=7784"),
    ("순자산·소득 분위", r"순자산|계급표|계급도|소득분위|자산분위|상위\d+(%|프로|퍼센트)|소득상위|자산상위|중위소득",
     ["순자산 상위", "소득 상위 10%"], "생활금융", "https://kosis.kr/"),
    ("연봉 실수령액", r"실수령|세후월급|세후연봉|월급계산", ["연봉 실수령액"], "생활금융", NTS + "mi=2289&cntntsId=7701"),
    ("실업급여", r"실업급여|구직급여", ["실업급여"], "지원금·정책", "https://www.work24.go.kr/"),
    ("출산·육아 지원", r"부모급여|아동수당|육아휴직|출산지원금|첫만남이용권|출산장려금", ["부모급여"], "지원금·정책", "https://www.mohw.go.kr/"),
    ("공모주 월 일정", IPO_ANY, [], "증시제도", "https://dart.fss.or.kr/"),
    ("증시 휴장·개장", r"휴장|개장시간|장시간|폐장|쉬는날|증시쉬|주식시장쉬", ["주식 휴장일"], "증시제도",
     "https://open.krx.co.kr/contents/MKD/01/0110/01100305/MKD01100305.jsp"),
    ("ETF 분배금·배당 일정", r"분배금|배당기준일|배당락|배당일|배당금지급", ["ETF 분배금 지급일"], "증시제도", "https://dart.fss.or.kr/"),
    ("기준금리·금통위·FOMC", r"기준금리|금통위|금리인하|금리인상|금리동결|fomc|연준", ["기준금리"], "증시제도",
     "https://www.bok.or.kr/portal/singl/crncyPolicyDrcMtg/listYear.do?mtgSe=A&menuNo=200755"),
    ("양도소득세", r"양도세|양도소득", ["양도소득세"], "세금", NTS + "mi=2308&cntntsId=7707"),
    ("종합소득세", r"종합소득세|종소세|중간예납", ["종합소득세"], "세금", NTS + "mi=2224&cntntsId=7664"),
    ("부가가치세", r"부가세|부가가치세", ["부가세 예정신고"], "세금", NTS + "mi=2272&cntntsId=7693"),
    ("종부세·재산세·취득세", r"종부세|종합부동산세|재산세|취득세", ["종부세"], "세금", NTS + "mi=2351&cntntsId=7733"),
    ("금융소득 과세", r"금융소득|배당소득|이자소득|분리과세", ["금융소득 종합과세"], "세금", NTS + "mi=2224&cntntsId=7664"),
    ("연금저축·IRP·ISA", r"연금저축|irp|isa|개인연금", ["연금저축"], "연금", "https://www.law.go.kr/법령/소득세법"),
    ("국민참여성장펀드", r"국민참여성장펀드|국민성장펀드", ["국민참여성장펀드"], "지원금·정책", "https://www.fsc.go.kr/"),
    ("세제개편·금투세", r"금투세|세제개편|증권거래세|세법개정", ["세제개편안"], "세금", "https://www.moef.go.kr/"),
    ("증시 제도(상폐·관리·공매도 등)", r"상장폐지|관리종목|거래정지|투자주의|투자경고|공매도|서킷브레이커|사이드카|동시만기|애프터마켓|넥스트레이드|대주주|자사주소각",
     ["상장폐지 요건"], "증시제도", "https://open.krx.co.kr/"),
    ("주택담보·전세 대출", r"주담대|주택담보대출|전세대출|dsr|ltv|신용대출|대출금리|대출규제", ["주택담보대출"], "생활금융", "https://www.fss.or.kr/"),
    ("예금·적금·파킹통장", r"예금금리|적금금리|파킹통장|cma|고금리적금|특판", ["적금 금리"], "생활금융", "https://finlife.fss.or.kr/"),
    ("실손·보험료", r"실손|실비|보험료", ["실손보험"], "생활금융", "https://www.fss.or.kr/"),
    ("최저임금·주휴수당", r"최저임금|주휴수당|통상임금", ["최저임금"], "생활금융", "https://www.minimumwage.go.kr/"),
    ("환율", r"환율|달러", ["환율"], "생활금융", "https://www.bok.or.kr/"),
    ("정부 지원금·쿠폰", r"지원금|바우처|소비쿠폰|민생|고유가|에너지바우처|지역화폐|환급금", ["지원금 신청"], "지원금·정책", "https://www.mohw.go.kr/"),
]
STOP = set("""총정리 정리 방법 신청방법 신청 조건 대상 기간 금액 얼마 이유 꿀팁 확인 알아보기 하는법 혜택 최신 최대 무조건 꼭 이것
진짜 정말 지금 오늘 내일 이번 다음 올해 내년 2025 2026 2027 2025년 2026년 2027년 1월 2월 3월 4월 5월 6월 7월 8월 9월 10월 11월 12월
한눈에 바로 쉽게 모두 전부 가지 개 원 만원 억 억원 이상 이하 받는 받을 받으려면 받기 받고 하는 하면 되는 된다 됩니다 있다 없다 있는 없는
나요 까요 무엇 뭐 왜 언제 어떻게 어디서 누가 그리고 그래서 하지만 때문 위한 관련 대한 통해 우리 내 나 저 이 그 것 수 등 및 더 덜 안 못
후기 리뷰 이야기 소식 뉴스 공개 발표 공지 안내 정보 가이드 tip top 베스트 추천 비교 차이 장단점 기준 계산 계산법 계산기 예시 사례 표""".split())
# 낱말 끝 조사 떼기. 「이·가·도·로·과·만」은 낱말 끝 글자와 헷갈려(나이·차이·제도·경로·결과) 떼지 않는다.
JOSA = ("에서는", "으로는", "이라는", "라는", "에서", "으로", "까지", "부터", "에게", "한테", "이란", "보다", "처럼", "만큼",
        "은", "는", "을", "를", "에", "의", "와")


def nk(s):
    return re.sub(r"[\s·ㆍ‧∙•・\-&/'\"“”‘’\[\]()<>「」『』!?,.:;~]+", "", unicodedata.normalize("NFKC", s or "").lower())


def tokens(title):
    out = []
    for w in re.findall(r"[가-힣A-Za-z0-9%]+", unicodedata.normalize("NFKC", title or "")):
        w = w.lower()
        for j in JOSA:
            if len(w) > len(j) + 1 and w.endswith(j):
                w = w[: -len(j)]
                break
        if len(w) >= 2 and w not in STOP and not re.fullmatch(r"\d+", w):
            out.append(w)
    return out


# ── RSS ────────────────────────────────────────────────────────────────────────
def read_rss(blog):
    url = f"https://rss.blog.naver.com/{blog}.xml"
    r = fetch(url, timeout=20)
    if r["reason"]:
        return None, r["reason"]
    items = []
    for it in re.findall(r"<item>(.*?)</item>", r["text"], re.S):
        def tag(n):
            m = re.search(rf"<{n}>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</{n}>", it, re.S)
            return html.unescape(m.group(1).strip()) if m else ""
        try:
            when = email.utils.parsedate_to_datetime(tag("pubDate")).astimezone(KST)
        except (TypeError, ValueError):
            continue
        link = tag("guid") or re.sub(r"\?.*$", "", tag("link"))
        items.append({"blog": blog, "title": tag("title"), "url": link, "when": when,
                      "category": tag("category"), "tags": tag("tag")})
    return items, None


def classify(p):
    t = nk(p["title"])
    ctx = t + nk(p["category"]) + nk(p["tags"])
    if re.search(IPO_ANY, t):
        p["ipo"] = "일정" if re.search(IPO_SCHEDULE, p["title"]) and not re.search(r"수요예측|경쟁률|균등배정|비례배정", t) else "단일"
        return "증시제도"
    if re.search(EXCLUDE, t) or re.search(STOCK_NAMES, t) or STOCK_TAIL.search(p["title"] or ""):
        p["drop"] = "종목·시황"
        return None
    if re.search(ETF_BRAND, t) and not re.search(ETF_OK, t):
        p["drop"] = "개별 상품"
        return None
    for name, rx in FIELD:
        if re.search(rx, t):
            return name
    for name, rx in FIELD:
        if re.search(rx, ctx) and not re.search(r"주식|코인|etf", nk(p["category"])):
            return name
    p["drop"] = "분야 밖"
    return None


def anchor_of(p):
    t = nk(p["title"])
    for a in ANCHORS:
        if re.search(a[1], t):
            return a
    return None


class UF:
    def __init__(self, n):
        self.p = list(range(n))

    def f(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def u(self, a, b):
        a, b = self.f(a), self.f(b)
        if a != b:
            self.p[b] = a


def cluster(posts):
    by_anchor = defaultdict(list)
    rest = []
    for p in posts:
        if p.get("ipo"):
            by_anchor["공모주 월 일정"].append(p)
            continue
        a = anchor_of(p)
        if a:
            p["anchor"] = a
            by_anchor[a[0]].append(p)
        else:
            rest.append(p)
    groups = []
    amap = {a[0]: a for a in ANCHORS}
    for name, ps in by_anchor.items():
        groups.append({"name": name, "anchor": amap.get(name), "posts": ps})
    # 닻 없는 글: 서로 다른 블로그끼리 핵심 명사 2개 이상 겹치면 묶는다
    toks = [set(tokens(p["title"])) for p in rest]
    uf = UF(len(rest))
    for i in range(len(rest)):
        for j in range(i + 1, len(rest)):
            if rest[i]["blog"] != rest[j]["blog"] and len(toks[i] & toks[j]) >= 2:
                uf.u(i, j)
    comp = defaultdict(list)
    for i in range(len(rest)):
        comp[uf.f(i)].append(i)
    for idxs in comp.values():
        ps = [rest[i] for i in idxs]
        c = Counter(w for i in idxs for w in toks[i])
        common = [w for w, n in c.most_common() if n >= 2][:2] or [w for w, _ in c.most_common(2)]
        groups.append({"name": " ".join(common) or ps[0]["title"][:12], "anchor": None, "posts": ps,
                       "seed": " ".join(common)})
    for g in groups:
        g["b1"] = sorted({p["blog"] for p in g["posts"] if p["grp"] == 1})
        g["b2"] = sorted({p["blog"] for p in g["posts"] if p["grp"] == 2})
        g["field"] = g["anchor"][3] if g["anchor"] else Counter(p["field"] for p in g["posts"]).most_common(1)[0][0]
    return groups


# ── 질문 고르기 ─────────────────────────────────────────────────────────────────
QWORD = r"얼마|언제|조건|기준|방법|신청|계산|한도|나이|기간|대상|금액|지급일|날짜|일정|차이|세금|면제|공제|신고|수령|자격|소득"


NAV = r"(공단|공사|홈페이지|사이트|로그인|고객센터|콜센터|어플|앱|전화번호|주소|지점|은행|카페|블로그|뉴스)$"


def rank_candidates(g, expand, limit=8):
    """묶음 → 자동완성 원문 후보 순위(점수 높은 순, 최대 limit). 씨앗 = 닻 씨앗 + 「닻 씨앗 + 묶음 제목에 2번 이상 나온 낱말」."""
    seeds = list(g["anchor"][2]) if g["anchor"] else ([g["seed"]] if g.get("seed") else [])
    ctoks = Counter(w for p in g["posts"] for w in set(tokens(p["title"])))
    hot = [w for w, n in ctoks.most_common() if n >= 2 and not re.match(r"\d", w)]
    if seeds:
        b = nk(seeds[0])
        extra = [w for w in hot if w not in b and b not in w]
        if extra:
            seeds.append(f"{seeds[0]} {extra[0]}")
    cand = {}
    notes = []
    for s in seeds[:4]:
        e = ac.expand(s, None, expand)
        if not e["google_all"] and all(r["google"] is None for r in e["rows"]):
            notes.append(f"구글 못 열었다({ac.LAST_ERR.get('google', '')})")
            continue
        nkeys = {ac.key(x): x for x in e["naver_all"]}
        for q in e["google_all"]:
            kq = ac.key(q)
            if kq == ac.key(s) or kq in {ac.key(x) for x in cand}:
                continue
            words = q.split()
            sc = (3 if kq in nkeys else 0) + 2 * sum(1 for w in tokens(q) if ctoks.get(w, 0) >= 2) \
                + (2 if re.search(QWORD, q) else 0) + (1 if len(words) >= 3 else 0) \
                - (4 if re.search(NAV, q.strip()) else 0) - (3 if any(a == b for a, b in zip(words, words[1:])) else 0)
            cand[q] = {"q": q, "seed": s, "n_in_seed": kq in nkeys, "n_form": nkeys.get(kq, ""), "score": sc}
    ranked = sorted(cand.values(), key=lambda x: -x["score"])[:limit]
    return ranked, notes


def finalize(q):
    """고른 질문 하나의 자동완성 개수·네이버 원문 여부를 채운다(질문 자체를 다시 넣어 본다)."""
    b = ac.both(q["q"])
    q.update({"g_n": b["g_n"], "n_n": b["n_n"], "n_has": bool(q.get("n_in_seed") or b["n_has"]), "g_has": True})
    # 네이버 원문이 다른 표기(「10 프로」 ↔ 「10%」)로만 있으면, 네이버 표기 그대로 넣어 개수를 잰다
    nf = q.get("n_form") or ""
    if q["n_has"] and nf and nf != q["q"] and not b["n_has"]:
        nb = ac.naver(nf)
        q["n_n"] = None if nb is None else len(nb)
        q["n_note"] = f"네이버 표기 「{nf}」"
    return q


# ── 게이트 ──────────────────────────────────────────────────────────────────────
def find_gate(repo, explicit):
    for p in [explicit, os.path.join(repo, ".claude", "gate", "gate_topic.py"), HQ_GATE_PY]:
        if p and os.path.exists(p):
            return p
    return None


def run_gate(gate, repo, rows):
    """rows: [(문구, 사건키)] → [판정 문자열], 요약"""
    if not gate:
        return ["게이트 없음"] * len(rows), "게이트 없음"
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        for q, k in rows:
            f.write(f"{q.replace(chr(9), ' ')}\t{k or '-'}\n")
        tmp = f.name
    try:
        r = subprocess.run([sys.executable, gate, tmp, "--repo", repo, "--json"], capture_output=True, text=True, timeout=300)
    finally:
        os.unlink(tmp)
    if r.returncode not in (0, 1):
        return [f"게이트 오류({r.returncode})"] * len(rows), "게이트 오류: " + (r.stderr.strip().splitlines() or [""])[-1][:120]
    try:
        data = json.loads(r.stdout)
    except ValueError:
        return ["게이트 오류(출력 해석 실패)"] * len(rows), "게이트 오류: JSON 아님"
    by_line = {x["line"]: x for x in data["results"]}
    out = []
    for i in range(1, len(rows) + 1):
        x = by_line.get(i)
        if not x:
            out.append("게이트 결과 없음")
            continue
        tag = f"({x['tag']})" if x.get("tag") else ""
        if x["verdict"] == "실패":
            h, s = (x["reasons"][0] if x["reasons"] else ["", ""])
            out.append(f"실패: {h} ← {s}")
        else:
            out.append(f"통과{tag}")
    sm = data["summary"]
    sha = sm.get("sha256", {}).get("gate_topic.py", "")
    return out, f"{gate} (sha256 앞 16자 {sha}) · 합계 {sm['합계']} · 통과 {sm['통과']} · 실패 {sm['실패']}"


# ── 본체 ────────────────────────────────────────────────────────────────────────
def main(argv=None):
    ap = argparse.ArgumentParser(description="네이버 1군 RSS 합의 정찰(0토큰)")
    ap.add_argument("--date", help="한국 날짜 YYYY-MM-DD(기본 오늘). 과거 날짜면 그날 23:59 KST까지를 창 끝으로 본다")
    ap.add_argument("--hours", type=int, default=72)
    ap.add_argument("--repo", default=os.path.normpath(os.path.join(HERE, "..")))
    ap.add_argument("--max-q", type=int, default=3, help="묶음당 질문 수(기본 3)")
    ap.add_argument("--expand", action="store_true", help="씨앗 × 접미어 확장(호출이 10배)")
    ap.add_argument("--no-ac", action="store_true")
    ap.add_argument("--no-open", action="store_true")
    ap.add_argument("--no-gate", action="store_true")
    ap.add_argument("--gate", help="gate_topic.py 경로(기본: 레포 .claude/gate → 본사 원본)")
    ap.add_argument("--force", action="store_true", help="원천표.md를 덮는다")
    ap.add_argument("--dry-run", action="store_true", help="파일을 쓰지 않고 화면에만")
    a = ap.parse_args(argv)

    now = dt.datetime.now(KST)
    day = dt.date.fromisoformat(a.date) if a.date else now.date()
    end = now if day == now.date() else dt.datetime.combine(day, dt.time(23, 59, 59), KST)
    start = end - dt.timedelta(hours=a.hours)
    repo = os.path.abspath(a.repo)
    if not os.path.isdir(os.path.join(repo, "운영")):
        print(f"오류: {repo}에 운영/ 폴더가 없다", file=sys.stderr)
        return 2

    # ① RSS
    feed_state = []
    posts = []
    for grp, lst in ((1, GROUP1), (2, GROUP2)):
        for blog, nick in lst:
            items, err = read_rss(blog)
            if items is None:
                feed_state.append((grp, blog, nick, f"못 열었다({err})", 0, 0))
                continue
            inwin = [x for x in items if start <= x["when"] <= end]
            oldest = min((x["when"] for x in items), default=None)
            full = "" if not oldest or oldest <= start else f" · RSS 50편이 창을 다 못 덮음(가장 옛 글 {oldest:%m-%d %H:%M})"
            feed_state.append((grp, blog, nick, "받음" + full, len(items), len(inwin)))
            for x in inwin:
                x["grp"] = grp
                x["nick"] = nick
                posts.append(x)
    n1_ok = sum(1 for s in feed_state if s[0] == 1 and s[3].startswith("받음"))
    if n1_ok == 0:
        print("1군 RSS를 하나도 못 받았다", file=sys.stderr)

    drops = Counter()
    kept = []
    for p in posts:
        f = classify(p)
        if f:
            p["field"] = f
            kept.append(p)
        else:
            drops[(p["grp"], p.get("drop", "?"))] += 1
    ipo_posts = [p for p in kept if p.get("ipo")]
    groups = [g for g in cluster(kept) if g["b1"]]

    # 달력·사건키
    cal = read_calendar(repo, day)
    gdir = gate_dir_default(repo)
    eidx = EventIndex(gdir)
    for g in groups:
        keys = []
        for p in g["posts"]:
            for r in eidx.find(p["title"]):
                if r["key"] not in keys:
                    keys.append(r["key"])
        g["events"] = keys
        g["cal"] = [k for k in keys if k in cal]
        if len(g["b1"]) >= 2:
            g["consensus"] = f"1군 {len(g['b1'])}곳"
        elif g["cal"]:
            g["consensus"] = "1곳+달력"
        else:
            g["consensus"] = ""
    # 공모주: 묶음 한 줄로(월 1편)
    ipo_group = next((g for g in groups if g["name"] == "공모주 월 일정"), None)
    groups = [g for g in groups if g["name"] != "공모주 월 일정"]
    ipo_month = day.month if day.day < 20 else (day.month % 12) + 1
    ok_groups = [g for g in groups if g["consensus"]]
    ok_groups.sort(key=lambda g: (-len(g["b1"]), -len(g["b2"]), 0 if g["cal"] else 1, g["name"]))
    weak = [g for g in groups if not g["consensus"]]

    # ② 질문 — 후보 순위 → (게이트를 먼저 한 번에 돌려) 통과 상위 max_q + 막힌 상위 1개만 자동완성 개수를 잰다
    gate = None if a.no_gate else find_gate(repo, a.gate)
    pre = []
    for gi, g in enumerate(ok_groups, 1):
        g["no"] = gi
        if a.no_ac:
            g["ranked"], g["notes"] = [], ["자동완성 안 봄(--no-ac)"]
        else:
            g["ranked"], g["notes"] = rank_candidates(g, a.expand)
        for q in g["ranked"]:
            ek = [r["key"] for r in eidx.find(q["q"])]
            q["key"] = next((k for k in ek if k in g["events"]), ek[0] if ek else (g["cal"][0] if g["cal"] else "-"))
            pre.append(q)
    pv, _ = run_gate(gate, repo, [(q["q"], q["key"]) for q in pre]) if pre else ([], "")
    for q, v in zip(pre, pv):
        q["gate"] = v
    qrows = []
    for g in ok_groups:
        ok = [q for q in g["ranked"] if not q["gate"].startswith("실패")][: a.max_q]
        ng = [q for q in g["ranked"] if q["gate"].startswith("실패")][:1]
        g["n_blocked"] = sum(1 for q in g["ranked"] if q["gate"].startswith("실패"))
        for q in ok + ng:
            qrows.append((g, finalize(q)))
    ipo_line = None
    if ipo_group and ipo_group["b1"]:
        qtxt = f"{ipo_month}월 공모주 청약 일정"
        b = ac.both(qtxt) if not a.no_ac else {"g_n": None, "n_n": None, "g_has": None, "n_has": None}
        ipo_line = {"g": ipo_group, "q": {"q": qtxt, "seed": qtxt, "g_n": b["g_n"], "n_n": b["n_n"],
                                          "n_has": bool(b["n_has"]), "g_has": bool(b["g_has"]),
                                          "key": f"공모주{ipo_month}월"}}
        ipo_group["no"] = "공모"
        qrows.append((ipo_group, ipo_line["q"]))

    # ④ 원문 열림(묶음마다 대표 원문 하나, 달력 사건이면 달력의 공식 URL을 먼저)
    open_cache = {}
    for g in ok_groups + ([ipo_group] if ipo_line else []):
        url = cal[g["cal"][0]][1] if g.get("cal") and g["cal"][0] in cal else (g["anchor"][4] if g["anchor"] else "")
        g["src_url"] = url
        if not url or a.no_open:
            g["open"] = "확인 안 함" if a.no_open else "원문 URL 없음(닻 없는 묶음 — 작가가 찾는다)"
            continue
        if url not in open_cache:
            open_cache[url] = open_check(url)["verdict"]
        g["open"] = open_cache[url]

    # ③ 게이트 — 남은 줄(공모주 묶음 줄)까지 한 번 더 모두 돌려 요약 줄을 만든다(이미 본 줄은 같은 결과)
    verdicts, gate_sum = run_gate(gate, repo, [(q["q"], q["key"]) for _, q in qrows]) if qrows else ([], "후보 없음")
    for (g, q), v in zip(qrows, verdicts):
        q["gate"] = v

    # 쓰기
    stamp = now.strftime("%Y-%m-%d %H:%M")
    wdir = os.path.join(repo, "작업", day.isoformat())
    out_path = os.path.join(wdir, "원천표.md")
    if os.path.exists(out_path) and not a.force:
        out_path = os.path.join(wdir, f"원천표_{now:%H%M}.md")
    L = [f"# 원천표 {day.isoformat()} — 네이버 1군 합의 → 질문 원문 (scout.py)", "",
         f"- 회차: {stamp} KST · 창: {start:%Y-%m-%d %H:%M} ~ {end:%Y-%m-%d %H:%M} KST ({a.hours}시간)",
         f"- 1군 RSS {n1_ok}/{len(GROUP1)}곳 받음 · 2군 {sum(1 for s in feed_state if s[0] == 2 and s[3].startswith('받음'))}/{len(GROUP2)}곳 받음 · "
         f"2군 ID 확인 안 됨: {'·'.join(GROUP2_UNKNOWN)}",
         f"- 창 안 글: 1군 {sum(1 for p in posts if p['grp'] == 1)}편(서치 분야 {sum(1 for p in kept if p['grp'] == 1)}편) · "
         f"2군 {sum(1 for p in posts if p['grp'] == 2)}편(서치 분야 {sum(1 for p in kept if p['grp'] == 2)}편)",
         "- 뺀 글(1군/2군): " + " · ".join(f"{k[1]} {drops[(1, k[1])]}/{drops[(2, k[1])]}" for k in sorted({(0, d) for _, d in drops})) if drops else "- 뺀 글: 없음",
         f"- 합의 묶음 {len(ok_groups)}개 · 합의 미달 {len(weak)}개 · 공모주 묶음 후보 {'1줄' if ipo_line else '없음'}",
         f"- 달력: 운영/달력_*.md 오늘 이후 사건 {len(cal)}개 · 사건키.tsv: {gdir or '없음'}",
         f"- 게이트: {gate_sum}",
         "- 합의 = 1군 2곳 이상(72시간) 또는 1군 1곳 + 달력 사건. 2군은 「2군 동조」 칸(순서 정하기)에만 센다.",
         "- 다음 단계 조건(본사 안 1-2): ② 구글 원문 + 네이버 원문(네이버 칸 0이면 미달) → ③ 게이트 통과 → ④ 원문 「열림」(아니면 보류).",
         "", "## 1. 합의 묶음(우선순위 순)",
         "| # | 묶음 | 분야 | 합의 | 1군 블로그 | 2군 동조 | 원천 URL(1군) | 사건키(사건일) | 대표 원문 | 열림 |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for g in ok_groups:
        urls = " ".join(p["url"] for p in g["posts"] if p["grp"] == 1)
        ev = ", ".join(f"{k}({cal[k][0].isoformat()})" if k in cal else k for k in g["events"]) or "-"
        L.append(f"| {g['no']} | {g['name']} | {g['field']} | {g['consensus']} | {', '.join(g['b1'])} | "
                 f"{', '.join(g['b2']) or '-'} | {urls} | {ev} | {g.get('src_url') or '-'} | {g.get('open', '-')} |")
    if not ok_groups:
        L.append("| - | (합의 묶음 없음) | | | | | | | | |")
    L += ["", "## 2. 질문 후보(구글 자동완성 원문)",
          "| 묶음# | 질문 원문 | 씨앗 | 구글 n | 네이버 n | ② 두 곳 원문 | 사건키 | 열림 | 게이트 |", "|---|---|---|---|---|---|---|---|---|"]
    for g, q in qrows:
        nn = q["n_n"] if q["n_has"] else 0
        na = "안 봄" if a.no_ac else "못 열었다"
        L.append(f"| {g['no']} | {q['q']}{(' (' + q['n_note'] + ')') if q.get('n_note') else ''} | {q['seed']} | {q['g_n'] if q['g_n'] is not None else na} | "
                 f"{nn if q['n_n'] is not None else na} | {'예' if q['n_has'] and q.get('g_has') else '아니오'} | "
                 f"{q['key']} | {g.get('open', '-')} | {q.get('gate', '-')} |")
    for g in ok_groups:
        if g.get("notes"):
            L.append(f"| {g['no']} | (질문 없음: {'; '.join(g['notes'])}) | | | | | | | |")
        if g.get("n_blocked"):
            L.append(f"| {g['no']} | (후보 {len(g.get('ranked', []))}개 중 게이트에 막힌 것 {g['n_blocked']}개 — 위 「실패」 줄은 그중 점수 1위) | | | | | | | |")
    if not qrows:
        L.append("| - | (질문 후보 없음) | | | | | | | |")
    L += ["", "## 3. 공모주 월 묶음 후보(월 1편, v2 B1)"]
    if ipo_line:
        g = ipo_line["g"]
        n_single = sum(1 for p in ipo_posts if p.get("ipo") == "단일")
        L.append(f"- 「{ipo_line['q']['q']}」 · 사건키 {ipo_line['q']['key']} · 공모주 글 1군 {len(g['b1'])}곳({', '.join(g['b1'])})"
                 f" · 2군 {len(g['b2'])}곳 · 한 종목 글 {n_single}편은 뺐다 · 게이트 {ipo_line['q'].get('gate', '-')}")
    else:
        L.append("- 없음(창 안 1군 공모주 글 0편)")
    L += ["", "## 4. 합의 미달(참고 — 질문은행에 넣지 않는다)", "| 묶음 | 분야 | 1군 | 2군 | 편수 | 사건키 |", "|---|---|---|---|---|---|"]
    shown = [g for g in weak if g["anchor"] or len(g["posts"]) >= 2]
    for g in sorted(shown, key=lambda g: (-len(g["posts"]), g["name"]))[:40]:
        L.append(f"| {g['name']} | {g['field']} | {', '.join(g['b1'])} | {', '.join(g['b2']) or '-'} | {len(g['posts'])} | {', '.join(g['events']) or '-'} |")
    if not shown:
        L.append("| (없음) | | | | | |")
    if len(weak) > len(shown):
        L.append(f"- 닻 없는 1편 묶음 {len(weak) - len(shown)}개는 줄을 줄였다(서로 다른 블로그와 핵심 명사 2개가 겹치지 않은 글).")
    L += ["", "## 5. 원천 글 목록(합의 묶음·공모주 묶음만, 제목·URL만 — 본문은 받지 않는다)",
          "| 묶음# | 군 | 블로그 | 시각(KST) | 제목 | URL |", "|---|---|---|---|---|---|"]
    for g in ok_groups + ([ipo_line["g"]] if ipo_line else []):
        for p in sorted(g["posts"], key=lambda p: p["when"]):
            L.append(f"| {g['no']} | {p['grp']} | {p['blog']} | {p['when']:%m-%d %H:%M} | {p['title'].replace('|', '/')} | {p['url']} |")
    L += ["", "## 6. RSS 받기 기록", "| 군 | 블로그 | 이름 | 결과 | RSS 글 | 창 안 |", "|---|---|---|---|---:|---:|"]
    for s in feed_state:
        L.append(f"| {s[0]} | {s[1]} | {s[2]} | {s[3]} | {s[4]} | {s[5]} |")
    text = "\n".join(L) + "\n"

    # 질문은행
    bank = os.path.join(repo, "운영", "질문은행.csv")
    new_rows = []
    have = set()
    if os.path.exists(bank):
        with open(bank, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                have.add((r.get("날짜"), ac.key(r.get("질문", ""))))
    for g, q in qrows:
        if (day.isoformat(), ac.key(q["q"])) in have:
            continue
        have.add((day.isoformat(), ac.key(q["q"])))
        k = q["key"]
        b1 = ";".join(g["b1"]) + (f"+2군:{';'.join(g['b2'])}" if g["b2"] else "") + ("+달력" if g.get("consensus") == "1곳+달력" else "")
        new_rows.append({
            "날짜": day.isoformat(), "질문": q["q"],
            "구글자동완성": "" if q["g_n"] is None else q["g_n"],
            "네이버자동완성": "" if q["n_n"] is None else (q["n_n"] if q["n_has"] else 0),
            "합의블로그": b1, "합의수": len(g["b1"]),
            "원천URL": " ".join([p["url"] for p in g["posts"] if p["grp"] == 1][:6]),
            "사건키": k, "사건일": cal[k][0].isoformat() if k in cal else "-",
            "원문URL": g.get("src_url") or "-", "열림": g.get("open", "-"), "gate_topic": q.get("gate", "-")})
    if a.dry_run:
        print(text)
        print(f"# 질문은행에 더할 줄 {len(new_rows)}")
        return 0 if n1_ok else 1
    os.makedirs(wdir, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    exists = os.path.exists(bank) and os.path.getsize(bank) > 0
    with open(bank, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=BANK_COLS)
        if not exists:
            w.writeheader()
        w.writerows(new_rows)
    print(f"썼다: {out_path}")
    print(f"질문은행: +{len(new_rows)}줄 → {bank}")
    print(f"합의 묶음 {len(ok_groups)} · 질문 {len(qrows)} · 게이트 {gate_sum}")
    return 0 if n1_ok else 1


if __name__ == "__main__":
    sys.exit(main())
