# -*- coding: utf-8 -*-
"""원고 마크다운 -> 티스토리 HTML (본사 도구, v3.1 계약 — 2026-10-03 본사가 다시 씀).

사용
  python3 도구/원고_HTML변환.py W/원고.md > W/발행.html     # 종료 0 · 1 = 원고 규격 위반(표준 오류에 「규격 위반」 줄)
  python3 도구/원고_HTML변환.py --self-test                 # 견본 원고 -> 변환 -> 계약 확인 -> gate_search 치명 0

계약(CLAUDE.md §4 「변환기 계약」, 작가 규격 jakga-a/b 4절)
  - `<!-- 제목: … -->`·`<!-- 디스커버 제목: … -->` 줄을 HTML 첫 줄에 남긴다(제목 주석이 없으면 h1 글자로 만든다).
  - `# h1` 아래 첫 문단부터 변환한다(h1 자체는 티스토리 제목 칸에 들어가므로 본문에 넣지 않는다).
  - `[[목차]]` -> h2 목록(앵커 링크) · `표: …` -> 다음 표의 caption · `![alt](그림)` -> figure·img alt
  - `[[저자 박스]]` -> `발행/저자소개_원고.md` 「## 1.」 아래 첫 ```html 덩어리 · `[[같은 묶음: …]]` -> HTML 주석
  - `[집필 메모]`부터 끝까지 버린다. 그 밖의 `[[…]]` 줄·표 없는 `표:` 줄·alt 없는 그림은 규격 위반(종료 1).
표준 라이브러리만 쓴다.
"""
import html as H
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUTHOR_SRC = os.path.join(ROOT, "발행", "저자소개_원고.md")
SITE = "https://moneyproducer.co.kr"


class SpecError(Exception):
    pass


LINK = ('color:#0a6350;font-weight:600;border-bottom:2px solid #8fd0bb;'
        'text-decoration:none;padding-bottom:1px;')
CODE = 'background:#f1f3f5;padding:1px 5px;border-radius:3px;font-size:.93em;'
H2 = 'margin:52px 0 18px;font-size:1.34em;line-height:1.45;font-weight:800;color:#16212e;'
H3 = 'margin:34px 0 12px;font-size:1.12em;line-height:1.5;font-weight:700;color:#16212e;'
P = 'margin:0 0 19px;line-height:1.85;'
NOTE = 'margin:0 0 6px;font-size:.9em;color:#7a8592;line-height:1.7;'
BQ = 'margin:24px 0;padding:14px 18px;background:#f7f8f9;border-left:3px solid #9aa5b1;color:#3d4852;line-height:1.8;font-size:.97em;'
HR = 'margin:40px 0;border:0;border-top:1px solid #e6e8ea;'
TB = 'width:100%;border-collapse:collapse;min-width:320px;margin:0;font-size:.95em;'
CAP = 'caption-side:top;text-align:left;padding:0 0 8px;font-weight:700;color:#16212e;'
TH = 'padding:10px 12px;border-bottom:2px solid #16212e;text-align:left;font-weight:700;'
TD = 'padding:10px 12px;border-bottom:1px solid #e6e8ea;vertical-align:top;'
LST = 'margin:0 0 19px;padding-left:1.4em;line-height:1.85;'
FIG = 'margin:28px 0;text-align:center;'
IMG = 'max-width:100%;height:auto;'
TOC = 'margin:8px 0 30px;padding:14px 18px;background:#f7f8f9;border:1px solid #e6e8ea;line-height:1.9;'
PRE = ('margin:26px 0;padding:20px 18px;background:#0f1b26;color:#e8eef3;border-radius:5px;'
       'overflow-x:auto;font-family:\'D2Coding\',\'Menlo\',\'Consolas\',monospace;'
       'font-size:.88em;line-height:1.9;white-space:pre;')


def inline(t):
    t = H.escape(t, quote=False)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'(?<![\*\w])\*(?!\s)(.+?)(?<!\s)\*(?![\*\w])', r'<i>\1</i>', t)
    t = re.sub(r'\[([^\]]+)\]\((https?://[^\)\s]+)\)',
               lambda m: f'<a href="{m.group(2).replace("&amp;", "&").replace("&", "&amp;")}" target="_blank" rel="noopener" style="{LINK}">{m.group(1)}</a>', t)
    t = re.sub(r'\[([^\]]+)\]\((/\d+)\)', rf'<a href="{SITE}\2" style="{LINK}">\1</a>', t)
    t = re.sub(r'`(\d{14})`',
               rf'<a href="https://dart.fss.or.kr/dsaf001/main.do?rcpNo=\1" target="_blank" rel="noopener" style="{LINK}">\1</a>', t)
    t = re.sub(r'`([^`]+)`', rf'<code style="{CODE}">\1</code>', t)
    t = re.sub(r'\\([*_`~\[\]()#|>!\\.-])', r'\1', t)
    return t


