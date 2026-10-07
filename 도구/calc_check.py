#!/usr/bin/env python3
"""calc_check — 대조 스크립트(0토큰): calc.py 재실행 ↔ 발행 HTML 표 숫자 ↔ 계산기 쪽 ↔ 수치대장 원문.

사용:
  python3 도구/calc_check.py <작업 폴더> [--html <발행.html|계산기 HTML>] [--no-open] [--out <대조.txt>] [--stdout]
작업 폴더(공용 경로): 작업/<YYYY-MM-DD>_<영문>/ — calc.py · 수치대장.csv · 발행.html(없으면 --html) → 대조.txt
하는 일:
  1) calc.py를 다시 돌린다(작업 폴더에서, 60초). 표준 출력의 숫자를 모은다.
  2) 발행 HTML의 <table> 안 숫자 하나하나가 calc 출력 숫자와 맞는지 본다(표시 자릿수 안에서 같으면 맞음).
     날짜(2026-10-03·10월 3일·2026년)·조문 번호(제53조·2항·3호)·쪽 번호·한 자리 맨 정수(단위 없음)는 세지 않는다.
  3) 계산기 대조(v3.1): calc.py에 TESTS(입력 dict 10개)와 compute(**입력) → dict가 있고, HTML에
     function calcCompute(input){… return {…}}가 있으면 node로 같은 입력을 돌려 칸마다 맞댄다(차이 0.5 이하 = 같음).
     node가 없으면 「확인 못 함(node 없음)」.
  4) 수치대장.csv(칸: 숫자,단위,원문URL,조항또는쪽,기준일)의 숫자가 원문 페이지에 그대로 있는지 본다.
     원문을 열어 글자로 찾는다(쉼표 있음·없음, 만·억·천만 표기, % 둘 다 시험). 못 열거나 PDF·JS 화면이면 「확인 못 함(이유)」.
산출: 대조.txt — 다른 숫자 목록 · 계산기 불일치 · 원문에 없는 숫자 · 확인 못 함 목록과 판정 한 줄.
종료코드: 0 = 다른 숫자 0 · 계산기 불일치 0 · 원문에 없음 0 · 1 = 하나라도 있음(「확인 못 함」은 실패로 세지 않고 심사관에게 넘긴다) · 2 = 사용 오류
"""
import argparse
import csv
import datetime as dt
import html as htmlmod
import json
import os
import re
import runpy
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True  # 도구/에 __pycache__를 남기지 않는다(커밋 대상 아님)
sys.path.insert(0, HERE)
from source_open import fetch, visible_text  # noqa: E402

KST = dt.timezone(dt.timedelta(hours=9))
MULT = {"억": 1e8, "천만": 1e7, "백만": 1e6, "만": 1e4, "천": 1e3}
IGNORE = [r"\d{4}\s*[.\-/]\s*\d{1,2}\s*[.\-/]\s*\d{1,2}\.?", r"\d{4}\s*년", r"\d{1,2}\s*월\s*\d{1,2}\s*일", r"\d{1,2}\s*월",
          r"\d{1,2}\s*일(?![\d,])", r"제\s*\d+\s*조(의\s*\d+)?", r"\d+\s*항", r"\d+\s*호", r"\d+\s*쪽", r"\d+\s*페이지",
          r"[’']\d{2}\.\d{1,2}\.\d{1,2}\.?", r"\d{1,2}:\d{2}"]
NUM = re.compile(r"(?<![\d.,])(\d{1,3}(?:,\d{3})+|\d+)(?:\.(\d+))?\s*(억|천만|백만|만|천)?\s*(\d{1,3}(?:,\d{3})+|\d+)?\s*(만)?\s*(원|%|명|세|개월|주|배|가구|건|회|년)?")


def numbers(text):
    """글 → [(값, 표시 정밀도, 원문 조각)]"""
    t = text
    for rx in IGNORE:
        t = re.sub(rx, " ", t)
    out = []
    for m in NUM.finditer(t):
        a, dec, mul, b, mul2, unit = m.groups()
        v = float(a.replace(",", "") + ("." + dec if dec else ""))
        prec = 10 ** -(len(dec)) if dec else 1.0
        if mul:
            v *= MULT[mul]
            prec *= MULT[mul]
            if mul == "억" and b and mul2 == "만":  # 「1억 2,000만」
                v += float(b.replace(",", "")) * 1e4
                prec = 1e4
        elif b:  # 붙은 다른 숫자 — 따로 센다
            pass
        raw = m.group(0).strip()
        if not unit and not mul and not dec and v < 10:
            continue
        out.append((v, prec, raw))
        if b and not mul:
            vb = float(b.replace(",", ""))
            if vb >= 10:
                out.append((vb, 1.0, b))
    return out


