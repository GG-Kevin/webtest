# 원고 마크다운 -> 티스토리 HTML. 공시 접수번호는 DART 실제 링크로.
import re, html as H, sys, io

def convert(md_path: str) -> str:
    src = open(md_path, encoding='utf-8').read()
    i = src.find('\n## '); j = src.rfind('[집필 메모]')
    body = src[i:j if j > 0 else len(src)].strip()
    body = re.sub(r'\n---\s*\n##\s*$', '', body).rstrip().rstrip('#').rstrip().rstrip('-').rstrip()

    LINK = 'color:#1a6b4f;border-bottom:1px solid #b7d6c9;text-decoration:none;'
    CODE = 'background:#f1f3f5;padding:1px 5px;border-radius:3px;font-size:.93em;'

    def inline(t):
        t = H.escape(t, quote=False)
        t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
        t = re.sub(r'(?<![\*\w])\*(?!\s)(.+?)(?<!\s)\*(?![\*\w])', r'<i>\1</i>', t)
        t = re.sub(r'\[([^\]]+)\]\((https?://[^\)]+)\)',
                   rf'<a href="\2" target="_blank" rel="noopener" style="{LINK}">\1</a>', t)
        t = re.sub(r'\[([^\]]+)\]\((/\d+)\)',
                   rf'<a href="https://moneyproducer.co.kr\2" style="{LINK}">\1</a>', t)
        # 공시 접수번호 -> DART 원문
        t = re.sub(r'`(\d{14})`',
                   rf'<a href="https://dart.fss.or.kr/dsaf001/main.do?rcpNo=\1" target="_blank" rel="noopener" style="{LINK}">\1</a>', t)
        # dart.fss.or.kr -> 공시통합검색
        t = re.sub(r'`dart\.fss\.or\.kr`',
                   rf'<a href="https://dart.fss.or.kr/dsab007/main.do" target="_blank" rel="noopener" style="{LINK}">dart.fss.or.kr</a>', t)
        t = re.sub(r'`([^`]+)`', rf'<code style="{CODE}">\1</code>', t)
        # 마크다운 이스케이프 해제 (\* 는 각주 별표다)
        t = re.sub(r'\\([*_`~\[\]()#|>!\\.-])', r'\1', t)
        return t

    H2  = 'margin:52px 0 18px;font-size:1.34em;line-height:1.45;font-weight:800;color:#16212e;'
    P   = 'margin:0 0 19px;line-height:1.85;'
    BQR = 'margin:24px 0;padding:14px 18px;background:#f7f8f9;border-left:3px solid #9aa5b1;color:#3d4852;line-height:1.8;font-size:.97em;'
    BQD = 'margin:24px 0;padding:16px 18px;background:#fbfaf6;border:1px solid #e6e2d6;line-height:1.85;font-size:.96em;'
    HR  = 'margin:40px 0;border:0;border-top:1px solid #e6e8ea;'
    TB  = 'width:100%;border-collapse:collapse;margin:26px 0;font-size:.95em;'
    TH  = 'padding:10px 12px;border-bottom:2px solid #16212e;text-align:left;font-weight:700;'
    TD  = 'padding:10px 12px;border-bottom:1px solid #e6e8ea;vertical-align:top;'
    NOTE= 'margin:0 0 6px;font-size:.9em;color:#7a8592;line-height:1.7;'
    PRE = ('margin:26px 0;padding:20px 18px;background:#0f1b26;color:#e8eef3;border-radius:5px;'
           'overflow-x:auto;font-family:\'D2Coding\',\'Menlo\',\'Consolas\',monospace;'
           'font-size:.88em;line-height:1.9;white-space:pre;')

    out, lines, k = [], body.split('\n'), 0
    while k < len(lines):
        s = lines[k].strip()
        if not s:
            k += 1; continue
        if s.startswith('```'):
            k += 1; buf = []
            while k < len(lines) and not lines[k].strip().startswith('```'):
                buf.append(lines[k]); k += 1
            k += 1
            esc = [H.escape(b, quote=False).replace(' ', '&nbsp;') for b in buf]
            esc = [re.sub(r'★', '<span style="color:#ffd166;font-weight:700;">★</span>', e) for e in esc]
            out.append(f'<pre style="{PRE}">' + '<br>'.join(esc) + '</pre>')
            continue
        if s == '---':
            out.append(f'<hr style="{HR}">'); k += 1; continue
        if s.startswith('## '):
            out.append(f'<h2 style="{H2}">{inline(s[3:].strip())}</h2>'); k += 1; continue
        if s.startswith('>'):
            buf = []
            while k < len(lines) and lines[k].strip().startswith('>'):
                buf.append(lines[k].strip().lstrip('>').strip()); k += 1
            joined = ''.join(buf)
            st = BQD if ('「' in joined or '⇨' in joined) else BQR
            out.append(f'<blockquote style="{st}">' + '<br>'.join(inline(b) for b in buf if b) + '</blockquote>')
            continue
        if s.startswith('|'):
            rows = []
            while k < len(lines) and lines[k].strip().startswith('|'):
                rows.append([c.strip() for c in lines[k].strip().strip('|').split('|')]); k += 1
            rows = [r for r in rows if not all(re.fullmatch(r'[-: ]*', c) for c in r)]
            t = [f'<table style="{TB}"><thead><tr>']
            t += [f'<th style="{TH}">{inline(c)}</th>' for c in rows[0]]
            t.append('</tr></thead><tbody>')
            for r in rows[1:]:
                t.append('<tr>' + ''.join(f'<td style="{TD}">{inline(c)}</td>' for c in r) + '</tr>')
            t.append('</tbody></table>')
            out.append(''.join(t)); continue
        buf = []
        while k < len(lines) and lines[k].strip() and not re.match(r'^(##\s|>|\||```|---$)', lines[k].strip()):
            buf.append(lines[k].strip()); k += 1
        para = ' '.join(buf)
        style = NOTE if (para.startswith('*') and para.endswith('*') and '**' not in para) else P
        out.append(f'<p style="{style}">{inline(para)}</p>')
    return '\n'.join(out) + '\n'

if __name__ == '__main__':
    print(convert(sys.argv[1]), end='')
