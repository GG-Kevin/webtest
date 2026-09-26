import re,sys,html

TAG=re.compile(r'(?is)<\s*(/?)div\b[^>]*>')

def body_of(s):
    m=re.search(r'(?is)<div[^>]*class="[^"]*contents_style[^"]*"[^>]*>', s)
    if not m: return None
    i=m.end(); depth=1
    for t in TAG.finditer(s, i):
        depth += -1 if t.group(1) else 1
        if depth==0:
            return s[i:t.start()]
    return None

def text(b):
    b=re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>',' ',b)
    b=re.sub(r'(?i)<br\s*/?>','\n',b)
    b=re.sub(r'(?i)</(p|li|h[1-6]|div|tr|td|blockquote)>','\n',b)
    t=html.unescape(re.sub(r'<[^>]+>',' ',b))
    t=re.sub(r'[ \t\xa0]+',' ',t)
    return '\n'.join(l.strip() for l in t.split('\n') if l.strip())

if __name__=='__main__':
    s=open(sys.argv[1],encoding='utf-8',errors='replace').read()
    b=body_of(s)
    print('body len:', len(b) if b else None)
    t=text(b)
    print('chars:', len(t.replace('\n','')))
    L=t.split('\n')
    print('--- 첫 8 ---'); print('\n'.join(L[:8]))
    print('--- 끝 14 ---'); print('\n'.join(L[-14:]))
