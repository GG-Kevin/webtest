#!/usr/bin/env python3
"""구글 자동완성 수요 측정(0토큰). 사용: python3 도구/demand_google.py 검색어1 검색어2 ... [--out 파일.json]
suggestqueries.google.com (client=firefox, hl=ko, gl=kr). 트렌드는 429로 막혀 쓰지 않는다.
각 검색어마다: 자동완성 개수(n), 대표 연관어 3개, 접미어(알파벳·가나다 확장) 포함 합계를 낸다."""
import json, os, subprocess, sys, urllib.parse, time, datetime

# 10/3 본사: 자동완성 호출은 autocomplete.py(구글·네이버 공용)를 쓴다. 이 파일의 사용법·출력은 그대로 둔다.
sys.dont_write_bytecode = True  # 도구/에 __pycache__를 남기지 않는다(커밋 대상 아님)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import autocomplete as _ac
except Exception:  # autocomplete.py가 없으면 옛 curl 방식
    _ac = None


def suggest(q):
    if _ac is not None:
        return _ac.google(q)
    url = "https://suggestqueries.google.com/complete/search?client=firefox&hl=ko&gl=kr&q=" + urllib.parse.quote(q)
    out = subprocess.run(["curl", "-sS", "-m", "15", "-A", "Mozilla/5.0", url], capture_output=True, text=True).stdout
    try:
        return json.loads(out)[1]
    except Exception:
        return None

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = None
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]
        args = [a for a in args if a != out]
    rows = []
    for q in args:
        base = suggest(q)
        time.sleep(0.4)
        ext = set(base or [])
        for suf in [" 방법", " 계산", " 비교", " 2026", " 얼마"]:
            r = suggest(q + suf)
            time.sleep(0.4)
            ext.update(r or [])
        rows.append({"query": q, "n_base": None if base is None else len(base),
                     "n_expanded": len(ext), "top": (base or [])[:3], "date": str(datetime.date.today())})
        print(f"{q}\t기본 {rows[-1]['n_base']}\t확장 {len(ext)}\t{' | '.join((base or [])[:3])}")
    if out:
        json.dump(rows, open(out, "w"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
