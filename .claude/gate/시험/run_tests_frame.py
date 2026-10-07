#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gate_frame · overlap21 · gate_search 시험 세트(본사 원본). run_tests_frame.sh 가 부른다.

사용: python3 run_tests_frame.py [--repo <서치 레포 루트>] [--live <라이브 스냅숏 폴더>] [--md <결과 표 파일>]
  --repo 가 없으면: 이 파일이 <레포>/.claude/gate/시험/ 에 있으면 그 레포, 아니면 환경변수 SEARCH_REPO.
  --live 가 없으면: 환경변수 LIVE_DIR. 스냅숏이 없으면 라이브 대조 시험은 「건너뜀」으로 적는다(실패 아님).
  변형 HTML(번호형·면책·앵커 등)과 겹침 시험 파일은 임시 폴더에 만들고 지운다 — 라이브 글 조각은 저장소에 남기지 않는다.
  10/3 검증 반영: 반대 검증이 찾은 음성 사례(완전 중복·가짜 사건키·묶음 재사용·보장 문장·AI 문구·워드프레스 래퍼·
  「」 감싸기·제목 없는 변환기 출력 등)를 모두 넣고 기대값을 실패로 둔다. 옛 ①-4(문자열 포함 여부만 보던 동어반복)는 지웠다.
종료코드: 기대와 다른 시험이 하나라도 있으면 1.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

T = os.path.dirname(os.path.abspath(__file__))
G = os.path.dirname(T)
LIVE_IDS = [2, 5, 6, 7, 8, 10, 11, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 27, 28, 30]
LIVE22_TITLE = "추석 주식시장 휴장은 24일·25일 — 28일 월요일은 정상 개장합니다"
WONJANG_HEAD = "묶음,편,검색어,가제,최종제목,사건키,골격,작가,상태,작업폴더,대기파일,라이브URL,게시일,갱신\n"
sys.dont_write_bytecode = True
sys.path.insert(0, G)


def run(cmd, cwd=None):
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return p.returncode, p.stdout + p.stderr


class Book:
    def __init__(self):
        self.rows = []

    def add(self, no, name, expect, got_rc, out, must=None, must_not=None, note=""):
        ok = (got_rc == expect) if expect is not None else True
        miss = []
        for m in (must or []):
            if m not in out:
                ok = False
                miss.append(f"없음「{m}」")
        for m in (must_not or []) + ["Traceback"]:
            if m in out:
                ok = False
                miss.append(f"있음「{m}」")
        exp = f"종료 {expect}" if expect is not None else "기록"
        self.rows.append((no, name, exp, f"종료 {got_rc}" + (" · " + ", ".join(miss) if miss else "")
                          + (f" · {note}" if note else ""), "맞음" if ok else "틀림"))
        return ok

    def skip(self, no, name, why):
        self.rows.append((no, name, "-", why, "건너뜀"))


def find_repo(arg):
    if arg:
        return os.path.realpath(arg)
    cand = os.path.realpath(os.path.join(T, "..", "..", ".."))
    if os.path.exists(os.path.join(cand, "도구", "gate_search.py")):
        return cand
    env = os.environ.get("SEARCH_REPO")
    return os.path.realpath(env) if env else None


