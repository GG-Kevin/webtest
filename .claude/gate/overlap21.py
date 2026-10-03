#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""21자 겹침 게이트 overlap21.py — 0토큰, 표준 라이브러리만 (본사 원본, H-133·H-189 v3.1 복제 금지선)

사용
  python3 overlap21.py <대상 원고.md|발행.html|.txt> --against <파일|폴더 ...> [--min 21] [--warn]
          [--include-same-dir] [--show-text]

  대상과 상대(파일·폴더, 폴더는 안의 .html·.htm·.md·.txt 전부)에서 본문 글자만 뽑아
  21자 창의 롤링 해시로 같은 글자열을 찾는다. 하나라도 있으면 종료 1(--warn 이면 0, 「경고」로만 찍는다).
  종료 2 = 뽑기 실패(대상·상대에서 뽑은 글자가 0이거나 그쪽 본문의 50% 미만) 또는 사용법·읽기 오류.

본문 글자 뽑기(검증 반영 10/3)
  .html  본문 영역 = 티스토리 바깥 div.contents_style → 네이버 .se-main-container → 워드프레스 .entry-content
         → article → main → body → 조각 전체. 문단(블록)마다 따로 잰다.
  .md    <!-- --> 주석·코드 울타리 표시·# 머리표·**·> 기호를 지우고 줄(문단)마다 잰다. .txt 는 줄마다 그대로.
