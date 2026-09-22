# -*- coding: utf-8 -*-
# 결정 71 — 원고 본문 구간 · A · B 셋을 같은 규칙으로 정규화해 md5 대조
import re, hashlib, html as H
W='/home/user/webtest/작업/20260922_대주주기준일/'
INLINE = r'</?(?:a|strong|em|b|i|span|code)\b[^>]*>'

def norm(t):
    t = re.sub(r'<!--.*?-->', ' ', t, flags=re.S)         # 1 HTML 주석 제거
    t = re.sub(INLINE, '', t)                             # 2a 인라인 태그는 붙여서 제거(낱말 안 쪼갠다)
    t = re.sub(r'<[^>]+>', ' ', t)                        # 2b 나머지 블록 태그는 공백으로
    t = H.unescape(t)                                     # 3 엔티티 복원
    t = re.sub(r'\[([^\]]*)\]\((/\d+)\)', r'\1', t)       # 4 마크다운 링크 → 글자만
    t = '\n'.join(l for l in t.split('\n')
                  if not (('|' in l) and re.fullmatch(r'[\s|:\-]+', l)))   # 5a 표 구분행 제거
    t = t.replace('|', ' ')                               # 5b 표 파이프
    t = re.sub(r'(?m)^\s*#+\s*', ' ', t)                  # 5c 소제목 마커
    t = re.sub(r'(?m)^\s*>\s*', ' ', t)                   # 5d 인용 마커
    t = t.replace('**', '')                               # 5e 굵게 마커
    t = re.sub(r'\s+', ' ', t).strip()                    # 6 공백 정규화
    return t

raw = open(W+'05_원고.md', encoding='utf-8').read()
md  = raw.split('\n## 본문\n',1)[1].split('\n## 집필 메모',1)[0].rsplit('\n---',1)[0]
cut = lambda p: open(W+p,encoding='utf-8').read().split('<!-- BODY-START -->',1)[1].split('<!-- BODY-END -->',1)[0]

for name, txt in (('원고 본문 구간', md),
                  ('A 미리보기 HTML', cut('06_미리보기.html')),
                  ('B 업로드 TXT',   cut('06_발행본.txt'))):
    n = norm(txt)
    print('%-16s len=%5d  md5=%s' % (name, len(n), hashlib.md5(n.encode()).hexdigest()))