def last_line(out, prefix):
    lines = [ln for ln in out.strip().splitlines() if ln.startswith(prefix)]
    return lines[-1] if lines else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--live")
    ap.add_argument("--md")
    a = ap.parse_args()
    repo = find_repo(a.repo)
    live = a.live or os.environ.get("LIVE_DIR")
    if live and not os.path.exists(os.path.join(live, "30.html")):
        live = None
    gs = os.path.join(repo, "도구", "gate_search.py") if repo else None
    if gs and not os.path.exists(gs):
        gs = None
    conv = os.path.join(repo, "도구", "원고_HTML변환.py") if repo else None
    if conv and not os.path.exists(conv):
        conv = None
    gf, ov = os.path.join(G, "gate_frame.py"), os.path.join(G, "overlap21.py")
    sample = os.path.join(T, "견본_통과.html")
    base = open(sample, encoding="utf-8").read()
    tmp = tempfile.mkdtemp(prefix="gate_frame_test_")
    py = sys.executable
    bk = Book()
    live_files = [os.path.join(live, f"{n}.html") for n in LIVE_IDS] if live else []

    def mkrepo(name, wonjang=None):
        r = os.path.join(tmp, name)
        os.makedirs(os.path.join(r, "운영"), exist_ok=True)
        with open(os.path.join(r, "운영", "원장.csv"), "w", encoding="utf-8") as f:
            f.write(open(wonjang, encoding="utf-8").read() if wonjang else WONJANG_HEAD)
        return r

    empty = mkrepo("빈레포")

    def var(name, text, sub=None):
        d = os.path.join(tmp, sub) if sub else tmp
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, name)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        return p

    def rep(old, new, src=None):
        s = src if src is not None else base
        assert old in s, f"견본에 「{old[:30]}」 없음"
        return s.replace(old, new)

    allowed = "<p>이 글은 기준일의 공개 원문을 정리한 일반 정보이며, 개인의 사정에 따라 결과가 달라질 수 있습니다.</p>"

    def add_p(text):
        return rep(allowed, allowed + f"\n<p>{text}</p>")

    # ① 견본 — 세 게이트 모두 통과
    if gs:
        rc, out = run([py, gs, sample, "--keyword", "전월세 전환율"])
        bk.add("①-1", "견본 gate_search(--keyword 전월세 전환율)", 0, rc, out, must=["치명 0 · 경고 0"])
    else:
        bk.skip("①-1", "견본 gate_search", "서치 레포 없음(--repo)")
    rc, out = run([py, gf, sample, "--repo", empty])
    bk.add("①-2", "견본 gate_frame", 0, rc, out, must=["실패 0 · 경고 0"])
    if live_files:
        rc, out = run([py, ov, sample, "--against"] + live_files)
        bk.add("①-3", "견본 overlap21 대 라이브 22편", 0, rc, out, must=["겹침 0", "상대 22개 파일"])
    else:
        bk.skip("①-3", "견본 overlap21 대 라이브 22편", "스냅숏 없음(--live)")
    if gs:  # 옛 ①-4(문자열 포함 여부만 보던 동어반복)를 실제 실행으로 바꿈
        p = var("s_부정문.html", add_p("원금이 보장되지 않는 상품입니다. 수익을 보장하지 않습니다."))
        rc, out = run([py, gs, p])
        bk.add("①-4", "부정문 「원금이 보장되지 않는」「수익을 보장하지 않습니다」 — gate_search 실제 실행", 0, rc, out,
               must=["치명 0"], must_not=["금지어"])
    else:
        bk.skip("①-4", "부정문 gate_search", "서치 레포 없음(--repo)")

    # ② 라이브 22편 gate_frame — 번호형 17편 치명
    if live_files:
        import gate_frame as gfm
        fp = {r["id"]: r for r in gfm.load_fp(os.path.join(G, "지문_22.tsv"))}
        numbered = {f"/{n}" for n in LIVE_IDS if fp.get(f"/{n}", {}).get("ratio", 0) >= 0.5}
        caught, other_fail, crash = set(), [], []
        for n, p in zip(LIVE_IDS, live_files):
            rc, out = run([py, gf, p, "--repo", empty])
            if rc == 2 or "Traceback" in out:
                crash.append(f"/{n}")
            if "번호형 h2" in out:
                caught.add(f"/{n}")
            extra = [ln for ln in out.splitlines() if ln.startswith("실패") and "번호형 h2" not in ln]
            if extra:
                other_fail.append(f"/{n}: " + "; ".join(x.split(" ← ")[0][4:] for x in extra))
        ok = caught == numbered and len(caught) == 17 and not crash
        bk.rows.append(("②", "라이브 22편 gate_frame 번호형 치명", "17편(지문_22 번호형과 같은 글)",
                        f"{len(caught)}편: " + " ".join(sorted(caught, key=lambda x: int(x[1:])))
                        + (" · 그 밖의 실패 " + " | ".join(other_fail) if other_fail else " · 그 밖의 실패 없음")
                        + (" · 종료 2 " + " ".join(crash) if crash else ""), "맞음" if ok else "틀림"))
    else:
        bk.skip("②", "라이브 22편 gate_frame", "스냅숏 없음(--live)")

    # ③ overlap21 — 라이브 문단 25자를 넣으면 실패, 빼면 통과
    if live_files:
        import overlap21 as ovm
        frag = None
        raw13, _, _ = ovm.html_segments(open(os.path.join(live, "13.html"), encoding="utf-8").read())
        for _, chunk in raw13:
            m = re.search(r"[가-힣0-9][가-힣0-9 ]{23}[가-힣0-9]", chunk)
            if m and len(m.group(0)) == 25:
                frag = m.group(0)
                break
        if frag:
            bad = var("겹침_25자.html", rep("<h2>월세를 보증금으로 환산하면 얼마인가요</h2>",
                                            f"<p>{frag}</p>\n<h2>월세를 보증금으로 환산하면 얼마인가요</h2>"))
            rc, out = run([py, ov, bad, "--against"] + live_files)
            bk.add("③-1", "견본 + 라이브 /13 문단 25자", 1, rc, out, must=["13.html", "길이 25"])
            rc, out = run([py, ov, sample, "--against"] + live_files)
            bk.add("③-2", "같은 조각을 뺀 견본", 0, rc, out, must=["겹침 0"])
            rc, out = run([py, ov, bad, "--against"] + live_files + ["--warn"])
            bk.add("③-3", "--warn(우리 글 겹침 시범 경고)", 0, rc, out, must=["결과: 경고"])
        else:
            bk.skip("③", "overlap21 25자", "/13 에서 25자 조각을 못 찾음")
    else:
        bk.skip("③", "overlap21 25자", "스냅숏 없음(--live)")

    # ④ gate_search 라이브 /30
    if gs and live:
        rc, out = run([py, gs, os.path.join(live, "30.html")])
        bk.add("④", "gate_search 라이브 /30(h2 4·외부 링크 0)", 1, rc, out,
               must=["h2 4개", "원문 딥링크 0개", "번호형 h2 4/4"], note=last_line(out, "치명 "))
    else:
        bk.skip("④", "gate_search 라이브 /30", "서치 레포 또는 스냅숏 없음")

    # ⑤ gate_frame — 편성표·설계 견본(통과 1 · 실패 각 1) + 10/3 검증 음성 사례
    md_cases = [
        ("⑤-1", "frame_편성표_통과.md", 0, ["실패 0 · 경고 0"], []),
        ("⑤-2", "frame_편성표_쌍둥이.md", 1, ["쌍둥이 글"], []),
        ("⑤-3", "frame_편성표_같은골격.md(H-194: 기록만)", 0, ["묶음 B01 안 같은 골격"], []),
        ("⑤-4", "frame_편성표_번호중복.md", 1, ["번호만 다른 같은 제목"], []),
        ("⑤-5", "frame_편성표_서브도메인.md", 1, ["서브도메인 링크 https://tax.moneyproducer.co.kr/18"], []),
        ("⑤-6", "frame_편성표_하루골격.md(H-194: 기록만)", 0, ["참고, H-194"], []),
        ("⑤-7", "frame_편성표_골격이름.md(H-194: 기록만)", 0, ["4종 밖(참고, H-194)"], []),
        ("⑤-8", "frame_설계_번호h2.md", 0, ["번호형 h2 5/5"], []),
        ("⑤-17", "frame_편성표_완전중복.md(검증 f1: 검색어·가제 같음, 묶음·게시일만 다름)", 1, ["쌍둥이 글 — 같은 질문"], []),
        ("⑤-18", "frame_편성표_가짜사건키.md(검증 f2: 사건키.tsv 에 없는 키)", 1, ["쌍둥이 글 — 같은 질문"], []),
        ("⑤-19", "frame_편성표_사건키날짜없음.md(등록 키지만 날짜 토큰·정규식 안 맞음)", 1, ["쌍둥이 글 — 같은 질문"], []),
        ("⑤-20", "frame_편성표_같은묶음편.md(검증 f10: 한 파일 같은 묶음·편 두 줄)", 1,
         ["같은 묶음·편 두 줄", "이상한골격"], []),
        ("⑤-21", "frame_편성표_서브도메인무스킴.md(검증 f4: 스킴 없는 주소)", 1,
         ["서브도메인 링크 tax.moneyproducer.co.kr/18", "서브도메인 링크 tax.moneyproducer.co.kr/20"], []),
        ("⑤-22", "frame_편성표_게시일없음.md(검증 f5: 편성표인데 게시일 칸 없음)", 1, ["편성표인데 게시일 칸 없음"], []),
        ("⑤-23", "frame_편성표_원숫자h2.md(검증 f8: h2 칸 ①~⑤)", 0, ["번호형 h2 5/5"], []),
    ]
    for no, f, exp, must, must_not in md_cases:
        name = f.split("(")[0]
        rc, out = run([py, gf, os.path.join(T, name), "--repo", empty])
        bk.add(no, f, exp, rc, out, must=must, must_not=must_not)
    rc, out = run([py, gf, os.path.join(T, "frame_편성표_통과.md"), os.path.join(T, "frame_설계_합치기.md"), "--repo", empty])
    bk.add("⑤-24", "편성표 + 설계(같은 묶음·편 B01-1·2) — 한 글로 셈", 0, rc, out, must=["실패 0 · 경고 0"])
    rc, out = run([py, gf, os.path.join(T, "frame_편성표_통과.md"), os.path.join(T, "frame_설계_불일치.md"), "--repo", empty])
    bk.add("⑤-25", "편성표 + 설계(B01-1 검색어가 다름)", 1, rc, out, must=["편성표·설계 불일치"])
    # 게시일 칸 필수 — 실제 경로 작업/<D>/편성표.md 로 놓아도 막는다
    sched = os.path.join(tmp, "편성레포", "작업", "2026-10-05")
    os.makedirs(sched)
    shutil.copy(os.path.join(T, "frame_편성표_게시일없음.md"), os.path.join(sched, "편성표.md"))
    rc, out = run([py, gf, os.path.join(sched, "편성표.md"), "--repo", empty])
    bk.add("⑤-26", "작업/2026-10-05/편성표.md(게시일 칸 없음)", 1, rc, out, must=["편성표인데 게시일 칸 없음"])
    # 원장 대조
    r2 = mkrepo("원장레포", os.path.join(T, "frame_원장.csv"))
    rc, out = run([py, gf, os.path.join(T, "frame_편성표_원장쌍둥이.md"), "--repo", r2])
    bk.add("⑤-9", "원장 대조(자기 줄 통과·대기 쌍둥이 실패·취소 무시)", 1, rc, out,
           must=["원장 줄2", "실패 1 ·"], must_not=["원장 줄3", "원장 줄4"])
    r3 = mkrepo("라이브원장레포", os.path.join(T, "frame_원장_라이브.csv"))
    rc, out = run([py, gf, os.path.join(T, "frame_편성표_묶음재사용.md"), "--repo", r3])
    bk.add("⑤-27", "원장 라이브 줄과 묶음·편 같음 + 검색어 띄어쓰기만 다름(검증 f11)", 1, rc, out,
           must=["묶음·편이 같은데", "쌍둥이 글 — 같은 질문"])
    # 원장·레포 없이 돌리면 막는다(종료 2)
    lone = os.path.join(tmp, "가", "나", "gate")  # ../../ 에 도구/gate_search.py 가 없는 자리(본사 원본과 같은 처지)
    os.makedirs(lone)
    for f in ("gate_frame.py", "지문_22.tsv", "주제대장.tsv", "사건키.tsv", "동의어.tsv"):
        if os.path.exists(os.path.join(G, f)):
            shutil.copy(os.path.join(G, f), lone)
    rc, out = run([py, os.path.join(lone, "gate_frame.py"), sample])
    bk.add("⑤-28", "--repo 없이 실행 — 자동 인식 위치(../../)가 서치 레포 아님(본사 원본 처지)", 2, rc, out, must=["서치 레포 아님"])
    norepo = os.path.join(tmp, "원장없는레포")
    os.makedirs(os.path.join(norepo, "운영"))
    rc, out = run([py, gf, sample, "--repo", norepo])
    bk.add("⑤-29", "--repo 에 운영/원장.csv 없음", 2, rc, out, must=["원장 없음"])
    rc, out = run([py, gf, sample, "--repo", norepo, "--no-ledger"])
    bk.add("⑤-30", "같은 레포 + --no-ledger(명시할 때만 건너뜀)", 0, rc, out, must=["실패 0"])

    # ⑤ HTML 견본 변형
    import gate_frame as gfm2
    h27 = {r["id"]: r for r in gfm2.load_fp(os.path.join(G, "지문_22.tsv"))}["/27"]["h2"]
    body = "".join(f"<h2>{re.sub(r'10월 5일', '11월 3일', h)}</h2>\n<p>본문 {i}.</p>\n" for i, h in enumerate(h27, 1))
    num_h2 = lambda fmt: re.sub(r"<h2>", lambda m, c=iter(range(1, 20)): f"<h2>{fmt.format(next(c))}", base)  # noqa: E731
    circ = "①②③④⑤⑥⑦⑧⑨"
    html_cases = [
        ("⑤-10", "HTML 번호형 h2", var("f_번호형.html", num_h2("{}. ")), 0, ["번호형 h2 6/6"], []),
        ("⑤-11", "HTML h2 순서 = 라이브 /27(날짜만 바꿈, H-194: 경고)", var("f_h2복제.html", "<!-- 제목: 시험 -->\n" + body), 0,
         ["h2 순서가 라이브 글과 같음", "지문 /27"], []),
        ("⑤-12", "HTML 서브도메인 링크", var("f_서브도메인.html", rep('href="https://moneyproducer.co.kr/18"',
                                                               'href="https://blog.moneyproducer.co.kr/18"')),
         1, ["서브도메인 링크 https://blog.moneyproducer.co.kr/18"], []),
        ("⑤-13", "HTML 제목 = 라이브 /22 제목 + 「(2)」(제목 주석 있는 견본)", var("f_번호제목.html", rep(
            "<!-- 제목: 전월세 전환율 상한 2026, 5천만원 전환 시 월세 계산 -->",
            f"<!-- 제목: {LIVE22_TITLE} (2) -->")), 1, ["번호만 다른 같은 제목"], []),
        ("⑤-31", "HTML h2 「①」~「⑥」(검증 g8)", var("f_원숫자.html", re.sub(
            r"<h2>", lambda m, c=iter(circ): f"<h2>{next(c)} ", base)), 0, ["번호형 h2 6/6"], []),
        ("⑤-32", "HTML h2 전각 「１．」(검증 g9)", var("f_전각.html", num_h2("{}． ").replace("1．", "１．")), 0,
         ["번호형 h2 6/6"], []),
        ("⑤-33", "HTML h2 「1단계」(검증 g10)", var("f_단계.html", num_h2("{}단계 ")), 0, ["번호형 h2 6/6"], []),
        ("⑤-34", "HTML h2 소수로 시작(「3.3% …」 — 번호 아님)", var("f_소수.html", re.sub(
            r"<h2>", lambda m, c=iter(["3.3% ", "4.5% ", "2.5% ", "1.5배 ", "0.5%p ", "10.5% "]): f"<h2>{next(c)}", base)),
         0, ["번호 h2 0"], ["번호형 h2"]),
        ("⑤-35", "HTML 깨진 href(검증 k1) — traceback 없이 기록", var("f_깨진주소.html", rep(
            'href="https://moneyproducer.co.kr/18"', 'href="http://[bad-ipv6/18"')), 0, ["깨진 주소"], []),
    ]
    for no, name, p, exp, must, must_not in html_cases:
        rc, out = run([py, gf, p, "--repo", empty, "-v"])
        bk.add(no, name, exp, rc, out, must=must, must_not=must_not)
    # 표 없는 마크다운은 막는다(틀 검사를 할 수 없음)
    rc, out = run([py, gf, var("f_표없음.md", "# 설계\n\n- 검색어: 결혼 증여세\n- 골격: 계산형\n"), "--repo", empty])
    bk.add("⑤-14", "표 없는 설계 마크다운", 1, rc, out, must=["마크다운 표가 없음"])
    # 같은 글의 작업 사본과 대기 사본은 「h2 순서 같음」으로 보지 않는다
    r4 = mkrepo("사본레포")
    os.makedirs(os.path.join(r4, "작업", "2026-10-05_jeonwolse"))
    os.makedirs(os.path.join(r4, "발행", "대기"))
    shutil.copy(sample, os.path.join(r4, "작업", "2026-10-05_jeonwolse", "발행.html"))
    shutil.copy(sample, os.path.join(r4, "발행", "대기", "2026-10-05_jeonwolse.html"))
    rc, out = run([py, gf, os.path.join(r4, "작업", "2026-10-05_jeonwolse", "발행.html"), "--repo", r4])
    bk.add("⑤-15", "작업 사본 + 대기 사본(같은 글) — 자기 사본은 비교에서 뺌", 0, rc, out, must=["실패 0"])
    other = rep("<!-- 제목: 전월세 전환율 상한 2026, 5천만원 전환 시 월세 계산 -->", "<!-- 제목: 월세 상한 계산 2026, 보증금 1억 전환 예시 -->")
    with open(os.path.join(r4, "발행", "대기", "2026-10-06_other.html"), "w", encoding="utf-8") as f:
        f.write(other)
    rc, out = run([py, gf, os.path.join(r4, "작업", "2026-10-05_jeonwolse", "발행.html"), "--repo", r4])
    bk.add("⑤-16", "대기 폴더의 다른 글과 h2 순서 같음(H-194: 경고)", 0, rc, out, must=["h2 순서가 다른 글과 같음"])
    # 변환기 출력(새 변환기는 제목 주석을 남긴다 — 원고 제목이 /22 제목 (2)라 번호만 다른 같은 제목으로 걸려야 한다)
    if conv:
        rc0, chtml = run([py, conv, os.path.join(T, "원고_변환시험.md")])
        cpath = var("발행.html", chtml, sub="변환")
        rc, out = run([py, gf, cpath, "--repo", empty])
        bk.add("⑤-36", "변환기 출력 발행.html(제목 주석 유지 — /22 제목 (2))", 1, rc, out, must=["번호만 다른 같은 제목"])
        rc, out = run([py, gf, cpath, "--repo", empty, "--title", LIVE22_TITLE + " (2)"])
        bk.add("⑤-37", "변환기 출력 + --title 「/22 제목 (2)」", 1, rc, out, must=["번호만 다른 같은 제목"])
        r5 = mkrepo("변환레포")
        wdir = os.path.join(r5, "작업", "2026-10-05_chuseok")
        os.makedirs(wdir)
        shutil.copy(cpath, os.path.join(wdir, "발행.html"))
        with open(os.path.join(r5, "운영", "원장.csv"), "a", encoding="utf-8") as f:
            f.write(f"B20,1,추석 휴장,추석 휴장 2027,{LIVE22_TITLE} (2),-,날짜형,A,집필,작업/2026-10-05_chuseok,,,,2026-10-03\n")
        rc, out = run([py, gf, os.path.join(wdir, "발행.html"), "--repo", r5])
        bk.add("⑤-38", "변환기 출력 + 원장 작업폴더 줄의 최종제목", 1, rc, out, must=["번호만 다른 같은 제목"])
    else:
        bk.skip("⑤-36~38", "변환기 출력 gate_frame", "서치 레포 도구/원고_HTML변환.py 없음")
    # 지문 0.8 유사 5편(질문형 h2 6개, 표 위치 같음) — 첫 2주는 경고(정상 새 글을 막지 않음)
    r6 = mkrepo("지문레포")
    nouns = ["보증금", "기준금리", "가산이율", "전환율", "월세액", "계약일", "임대인", "갱신권", "확정일자", "전입신고",
             "중개보수", "관리비", "보험료", "공시가격", "취득세", "재산세", "등기비용", "주택수", "대출한도", "상환기간",
             "기초연금", "선정기준", "소득인정", "근로소득", "재산환산", "부채공제", "부부감액", "신청서류", "지급일자", "수급자격",
             "연금저축", "세액공제", "납입한도", "환급금액", "연말정산", "퇴직연금"]
    for i in range(6):
        ws = nouns[i * 6:(i + 1) * 6]
        h = "".join(f"<h2>{w} 확인은 언제 하나요</h2>\n<p>본문 {i}-{j}.</p>\n" + ("<table><tr><td>1</td></tr></table>\n" if 1 <= j <= 3 else "")
                    for j, w in enumerate(ws))
        d = os.path.join(r6, "작업", f"2026-10-0{4 + i // 3}_{i}")
        os.makedirs(d)
        with open(os.path.join(d, "발행.html"), "w", encoding="utf-8") as f:
            f.write(f"<!-- 제목: 시험 글 {ws[0]} {i} -->\n{h}")
    rc, out = run([py, gf, os.path.join(r6, "작업", "2026-10-05_5", "발행.html"), "--repo", r6])
    bk.add("⑤-39", "지문 0.8 이상 비슷한 글 5편(질문형 h2 6·표 위치 같음) — 경고만", 0, rc, out,
           must=["경고: 지문 0.8 이상 비슷한 글 5편"], must_not=["실패: 지문"])

    # ⑥ gate_search 변형(새 치명·경고와 고친 버그) + 10/3 검증 음성 사례
    if gs:
        first_p = base[base.index("<p>전월세 전환율 상한은"):base.index("</p>", base.index("<p>전월세 전환율 상한은")) + 4]
        nodigit = ("<p>전월세 전환율 상한은 기준금리에 법이 정한 가산 이율을 더한 값과 법이 정한 고정 비율 가운데 낮은 쪽입니다. "
                   "이 글은 그 상한을 계산하는 순서를 표로 나눠 보여 드리고, 계약 전에 확인할 것을 차례로 적습니다. "
                   "계산은 곱하기와 나누기뿐이라 표를 따라가면 됩니다.</p>\n"
                   "<p>조문은 2026년 10월 3일 법령 원문 기준입니다.</p>")
        check_p = "<p>확인에 쓴 원문은 법 조문 두 쪽과 기준금리 쪽 하나입니다. 조문은 2026년 10월 3일 열람본이고, 숫자는 모두 그 원문에서 다시 옮겼습니다. "
        rev_prev = rep('<div class="author-box">', '<div class="rev"><p>수정 이력</p><ul><li>2026-10-05 표 셋째 줄 숫자 정정</li></ul>'
                                                 '<p>최종 수정 2026-10-05</p></div>\n<div class="author-box">')
        rev_cur = rep('<div class="author-box">', '<div class="rev"><p>수정 이력</p><ul><li>2026-10-05 표 셋째 줄 숫자 정정</li>'
                                                '<li>2026-10-12 기준금리 줄 갱신</li></ul><p>최종 수정 2026-10-12</p></div>\n<div class="author-box">')
        prev_path = var("s_이전판.html", rev_prev)
        s_cases = [
            ("⑥-1", "허용 목록 밖 면책 문장", rep(allowed, "<p>투자 판단의 책임은 본인에게 있습니다.</p>"), 1, ["허용 목록 밖 면책"], [], []),
            ("⑥-2", "내부 직함 「전문가」", rep("공공 상담 창구에서", "세무 전문가와 공공 상담 창구에서"), 1, ["내부 직함"], [], []),
            ("⑥-3", "바이라인 앵커 없음(#저자 뺌)", rep("머니프로듀서를-소개합니다#저자", "머니프로듀서를-소개합니다"), 1, ["저자 앵커"], [], []),
            ("⑥-4", "FAQPage 구조화 데이터", base + '<script type="application/ld+json">{"@type":"FAQPage"}</script>\n', 1,
             ["FAQPage"], [], []),
            ("⑥-5", "번호형 h2", re.sub(r"<h2>", lambda m, c=iter(range(1, 20)): f"<h2>{next(c)}) ", base), 0, ["번호형 h2 6/6"], [], []),
            ("⑥-6", "첫 130자에 숫자 없음", rep(first_p, nodigit), 0, ["첫 130자"], [], []),
            ("⑥-7", "첫 3단락 기준일 없음", rep(first_p, first_p.replace(", 2026년 10월 3일 법령 원문 기준", "")), 1,
             ["기준일 문장 없음"], [], []),
            ("⑥-8", "공공 링크 0(외부 딥링크는 4개)",
             re.sub(r"https://www\.(law|easylaw)\.go\.kr[^\"]*|https://www\.bok\.or\.kr[^\"]*",
                    lambda m, c=iter(range(1, 9)): f"https://example.com/source/{next(c)}", base), 1, ["공공 원문 딥링크 0개"], [], []),
            ("⑥-9", "저자 박스 없음", re.sub(r'(?s)<div class="author-box">.*?</div>', "", base), 1, ["저자 박스 없음"], [], []),
            ("⑥-10", "「수익을 보장합니다」(긍정)", add_p("이 방법은 수익을 보장합니다."), 1, ["금지어"], [], []),
            ("⑥-11", "우리 글 링크가 소개 쪽뿐(옛 버그: 소개 링크를 내부 링크로 셈)",
             rep('<a href="https://moneyproducer.co.kr/20">', '<a href="https://moneyproducer.co.kr/pages/개인정보처리방침">'),
             0, ["우리 글 링크 1개"], [], []),
            ("⑥-12", "FAQ 소제목(경고만)", rep("<h2>계약 전에 무엇을 확인하면 되나요</h2>", "<h2>자주 묻는 질문</h2>"), 0,
             ["FAQ 소제목", "치명 0"], [], []),
            ("⑥-16", "「원금 보장, 손실 없는 구조」(검증 g1)", add_p("이 상품은 원금 보장, 손실 없는 구조입니다."), 1, ["금지어"], [], []),
            ("⑥-17", "「손실 없이 수익 보장되는」(검증 g2)", add_p("손실 없이 수익 보장되는 방법입니다."), 1, ["금지어"], [], []),
            ("⑥-18", "「수익을 보장합니다. 걱정할 필요 없습니다.」(검증 g3)",
             add_p("이 방법은 수익을 보장합니다. 걱정할 필요 없습니다."), 1, ["금지어"], [], []),
            ("⑥-19", "「연 5% 확정 수익」(검증 g7)", add_p("이 방법이면 연 5% 확정 수익을 얻습니다."), 1, ["금지어", "확정 수익"], [], []),
            ("⑥-20", "「AI의 도움」(검증 h1)", add_p("이 표는 AI의 도움을 받아 정리했습니다."), 1, ["금지어", "AI의 도움"], [], []),
            ("⑥-21", "「생성형 AI 도구로」(검증 h2)", add_p("계산은 생성형 AI 도구로 검산했습니다."), 1, ["금지어", "생성형 AI"], [], []),
            ("⑥-22", "「매수를 권유합니다」", add_p("이 종목 매수를 권유합니다."), 1, ["금지어"], [], []),
            ("⑥-23", "저자 박스를 지우고 본문 문단에 소개 링크만(검증 g11)",
             re.sub(r'(?s)<div class="author-box">.*?</div>', "", rep(
                 "<p>세 가지를 순서대로 보시면 됩니다.",
                 '<p>이 계산은 <a href="https://moneyproducer.co.kr/pages/머니프로듀서를-소개합니다#저자">머니프로듀서 소개</a>에 적은 방식대로 했습니다. 세 가지를 순서대로 보시면 됩니다.')),
             1, ["저자 박스 없음"], [], []),
            ("⑥-24", "허용 면책 문장을 표 바로 뒤에(검증 g4)",
             rep("</table>\n</div>\n<p>조문 원문은", "</table>\n</div>\n" + allowed + "\n<p>조문 원문은", rep(allowed, "")), 0,
             ["치명 0"], ["면책"], []),
            ("⑥-25", "허용 면책 문장을 <h3>참고</h3> 뒤에(검증 g5)", rep(allowed, "<h3>참고</h3>\n" + allowed), 0,
             ["치명 0"], ["면책"], []),
            ("⑥-26", "「아래 계산은 참고용 예시입니다」(검증 g6)", rep("<p>표를 읽는 법은 간단합니다.", "<p>아래 계산은 참고용 예시입니다. 표를 읽는 법은 간단합니다."),
             0, ["치명 0"], ["면책"], []),
            ("⑥-27", "기준일 문장을 지우고 「2026년 1월 1일부터 적용되는 선정기준액」만(검증 h3)",
             rep("<p>먼저 숫자 두 개만", "<p>2026년 1월 1일부터 적용되는 선정기준액도 함께 봅니다. 먼저 숫자 두 개만",
                 rep(first_p, first_p.replace(", 2026년 10월 3일 법령 원문 기준", ""))), 1, ["기준일 문장 없음"], [], []),
            ("⑥-28", "깨진 HTML(</h2> 3개 빠짐, 검증 g12)", base.replace("</h2>", "", 3), 1, ["구조 깨짐"], [], []),
            ("⑥-29", "h2 「①」(검증 g8)", re.sub(r"<h2>", lambda m, c=iter(circ): f"<h2>{next(c)} ", base), 0, ["번호형 h2 6/6"], [], []),
            ("⑥-30", "h2 전각 「１．」(검증 g9)", re.sub(r"<h2>", lambda m, c=iter("１２３４５６７"): f"<h2>{next(c)}． ", base), 0,
             ["번호형 h2 6/6"], [], []),
            ("⑥-31", "h2 「1단계」(검증 g10)", re.sub(r"<h2>", lambda m, c=iter(range(1, 20)): f"<h2>{next(c)}단계 ", base), 0,
             ["번호형 h2 6/6"], [], []),
            ("⑥-32", "h2 소수로 시작 「3.3% …」 — 번호 아님",
             re.sub(r"<h2>", lambda m, c=iter(["3.3% ", "4.5% ", "2.5% ", "1.5배 ", "0.5%p ", "10.5% "]): f"<h2>{next(c)}", base), 0,
             ["치명 0"], ["번호형"], []),
            ("⑥-33", "깨진 href(검증 k1) — traceback 없음", rep('href="https://moneyproducer.co.kr/18"', 'href="http://[bad-ipv6/18"'), 1,
             ["깨진 링크 주소"], [], []),
            ("⑥-34", "「확인 과정」 단락 없음(경고만)", rep(check_p, "<p>"), 0, ["경고: 「확인 과정」 단락 없음", "치명 0"], [], []),
            ("⑥-35", "새 글에 「수정 이력」(H-212: 경고도 없음 — 변환기가 넣는다)", rev_prev, 0, ["치명 0"], [], []),
            ("⑥-36", "수정 HTML: 이력 +1 · 최종 수정 = 넘기는 날(E5 통과)", rev_cur, 0, ["치명 0"], ["E5"],
             ["--revision", prev_path, "--date", "2026-10-12"]),
            ("⑥-37", "수정 HTML: 이력이 늘지 않음(E5)", rev_prev, 1, ["E5 수정 이력 줄 1개"], [],
             ["--revision", prev_path, "--date", "2026-10-05"]),
            ("⑥-38", "수정 HTML: 최종 수정 날짜 ≠ 넘기는 날(E5)", rev_cur, 1, ["E5 최종 수정 2026-10-12 ≠ 넘기는 날 2026-10-13"], [],
             ["--revision", prev_path, "--date", "2026-10-13"]),
        ]
        for no, name, text, exp, must, must_not, extra in s_cases:
            p = var(f"s_{no}.html", text)
            rc, out = run([py, gs, p] + extra)
            bk.add(no, name, exp, rc, out, must=must, must_not=must_not)
        rc, out = run([py, gs, sample, "--keyword", "월세 계산"])
        bk.add("⑥-13", "--keyword 「월세 계산」(제목 뒤쪽, 경고만)", 0, rc, out, must=["앞 15자 밖"])
        p = var("s_예금자보호.html", add_p("예금자보호 한도 안에서는 원금이 보장됩니다."))
        rc, out = run([py, gs, p])
        bk.add("⑥-14", "「예금자보호 … 원금이 보장됩니다」(제도 설명)", 0, rc, out, must_not=["금지어"])
        p = var("s_보장성.html", add_p("보장성 보험료와 보장 내용은 따로 봅니다. 국민기초생활보장법 수급자도 같습니다."))
        rc, out = run([py, gs, p])
        bk.add("⑥-15", "「보장성 보험료·보장 내용·국민기초생활보장법」(제도·보험 용어)", 0, rc, out, must_not=["금지어"])
        if conv:
            rc, out = run([py, gs, cpath])
            bk.add("⑥-39", "변환기 출력 발행.html — 제목은 있고(주석 유지) 다른 치명으로 막힘", 1, rc, out, must=["치명"], must_not=["치명: 제목 없음"])
            rc, out = run([py, gs, cpath, "--title", LIVE22_TITLE])
            bk.add("⑥-40", "변환기 출력 + --title(제목 검사는 돎)", 1, rc, out, must=["제목 "], must_not=["치명: 제목 없음"])
    else:
        bk.skip("⑥", "gate_search 변형", "서치 레포 없음(--repo)")

    # ⑦ overlap21 — 제외 규칙 회귀(10/3 검증)
    wp = os.path.join(T, "bench_wp_page.html")
    rc, out = run([py, ov, os.path.join(T, "겹침_대상.md"), "--against", wp])
    bk.add("⑦-1", "워드프레스형 래퍼 상대(메뉴 /about/·「작성자 admin」·body class author) — 같은 문장 67자", 1, rc, out,
           must=["bench_wp_page.html", "결과: 실패"])
    wrapped = ('<div id="page"><nav><a href="https://moneyproducer.co.kr/pages/소개">소개</a></nav>\n'
               '<div class="post">\n' + base + '\n</div><footer>작성자 머니프로듀서 · <a href="/pages/소개">소개</a></footer></div>')
    tw = var("o_래퍼대상.html", wrapped)
    od = var("o_원본.html", base, sub="상대")
    rc, out = run([py, ov, tw, "--against", od])
    bk.add("⑦-2", "대상을 래퍼 div 로 감쌈(바이라인·소개 링크 포함) — 대상 글자가 지워지지 않음", 1, rc, out,
           must=["결과: 실패"], must_not=["대상 0문단"])
    copy30 = "한 달 월세에 12를 곱해 1년 치로 만든 뒤 전환율로 나누면"
    rc, out = run([py, ov, var("o_따옴표.html", f"<p>흔히 「{copy30}」 같은 설명을 봅니다.</p>"), "--against", od])
    bk.add("⑦-3", "남의 문장 30자를 「」로 감쌈(검증 o4)", 1, rc, out, must=["결과: 실패"])
    rc, out = run([py, ov, var("o_참고용.html", f"<p>참고용으로 적으면, {copy30} 그 월세가 보증금 얼마에 해당하는지 나옵니다.</p>"),
                   "--against", od])
    bk.add("⑦-4", "같은 문장 앞에 「참고용으로 적으면,」(검증 o5)", 1, rc, out, must=["결과: 실패"])
    rc, out = run([py, ov, var("o_안내상자.html", f"<section><p>안내 이 글은 표 세 개로 계산 순서를 보여 드립니다.</p>\n<p>거꾸로 계산할 수도 있습니다. {copy30} 그 월세가 보증금 얼마에 해당하는지 나옵니다.</p></section>"),
                   "--against", od])
    bk.add("⑦-5", "「안내」로 시작하는 section 래퍼(검증 o3)", 1, rc, out, must=["결과: 실패"])
    qd = os.path.join(tmp, "발행", "대기")
    os.makedirs(qd)
    shutil.copy(sample, os.path.join(qd, "2026-10-06_other.html"))
    tq = os.path.join(qd, "2026-10-07_target.html")
    with open(tq, "w", encoding="utf-8") as f:
        f.write(f"<p>거꾸로 계산할 수도 있습니다. {copy30} 그 월세가 보증금 얼마에 해당하는지 나옵니다.</p>")
    rc, out = run([py, ov, tq, "--against", qd])
    bk.add("⑦-6", "발행/대기 안 대상 — 같은 폴더의 다른 대기 글도 대조(검증 대기 맹점)", 1, rc, out,
           must=["2026-10-06_other.html", "결과: 실패"])
    wd = os.path.join(tmp, "작업", "2026-10-05_other")
    os.makedirs(wd)
    shutil.copy(sample, os.path.join(wd, "발행.html"))
    rc, out = run([py, ov, os.path.join(wd, "발행.html"), "--against", qd])
    bk.add("⑦-7", "작업/2026-10-05_other/발행.html 대 발행/대기/2026-10-06_other.html(같은 영문 = 같은 글 사본)", 1, rc, out,
           must=["같은 글 사본이라 뺌", "2026-10-07_target.html"])
    rc, out = run([py, ov, var("o_빈.html", ""), "--against", od])
    bk.add("⑦-8", "빈 대상(뽑은 글자 0)", 2, rc, out, must=["뽑기 실패"])
    rc, out = run([py, ov, os.path.join(T, "겹침_대상.md"), "--against", os.path.join(T, "겹침_출처만.md")])
    bk.add("⑦-9", "상대 본문 대부분이 제외 규칙에 지워짐(50% 미만)", 2, rc, out, must=["뽑기 실패", "50% 미만"])
    rc, out = run([py, ov, var("o_깨진주소.html", rep('href="https://moneyproducer.co.kr/18"', 'href="http://[bad-ipv6/18"')),
                   "--against", os.path.join(T, "겹침_대상.md")])
    bk.add("⑦-10", "깨진 href 대상(검증 k1) — traceback 없음", 0, rc, out, must=["결과: 통과"])
    emptydir = os.path.join(tmp, "빈폴더")
    os.makedirs(emptydir)
    rc, out = run([py, ov, sample, "--against", emptydir])
    bk.add("⑦-11", "상대 0개 파일 — 경고", 0, rc, out, must=["경고: 상대 0개 파일"])
    if live_files:
        pairs, crash = set(), []
        for n, p in zip(LIVE_IDS, live_files):
            others = [q for q in live_files if q != p]
            rc, out = run([py, ov, p, "--against"] + others)
            if rc == 2:
                crash.append(f"/{n}")
            for ln in out.splitlines():
                m = re.match(r"겹침: .*?(\d+)\.html .*← .*?(\d+)\.html", ln)
                if m:
                    pairs.add(tuple(sorted((int(m.group(1)), int(m.group(2))))))
        txt = " ".join(f"/{x}·/{y}" for x, y in sorted(pairs))
        bk.rows.append(("⑦-12", "라이브 22편 서로 맞대기(공통 머리말·푸터 오탐 점검)", "뽑기 실패 0 · 겹친 쌍 기록",
                        f"뽑기 실패 {len(crash)} · 겹친 쌍 {len(pairs)}: {txt}", "맞음" if not crash else "틀림"))
    else:
        bk.skip("⑦-12", "라이브 22편 서로 맞대기", "스냅숏 없음(--live)")

    shutil.rmtree(tmp, ignore_errors=True)
    order = lambda r: (r[0][0], [int(x) if x.isdigit() else 0 for x in re.findall(r"\d+", r[0][1:])])  # noqa: E731
    rows = sorted(bk.rows, key=order)
    lines = ["| 번호 | 시험 | 기대 | 결과 | 판정 |", "|---|---|---|---|---|"]
    for r in rows:
        lines.append("| " + " | ".join(str(x).replace("|", "/") for x in r) + " |")
    bad = [r for r in rows if r[4] == "틀림"]
    lines.append("")
    lines.append(f"맞음 {sum(1 for r in rows if r[4] == '맞음')} · 틀림 {len(bad)} · 건너뜀 "
                 f"{sum(1 for r in rows if r[4] == '건너뜀')}  (레포 {repo or '없음'} · 스냅숏 {live or '없음'})")
    text = "\n".join(lines)
    print(text)
    if a.md:
        with open(a.md, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
