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
T={
 'A  종결문':'본 글을 근거로 한 의사결정의 책임은 이용자 본인에게 있습니다.',
 'B1 본 글은 2026년':'본 글은 2026년',
 'B2 기준 일반적인…작성되었으며':'기준 일반적인 정보 제공을 목적으로 작성되었으며',
 'C  특정 종목의 매수·매도…':'특정 종목의 매수·매도를 권유하거나 투자 자문을 제공하지 않습니다.',
 'D  하위 글입니다':'이 글은 동전주 상장폐지 기준 총정리의 하위 글입니다.',
}
nums=[2]+list(range(5,26))+[27,28]
res={k:{} for k in T}; months={}
for n in nums:
    b=body(n)
    if b is None:
        print("!! /%d 본문 div 못 찾음"%n); continue
    t=plain(b)
    for k,v in T.items():
        c=t.count(v)
        if c: res[k][n]=c
    for mm in re.finditer(r'본 글은 2026년\s*(\d+)월',t): months.setdefault(n,[]).append(mm.group(1))
for k in T:
    d=res[k]
    print("%-28s 편수=%2d 총회수=%2d  편=%s"%(k,len(d),sum(d.values()),[x[0] for x in sorted(d.items())]))
print("월 실측:",{n:v for n,v in sorted(months.items())})
