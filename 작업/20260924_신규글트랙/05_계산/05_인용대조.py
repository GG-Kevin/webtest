# 원고의 「」·> 인용을 저장 원문(태그 제거·공백 정규화)에 대고 문자열로 찾는다. 말줄임(…)은 조각별로.
import re,html,glob
def norm(t): return re.sub(r'\s+','',t)
def strip(path):
    t=open(path,encoding='utf-8',errors='ignore').read()
    t=re.sub(r'(?s)<script.*?</script>|<style.*?</style>','',t)
    return norm(html.unescape(re.sub(r'<[^>]+>',' ',t)))
src={}
for f in glob.glob('01_청취_증빙/kin_*.html')+glob.glob('03_사실자료_원문/*.html')+glob.glob('03_사실자료_원문/*.txt'):
    src[f]=strip(f) if f.endswith('.html') else norm(html.unescape(open(f,encoding='utf-8').read()))
s=open('05_원고.md',encoding='utf-8').read()
body=re.sub(r'<!--.*?-->','',s[:s.find('<!-- 원고 끝')])
qs=re.findall(r'「([^」]+)」',body)+[l[2:] for l in body.splitlines() if l.startswith('> ')]
bad=0
for q in qs:
    for part in [x.strip() for x in q.split('…') if x.strip()]:
        hits=[f for f,t in src.items() if norm(part) in t]
        print(('OK ' if hits else 'NG ')+part[:50]+' → '+(hits[0].split('/')[-1] if hits else '없음'))
        bad+= not hits
print('NG',bad)
