#!/usr/bin/env python3
"""gate_topic 시험 세트(집행 완료 조건). run_tests_topic.sh가 부른다.
사용: python3 topic_test.py [--repo <실제 서치 레포>]   (repo를 주면 실제 레포로 한 번 더 돌린다 — 기록만)
기대와 다르면 종료코드 1. 임시 폴더(/tmp/gate_topic_*)는 끝나면 지운다."""
import argparse
import json
import os
import subprocess
import sys
import tempfile

T = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(os.path.dirname(T), "gate_topic.py")
rows = []      # (시험, 기대, 결과, 맞음)


def run(path, repo, *extra, stdin=None):
    cmd = [sys.executable, GATE, path, "--repo", repo, "--json"] + list(extra)
    p = subprocess.run(cmd, capture_output=True, text=True, input=stdin)
    if p.returncode not in (0, 1):
        raise SystemExit(f"게이트 오류({p.returncode}): {' '.join(cmd)}\n{p.stderr}")
    d = json.loads(p.stdout)
    return d["results"], p.returncode, p.stderr


def run_rc(path, repo, *extra, stdin=None, gate=None):
    """종료코드·표준출력·표준오류만 본다(종료 2 시험용). repo=None이면 --repo를 주지 않는다."""
    cmd = [sys.executable, gate or GATE, path] + (["--repo", repo] if repo else []) + list(extra)
    p = subprocess.run(cmd, capture_output=True, text=True, input=stdin)
    return p.returncode, p.stdout, p.stderr


def hits(r):
    return {h for h, _ in r["reasons"]}


def add(name, expect, got, ok):
    rows.append((name, expect, got, ok))


def plain_expect(path):
    """셋째 칸 기대(통과|실패)·넷째·다섯째 칸을 읽는다."""
    out = []
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            if not line.strip() or line.startswith("#"):
                continue
            c = line.rstrip("\n").split("\t")
            out.append((n, c[0], c[2] if len(c) > 2 else "", c[3] if len(c) > 3 else "", c[4] if len(c) > 4 else ""))
    return out


def git(repo, *a):
    subprocess.run(["git", "-C", repo] + list(a), check=True, capture_output=True,
                   env=dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                            GIT_COMMITTER_EMAIL="t@t"))