def author_box(meta=None):
    try:
        src = open(AUTHOR_SRC, encoding="utf-8").read()
    except OSError:
        raise SpecError(f"저자 박스 원본이 없다: {os.path.relpath(AUTHOR_SRC, ROOT)}")
    m = re.search(r'(?ms)^## 1\..*?^```html\n(.*?)^```', src)
    if not m:
        raise SpecError("저자 박스 원본에 「## 1.」 아래 ```html 덩어리가 없다")
    return add_dates(m.group(1).strip(), meta)


DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')


def add_dates(box_html, meta):
    """저자 박스(div.author-box) 끝에 게시일·최종 수정일·수정 이력 줄을 넣는다(애드센스 관문 5).
    meta = {"pub": "YYYY-MM-DD", "mod": "YYYY-MM-DD", "hist": [(날짜, 내용), ...]}. pub 이 없으면 넣지 않는다."""
    if not meta or not meta.get("pub"):
        return box_html
    pub = meta["pub"]
    mod = meta.get("mod") or pub
    hist = meta.get("hist") or []
    rows = [f"{pub} 최초 게시"] + [f"{d} {t}" for d, t in hist]
    line = (f'<p style="margin:8px 0 0;font-size:.9em;color:#5a6670;">게시일 {pub} · 최종 수정일 {mod}</p>\n'
            f'<p style="margin:2px 0 0;font-size:.9em;color:#5a6670;">수정 이력: ' + " / ".join(rows) + "</p>\n")
    i = box_html.rfind("</div>")
    if i < 0:
        raise SpecError("저자 박스 끝(</div>)을 찾지 못했다")
    return box_html[:i] + line + box_html[i:]


def read_meta(src, default_pub=None):
    """원고 머리 주석 <!-- 게시일: --> <!-- 수정일: --> <!-- 수정이력: 날짜 | 내용 --> (없으면 편 폴더 날짜)"""
    meta = {"pub": default_pub, "mod": None, "hist": []}
    for m in re.finditer(r'<!--\s*(게시일|수정일|수정이력)\s*:\s*(.*?)\s*-->', src):
        k, v = m.group(1), m.group(2)
        if k == "게시일" and DATE_RE.match(v): meta["pub"] = v
        elif k == "수정일" and DATE_RE.match(v): meta["mod"] = v
        elif k == "수정이력" and "|" in v:
            d, t = [x.strip() for x in v.split("|", 1)]
            if DATE_RE.match(d) and t: meta["hist"].append((d, t))
    if meta["hist"] and not meta["mod"]:
        meta["mod"] = max(d for d, _ in meta["hist"])
    return meta


def split_head(src):
    """제목 주석·디스커버 주석·h1 -> (title, discover, body_lines)"""
    lines = src.split("\n")
    title = disc = h1 = None
    start = None
    for i, l in enumerate(lines):
        s = l.strip()
        m = re.fullmatch(r'<!--\s*제목\s*:\s*(.+?)\s*-->', s)
        if m:
            title = m.group(1); continue
        m = re.fullmatch(r'<!--\s*디스커버\s*제목\s*:\s*(.+?)\s*-->', s)
        if m:
            disc = m.group(1); continue
        if s.startswith("# "):
            h1 = s[2:].strip(); start = i + 1
            break
    if start is None:
        raise SpecError("h1(「# 제목」 줄)이 없다")
    body = lines[start:]
    for i, l in enumerate(body):
        if "[집필 메모]" in l:
            body = body[:i]
            break
    return title or h1, disc, body


