#!/usr/bin/env python3
"""gate_topic — 서치 반려·중복 게이트(0토큰, 표준 라이브러리만).

본사 원본: claude_ebook 본사/게이트/서치/ · 서치 사본: <서치 레포>/.claude/gate/ (서치는 실행만 한다)

사용:
  python3 gate_topic.py <후보파일|-> [--mode topic|title] [--repo <서치 레포 루트>]
                        [--exclude-self <원장 줄번호> ...] [--only-fail] [--json]
후보파일:
  - 줄마다 「문구<TAB>사건키」(사건키가 없으면 -). 「#」 줄과 빈 줄은 건너뛴다. 문구가 빈 줄은 오류(종료 2).
  - 마크다운(.md): 머리에 주제·질문·질문원문·검색어·가제·제목·최종제목·디스커버제목·사건키(·묶음·편) 칸 중 있는 것을 가진 표.
    각도·차별점·이유 칸은 읽지 않는다. 칸 이름 끝의 (…)는 떼고 읽는다(「가제(안)」 = 가제).
    머리에 질문·제목·가제·검색어·주제 글자가 있는데 정해진 칸 이름이 아니면 종료 2(조용히 건너뛰지 않는다).
  - CSV(.csv): 같은 칸 이름(질문은행.csv·원장.csv 모양).
  --mode title: 최종 제목만 본다(표에서는 최종제목·제목·디스커버제목, 없으면 가제).
판정 순서(한 후보 안):
  ① 반려(반려대장 제목·예외 없는 낱말·정규식·본사 결정 B7) → 실패, 예외 없음
  ② 사건키(후보가 낸 키 + 사건키.tsv 정규식이 문구에서 찾은 키) 중 우리 글이 이미 다룬 사건 → 실패
  ③ 주제대장 핵심어·회장 지적 중복 낱말 → 실패. 단 일정형 예외: 사건키.tsv 정규식이 이 문구에서 찾은 「아직 안 다룬」
     달력 사건이 있고, 걸린 낱말이 모두 그 정규식이 맞은 자리 안에 있고, 이미 다룬 사건이 없고, 날짜 토큰이 있으면 통과.
     낸 키만으로는(new·미등록·문구와 안 맞는 키) 열리지 않는다
  ④ 진행분(운영/원장.csv 상태 승인·집필·완성·대기·라이브의 검색어·가제·최종제목·사건키와 겹침) → 실패
     (묶음 「기존」 줄 = 개편 전 글은 ③과 같은 층: 일정형 예외로는 안 열리고 회장 1회 예외로만 넘는다)
  ⑤ 운영/반려_추가.txt 낱말 → 실패. git 기록(커밋·작업본)에서 이 파일의 줄이 지워진 흔적이 있으면 모든 후보 실패
  ⑥ 회장 1회 예외: 운영/회장지시_원문.md 「1회 예외: <문구>」와 정확히 같은 칸 하나만 ①②③④(기존)⑤를 넘는다.
     같은 행의 나머지 칸은 평소대로 판정한다. 예외 줄 하나는 한 실행에서 후보 하나만 통과시킨다.
     ④ 이번 개편 뒤 진행분·⑤ 삭제 흔적은 못 넘는다
정규화: NFKC → 소문자 → 동의어.tsv → 공백·기호(· - & /) 제거 뒤 대조. 영문으로 시작·끝나는 낱말(VI·SPY·QQQ·IRP·ISA 등)은
  공백을 지우기 전 문구에서 앞뒤 글자가 영문이 아닐 때만 맞춘다(VIG 안의 VI, ISAAC 안의 ISA는 통과).
대조 줄 번호: 모든 「줄n」은 그 파일의 실제 줄 번호(1부터, # 줄·빈 줄 포함)다.
종료코드: 0 = 전부 통과 · 1 = 실패 있음 · 2 = 사용·데이터 오류(후보 없음·빈 문구·읽을 수 없는 표 머리·데이터 칸 수·정규식·--repo)
"""
import argparse
import bisect
import csv
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
F_REJECT = "반려대장.tsv"
F_TOPIC = "주제대장.tsv"
F_SYN = "동의어.tsv"
F_EVENT = "사건키.tsv"
R_LEDGER = os.path.join("운영", "원장.csv")
R_ADD = os.path.join("운영", "반려_추가.txt")
R_CHAIR = os.path.join("운영", "회장지시_원문.md")

SEP_CHARS = r"\s·ㆍ‧∙•・\-&/"
SEP = "[" + SEP_CHARS + "]"
SEP_RUN = re.compile(SEP + "+")
SEP_ONE = re.compile(SEP)
# 날짜 토큰(일정형 예외의 셋째 조건). 좁게 잡는다: 「3일」(일수)·「2000만원」·「2030세대」·「연말정산」·「손익분기」는 날짜가 아니다.
DATE_RE = re.compile(
    r"(?<!\d)202[4-9](?!\d)(?!\s*(?:만|억|원|천|명|개|건|세대))"   # 연도 2024~2029(금액·인원·세대가 붙으면 아님)
    r"|(?<!\d)(?:1[0-2]|0?[1-9])\s*월"                                # N월(1~12, 「13월의 월급」은 아님)
    r"|연말(?!\s*정산)"                                                # 연말(연말정산은 아님)
    r"|(?<!\d)[1-4]\s*분기|(?:이번|다음|지난|올해|내년)\s*분기|분기\s*(?:말|초)"  # 몇 분기(손익분기·분기배당은 아님)
    r"|상반기|하반기")
