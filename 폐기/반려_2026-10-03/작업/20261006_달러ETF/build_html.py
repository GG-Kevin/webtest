#!/usr/bin/env python3
"""원고.md -> 발행.html (티스토리 HTML 모드 붙여넣기용). 사용: python3 build_html.py [제목]
표는 caption 포함, GRAPH_1은 계산결과.txt 숫자로 그린 인라인 SVG(role=img, aria-label=alt)."""
import re, html as H, sys
BYLINE_URL = "https://moneyproducer.co.kr/pages/머니프로듀서를-소개합니다"
TITLE = sys.argv[1] if len(sys.argv) > 1 else ""
src = open("원고.md", encoding="utf-8").read()
src = re.split(r"\n#+\s*제목 3안", src)[0]
src = re.sub(r"^# .*\n", "", src, count=1)               # 맨 위 H1은 티스토리 제목 칸이라 뺀다

LINK = "color:#0a6350;font-weight:600;border-bottom:2px solid #8fd0bb;text-decoration:none;"
def inline(t):
    t = H.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    def a(m):
        u = m.group(2)
        ext = ' target="_blank" rel="noopener"' if "moneyproducer.co.kr" not in u else ""
        return f'<a href="{u}"{ext} style="{LINK}">{m.group(1)}</a>'
    t = re.sub(r"\[([^\]]+)\]\((https?://[^\)\s]+)\)", a, t)
    t = re.sub(r"`([^`]+)`", r'<code style="background:#f1f3f5;padding:1px 5px;border-radius:3px;font-size:.93em;">\1</code>', t)
    return t

# ---- 그래프 (계산결과.txt [표3]에서 숫자를 읽는다) ----
def graph():
    txt = open("계산결과.txt", encoding="utf-8").read()
    t3 = txt.split("[표3]")[1].split("[표4]")[0]
    rows = []
    for l in t3.splitlines():
        m = re.match(r"(\d{4})\|환율 \d+→\d+ \(([+-][\d.]+)%\)\|KODEX선물 ([+-][\d.]+)%\|TIGER단기채권 (?:([+-][\d.]+)%|-)", l)
        if m and int(m.group(1)) >= 2020:
            rows.append((m.group(1), float(m.group(2)), float(m.group(3)), float(m.group(4)) if m.group(4) else None))
    W, Hh = 640, 380; top, bot, left = 46, 50, 46; ph = Hh - top - bot; lo, hi = -10, 22
    def y(v): return top + ph * (hi - v) / (hi - lo)
    out = [f'<svg viewBox="0 0 {W} {Hh}" role="img" aria-label="ALT" style="width:100%;height:auto;max-width:640px;display:block;margin:0 auto;font-family:sans-serif;">']
    for v in range(-10, 23, 10):
        out.append(f'<line x1="{left}" y1="{y(v):.1f}" x2="{W-8}" y2="{y(v):.1f}" stroke="{"#718096" if v==0 else "#e2e8f0"}"/><text x="{left-6}" y="{y(v)+4:.1f}" font-size="11" text-anchor="end" fill="#4a5568">{v:+d}%</text>')
    gw = (W - left - 10) / len(rows); bw = 14
    cols = ["#718096", "#4a6fa5", "#e0a030"]
    for i, (yr, fx, ko, ti) in enumerate(rows):
        x0 = left + gw * i + (gw - 3 * bw - 4) / 2
        for j, v in enumerate((fx, ko, ti)):
            if v is None: continue
            xx = x0 + j * (bw + 2); y0 = y(0); y1 = y(v)
            out.append(f'<rect x="{xx:.1f}" y="{min(y0,y1):.1f}" width="{bw}" height="{abs(y1-y0):.1f}" fill="{cols[j]}"/>')
            out.append(f'<text x="{xx+bw/2:.1f}" y="{(y1-4 if v>=0 else y1+11):.1f}" font-size="9" text-anchor="middle" fill="#1a202c">{v:+.1f}</text>')
        out.append(f'<text x="{left+gw*i+gw/2:.1f}" y="{top+ph+34}" font-size="12" text-anchor="middle" fill="#2d3748">{yr}</text>')
    for k, (lab, c) in enumerate((("원/달러 환율 변화", cols[0]), ("KODEX 미국달러선물", cols[1]), ("TIGER 미국달러단기채권", cols[2]))):
        out.append(f'<rect x="{left+k*165}" y="8" width="11" height="11" fill="{c}"/><text x="{left+k*165+15}" y="18" font-size="11" fill="#2d3748">{lab}</text>')
    out.append(f'<text x="{W-8}" y="38" font-size="10" text-anchor="end" fill="#4a5568">연초 첫 거래일~연말(2026은 10-01) 수익률 · 2026-10-01 기준</text>')
    out.append('</svg>')
    return "\n".join(out)

