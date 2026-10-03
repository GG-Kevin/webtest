#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""서치 Stop 훅 — 「할까요?」로 멈추지 않게 한다 (본사 작성 2026-10-03, H-189 v3.1 · v2 B16 · 반대 검증 뒤 고침).

Claude Code Stop 훅 입력(표준 입력 JSON, https://code.claude.com/docs/en/hooks 「Stop input」, 10/3 확인):
  session_id · transcript_path · cwd · hook_event_name("Stop") · stop_hook_active · last_assistant_message …
  last_assistant_message = 이번 턴의 마지막 응답 글(문서: transcript 파일은 늦게 써질 수 있으니 이것을 먼저 쓴다).
판정
  1) stop_hook_active 가 true 면 통과(이미 한 번 막아 이어 가는 중 — 끝없는 막기를 피한다).
  2) 글은 last_assistant_message 를 먼저 쓴다. 없으면 transcript_path(JSONL)에서 **마지막 사람 입력 뒤**의
     assistant 글만 읽는다(이미 답이 온 지난 턴의 물음을 다시 읽지 않는다). 이번 턴 글이 없으면 통과.
  3) 끝부분(마지막 문단)을 본다. 꼬리의 목록·표·코드·인용·서명·괄호 줄을 걷어 낸 뒤
     - 마지막 문장이 물음(「?」로 끝남, 「…까요」로 끝남)이거나 결정을 넘기는 부탁(「어느 쪽 … 말씀해 주세요」 등)이면 막는다.
     - 마지막 문단 안에 듣는 사람에게 묻는 문장(진행할까요?·하시겠어요?·괜찮을지요?·어느 쪽…?)이 있으면 막는다.
     막을 때는 {"decision":"block","reason":…} 를 표준 출력에 쓰고 종료 0(문서: exit 0 + decision block = 멈추지 않고 이어 감).
  4) 그 밖에는 아무것도 쓰지 않고 종료 0(통과). 입력이 깨졌거나 읽을 수 없어도 통과한다(훅이 일을 막지 않게).