PROGRESS = ("승인", "집필", "완성", "대기", "라이브")
OLD_BUNDLE = "기존"   # 원장의 개편 전 글 묶음 이름
NONE_KEYS = {"", "-", "—", "–", "없음", "none"}
NEW_KEYS = {"new", "새", "새사건", "신규"}   # 이름 없는 키 = 「-」와 같다(일정형 예외를 열지 못한다)
COLS_TOPIC = ("주제", "질문", "질문원문", "검색어", "가제", "제목", "최종제목", "디스커버제목")
COLS_TITLE = ("최종제목", "제목", "디스커버제목")
COLS_KNOWN = set(COLS_TOPIC) | {"사건키", "묶음", "편"}
HEAD_HINT = ("질문", "제목", "가제", "검색어", "주제")   # 이 글자가 든 머리는 정해진 이름이어야 한다
HEAD_IGNORE = {"각도", "차별점", "이유", "메모", "비고", "자기검토", "h2질문", "근거", "주제신호", "질문수",
               "제목길이", "제목글자수", "주제어수"}   # 후보가 아닌 줄 알고 일부러 읽지 않는 칸
LEDGER_COLS = ["묶음", "편", "검색어", "가제", "최종제목", "사건키", "골격", "작가", "상태",
               "작업폴더", "대기파일", "라이브URL", "게시일", "갱신"]

# ── 본사 결정 B7 정규식(미국 ETF·해외투자) ─────────────────────────────────────
# 켜고 끄는 것은 여기서 한다. 시험 세트에서 오탐이 나면 그 줄만 False로 바꾸고 README 「B7」 절에 적는다(본사).
B7_ON = {
    "B7-1": True,   # 영문 2~5자 티커(대소문자 무관) + ETF·배당·분배·커버드콜·상장지수·레버리지·적립식 문맥
    "B7-2": True,   # 서로 다른 티커 둘 이상 + (위 문맥 또는 비교·차이·vs·추천)
    "B7-3": True,   # 미국·해외·글로벌 … ETF 문맥(「미국 배당 ETF」)
    "B7-4": True,   # 미국·해외 배당(주)
}
B7_LABEL = {
    "B7-1": "티커+ETF·배당·분배·적립식 문맥",
    "B7-2": "티커 둘 이상+문맥·비교",
    "B7-3": "미국·해외 … ETF 문맥",
    "B7-4": "미국·해외 배당",
}
# 문맥: 「적립」은 투자 적립식만(적립식 적금·예금·저축·보험, 적립금, 카드 포인트 적립은 아님)
B7_CTX = re.compile(r"etf|배당|분배|커버드콜|상장지수|레버리지|인버스"
                    r"|적립식(?!적금|예금|저축|보험)|적립투자|적립매수|(?:매달|매월|매주|매일)적립|모아가기")
B7_CMP = re.compile(r"비교|차이|vs|대신|추천|순위|뭐가|어느")
# 티커로 보지 않는 영문 낱말(제도·기관·지표·국내 회사·국내 ETF 상표·흔한 영어). 대문자로 적는다. 오탐이 나면 본사가 더한다.
B7_STOP = set("""
ETF ETFS ETN ISA IRP DC DB VI CMA ELS ELB DLS DLB ELW MMF RP TDF TRF ESG IPO SPAC BDC REIT REITS ATM OTP HTS MTS
API PDF FAQ QNA QR SNS AI IT TV PC USB OTT KTX SRT MZ PB PF PEF VC LP GP CD CP CB BW EB CDS MBS ABS EU UN US UK VS VIP
NO OK TOP NEW YES
KOSPI KOSDAQ KONEX KRX NXT DART KIND KSD KDI BOK BOJ ECB FED FOMC IMF OECD WTO GDP GNI CPI PPI PCE PMI MSCI FTSE
LTV DSR DTI LTI RTI USD KRW JPY EUR CNY GBP HKD VAT YOY MOM QOQ CEO CFO IR PER PBR ROE ROA EPS BPS EV
COFIX KOFR SOFR FX CFD
HUG LH SH HF SGI SBI SC MG KCB NICE NPS CU BC KFB
KB NH SK LG GS LS CJ KT HD DL KG JB BNK DGB IBK KDB HMM OCI KCC SPC BGF POSCO NAVER SKT SKC SKB
LX HL DN HK HDC LIG KH SGC KEC ISC GKL KTB JYP YG SM HYBE SBS KBS MBC NHN NC LF AJ AK JW KC STX SNT DS IM HJ
KCTC KISCO TKG ENM OIL CJENM KTNG
KODEX TIGER ACE SOL RISE PLUS KOSEF TREX FOCUS WON HANARO KCGI ITF VITA
KAKAO TOSS NPAY PAY HANA WOORI KBANK EMART VISA AMEX CARD APP WEB SMS ID PW
AND OR THE FOR MY BEST HOT PICK TIP TIPS PRO MAX HOME ETC EX DIY
KG CM MM KM ML GB MB
""".split())


# ── 정규화 ──────────────────────────────────────────────────────────────────
def nfkc_lower(s):
    return unicodedata.normalize("NFKC", s or "").lower()


def flat_of(s):
    return SEP_RUN.sub("", s)