def convert_text(src, default_pub=None):
    title, disc, lines = split_head(src)
    meta = read_meta(src, default_pub)
    out, h2s, k = [], [], 0
    pending_cap = None
    toc_at = None
    isblock = re.compile(r'^(#{2,3}\s|>|\||```|---$|표\s*:|!\[|\[\[|[-*]\s|\d+\.\s|<!--)')
    while k < len(lines):
        s = lines[k].strip()
        if not s:
            k += 1; continue
        if pending_cap is not None and not s.startswith("|"):
            raise SpecError(f"「표: {pending_cap}」 다음 줄이 표가 아니다(줄 「{s[:30]}」)")
        if s.startswith("<!--") and s.endswith("-->"):
            k += 1; continue                       # 원고 안 내부 주석은 싣지 않는다
        if s.startswith("```"):
            k += 1; buf = []
            while k < len(lines) and not lines[k].strip().startswith("```"):
                buf.append(lines[k]); k += 1
            k += 1
            esc = [H.escape(b, quote=False).replace(" ", "&nbsp;") for b in buf]
            out.append(f'<pre style="{PRE}">' + "<br>".join(esc) + "</pre>")
            continue
        if s == "---":
            out.append(f'<hr style="{HR}">'); k += 1; continue
        m = re.fullmatch(r'\[\[(.+?)\]\]', s)
        if m:
            inner = m.group(1).strip()
            if inner == "목차":
                toc_at = len(out); out.append(None)
            elif inner == "저자 박스":
                out.append(author_box(meta))
            elif re.match(r'같은\s*묶음\s*:', inner):
                out.append("<!-- " + inner.replace("--", "—") + " -->")
            else:
                raise SpecError(f"모르는 자리표 [[{inner}]]")
            k += 1; continue
        if s.startswith("[[") or s.endswith("]]"):
            raise SpecError(f"자리표가 줄 하나를 다 차지하지 않는다: 「{s[:40]}」")
        if s.startswith("## "):
            n = len(h2s) + 1; text = s[3:].strip(); h2s.append(text)
            out.append(f'<h2 id="q{n}" style="{H2}">{inline(text)}</h2>'); k += 1; continue
        if s.startswith("### "):
            out.append(f'<h3 style="{H3}">{inline(s[4:].strip())}</h3>'); k += 1; continue
        m = re.fullmatch(r'표\s*:\s*(.+)', s)
        if m:
            pending_cap = m.group(1).strip(); k += 1; continue
        m = re.fullmatch(r'!\[(.*?)\]\((\S+?)\)', s)
        if m:
            alt, src_ = m.group(1).strip(), m.group(2)
            if len(alt) < 10:
                raise SpecError(f"그림 alt가 10자 미만: 「{alt}」({src_})")
            out.append(f'<figure style="{FIG}"><img src="{H.escape(src_)}" alt="{H.escape(alt)}" style="{IMG}"></figure>')
            out.append(f'<p style="{P}">&nbsp;</p>')  # H-233: 그림 다음 빈 줄 하나
            k += 1; continue
        if s.startswith(">"):
            buf = []
            while k < len(lines) and lines[k].strip().startswith(">"):
                buf.append(lines[k].strip().lstrip(">").strip()); k += 1
            out.append(f'<blockquote style="{BQ}">' + "<br>".join(inline(b) for b in buf if b) + "</blockquote>")
            continue
        if s.startswith("|"):
            rows = []
            while k < len(lines) and lines[k].strip().startswith("|"):
                rows.append([c.strip() for c in lines[k].strip().strip("|").split("|")]); k += 1
            seps = [r for r in rows if all(re.fullmatch(r'[-: ]*', c) for c in r)]
            rows = [r for r in rows if r not in seps]
            if not seps or len(rows) < 2:
                raise SpecError(f"표 형식이 깨졌다(구분 줄 |---| 또는 데이터 줄 없음): 「{'|'.join(rows[0]) if rows else ''}」")
            t = ['<div style="overflow-x:auto;">', f'<table style="{TB}">']
            if pending_cap:
                t.append(f'<caption style="{CAP}">{inline(pending_cap)}</caption>')
            t.append("<thead><tr>" + "".join(f'<th style="{TH}">{inline(c)}</th>' for c in rows[0]) + "</tr></thead><tbody>")
            for r in rows[1:]:
                t.append("<tr>" + "".join(f'<td style="{TD}">{inline(c)}</td>' for c in r) + "</tr>")
            t.append("</tbody></table></div>")
            out.append("\n".join(t)); pending_cap = None
            continue
        if re.match(r'^[-*]\s', s) or re.match(r'^\d+\.\s', s):
            ordered = bool(re.match(r'^\d+\.\s', s)); tag = "ol" if ordered else "ul"
            items = []
            pat = r'^\d+\.\s' if ordered else r'^[-*]\s'
            while k < len(lines) and re.match(pat, lines[k].strip()):
                items.append(re.sub(pat, "", lines[k].strip())); k += 1
            out.append(f'<{tag} style="{LST}">' + "".join(f"<li>{inline(i)}</li>" for i in items) + f"</{tag}>")
            continue
        buf = []
        while k < len(lines) and lines[k].strip() and not isblock.match(lines[k].strip()):
            buf.append(lines[k].strip()); k += 1
        if not buf:
            raise SpecError(f"읽을 수 없는 줄: 「{s[:40]}」")
        para = " ".join(buf)
        style = NOTE if (para.startswith("*") and para.endswith("*") and "**" not in para) else P
        out.append(f'<p style="{style}">{inline(para)}</p>')
    if pending_cap is not None:
        raise SpecError(f"「표: {pending_cap}」 뒤에 표가 없다")
    if toc_at is not None:
        if not h2s:
            raise SpecError("[[목차]]가 있는데 h2가 없다")
        out[toc_at] = (f'<div class="toc" id="toc" style="{TOC}"><p style="margin:0 0 4px;"><b>목차</b></p><ul style="margin:0;padding-left:1.2em;">'
                       + "".join(f'<li><a href="#q{i}" style="color:#3d4852;">{inline(h)}</a></li>' for i, h in enumerate(h2s, 1))
                       + "</ul></div>")
    head = [f"<!-- 제목: {title.replace('--', '—')} -->"]
    if disc:
        head.append(f"<!-- 디스커버 제목: {disc.replace('--', '—')} -->")
    return "\n".join(head + out) + "\n"