P = "margin:0 0 19px;line-height:1.85;"
H2 = "margin:48px 0 16px;padding-bottom:8px;border-bottom:2px solid #2d3748;font-size:1.4em;line-height:1.45;"
H3 = "margin:30px 0 10px;font-size:1.15em;color:#2d3748;"
TH = "padding:9px 8px;text-align:left;background:#2d3748;color:#fff;font-weight:700;"
TD = "padding:9px 8px;border-bottom:1px solid #e2e8f0;vertical-align:top;"
lines = src.split("\n"); out = []; i = 0; pending_cap = None
while i < len(lines):
    l = lines[i]
    if not l.strip(): i += 1; continue
    m = re.match(r"^Table:\s*(.+)$", l)
    if m: pending_cap = m.group(1).strip(); i += 1; continue
    if l.startswith("|"):
        rows = []
        while i < len(lines) and lines[i].startswith("|"): rows.append(lines[i]); i += 1
        cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows if not re.match(r"^\|[\s:|-]+\|?$", r)]
        h = "<div style=\"overflow-x:auto;margin:0 0 22px;\"><table style=\"width:100%;border-collapse:collapse;font-size:.92em;min-width:360px;\">"
        if pending_cap: h += f"<caption style=\"caption-side:top;text-align:left;padding:0 0 8px;font-size:.9em;color:#4a5568;\">{inline(pending_cap)}</caption>"; pending_cap = None
        h += "<tr>" + "".join(f"<th style=\"{TH}\">{inline(c)}</th>" for c in cells[0]) + "</tr>"
        for r in cells[1:]: h += "<tr>" + "".join(f"<td style=\"{TD}\">{inline(c)}</td>" for c in r) + "</tr>"
        out.append(h + "</table></div>"); continue
    m = re.match(r"^!\[([^\]]*)\]\(GRAPH_1\)", l)
    if m:
        alt = m.group(1)
        svg = graph().replace("ALT", H.escape(alt, quote=True))
        out.append(f"<figure style=\"margin:26px 0;\">{svg}</figure>"); i += 1; continue
    m = re.match(r"^(#{2,3})\s+(.+)$", l)
    if m:
        out.append(f"<h{len(m.group(1))} style=\"{H2 if len(m.group(1))==2 else H3}\">{inline(m.group(2))}</h{len(m.group(1))}>"); i += 1; continue
    if re.match(r"^\s*[-*]\s+", l):
        items = []
        while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]): items.append(re.sub(r"^\s*[-*]\s+", "", lines[i])); i += 1
        out.append("<ul style=\"margin:0 0 19px;padding-left:1.3em;line-height:1.85;\">" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>"); continue
    if l.startswith(">"):
        q = []
        while i < len(lines) and lines[i].startswith(">"): q.append(lines[i].lstrip("> ")); i += 1
        out.append(f"<blockquote style=\"margin:22px 0;padding:14px 18px;background:#f7f8f9;border-left:3px solid #9aa5b1;line-height:1.8;font-size:.97em;\">{inline(' '.join(q))}</blockquote>"); continue
    m = re.match(r"^<byline>(.*)</byline>\s*$", l)
    if m:
        t = m.group(1).replace("BYLINE_URL", BYLINE_URL)
        out.append(f"<p style=\"margin:36px 0 0;padding-top:16px;border-top:1px solid #e2e8f0;font-size:.9em;color:#4a5568;line-height:1.8;\">{inline(t)}</p>"); i += 1; continue
    if re.match(r"^[-*_]{3,}\s*$", l): out.append("<hr style=\"margin:36px 0;border:0;border-top:1px solid #e6e8ea;\">"); i += 1; continue
    out.append(f"<p style=\"{P}\">{inline(l)}</p>"); i += 1
head = f"<!-- 제목: {TITLE} -->\n" if TITLE else ""
open("발행.html", "w", encoding="utf-8").write(head + "\n".join(out) + "\n")
print("발행.html", len("\n".join(out)), "자")
