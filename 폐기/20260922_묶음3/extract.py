import re,html,sys
def body(n):
    s=open('p%d.html'%n,encoding='utf-8').read()
    m=re.search(r'<div class="contents_style"', s)
    if not m: return None
    i=m.start(); depth=0; j=i
    for t in re.finditer(r'<(/?)div\b[^>]*?(/?)>', s[i:]):
        if t.group(2)=='/': continue
        depth += -1 if t.group(1)=='/' else 1
        if depth==0:
            j=i+t.end(); break
    return s[i:j]
def plain(b):
    b=re.sub(r'<(script|style)\b.*?</\1>','',b,flags=re.S|re.I)
    t=html.unescape(re.sub(r'<[^>]+>','',b))
    return re.sub(r'\s+',' ',t)
for n in [8,16,17,21,22]:
    b=body(n)
    open('body%d.html'%n,'w',encoding='utf-8').write(b)
    t=plain(b)
    open('body%d.txt'%n,'w',encoding='utf-8').write(t)
    print(n, "HTMLlen=%d"%len(b), "plain(공백포함)=%d"%len(t), "plain(공백제외)=%d"%len(re.sub(r'\s','',t)))
