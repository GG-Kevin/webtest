import re,os,sys,glob
sys.path.insert(0,'/tmp/wk')
from extract import body_of, text
DOT=r'(?:·|&middot;|&#183;|&#xB7;)'
END=re.compile(r'\s*본 글을 근거로 한 의사결정의 책임은 이용자 본인에게 있습니다\.')
LEAD=re.compile(r'본 글은\s*20\d\d년\s*\d+월(?:\s*\d+일)?\s*기준\s*일반적인 정보 제공을 목적으로 작성되었으며,\s*')
SEC=re.compile(r'^특정 종목의 매수'+DOT+r'매도를 권유하거나 투자 자문을 제공하지 않습니다\.\s*')
SUBP=re.compile(r'(?is)<p[^>]*>\s*이 글은\b.{0,300}?하위 글입니다\.\s*</p>\s*')
SUBS=re.compile(r'(?is)이 글은\b.{0,300}?하위 글입니다\.\s*')

def clean(b):
    log=[]
    b,k=SUBP.subn('',b)
    if not k:
        b,k=SUBS.subn('',b)
        if k: log.append('하위글 문장 제거')
    else: log.append('하위글 문단 제거')
    b,k=END.subn('',b)
    if k: log.append('종결문 제거')
    b,k=LEAD.subn('',b)
    if k:
        log.append('안내 앞문장 제거')
        b2,k2=SEC.subn('',b)
        m=re.search(r'(?i)(<(?:b|strong)>\s*안내\s*</(?:b|strong)>\s*<br\s*/?>\s*)(특정 종목의 매수(?:·|&middot;|&#183;)매도를 권유하거나 투자 자문을 제공하지 않습니다\.\s*)', b)
        if m:
            b=b[:m.start(2)]+b[m.end(2):]
            log.append('투자자문 문장 제거')
    b=re.sub(r'(?i)(<(?:b|strong)>\s*안내\s*</(?:b|strong)>\s*<br\s*/?>)\s*(?:<br\s*/?>\s*)+', r'\1\n', b)
    return b, log

os.makedirs('/home/user/webtest/발행/정리', exist_ok=True)
for f in glob.glob('/home/user/webtest/발행/정리/*.html'): os.remove(f)
rep=[]
for f in sorted(glob.glob('/tmp/wk/raw/*.html'), key=lambda p:int(os.path.basename(p)[:-5])):
    n=os.path.basename(f)[:-5]
    b=body_of(open(f,encoding='utf-8',errors='replace').read())
    a=len(text(b).replace('\n',''))
    nb,log=clean(b)
    c=len(text(nb).replace('\n',''))
    if log: open(f'/home/user/webtest/발행/정리/{n}.html','w',encoding='utf-8').write(nb.strip()+'\n')
    rep.append((n,log,a,c))
print(f"{'글':>5} {'전':>6} {'후':>6} {'감소':>5}  내역")
for n,log,a,c in rep: print(f"/{n:<4} {a:>6} {c:>6} {a-c:>5}  {'; '.join(log) or '— 변경 없음'}")
print('\n총 감소:', sum(a-c for _,l,a,c in rep if l), '자 / 파일', len([1 for _,l,_,_ in rep if l]),'개')
