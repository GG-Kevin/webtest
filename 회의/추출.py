#!/usr/bin/env python3
"""대화 원본(JSONL)에서 회의록을 뽑는다. 요약하지 않는다 — 말한 그대로 옮긴다.

회의 = 회장의 말 + 사장의 답. 도구 호출·파일 내용·에이전트 내부는 회의가 아니다.
다만 사장이 답변 안에 옮긴 에이전트 발언은 그대로 남는다(사장 답의 일부이므로).

사용:  python3 회의/추출.py [세션ID]
"""
import json, io, os, re, sys, glob, datetime

SRC_DIR = '/root/.claude/projects/-home-user-webtest'
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))

NOISE = (
    '[SYSTEM NOTIFICATION', '<task-notification>', '<system-reminder>',
    'Stop hook feedback', '[Subagent hand-back]', 'Caveat:',
    'This session is being continued', 'Another Claude session sent a message',
)

def text_of(content):
    """content(문자열 또는 블록 목록)에서 사람이 말한 텍스트만 뽑는다."""
    if isinstance(content, str):
        return content
    out = []
    for b in content or []:
        if not isinstance(b, dict):
            continue
        if b.get('type') == 'text':
            out.append(b.get('text', ''))
        # tool_use / tool_result / thinking 은 회의가 아니다
    return '\n'.join(out)

def is_noise(t):
    s = t.lstrip()
    return any(s.startswith(n) or n in s[:400] for n in NOISE)

def strip_reminders(t):
    t = re.sub(r'<system-reminder>.*?</system-reminder>', '', t, flags=re.S)
    return t.strip()

def extract(path):
    rows = []
    for line in io.open(path, encoding='utf-8', errors='ignore'):
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get('isSidechain'):      # 서브에이전트 내부 대화
            continue
        t = d.get('type')
        if t not in ('user', 'assistant'):
            continue
        msg = d.get('message') or {}
        txt = strip_reminders(text_of(msg.get('content')))
        if not txt or is_noise(txt):
            continue
        rows.append((t, d.get('timestamp', ''), txt))
    return rows

def main():
    sid = sys.argv[1] if len(sys.argv) > 1 else None
    files = ([os.path.join(SRC_DIR, sid + '.jsonl')] if sid
             else sorted(glob.glob(os.path.join(SRC_DIR, '*.jsonl')), key=os.path.getmtime))
    for f in files:
        if not os.path.exists(f):
            print('없음:', f); continue
        rows = extract(f)
        if not rows:
            continue
        day = datetime.datetime.fromtimestamp(os.path.getmtime(f)).strftime('%Y%m%d')
        out = os.path.join(OUT_DIR, '%s_회의록.md' % day)
        with io.open(out, 'w', encoding='utf-8') as w:
            w.write('# 회의록 %s\n\n' % day)
            w.write('> **여과 없이 옮긴 것이다.** 요약·교정·삭제를 하지 않는다.\n')
            w.write('> 원본 `%s`에서 `회의/추출.py`로 뽑았다.\n' % os.path.basename(f))
            w.write('> 회장의 말과 사장의 답만 남긴다 — 도구 호출·파일 내용·에이전트 내부는 회의가 아니다.\n')
            w.write('> 사장이 답변에 옮긴 에이전트 발언은 사장 답의 일부이므로 그대로 있다.\n\n')
            w.write('발언 %d건 · 뽑은 시각 %s\n\n---\n\n'
                    % (len(rows), datetime.datetime.now().strftime('%Y-%m-%d %H:%M')))
            for who, ts, txt in rows:
                stamp = ts[11:16] if len(ts) > 16 else ''
                w.write('## %s%s\n\n%s\n\n---\n\n'
                        % ('회장' if who == 'user' else '사장',
                           ' · %s' % stamp if stamp else '', txt))
        print('%s  발언 %d건  %d KB' % (out, len(rows), os.path.getsize(out) // 1024))

if __name__ == '__main__':
    main()