def tables_numbers(page):
    res = []
    for ti, tb in enumerate(re.findall(r"(?is)<table[^>]*>.*?</table>", page), 1):
        for ri, tr in enumerate(re.findall(r"(?is)<tr[^>]*>.*?</tr>", tb), 1):
            cells = re.findall(r"(?is)<t[dh][^>]*>(.*?)</t[dh]>", tr)
            for ci, c in enumerate(cells, 1):
                txt = htmlmod.unescape(re.sub(r"<[^>]+>", " ", c))
                for v, p, raw in numbers(txt):
                    res.append({"table": ti, "row": ri, "col": ci, "v": v, "prec": p, "raw": raw, "cell": re.sub(r"\s+", " ", txt).strip()[:40]})
    return res


def match(v, prec, pool):
    for c in pool:
        if abs(c - v) < max(prec, 0.5) or (c != 0 and abs(c - v) / abs(c) < 1e-9):
            return True
    return False


def run_calc(folder):
    p = os.path.join(folder, "calc.py")
    if not os.path.exists(p):
        return None, "calc.py 없음"
    r = subprocess.run([sys.executable, "calc.py"], cwd=folder, capture_output=True, text=True, timeout=60)
    return r, f"종료 {r.returncode}"


def js_check(folder, page):
    """calc.py TESTS·compute ↔ HTML calcCompute — [(입력, 칸, py, js)] 불일치, 상태 문자열"""
    p = os.path.join(folder, "calc.py")
    if not os.path.exists(p):
        return [], "확인 못 함(calc.py 없음)", 0
    m = re.search(r"(?s)<script[^>]*>(.*?function\s+calcCompute\s*\(.*?)</script>", page)
    if not m:
        return [], "해당 없음(HTML에 calcCompute 없음 — 계산기 쪽이 아니면 정상)", 0
    try:
        cwd = os.getcwd()
        os.chdir(folder)
        try:
            ns = runpy.run_path("calc.py", run_name="calc_check")
        finally:
            os.chdir(cwd)
    except Exception as e:  # noqa: BLE001
        return [], f"확인 못 함(calc.py 불러오기 실패: {type(e).__name__})", 0
    tests, comp = ns.get("TESTS"), ns.get("compute")
    if not tests or not callable(comp):
        return [], "확인 못 함(calc.py에 TESTS·compute 없음)", 0
    node = shutil.which("node")
    if not node:
        return [], "확인 못 함(node 없음)", len(tests)
    js = m.group(1) + "\nconst T=" + json.dumps(tests, ensure_ascii=False) + ";\nconsole.log(JSON.stringify(T.map(x=>calcCompute(x))));\n"
    r = subprocess.run([node, "-e", js], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        return [], f"확인 못 함(node 오류: {(r.stderr.strip().splitlines() or [''])[-1][:80]})", len(tests)
    jres = json.loads(r.stdout)
    bad = []
    for inp, jr in zip(tests, jres):
        pr = comp(**inp)
        for k, pv in pr.items():
            jv = (jr or {}).get(k)
            if isinstance(pv, (int, float)) and (not isinstance(jv, (int, float)) or abs(pv - jv) > 0.5):
                bad.append((inp, k, pv, jv))
    return bad, f"시험 입력 {len(tests)}개 · 불일치 {len(bad)}", len(tests)


def variants(num, unit):
    s = str(num).strip().replace(" ", "")
    out = {s}
    try:
        v = float(s.replace(",", ""))
    except ValueError:
        return out
    iv = int(v) if v == int(v) else None
    if iv is not None:
        out |= {f"{iv:,}", str(iv)}
        if iv >= 1e8 and iv % 10**8 == 0:
            out.add(f"{iv // 10**8}억")
        if iv >= 1e4 and iv % 10**4 == 0:
            out |= {f"{iv // 10**4:,}만", f"{iv // 10**4}만"}
        if iv >= 1e7 and iv % 10**7 == 0 and iv < 1e8:
            out.add(f"{iv // 10**7}천만")
        if iv >= 1e8 and iv % 10**7 == 0 and iv % 10**8:
            out.add(f"{iv / 1e8:g}억")  # 「2.4억」
        if iv >= 1e8 and iv % 10**4 == 0 and iv % 10**8:
            out.add(f"{iv // 10**8}억{(iv % 10**8) // 10**4:,}만")
            out.add(f"{iv // 10**8}억{(iv % 10**8) // 10**4}만")
    else:
        out |= {f"{v:,}", f"{v:g}"}
    return {x for x in out if x}


def ledger_check(folder, no_open):
    p = os.path.join(folder, "수치대장.csv")
    if not os.path.exists(p):
        return [], "수치대장.csv 없음"
    rows = list(csv.DictReader(open(p, encoding="utf-8-sig", newline="")))
    cache = {}
    res = []
    for i, r in enumerate(rows, 2):
        url = (r.get("원문URL") or "").strip()
        num, unit = (r.get("숫자") or "").strip(), (r.get("단위") or "").strip()
        if no_open:
            res.append((i, num, unit, url, "확인 못 함(--no-open)"))
            continue
        if not url.startswith("http"):
            res.append((i, num, unit, url, "확인 못 함(URL 없음)"))
            continue
        if url not in cache:
            f = fetch(url, timeout=30, retries=2)  # 정부 누리집 연결 끊김이 섞인다(10/3)
            if f["reason"]:
                cache[url] = (None, f"확인 못 함({f['reason']})")
            elif "pdf" in (f["ctype"] or "").lower():
                txt = None
                if shutil.which("pdftotext"):
                    tmp = os.path.join(folder, ".calc_check_tmp.pdf")
                    open(tmp, "wb").write(f["bytes"])
                    q = subprocess.run(["pdftotext", "-layout", tmp, "-"], capture_output=True, text=True)
                    os.unlink(tmp)
                    txt = q.stdout if q.returncode == 0 else None
                cache[url] = (txt, None) if txt else (None, "확인 못 함(PDF — pdftotext 없음, 사람 확인)")
            else:
                t = visible_text(f["text"])
                cache[url] = (t, None) if len(re.sub(r"\s", "", t)) >= 300 else (None, "확인 못 함(본문 짧음 — JS 화면)")
        txt, why = cache[url]
        if txt is None:
            res.append((i, num, unit, url, why))
            continue
        flat = re.sub(r"\s+", "", txt)
        hit = next((v for v in sorted(variants(num, unit), key=len, reverse=True) if v in flat), None)
        res.append((i, num, unit, url, f"있음(「{hit}」)" if hit else "원문에 없음"))
    return res, f"{len(rows)}줄"


def main(argv=None):
    ap = argparse.ArgumentParser(description="calc ↔ 표 ↔ 계산기 ↔ 원문 대조(0토큰)")
    ap.add_argument("folder")
    ap.add_argument("--html")
    ap.add_argument("--no-open", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--stdout", action="store_true")
    a = ap.parse_args(argv)
    folder = os.path.abspath(a.folder)
    if not os.path.isdir(folder):
        print(f"오류: 폴더 없음 {folder}", file=sys.stderr)
        return 2
    hp = a.html or os.path.join(folder, "발행.html")
    page = open(hp, encoding="utf-8").read() if os.path.exists(hp) else ""
    page = re.sub(r"(?s)<!--.*?-->", " ", page)  # 주석 안의 <script>·표 이야기는 세지 않는다
    now = dt.datetime.now(KST)
    L = [f"# 대조 {os.path.basename(folder)} — calc_check.py {now:%Y-%m-%d %H:%M} KST", ""]
    fails = 0

    r, st = run_calc(folder)
    pool = []
    if r is None:
        L.append(f"## 1. calc.py 재실행: {st}")
    else:
        pool = [v for v, _, _ in numbers(r.stdout)]
        L.append(f"## 1. calc.py 재실행: {st} · 출력 숫자 {len(pool)}개")
        if r.returncode != 0:
            fails += 1
            L.append("- 오류: " + ((r.stderr.strip().splitlines() or [""])[-1])[:200])

    L.append("")
    if not page:
        L.append(f"## 2. 표 숫자 대조: HTML 없음({hp})")
    else:
        tn = tables_numbers(page)
        miss = [x for x in tn if pool and not match(x["v"], x["prec"], pool)]
        n_tab = len(re.findall(r"(?i)<table[\s>]", page))
        L.append(f"## 2. 표 숫자 대조: 표 {n_tab}개 · 숫자 {len(tn)}개 · calc 출력에 없는 숫자 {len(miss) if pool else '확인 못 함(calc 출력 없음)'}개")
        for x in miss:
            L.append(f"- 표{x['table']} {x['row']}행 {x['col']}칸: 「{x['raw']}」 (칸: {x['cell']})")
        fails += len(miss)

    L.append("")
    bad, st = js_check(folder, page)[:2] if page else ([], "해당 없음(HTML 없음)")
    L.append(f"## 3. 계산기 대조(calc.py TESTS ↔ HTML calcCompute): {st}")
    for inp, k, pv, jv in bad:
        L.append(f"- 입력 {json.dumps(inp, ensure_ascii=False)} · 칸 {k}: calc.py {pv} / 계산기 {jv}")
    fails += len(bad)

    L.append("")
    res, st = ledger_check(folder, a.no_open)
    n_has = sum(1 for x in res if x[4].startswith("있음"))
    n_no = sum(1 for x in res if x[4] == "원문에 없음")
    n_unk = sum(1 for x in res if x[4].startswith("확인 못 함"))
    L.append(f"## 4. 수치대장 원문 대조: {st} · 있음 {n_has} · 원문에 없음 {n_no} · 확인 못 함 {n_unk}")
    for i, num, unit, url, v in res:
        if not v.startswith("있음"):
            L.append(f"- 줄{i}: {num} {unit} ← {url} — {v}")
    fails += n_no

    L += ["", f"판정: {'통과' if fails == 0 else '다른 숫자 있음'} (다른 숫자·불일치·원문에 없음 합 {fails} · 확인 못 함 {n_unk}은 심사관이 원문과 맞춘다)"]
    text = "\n".join(L) + "\n"
    if a.stdout:
        print(text)
    else:
        out = a.out or os.path.join(folder, "대조.txt")
        with open(out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"썼다: {out}")
        print(L[-1])
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