시험: python3 .claude/hooks/stop_guard.py --self-test  → 「Stop 훅 시험: 통과 n/n」, 하나라도 틀리면 종료 1.
표준 라이브러리만 쓴다. 대화 내용은 어디에도 저장하지 않는다.
"""
import json
import os
import re
import sys
import tempfile
import unicodedata

REASON = ("분기 표대로 하나를 고르고 이유 한 줄을 운영/07_결정로그.md에 적고 계속한다"
          "(회장에게 묻지 않는다).")

# 듣는 사람에게 묻는 어미(물음표 앞). 문단 안 어디에 있어도 막는다.
ASK_STRONG = re.compile(
    r"(할까요|볼까요|갈까요|드릴까요|될까요|을까요|ㄹ까요|까요"
    r"|하시겠어요|하시겠습니까|시겠어요|시겠습니까|겠어요|겠습니까"
    r"|을지요|ㄹ지요|할지요|는지요|좋을지요|괜찮을지요|지요"
    r"|원하시나요|원하세요|어떠세요|어떠신가요|어떨까요|괜찮을까요|괜찮으세요|괜찮으신가요"
    r"|되나요|할래요|하실래요|해도 될까요|해도 되나요)\s*[?？]")
# 「어느 쪽…」·「어떤 안…」 류가 물음으로 끝나는 문장
WHICH_Q = re.compile(r"(어느|어떤|무슨)\s*\S{0,8}\s*(쪽|것|안|방향|방식|순서|편|걸|거)\S*[^.!。]*[?？]")
# 물음표 없이 결정을 넘기는 부탁
DECIDE_REQ = re.compile(
    r"((어느|어떤|무엇|무얼|뭘|어떻게|할지|좋을지|갈지|할지를)[^.!?。]*"
    r"(말씀\s*해|말해|말씀|알려|정해|골라|선택해|결정해|지시해)\s*(주세요|주십시오|주시면|주시기\s*바랍니다|주시겠어요))"
    r"|((정해|골라|선택해|결정해|지시해|승인해)\s*(주세요|주십시오|주시면|주시기\s*바랍니다))"
    r"|((결정|선택|승인|지시)\s*(을|를)?\s*부탁(드립니다|드려요|합니다))")
EN_ASK = re.compile(r"\b(shall i|should i|would you like|do you want|want me to|which (one|option)|let me know which)\b", re.I)

LIST_LINE = re.compile(r"^\s*(\d+[.)]|[-*+•·]|[①-⑳]|[A-Za-z가-힣][.)])\s+\S")
SIGN_LINE = re.compile(r"^\s*([—–\-~]+\s*)?(사장|서치|본사|실장|서치\s*사장)(\s*\S{0,6})?\s*$")
PAREN_LINE = re.compile(r"^\s*[(（\[].*[)）\]]\s*$")
TRAIL = " \t\r\n*_`~\"'”’」』>.。…!！"
SENT_SPLIT = re.compile(r"(?<=[.!?。！？])\s+")


def _texts(content):
    if isinstance(content, str):
        return [content]
    if isinstance(content, list):
        return [c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"]
    return []


def _is_human(d):
    """사람이 친 입력인가(tool_result 만 있는 user 항목·메타 항목은 아니다)."""
    if d.get("type") != "user" or d.get("isSidechain") or d.get("isMeta"):
        return False
    content = (d.get("message") or {}).get("content")
    if isinstance(content, str):
        return bool(content.strip())
    if isinstance(content, list):
        return any(isinstance(c, dict) and c.get("type") == "text" and (c.get("text") or "").strip() for c in content)
    return False


def last_text_from_transcript(path):
    """마지막 사람 입력 뒤의 assistant(isSidechain 아님) 글 중 마지막 것. 없으면 None."""
    last = None
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(d, dict):
                    continue
                if _is_human(d):
                    last = None            # 새 턴 — 지난 턴의 글은 버린다
                    continue
                if d.get("type") != "assistant" or d.get("isSidechain"):
                    continue
                texts = [t for t in _texts((d.get("message") or {}).get("content")) if t and t.strip()]
                if texts:
                    last = "\n".join(texts)
    except OSError:
        return None
    return last


def tail_paragraph(text):
    """코드 울타리를 지우고, 꼬리의 목록·표·인용·서명·괄호·구분선 줄을 걷어 낸 뒤 마지막 문단(줄 목록)을 돌려준다."""
    t = unicodedata.normalize("NFKC", text or "")
    t = re.sub(r"(?s)```.*?(```|$)", "\n", t)
    lines = t.split("\n")
    while lines:
        s = lines[-1].strip()
        if (not s or s.startswith("|") or s.startswith(">") or LIST_LINE.match(s) or SIGN_LINE.match(s)
                or PAREN_LINE.match(s) or re.fullmatch(r"[-=*_—–]{3,}", s) or s.startswith("#")):
            lines.pop()
            continue
        break
    para = []
    for ln in reversed(lines):
        s = ln.strip()
        if not s:
            break
        if s.startswith("|") or LIST_LINE.match(s):
            break
        para.insert(0, s)
    return para


def clean_end(s):
    s = s.strip()
    # 끝에 붙은 괄호 덩어리(「(A/B)」 같은 선택지 표시)를 걷어 낸다
    while True:
        m = re.search(r"\s*[(（\[][^()（）\[\]]{0,40}[)）\]]\s*$", s)
        if not m or m.start() == 0:
            break
        s = s[:m.start()].rstrip()
    while s and s[-1] in TRAIL and s[-1] not in "?？":
        s = s[:-1].rstrip()
    return s


def is_asking(text):
    para = tail_paragraph(text)
    if not para:
        return False
    joined = " ".join(para)
    sents = [clean_end(x) for x in SENT_SPLIT.split(joined) if x.strip()]
    sents = [x for x in sents if x]
    if not sents:
        return False
    last = sents[-1]
    if last.endswith(("?", "？")) or re.search(r"까요$", last) or DECIDE_REQ.search(last) or EN_ASK.search(last):
        return True
    for s in sents:
        if ASK_STRONG.search(s) or WHICH_Q.search(s) or DECIDE_REQ.search(s):
            return True
        if EN_ASK.search(s) and s.endswith("?"):
            return True
    return False


def decide(data):
    """입력 dict → 막으면 출력 dict, 통과면 None"""
    if not isinstance(data, dict) or data.get("stop_hook_active") is True:
        return None
    text = data.get("last_assistant_message")
    if not isinstance(text, str) or not text.strip():
        path = data.get("transcript_path")
        text = last_text_from_transcript(path) if isinstance(path, str) and path else None
    if text and is_asking(text):
        return {"decision": "block", "reason": REASON}
    return None


# ── 시험 (0번 회차) ──
CASES = [
    # (이름, 마지막 응답 글, 막아야 하나)
    ("묻는 끝", "두 안이 있습니다. 어느 쪽으로 할까요?", True),
    ("보통 끝", "2편을 대기에 넣었습니다.", False),
    ("물음 + 번호 목록", "두 안이 있습니다. 어느 쪽으로 진행할까요?\n1. A안 — 허브 먼저\n2. B안 — 하위 먼저", True),
    ("물음 + 표", "어느 쪽으로 할까요?\n\n| 안 | 내용 |\n|---|---|\n| A | 허브 |\n| B | 하위 |", True),
    ("물음 + 괄호 선택지", "진행할까요? (A/B)", True),
    ("물음 + 서명", "어느 쪽으로 할까요?\n— 사장", True),
    ("결정 넘기는 부탁", "A안과 B안 중 어느 쪽이 좋을지 말씀해 주세요.", True),
    ("하시겠어요", "바로 진행하시겠어요?", True),
    ("괜찮을지요", "이대로 진행해도 괜찮을지요?", True),
    ("물음 + 코드", "이 명령으로 갈까요?\n```\npython3 도구/scout.py\n```", True),
    ("물음 뒤 설명 문장", "편성을 이대로 둘까요? 예비는 2편입니다.", True),
    ("영어 물음", "Shall I continue with option A?", True),
    ("스스로 묻고 답함", "왜 막혔나? 원장 줄이 승인 상태라서 진행분에 걸렸습니다. 같은 묶음 줄을 빼고 다시 돌려 통과했습니다.", False),
    ("보고 + 표", "묶음 B1004-1 끝.\n\n| 편 | 상태 |\n|---|---|\n| 1 | 대기 |\n| 2 | 대기 |", False),
    ("보고 + 목록", "0번 회차를 마쳤습니다.\n- 게이트 시험 통과\n- Stop 훅 시험 통과", False),
    ("물음표 없는 결론", "분기 표대로 예비 편으로 바꿨고 결정로그 D-3에 적었습니다.", False),
]


def self_test():
    ok = 0
    rows = []
    for name, msg, want in CASES:
        got = decide({"stop_hook_active": False, "last_assistant_message": msg}) is not None
        rows.append((name, want, got))
        ok += got == want
    # stop_hook_active: true 면 묻는 끝도 통과
    got = decide({"stop_hook_active": True, "last_assistant_message": "어느 쪽으로 할까요?"}) is not None
    rows.append(("stop_hook_active true", False, got))
    ok += got is False
    # transcript 대체 경로: 이번 턴 글만 읽는다
    tmpd = tempfile.mkdtemp()
    def tr(lines):
        p = os.path.join(tmpd, f"t{len(os.listdir(tmpd))}.jsonl")
        with open(p, "w", encoding="utf-8") as f:
            for x in lines:
                f.write(json.dumps(x, ensure_ascii=False) + "\n")
        return p
    U = lambda s: {"type": "user", "message": {"role": "user", "content": s}}
    A = lambda s: {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": s}]}}
    R = {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "x", "content": "ok"}]}}
    tcases = [
        ("transcript 묻는 끝", [U("시작"), A("편성표를 만들었습니다."), R, A("어느 쪽으로 할까요?")], True),
        ("transcript 보통 끝", [U("시작"), A("어느 쪽으로 할까요?"), U("A로 해"), A("A로 했습니다."), R, A("대기 2편을 커밋했습니다.")], False),
        ("transcript 지난 턴 물음만", [U("시작"), A("어느 쪽으로 할까요?"), U("A로 해")], False),
    ]
    for name, lines, want in tcases:
        got = decide({"stop_hook_active": False, "transcript_path": tr(lines)}) is not None
        rows.append((name, want, got))
        ok += got == want
    for f in os.listdir(tmpd):
        os.unlink(os.path.join(tmpd, f))
    os.rmdir(tmpd)
    for name, want, got in rows:
        mark = "맞음" if want == got else "틀림"
        print(f"{mark}\t{name}\t기대 {'막음' if want else '통과'}\t실제 {'막음' if got else '통과'}")
    print(f"Stop 훅 시험: {'통과' if ok == len(rows) else '실패'} {ok}/{len(rows)}")
    return 0 if ok == len(rows) else 1


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        return self_test()
    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
    except ValueError:
        return 0
    out = decide(data)
    if out:
        sys.stdout.write(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # 훅 오류로 세션 일을 막지 않는다(시험 모드는 위에서 이미 끝난다)
        sys.exit(0)