def write(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


LEDGER_HEAD = "묶음,편,검색어,가제,최종제목,사건키,골격,작가,상태,작업폴더,대기파일,라이브URL,게시일,갱신\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", help="실제 서치 레포(있으면 한 번 더 돌려 기록)")
    a = ap.parse_args()
    tmp = tempfile.mkdtemp(prefix="gate_topic_")
    empty = os.path.join(tmp, "empty")
    os.makedirs(os.path.join(empty, "운영"))

    # ① 반려 15
    res, _, _ = run(os.path.join(T, "topic_neg15.txt"), empty)
    nf = sum(r["verdict"] == "실패" for r in res)
    add("① 반려 15 제목", "15/15 실패", f"{nf}/{len(res)} 실패", nf == 15 and len(res) == 15)

    # ② 라이브 22
    res, _, _ = run(os.path.join(T, "topic_live22.txt"), empty)
    nf = sum(r["verdict"] == "실패" for r in res)
    add("② 라이브 22 제목(전체)", "22/22 실패", f"{nf}/{len(res)} 실패", nf == 22 and len(res) == 22)
    res, _, _ = run(os.path.join(T, "topic_live22.txt"), empty, "--mode", "title")
    nf = sum(r["verdict"] == "실패" for r in res)
    add("② 라이브 22 제목(--mode title)", "22/22 실패", f"{nf}/{len(res)} 실패", nf == 22)
    res, _, _ = run(os.path.join(T, "topic_old22.txt"), empty)
    nf = sum(r["verdict"] == "실패" for r in res)
    add("② 옛 제목 22(9/20 목록, 비공개 3 포함)", "22/22 실패", f"{nf}/{len(res)} 실패", nf == 22 and len(res) == 22)

    # ③ 달력 20 — 사건키 있음 / 「-」
    want_fail = {"2026 대주주 양도세 기준 12월 마지막 거래일", "연말 증시 폐장일과 12월 31일 휴장",
                 "10월 9일 한글날 증시 휴장", "연금계좌 12월 31일 납입 마감과 세액공제"}
    for f, label in (("topic_cal20.txt", "③ 달력 20(사건키 있음)"), ("topic_cal20_dash.txt", "③ 달력 20(사건키 「-」)")):
        res, _, _ = run(os.path.join(T, f), empty)
        failed = {r["text"] for r in res if r["verdict"] == "실패"}
        npass = sum(r["verdict"] == "통과" for r in res)
        nsched = sum(r["tag"] == "일정형 예외" for r in res)
        add(label, "16 통과 · 4 실패(한글날·연말 휴장 /27, 연금계좌 /18, 대주주 /28)",
            f"{npass} 통과(일정형 예외 {nsched}) · {len(failed)} 실패" + ("" if failed == want_fail else f" 다름: {sorted(failed ^ want_fail)}"),
            failed == want_fail and npass == 16)

    # ④ 분야 예시 낱말
    exp = plain_expect(os.path.join(T, "topic_field.txt"))
    res, _, _ = run(os.path.join(T, "topic_field.txt"), empty)
    by = {}
    bad = []
    for (n, text, e, area, _), r in zip(exp, res):
        by.setdefault(area, [0, 0])
        by[area][1] += 1
        by[area][0] += r["verdict"] == "통과"
        if r["verdict"] != e:
            bad.append(text)
    got = " · ".join(f"{k} {v[0]}/{v[1]} 통과" for k, v in by.items())
    add("④ 분야 예시 낱말(v2 부록 C)", "① 6/10 · ② 4/8 · ③ 2/3 통과", got + (f" 다름: {bad}" if bad else ""), not bad)

    # ⑤ 시연(통과) + 3-3 거름 예(실패)
    exp = plain_expect(os.path.join(T, "topic_demo.txt"))
    for mode in ("topic", "title"):
        res, _, _ = run(os.path.join(T, "topic_demo.txt"), empty, "--mode", mode)
        bad = [f"{x[1]}(기대 {x[2]})" for x, r in zip(exp, res) if r["verdict"] != x[2]]
        npass = sum(1 for x, r in zip(exp, res) if x[2] == "통과" and r["verdict"] == "통과")
        nwant = sum(1 for x in exp if x[2] == "통과")
        nrej = sum(1 for x, r in zip(exp, res) if x[2] == "실패" and r["verdict"] == "실패")
        nrw = sum(1 for x in exp if x[2] == "실패")
        add(f"⑤ 시연 3 + v3.1 첫날 2(--mode {mode})", f"통과 {nwant}/{nwant} · 3-3 거름 예 {nrw}/{nrw} 실패",
            f"통과 {npass}/{nwant} · 거름 {nrej}/{nrw}" + (f" 다름: {bad}" if bad else ""), not bad)

    # ⑥ 짧은 영문 경계·B7 오탐
    exp = plain_expect(os.path.join(T, "topic_boundary.txt"))
    res, _, _ = run(os.path.join(T, "topic_boundary.txt"), empty)
    bad = []
    for (n, text, e, must, mustnot), r in zip(exp, res):
        h = hits(r)
        ok = r["verdict"] == e
        for w in [x for x in must.split(",") if x and x != "-"]:
            ok &= w in h
        for w in [x for x in mustnot.split(",") if x and x != "-"]:
            ok &= w not in h
        if not ok:
            bad.append(f"{text} → {r['verdict']} {sorted(h)}")
    add("⑥ 짧은 영문 경계·B7 오탐", f"{len(exp)}/{len(exp)} 기대대로(VIG·ISAAC·VISA·DIVI·SPYD 통과, 국내 ETF·LTV·DC형 통과)",
        f"{len(exp) - len(bad)}/{len(exp)}" + (f" 다름: {bad}" if bad else ""), not bad)

    # ⑥' 공격형(반대 검증 10/3 치명): 낸 키·넓은 날짜로 일정형 예외를 여는 시도
    exp = plain_expect(os.path.join(T, "topic_attack.txt"))
    res, _, _ = run(os.path.join(T, "topic_attack.txt"), empty)
    bad = []
    for (n, text, e, must, mustnot), r in zip(exp, res):
        h = hits(r)
        ok = r["verdict"] == e
        for w in [x for x in must.split(",") if x and x != "-"]:
            ok &= w in h
        for w in [x for x in mustnot.split(",") if x and x != "-"]:
            ok &= w not in h
        if e == "통과":
            ok &= r["tag"] == "일정형 예외"
        if not ok:
            bad.append(f"{text} → {r['verdict']}({r['tag']}) {sorted(h)}")
    nf = sum(1 for x in exp if x[2] == "실패")
    add("⑥' 공격형: 낸 키(new·미등록·안 맞는 키)·넓은 날짜(3일·2000만원·2030세대·연말정산·손익분기)·다른 사건 꼬리 붙이기",
        f"{nf}/{nf} 실패 · 진짜 일정형 {len(exp) - nf}/{len(exp) - nf} 통과(일정형 예외)",
        f"{len(exp) - len(bad)}/{len(exp)} 기대대로" + (f" 다름: {bad}" if bad else ""), not bad and len(res) == len(exp))

    # ⑦ 서치 레포 쪽: 진행분·자기 빼기·반려_추가·삭제 흔적·회장 1회 예외·표 입력
    fx = os.path.join(tmp, "fx1")
    write(os.path.join(fx, "운영", "원장.csv"), LEDGER_HEAD +
          "B001,1,결혼 증여세 면제 한도,결혼 증여세 면제 한도 2026: 양가 합쳐 3억까지 되는 조건,,-,계산형,A,승인,,,,,\n"
          "B002,1,11월 공모주 청약 일정,11월 공모주 청약 일정 2026,,공모주청약일정,날짜형,B,후보,,,,,\n"
          "B003,1,청년미래적금 중도해지,청년미래적금 중도해지 하면 이자는,,-,조건형,B,취소,,,,,\n"
          "B004,1,IRP 수수료,IRP 수수료 비교 2026,,-,비교형,A,집필,,,,,\n"
          "B005,1,종부세 고지,종부세 고지서 2026 언제 오나,,종부세2026,날짜형,B,대기,,,,,\n"
          "B008,1,FOMC 금리 결정 10월 2026,FOMC 금리 결정 2026년 10월 한국 시간,,FOMC10월,날짜형,B,집필,,,,,\n"
          "기존,/11,VI 발동,VI가 떴다고 파는 게 맞을까요,VI가 떴다고 파는 게 맞을까요,-,-,기존,라이브,,,https://moneyproducer.co.kr/11,2026-09-05,2026-10-03\n")
    write(os.path.join(fx, "운영", "반려_추가.txt"), "# 회장이 서치에 직접 반려한 것(서치는 더하기만)\n청년도약계좌\t회장 10/4 09:10 「그건 쓰지 마」\n")
    write(os.path.join(fx, "운영", "회장지시_원문.md"),
          "# 회장지시 원문\n\n## 4. 직접 받은 말\n| 날짜 시각 | 원문 | 한 일 |\n|---|---|---|\n"
          "| 10/4 09:00 | 「연금저축 이전 방법 써」 | 1회 예외: 연금저축 계좌 이전 방법 |\n"
          "| 10/4 09:05 | 「IRP 수수료도」 | 1회 예외: IRP 수수료 비교 |\n"
          "| 10/4 09:20 | 「VI 원리 써」 | 1회 예외: VI 발동 원리 |\n")
    git(fx, "init", "-q")
    git(fx, "add", "-A")
    git(fx, "commit", "-qm", "fixture")

    cases = [
        ("결혼 증여세 면제 한도 계산", [], "실패", "진행분 검색어(원장 줄2 승인)"),
        ("결혼 증여세 면제 한도 계산", ["--exclude-self", "2"], "통과", "--exclude-self 2로 자기 줄 빼기"),
        ("11월 공모주 청약 일정 2026", [], "통과", "원장 「후보」 줄은 진행분이 아니다"),
        ("청년미래적금 중도해지", [], "통과", "원장 「취소」 줄은 진행분이 아니다"),
        ("종부세 고지서 11월 납부", [], "실패", "진행분 검색어(원장 줄6 대기)"),
        ("부가세 예정신고 10월\t종부세2026", [], "실패", "진행분 사건키(원장 줄6)"),
        ("연준 FOMC 10월 회의 한국 시간", [], "실패", "같은 달 되풀이 사건은 진행분 사건키로 실패(FOMC10월, 원장 줄7)"),
        ("12월 FOMC 일정 2026", [], "통과", "되풀이 사건은 달이 다르면 다른 키(FOMC12월)"),
        ("청년도약계좌 만기 수령", [], "실패", "반려_추가 줄2"),
        ("연금저축 계좌 이전 방법", [], "통과", "회장 1회 예외(원문 6줄) — 주제대장 /18을 넘음"),
        ("연금저축 계좌 이전 방법 2026", [], "실패", "회장 예외는 문구가 정확히 같을 때만"),
        ("IRP 수수료 비교", [], "실패", "회장 예외도 이번 개편 뒤 진행분(원장 줄5 집필)은 못 넘음"),
        ("VI 발동 원리", [], "통과", "회장 1회 예외(원문 8줄) — 주제대장 /11과 원장 「기존」 줄(/11 라이브)을 넘음"),
        ("VI 발동 원리 10월 FOMC 2026", [], "실패", "일정형 예외로는 원장 「기존」 줄(VI 발동)을 못 넘음"),
    ]
    for text, extra, e, why in cases:
        res, _, _ = run("-", fx, *extra, stdin=text + "\n")
        r = res[0]
        ok = r["verdict"] == e
        if why.startswith("회장 1회 예외(원문 6줄)"):
            ok &= r["tag"] == "회장 예외 원문 6줄"
        if why.startswith("회장 1회 예외(원문 8줄)"):
            ok &= r["tag"] == "회장 예외 원문 8줄"
        add(f"⑦ {why}", e, f"{r['verdict']}{'(' + r['tag'] + ')' if r['tag'] else ''}", ok)

    # 표 입력: .md(각도 칸은 읽지 않음, 묶음·편 같은 원장 줄은 자기 줄로 뺌) · .csv · --mode title
    md = os.path.join(tmp, "편성표.md")
    write(md, "# 편성표\n\n| 묶음 | 편 | 검색어 | 가제 | 각도 | 차별점 | 사건키 |\n|---|---|---|---|---|---|---|\n"
              "| B001 | 1 | 결혼 증여세 면제 한도 | 결혼 증여세 면제 한도 2026: 양가 합쳐 3억까지 되는 조건 | TQQQ와 다른 각도 | QQQ 없이 | - |\n"
              "| B006 | 1 | 순자산 상위 10% | 순자산 상위 10% 기준 2026 | 월배당과 비교 | - | - |\n"
              "| B007 | 1 | 한글날 증시 | 10월 9일 한글날 증시 휴장 | 다른 각도 | 새로움 | - |\n")
    res, rc, _ = run(md, fx)
    v = [r["verdict"] for r in res]
    add("⑦ .md 편성표(각도·차별점 칸 무시, 자기 줄 자동 빼기)", "통과·통과·실패(한글날 /27)", "·".join(v) + f" (종료 {rc})",
        v == ["통과", "통과", "실패"] and rc == 1)
    csvp = os.path.join(tmp, "질문은행.csv")
    write(csvp, "날짜,질문,구글자동완성,네이버자동완성,합의블로그,합의수,원천URL,사건키,사건일,원문URL,열림,gate_topic\n"
                "2026-10-04,결혼 증여세 면제 한도,10,10,a·b,2,-,-,-,-,예,\n"
                "2026-10-04,추석 증시 휴장 2027,10,9,a,1,-,추석휴장,2027-09-15,-,예,\n")
    res, _, _ = run(csvp, empty)
    v = [r["verdict"] for r in res]
    add("⑦ .csv 질문은행 입력", "통과·실패(추석 /22)", "·".join(v), v == ["통과", "실패"])
    res, _, _ = run(md, fx, "--mode", "title")
    v = [r["verdict"] for r in res]
    add("⑦ .md --mode title(가제 칸만, 최종제목 없을 때)", "통과·통과·실패", "·".join(v), v == ["통과", "통과", "실패"])

    # 회장 예외는 정확히 같은 칸 하나만 — 같은 행의 다른 칸은 평소대로
    md2 = os.path.join(tmp, "편성표_예외.md")
    write(md2, "| 묶음 | 편 | 검색어 | 가제 | 사건키 |\n|---|---|---|---|---|\n"
               "| B010 | 1 | 연금저축 계좌 이전 방법 | TQQQ 월배당 달러 투자 SCHD 비교 | - |\n")
    res, rc, _ = run(md2, fx)
    r = res[0]
    add("⑦ 회장 예외는 같은 칸만 — 같은 행 가제의 반려 낱말(TQQQ·월배당·SCHD)은 실패",
        "실패(종료 1)", f"{r['verdict']}({r['tag']}) 종료 {rc}", r["verdict"] == "실패" and rc == 1
        and any(h in ("TQQQ", "SCHD", "월배당") for h in hits(r)))
    rc, out, _ = run_rc("-", fx, stdin="연금저축 계좌 이전 방법\n연금저축 계좌 이전 방법\n")
    v = [ln.split(":")[0] for ln in out.splitlines() if not ln.startswith("#")]
    summ = [ln for ln in out.splitlines() if ln.startswith("# 합계")]
    add("⑦ 회장 예외 줄 하나는 한 실행에서 후보 하나만(같은 문구 두 줄)", "통과(회장 예외 원문 6줄)·실패(…이미 입력 줄1에 썼다)",
        " · ".join(v) + f" 종료 {rc}", v == ["통과(회장 예외 원문 6줄)", "실패(회장 예외 원문 6줄은 이 실행에서 이미 입력 줄1에 썼다(1회))"] and rc == 1)
    add("⑦ 요약의 회장 예외 수는 통과한 것만 센다", "회장 예외 1", summ[0] if summ else "-",
        bool(summ) and "회장 예외 1)" in summ[0])
    rc, out, _ = run_rc("-", fx, stdin="IRP 수수료 비교\n")
    summ = [ln for ln in out.splitlines() if ln.startswith("# 합계")]
    add("⑦ 실패한 예외 시도는 회장 예외 수에 넣지 않는다", "통과 0(… 회장 예외 0)", summ[0] if summ else "-",
        bool(summ) and "통과 0(일정형 예외 0 · 회장 예외 0)" in summ[0])

    # 입력이 비거나 일부만 읽히면 종료 2(fail-closed)
    def rc2(label, path, *extra, stdin=None, repo=empty, want=2, gate=None):
        rc, out, err = run_rc(path, repo, *extra, stdin=stdin, gate=gate)
        add(f"⑧ {label}", f"종료 {want}", f"종료 {rc} · {(err.strip().splitlines() or ['-'])[-1][:90]}", rc == want)
    p0 = os.path.join(tmp, "빈.txt"); write(p0, "")
    p1 = os.path.join(tmp, "주석만.txt"); write(p1, "# 후보 없음\n\n")
    p2 = os.path.join(tmp, "머리만.csv"); write(p2, "날짜,질문,구글자동완성,네이버자동완성,합의블로그,합의수,원천URL,사건키,사건일,원문URL,열림,gate_topic\n")
    p3 = os.path.join(tmp, "빈문구.txt"); write(p3, "\tFOMC10월\n")
    p4 = os.path.join(tmp, "질문은행.csv"); write(p4, "날짜,질문,사건키\n2026-10-04,TQQQ 적립식,-\n")
    p5 = os.path.join(tmp, "예비표.md"); write(p5, "| 질문(구글 원문) | 가제(안) |\n|---|---|\n| TQQQ vs QQQ 적립식 | TQQQ 적립식 10년 |\n")
    p6 = os.path.join(tmp, "모르는머리.md"); write(p6, "| 질문 후보 | 메모 |\n|---|---|\n| TQQQ 적립식 | - |\n")
    p7 = os.path.join(tmp, "빈칸행.md"); write(p7, "| 묶음 | 편 | 검색어 | 가제 |\n|---|---|---|---|\n| B1 | 1 |  |  |\n")
    rc2("빈 파일 → 후보 없음", p0)
    rc2("# 줄만 있는 파일 → 후보 없음", p1)
    rc2("머리만 있는 CSV → 후보 없음", p2)
    rc2("문구가 빈 줄(「<TAB>FOMC10월」)", p3)
    rc2("질문은행.csv를 --mode title로(읽을 제목 칸 없음)", p4, "--mode", "title")
    rc2("「질문(구글 원문)·가제(안)」 머리는 괄호를 떼고 읽는다 → TQQQ 실패", p5, want=1)
    rc2("정해진 이름이 아닌 머리(「질문 후보」) → 이름을 알리고 멈춤", p6)
    rc2("문구 칸이 빈 표 행(묶음·편만 있음)", p7)

    # 데이터가 깨지면 종료 2(fail-closed) — 사본 폴더에서 시험
    import shutil
    def broken(label, fname, line, mode="a"):
        d = os.path.join(tmp, "data_" + str(len(rows)))
        shutil.copytree(os.path.dirname(GATE), d, ignore=shutil.ignore_patterns("시험", "__pycache__"))
        with open(os.path.join(d, fname), mode, encoding="utf-8") as f:
            f.write(line)
        rc2(label, os.path.join(T, "topic_demo.txt"), gate=os.path.join(d, "gate_topic.py"))
    broken("사건키.tsv 칸이 모자란 줄(「새사건11월<TAB>11월 무엇」)", "사건키.tsv", "새사건11월\t11월 무엇\n")
    broken("사건키.tsv 정규식이 빈 문구에도 맞음(「.*」)", "사건키.tsv", "새사건11월\t11월 무엇\t.*\t-\n")
    broken("사건키.tsv 정규식 칸이 빔", "사건키.tsv", "새사건11월\t11월 무엇\t\t-\n")
    broken("주제대장.tsv 핵심어가 정규화하면 빔(「·」)", "주제대장.tsv", "/99\t시험\t·\t-\t라이브\n")
    broken("주제대장.tsv 다루는사건키가 사건키.tsv에 없음", "주제대장.tsv", "/99\t시험\t시험낱말\t없는키\t라이브\n")
    broken("반려대장.tsv 문구 칸이 빔", "반려대장.tsv", "W-99\t낱말\t\t시험\t없음\t시험\n")

    # --repo: 본사 원본에서는 꼭 준다. 사본(.claude/gate/)에서만 ../../ 기본값
    if os.path.basename(os.path.dirname(os.path.dirname(GATE))) == ".claude":   # 서치 사본에서 돌리면 「본사 원본」 시험은 뜻이 없다
        rc2("사본 위치(.claude/gate/)에서 --repo 없이 → ../../를 레포로(종료 1)", os.path.join(T, "topic_demo.txt"), repo=None, want=1)
    else:
        rc2("본사 원본에서 --repo 없이 → 종료 2", os.path.join(T, "topic_demo.txt"), repo=None)
    cp = os.path.join(tmp, "fakerepo")
    os.makedirs(os.path.join(cp, "운영"))
    shutil.copytree(os.path.dirname(GATE), os.path.join(cp, ".claude", "gate"), ignore=shutil.ignore_patterns("시험", "__pycache__"))
    rc2("서치 사본(.claude/gate/)에서 --repo 없이 → ../../를 레포로(시연 15줄 중 거름 4 실패 = 종료 1)",
        os.path.join(T, "topic_demo.txt"), repo=None, want=1, gate=os.path.join(cp, ".claude", "gate", "gate_topic.py"))
    cp2 = os.path.join(tmp, "norepo", ".claude", "gate")
    shutil.copytree(os.path.dirname(GATE), cp2, ignore=shutil.ignore_patterns("시험", "__pycache__"))
    rc2("사본 위치인데 ../../에 운영/이 없음 → 종료 2", os.path.join(T, "topic_demo.txt"), repo=None,
        gate=os.path.join(cp2, "gate_topic.py"))

    # 반려_추가 삭제 흔적(git)
    fx2 = os.path.join(tmp, "fx2")
    write(os.path.join(fx2, "운영", "반려_추가.txt"), "청년도약계좌\n")
    git(fx2, "init", "-q")
    git(fx2, "add", "-A")
    git(fx2, "commit", "-qm", "add")
    write(os.path.join(fx2, "운영", "반려_추가.txt"), "")
    git(fx2, "commit", "-qam", "remove")
    res, _, _ = run("-", fx2, stdin="결혼 증여세 면제 한도\n")
    r = res[0]
    add("⑦ 반려_추가 줄을 지운 커밋이 있으면 모든 후보 실패", "실패", r["verdict"] + " " + "; ".join(h for h, _ in r["reasons"]),
        r["verdict"] == "실패" and any("삭제 흔적" in h for h, _ in r["reasons"]))
    fx3 = os.path.join(tmp, "fx3")
    write(os.path.join(fx3, "운영", "반려_추가.txt"), "청년도약계좌\n")
    git(fx3, "init", "-q")
    git(fx3, "add", "-A")
    git(fx3, "commit", "-qm", "add")
    write(os.path.join(fx3, "운영", "반려_추가.txt"), "")   # 커밋 전 작업본에서만 지움
    res, _, _ = run("-", fx3, stdin="결혼 증여세 면제 한도\n")
    add("⑦ 반려_추가 줄을 작업본에서 지워도 실패", "실패", res[0]["verdict"], res[0]["verdict"] == "실패")

    # 실제 서치 레포(기록만)
    if a.repo and os.path.isdir(os.path.join(a.repo, "운영")):
        res, rc, err = run(os.path.join(T, "topic_demo.txt"), a.repo)
        npass = sum(r["verdict"] == "통과" for r in res)
        nt = sum(1 for r in res if any("삭제 흔적" in h for h, _ in r.get("reasons", [])))
        rows.append((f"(기록) 실제 서치 레포로 시연 파일", "-",
                     f"통과 {npass}/{len(res)} · 삭제 흔적으로 실패 {nt} · 주의 {len(err.splitlines())}줄", True))

    import shutil
    shutil.rmtree(tmp, ignore_errors=True)

    # 표
    print("| 시험 | 기대 | 결과 | 판정 |")
    print("|---|---|---|---|")
    for name, e, g, ok in rows:
        print(f"| {name} | {e} | {g} | {'맞음' if ok else '다름'} |")
    nbad = sum(1 for r in rows if not r[3])
    print(f"\n시험 {len(rows)}개 · 맞음 {len(rows) - nbad} · 다름 {nbad}")
    return 1 if nbad else 0


if __name__ == "__main__":
    sys.exit(main())