def convert(md_path):
    m = re.search(r'(\d{4}-\d{2}-\d{2})_', os.path.basename(os.path.dirname(os.path.abspath(md_path))))
    return convert_text(open(md_path, encoding="utf-8").read(), m.group(1) if m else None)


# ───────────────────────── 자체 시험 ─────────────────────────
SAMPLE = os.path.join(ROOT, "도구", "견본_원고_변환시험.md")
SAMPLE_KEYWORD = "전월세 전환율 상한"


def self_test():
    bad = []
    try:
        src = open(SAMPLE, encoding="utf-8").read()
    except OSError:
        print(f"변환기 시험: 실패 — 견본 원고 없음 {os.path.relpath(SAMPLE, ROOT)}"); return 1
    try:
        out = convert_text(src)
    except SpecError as e:
        print(f"변환기 시험: 실패 — 견본 원고가 규격 위반: {e}"); return 1
    first = out.split("\n", 2)
    if not first[0].startswith("<!-- 제목:"): bad.append("첫 줄 제목 주석 없음")
    if "<!-- 디스커버 제목:" not in first[1]: bad.append("둘째 줄 디스커버 제목 주석 없음")
    lead = re.search(r'(?m)^# .+\n+(.+)', src).group(1).strip()[:20]
    if H.escape(lead, quote=False) not in out: bad.append("h1 아래 첫 문단이 빠짐")
    if 'class="toc"' not in out or out.count('href="#q') != out.count("<h2 "): bad.append("목차가 h2 수와 다름")
    caps = re.findall(r'(?m)^표\s*:\s*(.+)$', src.split("[집필 메모]")[0])
    if out.count("<caption") != len(caps): bad.append(f"caption {out.count('<caption')}개 ≠ 표: 줄 {len(caps)}개")
    if out.count("<figure") != len(re.findall(r'(?m)^!\[', src)) or 'alt=""' in out: bad.append("그림·alt 누락")
    if 'id="author"' not in out or "#저자" not in out: bad.append("저자 박스 누락")
    if "<!-- 같은 묶음:" not in out: bad.append("같은 묶음 주석 누락")
    if "집필 메모" in out or "버려져야 하는 문장" in out: bad.append("[집필 메모] 뒤가 남음")
    if "[[" in out: bad.append("자리표가 남음")
    # 규격 위반 감지 3가지
    for name, broken in [("모르는 자리표", src.replace("[[목차]]", "[[차례]]", 1)),
                         ("표 없는 표: 줄", src.replace("[[저자 박스]]", "표: 빈 표\n\n[[저자 박스]]", 1)),
                         ("alt 짧은 그림", re.sub(r'(?m)^!\[[^\]]+\]', "![그림]", src, count=1))]:
        try:
            convert_text(broken); bad.append(f"규격 위반을 못 잡음({name})")
        except SpecError:
            pass
    gs = os.path.join(ROOT, "도구", "gate_search.py")
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(out); tmp = f.name
    try:
        r = subprocess.run([sys.executable, gs, tmp, "--keyword", SAMPLE_KEYWORD], capture_output=True, text=True)
        last = (r.stdout.strip().split("\n") or [""])[-1]
        if r.returncode != 0:
            bad.append("gate_search 치명: " + " / ".join(l for l in r.stdout.split("\n") if "치명" in l)[:300])
    finally:
        os.remove(tmp)
    if bad:
        print("변환기 시험: 실패 — " + " · ".join(bad)); return 1
    print(f"변환기 시험: 통과 (h2 {out.count('<h2 ')} · 표 {out.count('<table')} · 그림 {out.count('<figure')} · gate_search {last})")
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        sys.exit(self_test())
    if len(sys.argv) != 2:
        print("사용: python3 도구/원고_HTML변환.py <원고.md> > 발행.html | --self-test", file=sys.stderr); sys.exit(2)
    try:
        print(convert(sys.argv[1]), end="")
    except SpecError as e:
        print(f"규격 위반: {e}", file=sys.stderr); sys.exit(1)