def flex(key):
    """정규화된(공백·기호 없는) 낱말 → 공백·기호를 사이에 허용하는 정규식. 영문 끝은 경계를 건다."""
    body = (SEP + "*").join(re.escape(c) for c in key)
    pre = r"(?<![a-z])" if re.match(r"[a-z]", key) else ""
    post = r"(?![a-z])" if re.search(r"[a-z]$", key) else ""
    return re.compile(pre + body + post)


def sha256(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except OSError:
        return "-"


def load_tsv(path, need):
    """# 줄·빈 줄을 건너뛰고 첫 줄을 머리로 읽는다. 칸 수가 머리와 다르면 오류. [(파일 줄번호, {칸: 값})]"""
    rows, head = [], None
    name = os.path.basename(path)
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.rstrip("\n").rstrip("\r")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            cells = [c.strip() for c in line.split("\t")]
            if head is None:
                head = cells
                miss = [c for c in need if c not in head]
                if miss:
                    raise ValueError(f"{name} 머리에 칸 없음: {miss}")
                continue
            if len(cells) != len(head):
                raise ValueError(f"{name} 줄{n}: 칸 {len(cells)}개 — 머리는 {len(head)}개(TAB으로 나눈다)")
            empty = [h for h, c in zip(head, cells) if h in need and not c]
            if empty:
                raise ValueError(f"{name} 줄{n}: 빈 칸 {empty}(없으면 「-」)")
            rows.append((n, dict(zip(head, cells))))
    if head is None:
        raise ValueError(f"{name}: 머리 줄이 없다")
    return rows


def compile_data_rx(pat, where):
    try:
        rx = re.compile(pat)
    except re.error as e:
        raise ValueError(f"{where} 정규식 오류: {e}")
    if rx.search(""):
        raise ValueError(f"{where} 정규식이 빈 문구에도 맞는다(모든 후보에 맞음): {pat!r}")
    return rx


class Gate:
    def __init__(self, data_dir=HERE, repo=None):
        self.data_dir = data_dir
        self.repo = repo
        self.notes = []          # 표준 오류로 내보낼 주의
        self._load_data()
        self._load_repo()

    # ── 본사 원본 데이터 ──
    def _load_data(self):
        d = self.data_dir
        # 동의어(긴 다른말부터)
        self.syn = []
        for n, r in load_tsv(os.path.join(d, F_SYN), ["다른말", "표준말"]):
            v = flat_of(nfkc_lower(r["다른말"]))
            if not v:
                raise ValueError(f"{F_SYN} 줄{n}: 다른말이 비었다")
            self.syn.append((len(v), flex(v), nfkc_lower(r["표준말"]), n))
        self.syn.sort(key=lambda x: -x[0])
        self.syn_lines = len(self.syn)

        # 반려대장
        self.titles, self.words, self.rxwords = [], [], []
        rej = load_tsv(os.path.join(d, F_REJECT), ["번호", "종류", "문구", "원천", "예외", "근거"])
        self.reject_lines = (min(n for n, _ in rej), max(n for n, _ in rej)) if rej else (0, 0)
        for n, r in rej:
            if r["예외"] not in ("없음", "일정형"):
                raise ValueError(f"{F_REJECT} 줄{n}: 예외는 없음|일정형 ({r['예외']})")
            if r["종류"] == "정규식":
                if r["예외"] != "없음":
                    raise ValueError(f"{F_REJECT} 줄{n}: 정규식 줄의 예외는 「없음」만")
                rx = compile_data_rx(r["문구"], f"{F_REJECT} 줄{n}")
                self.rxwords.append({"id": r["번호"], "rx": rx, "src": f"{r['번호']}(반려대장 줄{n})", "line": n})
                continue
            key = self.norm(r["문구"])[1]
            if not key:
                raise ValueError(f"{F_REJECT} 줄{n}: 문구를 정규화하니 비었다")
            if r["종류"] == "제목":
                self.titles.append({"id": r["번호"], "key": key, "line": n, "text": r["문구"]})
            elif r["종류"] == "낱말":
                exc = r["예외"] == "일정형"
                self.words.append({"id": r["번호"], "word": r["문구"], "key": key, "rx": flex(key),
                                   "soft": exc, "src": f"{r['번호']}(반려대장 줄{n})", "line": n,
                                   "kind": r["원천"]})
            else:
                raise ValueError(f"{F_REJECT} 줄{n}: 종류는 제목|낱말|정규식 ({r['종류']})")

        # 사건키
        self.events = []
        self.event_by_key = {}
        for n, r in load_tsv(os.path.join(d, F_EVENT), ["사건키", "이름", "찾는 정규식", "다루는 글"]):
            rx = compile_data_rx(r["찾는 정규식"], f"{F_EVENT} 줄{n}")
            kk = self._k(r["사건키"])
            if kk in NONE_KEYS or kk in NEW_KEYS:
                raise ValueError(f"{F_EVENT} 줄{n}: 사건키로 쓸 수 없는 이름 「{r['사건키']}」")
            if kk in self.event_by_key:
                raise ValueError(f"{F_EVENT} 줄{n}: 사건키 「{r['사건키']}」가 줄{self.event_by_key[kk]['line']}과 겹친다")
            cov = [p.strip() for p in r["다루는 글"].split(",") if p.strip() and p.strip() not in NONE_KEYS]
            ev = {"key": r["사건키"], "name": r["이름"], "rx": rx, "covered": cov, "line": n}
            self.events.append(ev)
            self.event_by_key[kk] = ev

        # 주제대장
        self.topic_lines = []
        self.topic_posts = set()
        for n, r in load_tsv(os.path.join(d, F_TOPIC), ["글", "제목", "핵심어", "다루는사건키", "상태"]):
            self.topic_lines.append(n)
            post = r["글"]
            self.topic_posts.add(post)
            kws = [x.strip() for x in r["핵심어"].split(",") if x.strip()]
            if not kws:
                raise ValueError(f"{F_TOPIC} 줄{n} {post}: 핵심어가 없다")
            for w in kws:
                key = self.norm(w)[1]
                if not key:
                    raise ValueError(f"{F_TOPIC} 줄{n} {post}: 핵심어 「{w}」를 정규화하니 비었다")
                self.words.append({"id": post, "word": w, "key": key, "rx": flex(key), "soft": True,
                                   "src": f"주제대장 {post}(줄{n})", "line": n, "kind": "주제대장"})
            for k in [x.strip() for x in r["다루는사건키"].split(",") if x.strip() and x.strip() not in NONE_KEYS]:
                ev = self.event_by_key.get(self._k(k))
                if ev is None:
                    raise ValueError(f"{F_TOPIC} 줄{n} {post}: 사건키 「{k}」가 {F_EVENT}에 없다")
                if post not in ev["covered"]:
                    ev["covered"].append(post)

    @staticmethod
    def _k(s):
        return flat_of(nfkc_lower(s))

    def norm(self, s):
        """→ (공백 둔 정규형, 공백·기호 지운 정규형)"""
        t = nfkc_lower(s)
        for _, rx, canon, _ in self.syn:
            t = rx.sub(canon, t)
        return t, flat_of(t)

    # ── 서치 레포 쪽 ──
    def _load_repo(self):
        self.ledger, self.add_words, self.tamper, self.chair_exc = [], [], [], []
        self.ledger_total = 0
        repo = self.repo
        if not repo or not os.path.isdir(os.path.join(repo, "운영")):
            raise ValueError(f"서치 레포 「{repo}」에 운영/ 폴더가 없다 — --repo로 서치 레포 루트를 준다")
        # 진행분
        p = os.path.join(repo, R_LEDGER)
        if os.path.isfile(p):
            with open(p, encoding="utf-8-sig", newline="") as f:
                rd = csv.reader(f)
                head = next(rd, None)
                if head is not None:
                    head = [h.strip() for h in head]
                    miss = [c for c in ("검색어", "가제", "최종제목", "사건키", "상태") if c not in head]
                    if miss:
                        raise ValueError(f"원장.csv 머리에 칸 없음: {miss}")
                    for n, cells in enumerate(rd, 2):
                        if not any(c.strip() for c in cells):
                            continue
                        r = dict(zip(head, [c.strip() for c in cells]))
                        self.ledger_total += 1
                        if r.get("상태") in PROGRESS:
                            r["_line"] = n
                            r["_old"] = self._is_old(r)
                            self.ledger.append(r)
        else:
            self.notes.append("주의: 운영/원장.csv 없음 — 진행분 0줄")
        # 반려_추가
        p = os.path.join(repo, R_ADD)
        cur = []
        if os.path.isfile(p):
            with open(p, encoding="utf-8") as f:
                for n, line in enumerate(f, 1):
                    s = line.strip()
                    if not s or s.startswith("#"):
                        continue
                    cur.append(s)
                    w = s.split("\t")[0].strip()
                    key = self.norm(w)[1]
                    if key:
                        self.add_words.append({"word": w, "key": key, "rx": flex(key), "line": n})
        self.tamper = self._deleted_lines(repo, R_ADD, set(cur))
        # 회장 1회 예외
        p = os.path.join(repo, R_CHAIR)
        if os.path.isfile(p):
            with open(p, encoding="utf-8") as f:
                for n, line in enumerate(f, 1):
                    m = re.search(r"1회\s*예외\s*[:：]\s*(.+)", line)
                    if not m:
                        continue
                    ph = m.group(1).split("|")[0].strip().strip("「」『』\"'`").strip()
                    if ph:
                        self.chair_exc.append((n, ph, self._exact(ph)))

    def _is_old(self, r):
        """개편 전 글(묶음 「기존」 또는 주제대장에 있는 /N)."""
        if r.get("묶음", "") == OLD_BUNDLE:
            return True
        if r.get("편", "") in self.topic_posts:
            return True
        m = re.search(r"(/\d+)/?$", r.get("라이브URL", "") or "")
        return bool(m and m.group(1) in self.topic_posts)

    @staticmethod
    def _exact(s):
        return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", s)).strip().strip("「」『』\"'`").strip()

    def _deleted_lines(self, repo, rel, current):
        """git 기록(커밋 + 작업본)에서 지워졌는데 지금 파일에 없는 줄."""
        def run(args):
            try:
                r = subprocess.run(["git", "-C", repo] + args, capture_output=True, text=True, timeout=60)
            except (OSError, subprocess.TimeoutExpired):
                return None
            return r.stdout if r.returncode == 0 else None
        if run(["rev-parse", "--is-inside-work-tree"]) is None:
            self.notes.append("주의: 서치 레포가 git 저장소가 아니다 — 반려_추가 삭제 흔적을 보지 않았다")
            return []
        out = []
        logs = run(["log", "-p", "--no-color", "--no-ext-diff", "--format=@@C %h", "--", rel]) or ""
        wt = run(["diff", "HEAD", "--no-color", "--no-ext-diff", "--", rel]) or ""
        commit = "?"
        for src, text in (("log", logs), ("작업본", wt)):
            for line in text.splitlines():
                if line.startswith("@@C "):
                    commit = line[4:].strip()
                    continue
                if line.startswith("-") and not line.startswith("---"):
                    s = line[1:].strip()
                    if s and not s.startswith("#") and s not in current:
                        out.append((commit if src == "log" else "작업본", s))
        return out

    # ── 판정 ──
    def _core(self, cells, given_key, exclude_lines, self_pair):
        """칸 목록 하나를 판정한다. → res(fails·hard_stop 포함)"""
        text = " | ".join(cells)
        spaced, flat = self.norm(text)          # flat = 칸마다 공백·기호를 지우고 「|」로 이은 것
        pos = [i for i, ch in enumerate(spaced) if not SEP_ONE.match(ch)]   # flat 글자 j = spaced 글자 pos[j]
        res = {"text": text, "hard": [], "events": [], "soft": [], "prog_new": [], "prog_old": [], "extra": [],
               "dates": DATE_RE.findall(spaced), "key_notes": []}

        # ① 반려
        for t in self.titles:
            if t["key"] in flat:
                res["hard"].append((f"제목 「{t['text']}」", f"{t['id']}(반려대장 줄{t['line']})"))
        for w in self.words:
            if not w["soft"] and w["rx"].search(spaced):
                res["hard"].append((w["word"], w["src"]))
        for w in self.rxwords:
            m = w["rx"].search(flat)
            if m:
                res["hard"].append((m.group(0), w["src"]))
        for hit, src in self._b7(spaced, flat):
            res["hard"].append((hit, src))

        # ② 사건키 — 찾은 키(정규식이 이 문구에 맞음)만 일정형 예외를 열 수 있다. 낸 키는 실패를 더할 수만 있다
        ev_info, found_kk = [], set()
        for ev in self.events:
            if ev["rx"].search(flat):
                found_kk.add(self._k(ev["key"]))
                ev_info.append({"key": ev["key"], "how": "찾은 키", "covered": list(ev["covered"]),
                                "line": ev["line"], "valid": True})
        for k in [x.strip() for x in re.split(r"[,，]", given_key or "-")]:
            kk = self._k(k)
            if kk in NONE_KEYS or kk in found_kk:
                continue
            if kk in NEW_KEYS:
                res["key_notes"].append(f"낸 키 「{k}」는 이름 없는 키 — 사건키.tsv 키만 인정")
                continue
            found_kk.add(kk)
            ev = self.event_by_key.get(kk)
            if ev is None:
                res["key_notes"].append(f"낸 키 「{k}」가 사건키.tsv에 없음 — 본사가 등록한 뒤")
                ev_info.append({"key": k, "how": "낸 키(미등록)", "covered": [], "line": None, "valid": False})
                self.notes.append(f"주의: 사건키 「{k}」가 사건키.tsv에 없다(본사가 줄을 더한 뒤에야 일정형 예외가 열린다)")
            else:
                res["key_notes"].append(f"낸 키 「{ev['key']}」의 정규식(사건키 줄{ev['line']})이 문구와 맞지 않음")
                ev_info.append({"key": ev["key"], "how": "낸 키(문구와 안 맞음)", "covered": list(ev["covered"]),
                                "line": ev["line"], "valid": False})
        res["events"] = ev_info
        covered = [e for e in ev_info if e["covered"]]
        open_keys = [e for e in ev_info if e["valid"] and not e["covered"]]

        # ③ 주제대장·회장 지적 중복 — 걸린 자리(flat 기준)를 같이 적는다
        soft_spans = []
        for w in self.words:
            if w["soft"]:
                spans = [(bisect.bisect_left(pos, m.start()), bisect.bisect_left(pos, m.end()))
                         for m in w["rx"].finditer(spaced)]
                if spans:
                    res["soft"].append((w["word"], w["src"]))
                    soft_spans.append((w["word"], spans))
        # 일정형 예외는 그 낱말이 「찾은 안 다룬 사건」 정규식이 맞은 자리 안에 있을 때만 연다
        # (「원달러 환율 10월 FOMC」: 환율은 FOMC10월 자리 「10월fomc」 밖 → 안 열림)
        ev_spans = []
        for e in open_keys:
            ev = self.event_by_key[self._k(e["key"])]
            ev_spans += [(m.start(), m.end(), e["key"]) for m in ev["rx"].finditer(flat)]
        outside = [wd for wd, spans in soft_spans
                   if not all(any(a <= fa and fb <= b for a, b, _ in ev_spans) for fa, fb in spans)]
        res["outside"] = list(dict.fromkeys(outside))

        # ④ 진행분(기존 줄은 prog_old = 회장 예외로 넘을 수 있음)
        cand_keys = {self._k(e["key"]) for e in ev_info}
        for r in self.ledger:
            n = r["_line"]
            if n in exclude_lines:
                continue
            if self_pair and (r.get("묶음", ""), r.get("편", "")) == self_pair:
                continue
            bucket = res["prog_old"] if r["_old"] else res["prog_new"]
            where = f"원장 줄{n}({r.get('묶음', '')}/{r.get('편', '')} {r.get('상태', '')})"
            rk = {self._k(x) for x in re.split(r"[,，]", r.get("사건키", "")) if self._k(x) not in NONE_KEYS | NEW_KEYS}
            for k in sorted(cand_keys & rk):
                bucket.append((f"진행분 사건키 {k}", where))
            q = self.norm(r.get("검색어", ""))[1]
            if len(q) >= 2 and q in flat:
                bucket.append((f"진행분 검색어 「{r.get('검색어')}」", where))
            for col in ("가제", "최종제목"):
                t = self.norm(r.get(col, ""))[1]
                if len(t) >= 6 and any(t == c or (len(c) >= 6 and (t in c or c in t)) for c in flat.split("|")):
                    bucket.append((f"진행분 {col} 「{r.get(col)}」", where))

        # ⑤ 반려_추가
        for w in self.add_words:
            if w["rx"].search(spaced):
                res["extra"].append((w["word"], f"반려_추가 줄{w['line']}"))
        tamper = [(f"반려_추가 삭제 흔적 「{s}」", f"git {c}") for c, s in self.tamper]

        # 모으기
        sched_ok = bool(open_keys) and not covered and bool(res["dates"]) and not res["outside"]
        res["sched_ok"] = sched_ok
        fails = list(res["hard"])
        fails += [(f"사건 {e['key']}", f"이미 다룬 글 {','.join(e['covered'])}(사건키 줄{e['line']})") for e in covered]
        if res["soft"] and not sched_ok:
            why = []
            if not open_keys:
                why.append("문구에서 찾은 안 다룬 달력 사건 없음")
            why += res["key_notes"]
            if open_keys and res["outside"]:
                why.append(f"「{'」「'.join(res['outside'])}」이(가) 찾은 사건({'·'.join(e['key'] for e in open_keys)})의 문구 자리 밖")
            if covered:
                why.append("이미 다룬 사건")
            if not res["dates"]:
                why.append("날짜 토큰 없음")
            fails += [(w, s + (f" [일정형 예외 안 됨: {' · '.join(why)}]" if i == 0 else ""))
                      for i, (w, s) in enumerate(res["soft"])]
        fails += res["prog_old"] + res["prog_new"] + res["extra"] + tamper
        res["fails"] = fails
        res["hard_stop"] = res["prog_new"] + tamper
        res["open_keys"] = open_keys
        return res

    def judge(self, cells, given_key="-", exclude_lines=(), self_pair=None, used=None, in_line=None):
        """cells: 문구 칸 목록. given_key: 후보가 낸 사건키(쉼표 가능). used: 이 실행에서 쓴 회장 예외 줄 {원문 줄: 입력 줄}."""
        used = {} if used is None else used
        cells = list(dict.fromkeys(c.strip() for c in cells if c and c.strip()))
        base = self._core(cells, given_key, exclude_lines, self_pair)
        out = {"text": base["text"], "events": base["events"], "dates": base["dates"], "tag": "", "verdict": "통과"}
        if not base["fails"]:
            if base["soft"]:
                out["tag"] = "일정형 예외"
                keys = [e["key"] for e in base["open_keys"]]
                out["reasons"] = base["soft"] + [(f"사건 {'·'.join(keys)}", "찾은 키 · 다룬 글 없음"),
                                                 (f"날짜 {'·'.join(dict.fromkeys(base['dates']))}", "날짜 토큰")]
            else:
                out["reasons"] = []
            return out

        # 회장 1회 예외: 정확히 같은 칸만, 예외 줄 하나당 이 실행에서 후보 하나
        exc_cells, blocked = {}, []
        taken = set()
        for i, c in enumerate(cells):
            cx = self._exact(c)
            for n, ph, phx in self.chair_exc:
                if phx != cx or n in taken:
                    continue
                if n in used:
                    blocked.append((n, used[n]))
                    continue
                exc_cells[i] = n
                taken.add(n)
                break
        if not exc_cells:
            out["verdict"] = "실패"
            out["reasons"] = base["fails"]
            if blocked:
                n, m = blocked[0]
                out["tag"] = f"회장 예외 원문 {n}줄은 이 실행에서 이미 입력 줄{m}에 썼다(1회)"
            return out
        rest = [c for i, c in enumerate(cells) if i not in exc_cells]
        stops = []
        for i in exc_cells:
            stops += self._core([cells[i]], given_key, exclude_lines, self_pair)["hard_stop"]
        r_rest = self._core(rest, "-", exclude_lines, self_pair) if rest else None
        lines = "·".join(str(n) for n in exc_cells.values())
        if stops:
            out["verdict"] = "실패"
            out["reasons"] = list(dict.fromkeys(stops))
            out["tag"] = f"회장 예외 원문 {lines}줄이 있으나 이번 개편 뒤 진행분·삭제 흔적은 못 넘음"
        elif r_rest and r_rest["fails"]:
            out["verdict"] = "실패"
            out["reasons"] = r_rest["fails"]
            out["tag"] = f"회장 예외 원문 {lines}줄은 「{'」「'.join(cells[i] for i in exc_cells)}」 칸만 — 나머지 칸 실패"
        else:
            out["verdict"] = "통과"
            out["tag"] = f"회장 예외 원문 {lines}줄"
            out["reasons"] = base["fails"]
            for n in exc_cells.values():
                used[n] = in_line
        return out

    def _b7(self, spaced, flat):
        """spaced: NFKC·소문자·동의어를 거친 문구(공백 둠). 티커는 대소문자와 상관없이 뽑는다(자동완성은 소문자로 온다)."""
        out = []
        toks = [t.upper() for t in re.findall(r"(?<![a-z])[a-z]{2,5}(?![a-z])", spaced)]
        toks = list(dict.fromkeys(t for t in toks if t not in B7_STOP))
        ctx = B7_CTX.search(flat)
        cmp_ = B7_CMP.search(flat)
        if B7_ON["B7-1"] and toks and ctx:
            out.append((f"{toks[0]}+{ctx.group(0)}", "B7-1(본사 결정 B7 정규식: " + B7_LABEL["B7-1"] + ")"))
        if B7_ON["B7-2"] and len(toks) >= 2 and (ctx or cmp_):
            out.append(("·".join(toks[:3]), "B7-2(본사 결정 B7 정규식: " + B7_LABEL["B7-2"] + ")"))
        m = re.search(r"(미국|해외|글로벌|선진국).{0,12}?(etf|상장지수펀드)", flat)
        if B7_ON["B7-3"] and m:
            out.append((m.group(0), "B7-3(본사 결정 B7 정규식: " + B7_LABEL["B7-3"] + ")"))
        m = re.search(r"미국(주식)?(고)?배당|해외(주식)?(고)?배당", flat)
        if B7_ON["B7-4"] and m:
            out.append((m.group(0), "B7-4(본사 결정 B7 정규식: " + B7_LABEL["B7-4"] + ")"))
        return out


