#!/usr/bin/env python3
"""calendar_build — 공식 페이지만으로 날짜형 주제 달력 운영/달력_YYYY-MM.md를 만든다(0토큰, 표준 라이브러리만).

사용:
  python3 도구/calendar_build.py --month 2026-10 --month 2026-11 [--repo <서치 레포>] [--gate-dir <게이트 폴더>] [--no-ac]
  옵션: --stdout(파일 대신 화면) · --json(뽑은 사건만)
칸(고정): 사건키 · 날짜(D) · 사건 · 공식 출처 URL · 자동완성 질문 원문 · 이 사건을 다루는 우리 글 · 게시 창 D−14~D−4 · 완성 목표 D−16
원천(페이지를 실제로 열어 날짜를 뽑는다. 못 열면 「못 열었다」로 남기고 날짜를 지어내지 않는다):
  ① KRX 휴장일 — open.krx.co.kr 휴장일 화면(화면이 부르는 자료 주소를 그대로 부른다: GenerateOTP → OPN99000001)
  ② 한국은행 통화정책방향 결정회의 일정 — bok.or.kr …/crncyPolicyDrcMtg/listYear.do?pYear=YYYY
  ③ 연준 FOMC 일정 — federalreserve.gov/monetarypolicy/fomccalendars.htm (D = 회의 둘째 날, 미국 동부 날짜)
  ④ 국세청 세무일정 — nts.go.kr/nts/ad/taxSchdul/selectList.do?taxYear=YYYY&taxMonth=MM (개인 관련 줄만)
  ⑤ 국세청 근로장려금 「심사 및 지급」 — 반기 상반기분 지급기한
  ⑥ 한국교육과정평가원 수능 누리집 — 수능 시험일(증시 개장 시각 변경은 거래소 공지 전이면 「확인 안 됨」)
  ⑦ NYSE 휴장일 표 — 추수감사절 휴장·다음 날 조기 마감
  ⑧ 국세청 보도자료 목록 — 「연말정산 미리보기」 공표 여부(없으면 「아직 공표 없음」)
「이 사건을 다루는 우리 글」: 게이트 폴더의 사건키.tsv(있으면). 키가 같으면 그 줄의 「다루는 글」, 키가 없으면 사건 이름에
  사건키.tsv 정규식을 걸어 이미 다룬 사건과 맞으면 그 글, 아니면 「없음」. 사건키.tsv에 없는 키는 5절에 모아 본사에 올린다.
게이트 폴더 기본값: <레포>/.claude/gate → 없으면 /home/user/claude_ebook/본사/게이트/서치.
"""
import argparse
import csv
import datetime as dt
import json
import os
import re
import sys
import unicodedata
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True  # 도구/에 __pycache__를 남기지 않는다(커밋 대상 아님)
sys.path.insert(0, HERE)
from source_open import fetch, visible_text  # noqa: E402
import autocomplete as ac  # noqa: E402

KST = dt.timezone(dt.timedelta(hours=9))
DOW = "월화수목금토일"
HQ_GATE = "/home/user/claude_ebook/본사/게이트/서치"
KRX_PAGE = "https://open.krx.co.kr/contents/MKD/01/0110/01100305/MKD01100305.jsp"
BOK_URL = "https://www.bok.or.kr/portal/singl/crncyPolicyDrcMtg/listYear.do?mtgSe=A&menuNo=200755&pYear={y}"
FOMC_URL = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
NTS_SCHED = "https://www.nts.go.kr/nts/ad/taxSchdul/selectList.do?taxYear={y}&taxMonth={m:02d}&mi=135747"
NTS_EITC = "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?mi=2453&cntntsId=7784"
NTS_PRESS = "https://www.nts.go.kr/nts/na/ntt/selectNttList.do?mi=2201&bbsId=1028"
SUNEUNG = "https://www.suneung.re.kr/main.do?s=suneung"
NYSE = "https://www.nyse.com/markets/hours-calendars"
KIND_IPO = "https://kind.krx.co.kr/listinvstg/pubofrprogcom.do?method=searchPubofrProgComMain"
EN_MON = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August",
                                      "September", "October", "November", "December"], 1)}

# ── 사건키.tsv 읽기·맞대기(scout.py도 쓴다) ──────────────────────────────────────
SEP = re.compile(r"[\s·ㆍ‧∙•・\-&/]+")
SEP_OPT = r"[\s·ㆍ‧∙•・\-&/]*"