제외 영역(대상·상대 모두, v2 2-7 「우리 글 겹침」 제외 목록) — 블록을 통째로 지우는 것은 작은 블록뿐이다
  · 바이라인: class/id 표지(author·byline·writer·저자) 블록(500자 이하) · 또는 자식 블록이 없는 300자 이하 한 줄이
    「글쓴이·저자·필명·작성자」로 시작하고 소개·작성자 쪽 링크가 있을 때. 바깥 래퍼(div#page 등)는 지우지 않는다.
  · 면책·「안내」 상자: 허용 면책 문장 1종과 라이브 22편 「안내」 상자 문장(지문_22.tsv 안내문장 칸)에 정확히 같은 문장만.
  · 수정 이력·최종 수정 문장(100자 이하) · 출처 줄(「출처:」 등으로 시작하는 300자 이하 블록) · 외부 링크 글자
  · 표 머리(th·thead, 마크다운 표 첫 줄) · 「」 안 법령명(…법·시행령·규정 …) · 기준일 꼬리말(「YYYY년 M월 D일 … 기준」 짧은 구)
  · 공식 명칭(OFFICIAL_NAMES, 낱말이 정확히 같은 문구 — 「」 있어도 없어도)은 우리 글끼리 대조할 때만 뺀다
    (상대가 moneyproducer canonical 글이거나 경로에 발행/·작업/ 이 있을 때).
정규화
  NFKC → 소문자 → 글자·숫자·공백만 남김(문장부호 지움) → 공백 여러 개를 하나로. 21자는 공백 포함 글자 수다.
출력(남의 글 20자 초과를 기록에 남기지 않으려고 조각은 앞 20자까지만 찍는다 — H-133)
  겹침: <대상> 문단n p자째 · 길이 L ← <상대 파일> 문단m 「앞 20자…」
  결과: 통과 — 겹침 0 | 실패 — 겹침 n곳(상대 m개 파일) | 뽑기 실패 — …(종료 2)
같은 글 빼기: 상대가 대상과 같은 파일, 또는 대상이 작업/<날짜>_<영문>/ 안에 있을 때 같은 폴더(원고·발행), 또는
  영문 이름이 같은 사본(작업/2026-10-05_x/발행.html ↔ 발행/대기/2026-10-06_x.html)이면 뺀다(--include-same-dir 로 끔).
  그 밖의 폴더(발행/대기 등)에서는 같은 폴더의 다른 글도 대조한다. 상대가 0개면 경고를 찍는다.
"""
import argparse
import os
import re
import sys
import unicodedata

sys.dont_write_bytecode = True  # 게이트 폴더에 __pycache__ 를 남기지 않는다(sha256 목록 고정)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gate_frame import BLOCK, SKIP, SITE, load_fp, parse_html, plain_text, safe_urlparse, canonical_id  # noqa: E402

K_DEFAULT = 21
EXTS = (".html", ".htm", ".md", ".txt")
MIN_RATIO = 0.5
# 면책 허용 문장(gate_search.py ALLOWED_DISCLAIMER 와 같은 문장 — 바꾸면 둘 다 고친다)
ALLOWED_DISCLAIMER = "이 글은 기준일의 공개 원문을 정리한 일반 정보이며, 개인의 사정에 따라 결과가 달라질 수 있습니다."
# 공식 명칭 허용 목록(정확 일치, 「」 안). 우리 글끼리 대조할 때만 뺀다. 라이브 /2·/10 공시 사유명. 더하기는 본사.
OFFICIAL_NAMES = ("주식의 병합, 분할 등 전자등록 변경, 말소",)

REVISION = re.compile(r"수정\s*이력|최종\s*수정|수정일\s*[:：]|업데이트\s*[:：]")
BYLINE_HEAD = re.compile(r"^\s*(글쓴이|저자|필명|작성자|쓴\s*사람)(\s|[:：·]|$)")
AUTHOR_MARK = re.compile(r"author|byline|writer|저자", re.I)
ABOUT_HREF = re.compile(r"(/pages?/|소개|about|/author/|%EC%86%8C%EA%B0%9C)", re.I)
SOURCE_LINE = re.compile(r"^\s*(출처|자료|참고|원문)\s*[:：·]")
LAW_QUOTE = re.compile(r"「[^」]{1,60}?(법|법률|시행령|시행규칙|규정|규칙|고시|조례|훈령|예규|지침|세칙|협약)"
                       r"(\s*제\s*\d+\s*조(의\s*\d+)?(\s*제\s*\d+\s*항)?)?\s*」")
BASEDATE = re.compile(r"20\d\d\s*년\s*\d{1,2}\s*월\s*\d{1,2}\s*일\s*(?:[가-힣A-Za-z]{1,8}\s*){0,2}기준"
                      r"|20\d\d[-.]\s?\d{1,2}[-.]\s?\d{1,2}\.?\s*기준")
SENT = re.compile(r"(?<=[.!?。])\s+|\n")
WORK_DIR = re.compile(r"^\d{4}-\d{2}-\d{2}_(.+)$")
# 공식 명칭 정규식: 낱말 사이 공백·쉼표·가운뎃점만 허용, 앞뒤 「」는 있어도 없어도 된다(정확 일치)
OFFICIAL_RX = [re.compile(r"[「『]?\s*" + r"[\s,.·ㆍ、]*".join(re.escape(t) for t in n.split()) + r"\s*[」』]?")
               for n in OFFICIAL_NAMES]


def norm(s):
    s = unicodedata.normalize("NFKC", s or "").lower()
    s = "".join(ch if (ch.isalnum() or ch.isspace()) else " " for ch in s)
    return re.sub(r"\s+", " ", s).strip()


def _fixed_set():
    out = {norm(ALLOWED_DISCLAIMER)}
    try:
        for r in load_fp(os.path.join(HERE, "지문_22.tsv")):
            for sline in r.get("notice", []):
                out.add(norm(sline))
    except (OSError, ValueError):
        pass
    out.discard("")
    return out


FIXED = _fixed_set()


def clean_chunks(t, drop_official=False):
    """문단 하나 → 뺄 문장(고정 면책·안내 문장, 짧은 수정 이력)을 뺀 연속 조각들. 뺀 자리에서 끊는다."""
    out, cur = [], []
    for s in SENT.split(t):
        if not s or not s.strip():
            continue
        if norm(s) in FIXED or (REVISION.search(s) and len(s.strip()) <= 100):
            if cur:
                out.append(" ".join(cur))
                cur = []
            continue
        s = LAW_QUOTE.sub(" ", s)
        if drop_official:
            for rx in OFFICIAL_RX:
                s = rx.sub(" ", s)
        s = BASEDATE.sub(" ", s)
        cur.append(s)
    if cur:
        out.append(" ".join(cur))
    return out


def _is_external(href):
    h = (href or "").strip()
    if h.startswith("//"):
        h = "https:" + h
    p = safe_urlparse(h)
    if p is None:  # 깨진 주소는 글자를 그대로 둔다(보수적)
        return False
    return p.scheme in ("http", "https") and SITE not in (p.netloc or "").lower()


def content_root(root):
    """본문 영역. 티스토리(바깥 contents_style) → 네이버 → 워드프레스 → article → main → body → 전체."""
    for n in root.iter():
        if n.tag == "div" and "contents_style" in n.cls():
            return n, "div.contents_style"
    for c in ("se-main-container", "entry-content"):
        for n in root.iter():
            if c in n.cls():
                return n, "." + c
    for t in ("article", "main", "body"):
        for n in root.iter():
            if n.tag == t:
                return n, t
    return root, "조각 전체"


def _has_block_child(n):
    for k in n.iter():
        if k is not n and k.tag in BLOCK and k.tag not in ("br", "hr"):
            return True
    return False


def _basis_text(n):
    """비율 분모: 본문 글자에서 외부 링크 글자·표 머리만 뺀 것(블록·문장 제외 규칙이 얼마나 지웠는지 잰다)."""
    out = []

    def rec(x):
        for k in x.kids:
            if isinstance(k, str):
                out.append(k)
                continue
            if k.tag in SKIP or k.tag in ("th", "thead") or (k.tag == "a" and _is_external(k.attrs.get("href"))):
                out.append(" ")
                continue
            blk = k.tag in BLOCK
            if blk:
                out.append(" ")
            rec(k)
            if blk:
                out.append(" ")
    rec(n)
    return "".join(out)


def html_segments(raw, drop_official=False):
    """→ ([(문단 번호, 조각)], 분모 글자 수, 본문 영역 이름). 문단 = 블록 요소 하나(p·li·h2·td …). <br>은 문단 안 줄바꿈."""
    body, how = content_root(parse_html(raw))
    segs, buf, para = [], [], [0]

    def flush():
        t = re.sub(r"[ \t\r\f\v]+", " ", "".join(buf)).strip()
        buf.clear()
        if not t:
            return
        para[0] += 1
        if SOURCE_LINE.match(t) and len(t) <= 300:
            return
        for c in clean_chunks(t, drop_official):
            segs.append((para[0], c))

    def excluded(k):
        if k.tag in ("th", "thead"):
            return True
        if k.tag == "a" and _is_external(k.attrs.get("href")):
            return True
        if k.tag in ("body", "html", "main", "article"):
            return False
        mark = " ".join(k.cls()) + " " + (k.attrs.get("id") or "")
        if AUTHOR_MARK.search(mark) and len(plain_text(k)) <= 500:
            return True
        if k.tag in BLOCK and k.tag not in ("br", "hr") and not _has_block_child(k):
            pt = plain_text(k)
            if len(pt) <= 300 and BYLINE_HEAD.match(pt) and any(
                    x.tag == "a" and ABOUT_HREF.search(x.attrs.get("href") or "") for x in k.iter()):
                return True
        return False

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
            if excluded(k):
                if k.tag == "a":
                    buf.append(" ")
                else:
                    flush()
                    para[0] += 1
                continue
            blk = k.tag in BLOCK
            if blk:
                flush()
            rec(k)
            if blk:
                flush()

    if not excluded(body):
        rec(body)
    flush()
    return segs, len(norm(_basis_text(body))), how


MD_LINK = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")


def md_segments(text, plain=False):
    """→ ([(줄 번호, 조각)], 분모 글자 수). .md 는 마크다운 기호·표 머리·외부 링크 글자·출처 줄·바이라인 줄을 뺀다."""
    if not plain:
        text = re.sub(r"(?s)<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), text)
    segs, basis = [], []
    lines = text.split("\n")
    prev_table = False
    for i, ln in enumerate(lines):
        s = ln.strip()
        if not plain:
            if s.startswith("```"):
                continue
            head_row = False
            if s.startswith("|"):
                nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
                if re.match(r"^:?-{2,}", s.strip("|").strip()):
                    continue
                if re.match(r"^:?-{2,}", nxt.strip("|").strip()) and not prev_table:
                    head_row = True
                prev_table = True
                s = " ".join(c.strip() for c in s.strip("|").split("|"))
            else:
                prev_table = False
            s = re.sub(r"^#{1,6}\s*", "", s)
            s = re.sub(r"^>\s*", "", s)
            s = re.sub(r"^[-*+]\s+|^\d+\.\s+", "", s)
            s = MD_LINK.sub(lambda m: " " if _is_external(m.group(2)) else m.group(1), s)
            s = re.sub(r"\*\*|__|`", "", s)
            if head_row:
                continue  # 표 머리 줄(분모에도 넣지 않는다)
            basis.append(s)
            if SOURCE_LINE.match(s) and len(s) <= 300:
                continue
            if len(s) <= 300 and BYLINE_HEAD.match(s) and ABOUT_HREF.search(ln):
                continue
        else:
            basis.append(s)
        if not s:
            continue
        for c in clean_chunks(s):
            segs.append((i + 1, c))
    return segs, len(norm(" ".join(basis)))


def is_ours(path, raw):
    """우리 글인가(공식 명칭 허용 목록을 쓸지): moneyproducer canonical·og:url, 또는 경로에 발행/·작업/."""
    if raw and (canonical_id(raw) or re.search(r'(og:url|canonical)[^>]+moneyproducer\.co\.kr', raw)):
        return True
    parts = os.path.realpath(path).replace("\\", "/").split("/")
    return "발행" in parts[:-1] or "작업" in parts[:-1]


def segments(path, drop_official=False):
    """→ ([(문단·줄 번호, 정규화한 조각)], 단위, 분모 글자 수, 뽑은 글자 수, 본문 영역)."""
    raw = open(path, encoding="utf-8", errors="replace").read()
    low = path.lower()
    if low.endswith((".html", ".htm")):
        segs, basis, how = html_segments(raw, drop_official)
        unit = "문단"
    elif low.endswith(".md"):
        segs, basis = md_segments(raw)
        unit, how = "줄", "마크다운"
    else:
        segs, basis = md_segments(raw, plain=True)
        unit, how = "줄", "텍스트"
    out = [(n, norm(c)) for n, c in segs]
    out = [(n, c) for n, c in out if c]
    return out, unit, basis, sum(len(c) for _, c in out), how


def extract_problem(name, basis, got, how):
    if got == 0:
        return f"{name}: 뽑은 글자 0자(본문 영역 {how}, 분모 {basis}자)"
    if basis and got < MIN_RATIO * basis:
        return f"{name}: 뽑은 글자 {got}자 = 본문 {basis}자의 {got * 100 // basis}%(50% 미만 — 제외 규칙이 본문을 지웠을 수 있음, 영역 {how})"
    return None


B, M = 911382323, (1 << 61) - 1


def window_hashes(s, k):
    n = len(s)
    if n < k:
        return []
    pw = pow(B, k, M)
    h, out = 0, []
    for i, ch in enumerate(s):
        h = (h * B + ord(ch)) % M
        if i >= k:
            h = (h - ord(s[i - k]) * pw) % M
        if i >= k - 1:
            out.append(h)
    return out


def collect(paths):
    files = []
    for p in paths:
        if os.path.isdir(p):
            for dp, dn, fn in os.walk(p):
                dn.sort()
                for f in sorted(fn):
                    if f.lower().endswith(EXTS):
                        files.append(os.path.join(dp, f))
        elif os.path.exists(p):
            files.append(p)
        else:
            print(f"기록: 상대 없음 {p}")
    return files


def find_overlaps(tsegs, against, k):
    """tsegs: [(번호, 조각)]. against: [(이름, [(번호, 조각)], 단위)].
    돌려주는 값: [(대상 조각 i, 위치, 길이, 상대 이름, 상대 번호, 상대 위치, 상대 단위)]."""
    index = {}
    for fi, (_, segs, _u) in enumerate(against):
        for si, (_, s) in enumerate(segs):
            for j, h in enumerate(window_hashes(s, k)):
                index.setdefault(h, []).append((fi, si, j))
    hits = set()
    for ti, (_, s) in enumerate(tsegs):
        for j, h in enumerate(window_hashes(s, k)):
            for fi, si, aj in index.get(h, ()):
                if against[fi][1][si][1][aj:aj + k] == s[j:j + k]:
                    hits.add((ti, j, fi, si, aj))
    runs = []
    for (ti, j, fi, si, aj) in sorted(hits):
        if (ti, j - 1, fi, si, aj - 1) in hits:
            continue
        n = 0
        while (ti, j + n + 1, fi, si, aj + n + 1) in hits:
            n += 1
        name, segs, unit = against[fi]
        runs.append((ti, j, n + k, name, segs[si][0], aj, unit))
    return runs


def post_slug(path):
    """같은 글 사본 판정용 영문 이름: 작업/<날짜>_<영문>/… → <영문>, 발행/대기/<날짜>_<영문>.html → <영문>."""
    rp = os.path.realpath(path)
    d = os.path.basename(os.path.dirname(rp))
    if os.path.basename(os.path.dirname(os.path.dirname(rp))) == "작업":
        m = WORK_DIR.match(d)
        if m:
            return m.group(1)
    m = WORK_DIR.match(os.path.splitext(os.path.basename(rp))[0])
    return m.group(1) if m else None


def same_post(target, other, include_same_dir):
    rt, ro = os.path.realpath(target), os.path.realpath(other)
    if rt == ro:
        return True
    if include_same_dir:
        return False
    tdir = os.path.dirname(rt)
    in_work = os.path.basename(os.path.dirname(tdir)) == "작업" and WORK_DIR.match(os.path.basename(tdir))
    if in_work and os.path.dirname(ro) == tdir:
        return True
    st, so = post_slug(target), post_slug(other)
    return bool(st and so and st == so)


def main():
    ap = argparse.ArgumentParser(description="21자 겹침 게이트")
    ap.add_argument("target")
    ap.add_argument("--against", nargs="+", required=True)
    ap.add_argument("--min", type=int, default=K_DEFAULT)
    ap.add_argument("--warn", action="store_true", help="겹침이 있어도 종료 0(경고로만 찍음). 뽑기 실패는 그래도 종료 2")
    ap.add_argument("--include-same-dir", action="store_true", help="같은 글 사본 빼기를 끈다")
    ap.add_argument("--show-text", action="store_true", help="겹친 조각을 20자 넘게 찍음(커밋할 기록에는 쓰지 말 것)")
    ap.add_argument("--max-lines", type=int, default=40)
    a = ap.parse_args()
    if not os.path.isfile(a.target):
        print(f"오류: 대상 없음 {a.target}")
        return 2
    k = a.min
    traw = open(a.target, encoding="utf-8", errors="replace").read()
    tsegs, tunit, tbasis, tgot, thow = segments(a.target, drop_official=False)
    tsegs_ours = segments(a.target, drop_official=True)[0]
    problems = []
    p = extract_problem("대상 " + os.path.relpath(a.target), tbasis, tgot, thow)
    if p:
        problems.append(p)
    ours, others, skipped = [], [], []
    for path in collect(a.against):
        if same_post(a.target, path, a.include_same_dir):
            if os.path.realpath(path) != os.path.realpath(a.target):
                skipped.append(os.path.relpath(path))
            continue
        oraw = open(path, encoding="utf-8", errors="replace").read()
        mine = is_ours(path, oraw)
        segs, unit, basis, got, how = segments(path, drop_official=mine)
        p = extract_problem("상대 " + os.path.relpath(path), basis, got, how)
        if p:
            problems.append(p)
            continue
        (ours if mine else others).append((os.path.relpath(path), segs, unit))
    del traw
    if skipped:
        print("기록: 같은 글 사본이라 뺌 " + ", ".join(skipped[:5]) + (f" 외 {len(skipped) - 5}개" if len(skipped) > 5 else ""))
    if problems:
        for x in problems:
            print("뽑기 실패: " + x)
        print(f"결과: 뽑기 실패 — {len(problems)}개 파일(종료 2). 본문 영역·제외 규칙을 확인한다")
        return 2
    runs = [("ours",) + r for r in find_overlaps(tsegs_ours, ours, k)] + \
        [("other",) + r for r in find_overlaps(tsegs, others, k)]
    tname = os.path.relpath(a.target)
    label = "경고" if a.warn else "겹침"
    for i, (kind, ti, j, L, an, sn, aj, unit) in enumerate(runs):
        if i >= a.max_lines:
            print(f"… {len(runs) - a.max_lines}곳 더")
            break
        src = tsegs_ours if kind == "ours" else tsegs
        frag = src[ti][1][j:j + L]
        shown = frag if a.show_text else (frag[:20] + ("…" if len(frag) > 20 else ""))
        print(f"{label}: {tname} {tunit}{src[ti][0]} {j + 1}자째 · 길이 {L} ← {an} {unit}{sn} {aj + 1}자째 「{shown}」")
    nfiles = len({r[4] for r in runs})
    print(f"기록: 대상 {len({n for n, _ in tsegs})}{tunit} {tgot}자(본문 {tbasis}자, 영역 {thow}) · 상대 {len(ours) + len(others)}개 파일"
          f"(우리 글 {len(ours)} · 남의 글 {len(others)})" + (f" · 같은 글 {len(skipped)}개 뺌" if skipped else "")
          + f" · 창 {k}자")
    if not ours and not others:
        print("경고: 상대 0개 파일 — 대조한 글이 없음(--against 경로를 확인한다)")
    if runs:
        print(f"결과: {'경고' if a.warn else '실패'} — 겹침 {len(runs)}곳(상대 {nfiles}개 파일)")
        return 0 if a.warn else 1
    print("결과: 통과 — 겹침 0")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001 — 예상 못 한 오류는 종료 2(「겹침 있음」 1 과 구분)
        print(f"오류: {type(e).__name__}: {e}")
        sys.exit(2)