# ── 후보 읽기 ─────────────────────────────────────────────────────────────────
def _colname(h):
    s = unicodedata.normalize("NFKC", h)
    s = re.sub(r"[\s*`_]", "", s)
    s = re.sub(r"\([^)]*\)$", "", s)          # 「가제(안)」 → 가제, 「질문(구글원문)」 → 질문
    if re.fullmatch(r"제목(\d+안?|안\d*|후보\d*)", s):
        return "제목"                           # 제목 1안·제목안·제목 후보2 → 제목(모두 읽는다)
    return s


def _check_head(head, where):
    bad = [h for h in head if h and h not in COLS_KNOWN and h not in HEAD_IGNORE and any(x in h for x in HEAD_HINT)]
    if bad:
        raise ValueError(f"{where}: 표 머리 「{'」「'.join(bad)}」를 읽을 수 없다 — 칸 이름을 "
                         f"{'·'.join(COLS_TOPIC)} 중 하나로 바꾸거나(후보) 이 이름을 쓰지 않는다")


def _split_md(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", s)]


def _row_to_cand(n, pairs, mode, where):
    """pairs: [(칸 이름, 값)] → 후보 하나. 빈 줄이면 None. 문구 칸이 다 비었는데 다른 칸이 있으면 오류."""
    if not any(v.strip() for _, v in pairs):
        return None
    cols = COLS_TITLE if mode == "title" else COLS_TOPIC
    cells = [v for h, v in pairs if h in cols and v.strip()]
    if mode == "title" and not cells:
        cells = [v for h, v in pairs if h == "가제" and v.strip()]
    if not cells:
        raise ValueError(f"{where} 줄{n}: 문구 칸({'·'.join(cols)}{'·가제' if mode == 'title' else ''})이 비었다")
    d = {h: v for h, v in pairs}
    key = d.get("사건키", "-") or "-"
    pair = (d["묶음"], d["편"]) if d.get("묶음") and d.get("편") else None
    return {"line": n, "cells": cells, "key": key, "pair": pair}


def _has_cols(head, mode):
    cols = COLS_TITLE + ("가제",) if mode == "title" else COLS_TOPIC
    return any(h in cols for h in head)


def read_candidates(path, mode):
    """→ (후보 목록, 표 정보 문자열)"""
    if path == "-":
        raw = sys.stdin.read()
        ext = ""
        name = "표준 입력"
    else:
        with open(path, encoding="utf-8-sig") as f:
            raw = f.read()
        ext = os.path.splitext(path)[1].lower()
        name = os.path.basename(path)
    lines = raw.splitlines()
    out = []
    if ext == ".csv":
        rd = csv.reader(io.StringIO(raw))
        head = [_colname(h) for h in next(rd, [])]
        _check_head(head, f"{name} 줄1")
        if not _has_cols(head, mode):
            raise ValueError(f"{name}: {mode} 모드로 읽을 칸이 없다(머리 {head})")
        for n, cells in enumerate(rd, 2):
            c = _row_to_cand(n, list(zip(head, [x.strip() for x in cells])), mode, name)
            if c:
                out.append(c)
        return out, "CSV 1개"
    if ext == ".md":
        i, n_read, n_skip = 0, 0, 0
        while i < len(lines):
            if lines[i].lstrip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{2,}", lines[i + 1]):
                head = [_colname(h) for h in _split_md(lines[i])]
                _check_head(head, f"{name} 줄{i + 1}")
                use = _has_cols(head, mode)
                n_read += use
                n_skip += not use
                i += 2
                while i < len(lines) and lines[i].lstrip().startswith("|"):
                    if use:
                        c = _row_to_cand(i + 1, list(zip(head, _split_md(lines[i]))), mode, name)
                        if c:
                            out.append(c)
                    i += 1
            else:
                i += 1
        return out, f"읽은 표 {n_read}개 · 건너뛴 표 {n_skip}개"
    for n, line in enumerate(lines, 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = line.split("\t")
        if not parts[0].strip():
            raise ValueError(f"{name} 줄{n}: 문구가 비었다(줄 「문구<TAB>사건키」)")
        out.append({"line": n, "cells": [parts[0].strip()],
                    "key": parts[1].strip() if len(parts) > 1 else "-", "pair": None})
    return out, "줄 파일"


def fmt(res, n):
    body = " ; ".join(f"{h} ← {s}" for h, s in res.get("reasons", [])) or "-"
    tag = f"({res['tag']})" if res["tag"] else ""
    return f"{res['verdict']}{tag}: {body} | 입력 줄{n}: {res['text']}"


def default_repo():
    """사본 위치(<레포>/.claude/gate/)에서만 ../../ 를 레포로 본다."""
    if os.path.basename(HERE) == "gate" and os.path.basename(os.path.dirname(HERE)) == ".claude":
        return os.path.normpath(os.path.join(HERE, "..", ".."))
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description="서치 반려·중복 게이트(gate_topic)")
    ap.add_argument("file", help="후보 파일(줄 「문구<TAB>사건키」 · .md 표 · .csv) 또는 - (표준 입력)")
    ap.add_argument("--mode", choices=["topic", "title"], default="topic")
    ap.add_argument("--repo", help="서치 레포 루트(없으면 사본 위치 .claude/gate/의 ../../ — 본사 원본에서는 꼭 준다)")
    ap.add_argument("--exclude-self", type=int, action="append", default=[], metavar="N",
                    help="진행분 대조에서 뺄 원장.csv 줄번호(자기 줄). 여러 번 줄 수 있다")
    ap.add_argument("--only-fail", action="store_true", help="실패 줄과 합계만 출력")
    ap.add_argument("--json", action="store_true", help="JSON으로 출력")
    a = ap.parse_args(argv)

    repo = a.repo or default_repo()
    try:
        if not repo:
            raise ValueError("--repo가 없다 — 본사 원본에서 돌릴 때는 --repo <서치 레포 루트>를 준다"
                             "(../../ 기본값은 서치 사본 .claude/gate/에서만 쓴다)")
        g = Gate(HERE, repo)
        cands, tables = read_candidates(a.file, a.mode)
        if not cands:
            raise ValueError(f"후보 없음({tables}) — 아무것도 검사하지 않았다")
    except (OSError, ValueError) as e:
        print(f"오류: {e}", file=sys.stderr)
        return 2

    results, used = [], {}
    for c in cands:
        r = g.judge(c["cells"], c["key"], set(a.exclude_self), c["pair"], used=used, in_line=c["line"])
        r["line"] = c["line"]
        results.append(r)
    n_fail = sum(1 for r in results if r["verdict"] == "실패")
    n_sched = sum(1 for r in results if r["verdict"] == "통과" and r["tag"] == "일정형 예외")
    n_chair = sum(1 for r in results if r["verdict"] == "통과" and r["tag"].startswith("회장 예외"))
    summary = {
        "합계": len(results), "통과": len(results) - n_fail, "실패": n_fail,
        "일정형 예외": n_sched, "회장 예외": n_chair, "모드": a.mode, "입력": tables,
        "반려대장": f"{F_REJECT} 줄{g.reject_lines[0]}~{g.reject_lines[1]} (제목 {len(g.titles)} · 낱말 "
                    f"{sum(1 for w in g.words if w['kind'] != '주제대장')} · 정규식 {len(g.rxwords)})",
        "주제대장": f"{F_TOPIC} 줄{min(g.topic_lines)}~{max(g.topic_lines)} ({len(g.topic_lines)}편)" if g.topic_lines else F_TOPIC,
        "사건키": f"{len(g.events)}개(다룬 사건 {sum(1 for e in g.events if e['covered'])})",
        "동의어": g.syn_lines,
        "원장": f"{len(g.ledger)}줄 진행분(기존 {sum(1 for r in g.ledger if r['_old'])}) / 전체 {g.ledger_total}",
        "반려_추가": f"{len(g.add_words)}줄, 삭제 흔적 {len(g.tamper)}",
        "회장 예외 줄": [n for n, _, _ in g.chair_exc],
        "repo": g.repo,
        "sha256": {os.path.basename(p): sha256(p)[:16] for p in
                   [os.path.abspath(__file__)] + [os.path.join(HERE, f) for f in (F_REJECT, F_TOPIC, F_SYN, F_EVENT)]},
    }
    for note in dict.fromkeys(g.notes):
        print(note, file=sys.stderr)
    if a.json:
        out = []
        for r in results:
            out.append({"line": r["line"], "verdict": r["verdict"], "tag": r["tag"], "text": r["text"],
                        "reasons": [list(x) for x in r.get("reasons", [])],
                        "events": [{"key": e["key"], "how": e["how"], "covered": e["covered"], "valid": e["valid"]}
                                   for e in r["events"]],
                        "dates": r["dates"]})
        print(json.dumps({"results": out, "summary": summary}, ensure_ascii=False, indent=1))
    else:
        for r in results:
            if a.only_fail and r["verdict"] != "실패":
                continue
            print(fmt(r, r["line"]))
        print(f"# 합계 {len(results)} · 통과 {len(results) - n_fail}(일정형 예외 {n_sched} · 회장 예외 {n_chair})"
              f" · 실패 {n_fail} · 모드 {a.mode} · 입력 {tables}")
        print(f"# 대조: {summary['반려대장']} · {summary['주제대장']} · 사건키 {summary['사건키']} · 동의어 {summary['동의어']}줄"
              f" · 원장 {summary['원장']} · 반려_추가 {summary['반려_추가']} · repo {summary['repo']}")
        print("# sha256(앞 16자): " + " · ".join(f"{k} {v}" for k, v in summary["sha256"].items()))
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