class EventIndex:
    """게이트 폴더의 사건키.tsv·동의어.tsv를 읽어 문구 → 사건키를 찾는다(gate_topic과 같은 정규화)."""

    def __init__(self, gate_dir):
        self.gate_dir = gate_dir
        self.rows = []
        self.syn = []
        self.ok = False
        p = os.path.join(gate_dir or "", "사건키.tsv")
        if gate_dir and os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                lines = [ln.rstrip("\n") for ln in f if ln.strip() and not ln.startswith("#")]
            head = lines[0].split("\t") if lines else []
            for ln in lines[1:]:
                c = dict(zip(head, ln.split("\t")))
                try:
                    rx = re.compile(c.get("찾는 정규식", "") or r"(?!x)x")
                except re.error:
                    rx = re.compile(r"(?!x)x")
                cov = (c.get("다루는 글") or "-").strip()
                self.rows.append({"key": c.get("사건키", "").strip(), "name": c.get("이름", ""), "rx": rx,
                                  "covered": "" if cov in ("-", "") else cov})
            self.ok = True
        s = os.path.join(gate_dir or "", "동의어.tsv")
        if gate_dir and os.path.exists(s):
            with open(s, encoding="utf-8") as f:
                for ln in f:
                    if ln.startswith("#") or not ln.strip():
                        continue
                    c = ln.rstrip("\n").split("\t")
                    if len(c) >= 2 and c[0] != "다른말":
                        self.syn.append((c[0], c[1]))
            self.syn.sort(key=lambda x: -len(x[0]))

    def norm(self, s):
        t = unicodedata.normalize("NFKC", s or "").lower()
        for a, b in self.syn:
            chars = [re.escape(ch) for ch in unicodedata.normalize("NFKC", a).lower() if not ch.isspace()]
            t = re.sub(SEP_OPT.join(chars), lambda _m, b=b: unicodedata.normalize("NFKC", b).lower(), t)
        return SEP.sub("", t)

    def find(self, text):
        """문구 → 맞은 사건키 줄 목록"""
        t = self.norm(text)
        return [r for r in self.rows if r["rx"].search(t)]

    def get(self, key):
        for r in self.rows:
            if r["key"] == key:
                return r
        return None


def gate_dir_default(repo):
    p = os.path.join(repo, ".claude", "gate")
    if os.path.exists(os.path.join(p, "사건키.tsv")):
        return p
    if os.path.exists(os.path.join(HQ_GATE, "사건키.tsv")):
        return HQ_GATE
    return None


# ── 원천별 수집 ─────────────────────────────────────────────────────────────────
def ev(key, d, name, url, note=""):
    return {"key": key, "date": d, "name": name, "url": url, "note": note}


