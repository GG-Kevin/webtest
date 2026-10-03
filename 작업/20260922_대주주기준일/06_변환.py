# -*- coding: utf-8 -*-
# 공정 12번 「지면」 — A(미리보기 HTML) · B(업로드 TXT)를 같은 변환 1회에서 낸다 (결정 71)
# 05_원고.md 는 읽기 전용. 쓰기 0.
import re, sys, os, hashlib

WORK = '/home/user/webtest/작업/20260922_대주주기준일'
SRC  = os.path.join(WORK, '05_원고.md')
TITLE = '2026년 대주주 기준일은 12월 31일이지만 50억은 12월 30일 종가입니다'

raw = open(SRC, encoding='utf-8').read()
body_md = raw.split('\n## 본문\n', 1)[1].split('\n## 집필 메모', 1)[0].rsplit('\n---', 1)[0]

# ---------- 마크다운 → HTML 조각 (한 번만 돈다) ----------
def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

LINK = re.compile(r'\[([^\]]*)\]\((/\d+)\)')

def inline(t):
    # 주석은 그대로 통과시킨다(화면에 안 보인다 · 결정 69)
    parts = re.split(r'(<!--.*?-->)', t)
    out = []
    for p in parts:
        if p.startswith('<!--'):
            out.append(p)
            continue
        p = esc(p)
        p = LINK.sub(lambda m: '<a href="%s">%s</a>' % (m.group(2), m.group(1)), p)
        out.append(p)
    return ''.join(out).strip()

lines = body_md.split('\n')
html = []
i = 0
SEP = re.compile(r'^\s*\|[\s|:-]+\|\s*$')
while i < len(lines):
    ln = lines[i]
    s = ln.strip()
    if not s:
        i += 1; continue
    # 단독 주석 줄 (표 이름표 등)
    if re.fullmatch(r'<!--.*?-->', s):
        html.append(s); i += 1; continue
    # 소제목
    m = re.match(r'^##\s+(.*)$', s)
    if m:
        html.append('<h2>%s</h2>' % inline(m.group(1)))
        i += 1; continue
    # 인용
    if s.startswith('>'):
        buf = []
        while i < len(lines) and lines[i].strip().startswith('>'):
            buf.append(re.sub(r'^\s*>\s?', '', lines[i]))
            i += 1
        html.append('<blockquote><p>%s</p></blockquote>' % inline(' '.join(x.strip() for x in buf)))
        continue
    # 표
    if s.startswith('|'):
        rows = []
        while i < len(lines) and lines[i].strip().startswith('|'):
            rows.append(lines[i].strip()); i += 1
        def cells(r):
            return [c.strip() for c in r.strip().strip('|').split('|')]
        has_head = len(rows) > 1 and SEP.match(rows[1])
        t = ['<table border="1">']
        start = 0
        if has_head:
            t.append('<thead><tr>' + ''.join('<th>%s</th>' % inline(c) for c in cells(rows[0])) + '</tr></thead>')
            start = 2
        t.append('<tbody>')
        for r in rows[start:]:
            if SEP.match(r):
                continue
            t.append('<tr>' + ''.join('<td>%s</td>' % inline(c) for c in cells(r)) + '</tr>')
        t.append('</tbody></table>')
        html.append(''.join(t))
        continue
    # 문단
    html.append('<p>%s</p>' % inline(s))
    i += 1

FRAG = '\n'.join(html)

MARK_A = '<!-- BODY-START -->'
MARK_B = '<!-- BODY-END -->'
BODY_BLOCK = MARK_A + '\n' + FRAG + '\n' + MARK_B

# ---------- B : 업로드용 TXT (본문 HTML 조각 그대로) ----------
B = BODY_BLOCK + '\n'

# ---------- A : 미리보기 HTML (본문은 위 BODY_BLOCK 그대로 재사용) ----------
CSS = """
:root{--ink:#16181d;--bg:#fff;--line:#d8dce3;--sub:#5b626e;--link:#0b57d0}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{background:#eef0f4;color:var(--ink);
 font-family:Pretendard,-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Malgun Gothic","Noto Sans KR",sans-serif;
 font-size:17px;line-height:1.85;-webkit-text-size-adjust:100%}
.note{background:#1f2430;color:#cfd6e4;font-size:13px;line-height:1.7;padding:12px 16px}
.note b{color:#fff}
.sheet{max-width:760px;margin:0 auto;background:var(--bg);padding:40px 28px 64px}
h1{font-size:30px;line-height:1.35;margin:0 0 28px;letter-spacing:-.02em}
h2{font-size:22px;line-height:1.45;margin:44px 0 14px;letter-spacing:-.01em;
 padding-top:18px;border-top:1px solid var(--line)}
p{margin:0 0 20px;word-break:keep-all}
a{color:var(--link);text-decoration:underline;text-underline-offset:3px;font-weight:600}
blockquote{margin:0 0 22px;padding:14px 18px;border-left:4px solid var(--ink);background:#f5f6f8}
blockquote p{margin:0;color:#2c313a}
table{width:100%;border-collapse:collapse;margin:0 0 24px;font-size:16px;line-height:1.6}
th,td{border:1px solid var(--line);padding:10px 12px;text-align:left;vertical-align:top;word-break:keep-all}
th{background:#f2f4f7;font-weight:700}
@media (max-width:640px){
 body{font-size:16px}
 .sheet{padding:24px 16px 48px}
 h1{font-size:24px}
 h2{font-size:20px}
 table{font-size:14px;display:block;overflow-x:auto}
 th,td{padding:8px 9px}
}
"""

A = ('<!DOCTYPE html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
     '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
     '<title>' + esc(TITLE) + '</title>\n'
     '<style>' + CSS + '</style>\n</head>\n<body>\n'
     '<div class="note"><b>미리보기</b> — 화면 확인용입니다. 티스토리에 붙일 것은 '
     '<b>06_발행본.txt</b>이고, 제목은 <b>06_발행_제목.txt</b>입니다.</div>\n'
     '<div class="sheet">\n'
     '<h1>' + esc(TITLE) + '</h1>\n'
     + BODY_BLOCK + '\n'
     '</div>\n</body>\n</html>\n')

open(os.path.join(WORK, '06_발행본.txt'), 'w', encoding='utf-8').write(B)
open(os.path.join(WORK, '06_미리보기.html'), 'w', encoding='utf-8').write(A)
open(os.path.join(WORK, '06_발행_제목.txt'), 'w', encoding='utf-8').write(TITLE + '\n')
print('A', len(A), 'B', len(B))
