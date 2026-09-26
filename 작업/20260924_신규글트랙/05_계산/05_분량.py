import re,sys
s=open(sys.argv[1],encoding='utf-8').read()
body=s[s.find('-->')+3:s.find('<!-- 원고 끝')]
body_nc=re.sub(r'<!--.*?-->','',body)
plain=re.sub(r'\]\([^)]*\)',']',body_nc).replace('**','').replace('[','').replace(']','')
print('A 마크업·URL 포함(주석 제외, 공백 포함):',len(body_nc.strip()))
print('B 링크URL·강조 제외(공백 포함, 표 포함):',len(plain.strip()))
print('C B의 공백 제외:',len(re.sub(r'\s','',plain)))
tbl=''.join(l for l in plain.splitlines(True) if l.startswith('|'))
print('D 표 글자(공백 포함):',len(tbl))
p=plain.strip(); print('첫 「결정세액」 위치:',p.find('결정세액'),'/ 첫 「0원」 위치:',p.find('0원'))
for x in re.split(r'\n## ',plain): print('  ',x.strip().split('\n',1)[0][:18], len(x.strip()))