def src_krx(year, log):
    o = fetch(f"https://open.krx.co.kr/contents/COM/GenerateOTP.jspx?bld=MKD/01/0110/01100305/mkd01100305_01&name=form",
              headers={"Referer": KRX_PAGE})
    if o["reason"] or not o["text"].strip():
        log.append(("KRX 휴장일", KRX_PAGE, f"못 열었다({o['reason'] or '빈 응답'})", 0))
        return []
    data = urllib.parse.urlencode({"search_bas_yy": str(year), "gridTp": "KRX",
                                   "pagePath": "/contents/MKD/01/0110/01100305/MKD01100305.jsp",
                                   "code": o["text"].strip()}).encode()
    r = fetch("https://open.krx.co.kr/contents/OPN/99/OPN99000001.jspx", data=data,
              headers={"Referer": KRX_PAGE, "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                       "X-Requested-With": "XMLHttpRequest"})
    try:
        rows = json.loads(r["text"]).get("block1", [])
    except ValueError:
        log.append(("KRX 휴장일", KRX_PAGE, f"못 열었다({r['reason'] or 'JSON 아님'})", 0))
        return []
    out = []
    keymap = [("개천절", "개천절휴장"), ("한글날", "한글날휴장"), ("연말", "연말휴장"), ("성탄", "성탄절휴장"),
              ("추석", "추석휴장"), ("근로자", "근로자의날휴장"), ("제헌절", "제헌절휴장"), ("설날", f"설날휴장{year}")]
    for x in rows:
        nm = x.get("holdy_nm", "")
        d = dt.date.fromisoformat(x["calnd_dd"])
        key = next((k for w, k in keymap if w in nm), "휴장_" + re.sub(r"\W", "", nm))
        out.append(ev(key, d, f"국내 증시 휴장 — {nm}", KRX_PAGE, "KRX 휴장일 표"))
    log.append((f"KRX 휴장일 {year}", KRX_PAGE, "열림", len(out)))
    return out


def src_bok(year, log):
    url = BOK_URL.format(y=year)
    r = fetch(url)
    if r["reason"]:
        log.append((f"한국은행 금통위 {year}", url, f"못 열었다({r['reason']})", 0))
        return []
    t = visible_text(r["text"])
    if f"{year}년" not in t:
        log.append((f"한국은행 금통위 {year}", url, "못 열었다(그 해 표 없음)", 0))
        return []
    out = []
    for mm, dd, _ in re.findall(r"(\d{2})월 (\d{2})일\((.)\)", t):
        d = dt.date(year, int(mm), int(dd))
        out.append(ev(f"금통위{int(mm)}월", d, f"한국은행 통화정책방향 결정회의(기준금리 결정) {int(mm)}월", url))
    log.append((f"한국은행 금통위 {year}", url, "열림", len(out)))
    return out


def src_fomc(year, log):
    r = fetch(FOMC_URL)
    if r["reason"]:
        log.append((f"연준 FOMC {year}", FOMC_URL, f"못 열었다({r['reason']})", 0))
        return []
    t = visible_text(r["text"])
    i = t.find(f"{year} FOMC Meetings")
    j = t.find(f"{year - 1} FOMC Meetings")
    if i < 0:
        log.append((f"연준 FOMC {year}", FOMC_URL, "못 열었다(그 해 일정 없음)", 0))
        return []
    seg = t[i:j if j > i else None]
    out = []
    for mon, days, star in re.findall(r"\n\s*([A-Z][a-z]+(?:/[A-Z][a-z]+)?)\s*\n\s*(\d{1,2}(?:-\d{1,2})?)(\*?)", seg):
        last_mon = mon.split("/")[-1]
        if last_mon not in EN_MON:
            continue
        m = EN_MON[last_mon]
        d = dt.date(year, m, int(days.split("-")[-1]))
        out.append(ev(f"FOMC{m}월", d, f"미국 FOMC 회의 {mon} {days}(D = 결정일, 미국 동부 날짜)"
                      + (" · 경제전망(SEP) 회의" if star else ""), FOMC_URL))
    log.append((f"연준 FOMC {year}", FOMC_URL, "열림", len(out)))
    return out


NTS_KEEP = [  # (정규식, 사건키 틀, 이름 틀)
    (r"부가가치세\s*예정신고", "부가세{gi}기예정", "부가가치세 {gi}기 예정신고·납부"),
    (r"부가가치세\s*확정신고", "부가세{gi}기확정", "부가가치세 {gi}기 확정신고·납부"),
    (r"종합부동산세\s*납부", "종부세{y}", "종합부동산세 납부기한({y}년 귀속)"),
    (r"소득세\s*중간예납", "중간예납{y}", "종합소득세 중간예납 납부(고지분)·추계액 신고"),
    (r"근로.{0,2}자녀장려금\s*기한\s*후", "장려금기한후신청{y}", "근로·자녀장려금 기한 후 신청기한"),
    (r"근로.{0,2}자녀장려금\s*(정기|반기)", "장려금신청{y}", "근로·자녀장려금 신청"),
    (r"종합소득세\s*(확정)?신고", "종소세신고{y}", "종합소득세 확정신고·납부"),
    (r"양도소득세\s*(예정|확정)", "양도세신고{y}", "양도소득세 신고"),
    (r"연말정산", "연말정산{y}", "연말정산 관련 일정"),
]


def src_nts(year, month, log):
    url = NTS_SCHED.format(y=year, m=month)
    r = fetch(url)
    if r["reason"]:
        log.append((f"국세청 세무일정 {year}-{month:02d}", url, f"못 열었다({r['reason']})", 0))
        return []
    t = visible_text(r["text"])
    i = t.find("보내기\n")
    j = t.find("콘텐츠 만족도")
    seg = t[i:j] if i >= 0 else ""
    lines = [x.strip() for x in seg.split("\n") if x.strip()]
    out = []
    k = 0
    while k + 3 < len(lines):
        if re.fullmatch(r"\d{1,2}", lines[k]) and re.fullmatch(r"\d{1,2}", lines[k + 1]) and int(lines[k]) == month:
            day, what, note = int(lines[k + 1]), lines[k + 2], lines[k + 3]
            for rx, kt, nt in NTS_KEEP:
                if re.search(rx, what):
                    gi = re.search(r"(\d)기", what)
                    out.append(ev(kt.format(gi=gi.group(1) if gi else "", y=year), dt.date(year, month, day),
                                  nt.format(gi=gi.group(1) if gi else "", y=year) + f" — {note}", url,
                                  f"국세청 원문 줄: {what}"))
                    break
            k += 4
        else:
            k += 1
    log.append((f"국세청 세무일정 {year}-{month:02d}", url, "열림" if seg else "못 열었다(표 없음)", len(out)))
    return out


def src_eitc(log):
    r = fetch(NTS_EITC)
    if r["reason"]:
        log.append(("국세청 근로장려금 심사 및 지급", NTS_EITC, f"못 열었다({r['reason']})", 0))
        return []
    t = visible_text(r["text"])
    out = []
    m = re.search(r"상반기\s*\n?\s*[’']\s*(\d{2})\.(\d{1,2})\.(\d{1,2})\.", t)
    if m:
        d = dt.date(2000 + int(m.group(1)), int(m.group(2)), int(m.group(3)))
        out.append(ev(f"근로장려금지급{d.month}월", d, "근로장려금 반기신청 상반기분 지급기한(연간산정액의 35%)", NTS_EITC))
    m2 = re.search(r"하반기\s*\n?\s*[’']\s*(\d{2})\.(\d{1,2})\.(\d{1,2})\.", t)
    if m2:
        d = dt.date(2000 + int(m2.group(1)), int(m2.group(2)), int(m2.group(3)))
        out.append(ev(f"근로장려금정산{d.year}", d, "근로장려금 반기신청 하반기분 정산 지급기한", NTS_EITC))
    log.append(("국세청 근로장려금 심사 및 지급", NTS_EITC, "열림" if out else "열림(날짜 못 찾음)", len(out)))
    return out


def src_suneung(log):
    r = fetch(SUNEUNG)
    if r["reason"]:
        log.append(("평가원 수능 누리집", SUNEUNG, f"못 열었다({r['reason']})", 0))
        return []
    h = r["text"]
    i = h.find('class="eventSche"')
    t = visible_text(h[i:i + 4000]) if i >= 0 else ""
    m = re.search(r"(\d{4})학년도\s*수능.*?대학수학능력시험.*?(\d{4})\.(\d{2})\.(\d{2})\.\s*\n?\s*시험 실시", t, re.S)
    out = []
    if m:
        d = dt.date(int(m.group(2)), int(m.group(3)), int(m.group(4)))
        out.append(ev(f"수능일증시{d.year}", d, f"{m.group(1)}학년도 수능 시험일(증시 개장 시각 변경은 거래소 공지 확인 전 — 확인 안 됨)",
                      SUNEUNG))
    log.append(("평가원 수능 누리집", SUNEUNG, "열림" if out else "열림(시험일 못 찾음)", len(out)))
    return out


def src_nyse(year, log):
    r = fetch(NYSE)
    if r["reason"]:
        log.append(("NYSE 휴장일", NYSE, f"못 열었다({r['reason']})", 0))
        return []
    h = r["text"]
    hdr = re.search(r"<th[^>]*>\s*Holiday\s*</th>((?:\s*<th[^>]*>\s*\d{4}\s*</th>)+)", h)
    years = [int(y) for y in re.findall(r"(\d{4})", hdr.group(1))] if hdr else []
    out = []
    m = re.search(r"<th[^>]*>\s*Thanksgiving Day\s*</th>((?:\s*<td[^>]*>.*?</td>)+)", h, re.S)
    if m and year in years:
        cells = [visible_text(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", m.group(1), re.S)]
        c = cells[years.index(year)] if years.index(year) < len(cells) else ""
        mm = re.search(r"([A-Z][a-z]+)\s+(\d{1,2})", c)
        if mm and mm.group(1) in EN_MON:
            d = dt.date(year, EN_MON[mm.group(1)], int(mm.group(2)))
            early = re.search(r"close early at ([\d:]+ [ap]\.m\.)[^.]*?on Friday, (\w+ \d{1,2}), " + str(year), visible_text(h))
            note = f" · 다음 날 조기 마감({early.group(2)} {early.group(1)} ET)" if early else ""
            out.append(ev(f"미국추수감사절{year}", d, f"미국 증시 추수감사절 휴장{note}", NYSE))
    log.append((f"NYSE 휴장일 {year}", NYSE, "열림" if out else "열림(추수감사절 못 찾음)", len(out)))
    return out


def src_press_ys(log, today):
    """연말정산 미리보기 공표 여부만 본다. 공표가 없으면 사건 없이 4절에 「아직 공표 없음」."""
    r = fetch(NTS_PRESS)
    if r["reason"]:
        log.append(("국세청 보도자료 목록(연말정산 미리보기)", NTS_PRESS, f"못 열었다({r['reason']})", 0))
        return [], f"못 열었다({r['reason']})"
    t = visible_text(r["text"])
    hits = [ln.strip() for ln in t.split("\n") if "미리보기" in ln and "연말정산" in ln]
    log.append(("국세청 보도자료 목록(연말정산 미리보기)", NTS_PRESS, "열림", len(hits)))
    if not hits:
        return [], f"아직 공표 없음(보도자료 1쪽 확인 {today})"
    return [], "보도자료 있음: " + hits[0][:60] + " — 날짜는 본문을 열어 확인할 것"


# ── 자동완성 질문 ───────────────────────────────────────────────────────────────
SEEDS = [
    (r"^금통위", ["금통위 일정", "기준금리 발표일"], ["금통위", "기준금리", "금리"]),
    (r"^FOMC", ["FOMC 일정", "FOMC 발표"], ["fomc"]),
    (r"^개천절휴장", ["개천절 주식", "개천절 증시"], ["개천절"]),
    (r"^한글날휴장", ["한글날 주식", "한글날 증시"], ["한글날"]),
    (r"휴장", ["주식 휴장일"], ["휴장"]),
    (r"^부가세\d기예정", ["부가세 예정신고", "부가세 예정고지"], ["부가세", "부가가치세"]),
    (r"^종부세", ["종부세 납부기한", "종부세 고지서"], ["종부세", "종합부동산세"]),
    (r"^중간예납", ["종합소득세 중간예납", "중간예납 납부"], ["중간예납"]),
    (r"^근로장려금지급", ["근로장려금 지급일", "근로장려금 반기 지급"], ["근로장려금"]),
    (r"^장려금기한후", ["근로장려금 기한후 신청", "근로장려금 기한 후 신청"], ["근로장려금", "장려금"]),
    (r"^수능일증시", ["수능 주식시장", "수능날 증시"], ["수능"]),
    (r"^미국추수감사절", ["미국 추수감사절 주식", "추수감사절 미국 증시"], ["추수감사절", "블랙프라이데이"]),
    (r"^연말정산", ["연말정산 미리보기"], ["연말정산"]),
]


def ac_questions(key, use_ac, year=None):
    if not use_ac:
        return "(자동완성 안 봄)"
    for rx, seeds, must in SEEDS:
        if re.search(rx, key):
            picks = []
            for s in seeds:
                g = ac.google(s)
                n = ac.naver(s)
                if g is None:
                    picks.append(f"구글 못 열었다({ac.LAST_ERR.get('google', '')})")
                    continue
                nk = {ac.key(x) for x in (n or [])}
                for q in g:
                    if ac.key(q) == ac.key(s) or not any(w in ac.key(q) for w in must):
                        continue
                    if year and any(int(y) != year for y in re.findall(r"20\d\d", q)):
                        continue  # 다른 해 질문(예: 「금통위 일정 2025」)은 쓰지 않는다
                    tag = "구글·네이버" if ac.key(q) in nk else "구글"
                    if all(ac.key(q) != ac.key(p.split(" (")[0]) for p in picks):
                        picks.append(f"{q} ({tag})")
                    if len(picks) >= 2:
                        break
                if len(picks) >= 2:
                    break
            return " · ".join(picks) if picks else "자동완성 원문 없음"
    return "씨앗 없음"


# ── 쓰기 ────────────────────────────────────────────────────────────────────────
def dstr(d):
    return f"{d.isoformat()}({DOW[d.weekday()]})"


def covered_text(e, idx, unreg):
    if not idx or not idx.ok:
        return "확인 안 됨(사건키.tsv 없음)"
    row = idx.get(e["key"])
    if row:
        return row["covered"] or "없음"
    hits = [r for r in idx.find(e["name"]) if r["covered"]]
    unreg.append(e)
    if hits:
        return ", ".join(f"{r['covered']}(사건키.tsv 「{r['key']}」 정규식)" for r in hits)
    return "없음(사건키.tsv 미등록)"


def row_md(e, idx, unreg, use_ac):
    d = e["date"]
    win = f"{(d - dt.timedelta(days=14)).isoformat()} ~ {(d - dt.timedelta(days=4)).isoformat()}"
    tgt = (d - dt.timedelta(days=16)).isoformat()
    cells = [e["key"], dstr(d), e["name"].replace("|", "/"), e["url"], ac_questions(e["key"], use_ac, d.year).replace("|", "/"),
             covered_text(e, idx, unreg), win, tgt]
    return "| " + " | ".join(cells) + " |"


def build(months, repo, gate_dir, use_ac, now):
    log = []
    years = sorted({y for y, _ in months} | {y for y, m in months if m == 12} | {(y + (m == 12)) for y, m in months})
    events = []
    for y in years:
        events += src_krx(y, log)
        events += src_bok(y, log)
        events += src_fomc(y, log)
        events += src_nyse(y, log)
    need = set()
    for y, m in months:
        need.add((y, m))
        need.add((y + (m == 12), 1 if m == 12 else m + 1))
    for y, m in sorted(need):
        events += src_nts(y, m, log)
    events += src_eitc(log)
    events += src_suneung(log)
    _, ys_state = src_press_ys(log, now.date().isoformat())
    ipo = fetch(KIND_IPO, retries=0)
    ipo_state = "열림" if not ipo["reason"] else f"못 열었다({ipo['reason']})"
    log.append(("KIND 공모 진행 기업(공모주 월 일정)", KIND_IPO, ipo_state, 0))
    # 같은 키·같은 날 중복 제거
    seen = set()
    uniq = []
    for e in sorted(events, key=lambda x: (x["date"], x["key"])):
        if (e["key"], e["date"]) in seen:
            continue
        seen.add((e["key"], e["date"]))
        uniq.append(e)
    idx = EventIndex(gate_dir)
    files = {}
    for y, m in months:
        unreg = []
        first = dt.date(y, m, 1)
        nxt = dt.date(y + (m == 12), 1 if m == 12 else m + 1, 1)
        nxt2 = dt.date(nxt.year + (nxt.month == 12), 1 if nxt.month == 12 else nxt.month + 1, 1)
        this = [e for e in uniq if first <= e["date"] < nxt]
        ahead = [e for e in uniq if nxt <= e["date"] < nxt2 and (e["date"] - dt.timedelta(days=16)) < nxt]
        out = [f"# 달력 {y}-{m:02d} — 날짜형 주제(공식 페이지만)",
               "",
               f"- 만든 것: `도구/calendar_build.py` · 수집 {now.strftime('%Y-%m-%d %H:%M')} KST · 사건키 원본 "
               f"`{('사건키.tsv @ ' + gate_dir) if idx.ok else '없음'}`.",
               "- 날짜는 공식 페이지에서 뽑은 것만 적는다. 못 연 곳은 3·4절에 「못 열었다」로 남기고 날짜를 지어내지 않는다.",
               "- 게시 창 = D−14 ~ D−4, 완성 목표 = D−16. D−3 안이면 새로 쓰지 않는다(v2 2-2, 본사 안 3-1). "
               "「이 사건을 다루는 우리 글」이 있으면 새 글 금지(gate_topic ②가 막는다).",
               "- 자동완성 질문 원문: 구글 자동완성이 돌려준 글자 그대로, 네이버에도 있으면 「구글·네이버」.",
               "",
               "## 1. 이 달 사건",
               "| 사건키 | 날짜(D) | 사건 | 공식 출처 URL | 자동완성 질문 원문 | 이 사건을 다루는 우리 글 | 게시 창 D−14~D−4 | 완성 목표 D−16 |",
               "|---|---|---|---|---|---|---|---|"]
        out += [row_md(e, idx, unreg, use_ac) for e in this] or ["| (없음) | | | | | | | |"]
        out += ["", "## 2. 다음 달 사건 중 완성 목표(D−16)가 이 달에 드는 것",
                "| 사건키 | 날짜(D) | 사건 | 공식 출처 URL | 자동완성 질문 원문 | 이 사건을 다루는 우리 글 | 게시 창 D−14~D−4 | 완성 목표 D−16 |",
                "|---|---|---|---|---|---|---|---|"]
        out += [row_md(e, idx, unreg, use_ac) for e in ahead] or ["| (없음) | | | | | | | |"]
        out += ["", "## 3. 원천 확인 기록", "| 원천 | URL | 결과 | 뽑은 사건 수(전체 해·달) |", "|---|---|---|---:|"]
        out += [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in log]
        out += ["", "## 4. 못 연 원천·날짜 없음(날짜를 적지 않는다)", "| 사건 | 원천 | 상태 |", "|---|---|---|",
                f"| {m}월 공모주 청약·상장 일정(월 1편 묶음) | KIND 공모 진행 기업 {KIND_IPO} | {ipo_state}. 날짜는 DART 증권신고서로 집필 때 확인 |",
                f"| 연말정산 미리보기 개시 | 국세청 보도자료 {NTS_PRESS} | {ys_state} |",
                "| 청년미래적금 출시·가입 일정 | 금융위원회 fsc.go.kr | 10/3 본사 시험에서 연결 끊김(못 열었다). 다시 열리면 보도자료로 확인 |",
                "| 12월 선물·옵션 동시만기일 | KRX 공지 | 이 스크립트가 아직 읽지 않음(확인 안 됨) |"]
        out += ["", "## 5. 사건키.tsv 미등록 — 본사에 올림(본사가 사건키.tsv에 더한다)",
                "| 사건키(제안) | 날짜 | 사건 | 공식 출처 |", "|---|---|---|---|"]
        seen_u = set()
        for e in unreg:
            if e["key"] in seen_u:
                continue
            seen_u.add(e["key"])
            out.append(f"| {e['key']} | {e['date'].isoformat()} | {e['name'].replace('|', '/')} | {e['url']} |")
        if not seen_u:
            out.append("| (없음) | | | |")
        files[f"달력_{y}-{m:02d}.md"] = "\n".join(out) + "\n"
    return files, uniq, log


def read_calendar(repo, today, months_ahead=2):
    """scout.py용: 운영/달력_*.md 1·2절 표 → {사건키: (날짜, 공식 URL)} (오늘 이후 사건만)"""
    out = {}
    d = os.path.join(repo, "운영")
    if not os.path.isdir(d):
        return out
    for fn in sorted(os.listdir(d)):
        if not re.fullmatch(r"달력_\d{4}-\d{2}\.md", fn):
            continue
        with open(os.path.join(d, fn), encoding="utf-8") as f:
            for ln in f:
                c = [x.strip() for x in ln.strip().strip("|").split("|")]
                if len(c) >= 4 and re.match(r"\d{4}-\d{2}-\d{2}", c[1] or ""):
                    dd = dt.date.fromisoformat(c[1][:10])
                    if dd >= today:
                        out.setdefault(c[0], (dd, c[3], c[2]))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="공식 페이지 달력(0토큰)")
    ap.add_argument("--month", action="append", required=True, help="YYYY-MM (여러 번)")
    ap.add_argument("--repo", default=os.path.normpath(os.path.join(HERE, "..")))
    ap.add_argument("--gate-dir")
    ap.add_argument("--no-ac", action="store_true")
    ap.add_argument("--stdout", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    months = []
    for s in a.month:
        m = re.fullmatch(r"(\d{4})-(\d{2})", s)
        if not m:
            print(f"오류: --month {s} (YYYY-MM)", file=sys.stderr)
            return 2
        months.append((int(m.group(1)), int(m.group(2))))
    now = dt.datetime.now(KST)
    gate_dir = a.gate_dir or gate_dir_default(a.repo)
    files, events, log = build(months, a.repo, gate_dir, not a.no_ac, now)
    if a.json:
        print(json.dumps([{**e, "date": e["date"].isoformat()} for e in events], ensure_ascii=False, indent=1))
        return 0
    for fn, txt in files.items():
        if a.stdout:
            print(txt)
        else:
            p = os.path.join(a.repo, "운영", fn)
            with open(p, "w", encoding="utf-8") as f:
                f.write(txt)
            print(f"썼다: {p}")
    bad = [x for x in log if not x[2].startswith("열림")]
    for x in log:
        print(f"# {x[0]}: {x[2]} · {x[3]}건")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
