#!/usr/bin/env python3
"""회차 자기 점검 (0토큰) — 회차 끝에 돌리면 빠뜨리기 쉬운 일을 한 번에 보여 준다 (H-244).
사용: python3 도구/회차_자기점검.py [--no-net]
점검: STOP · 미커밋·미푸시 · 사이트맵 새 번호 · 원장 대기 ↔ 발행/대기 파일 · 패키지(썸네일·붙여넣기) ·
      라이브가 된 묶음 편의 「같은 묶음」 자리표시 · 오늘 정찰 산출 · 본사보고 마지막 줄
종료 0 = 할 일 없음, 1 = 아래 「할 일」 줄을 처리."""
import csv, glob, json, os, re, subprocess, sys, datetime

ROOT = os.getcwd()
todo = []

def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()

def tick(ok, msg_ok, msg_todo):
    print(("  ok  " if ok else "할 일 ") + (msg_ok if ok else msg_todo))
    if not ok:
        todo.append(msg_todo)

kst = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
today = kst.strftime("%Y-%m-%d")
print(f"회차 자기 점검 {today} {kst.strftime('%H:%M')} KST")

tick(not os.path.exists("운영/STOP"), "STOP 없음", "운영/STOP이 있다 — 본사만 지운다, 회차기록에 STOP 한 줄")
dirty = sh("git status --short | wc -l")
tick(dirty == "0", "작업 트리 깨끗", f"커밋 안 된 변경 {dirty}건 — 커밋·푸시")
ahead = sh("git rev-list --count @{u}..HEAD 2>/dev/null") or "0"
tick(ahead == "0", "푸시 끝", f"푸시 안 된 커밋 {ahead}개")

rows = list(csv.DictReader(open("운영/원장.csv", encoding="utf-8")))
live_urls = {r["라이브URL"].rsplit("/", 1)[-1] for r in rows if r["라이브URL"]}
if "--no-net" not in sys.argv:
    try:
        xml = subprocess.run(
            ["curl", "-sS", "-m", "30", "-A", "Mozilla/5.0", "https://moneyproducer.co.kr/sitemap.xml"],
            capture_output=True, text=True).stdout
        site = set(re.findall(r"co\.kr/(\d+)</loc>", xml))
        new = sorted(site - live_urls, key=int)
        if not site:
            print("  --   사이트맵을 못 열었다(연결) — 다음 회차에 다시")
        else:
            tick(not new, f"사이트맵 {len(site)}개 모두 원장에 있음",
                 f"원장에 없는 새 번호 {new} — 제목을 확인해 상태 「라이브」·라이브URL·게시일을 적는다(§3-1)")
    except Exception as e:
        print("  --   사이트맵 확인 못 함:", e)

wait = {r["대기파일"] for r in rows if r["상태"] == "대기" and r["대기파일"]}
anyfile = {r["대기파일"] for r in rows if r["대기파일"]}  # 라이브가 된 글도 발행/대기에 남아 있다
files = set(glob.glob("발행/대기/*.html"))
miss_file = sorted(w for w in wait if w not in files)
extra = sorted(f for f in files if f not in anyfile and not any(f.endswith(os.path.basename(w)) for w in anyfile))
tick(not miss_file, f"원장 대기 {len(wait)}편 모두 파일 있음", f"원장 대기인데 파일 없음: {miss_file}")
tick(not extra, "발행/대기 파일 모두 원장에 있음", f"원장에 없는 대기 파일: {extra}")

nopkg = []
for f in sorted(files):
    slug = os.path.basename(f)[:-5]
    d = f"발행/패키지/{slug}"
    if not (os.path.exists(d + "/썸네일.png") and os.path.exists(d + "/붙여넣기_HTML.txt")):
        nopkg.append(slug)
tick(not nopkg, "대기 글 패키지(썸네일·붙여넣기) 모두 있음",
     f"패키지 없음: {nopkg} — python3 도구/패키지_만들기.py <슬러그> 후 썸네일 문구 추가")

key_live = {(r["묶음"] + "/" + r["편"]) for r in rows if r["상태"] == "라이브"}
live_files = {os.path.basename(r["대기파일"]) for r in rows if r["상태"] == "라이브" and r["대기파일"]}
stale = []
for f in sorted(files):
    if os.path.basename(f) in live_files:  # 이미 나간 글은 그대로 둔다(회장 지시)
        continue
    t = open(f, encoding="utf-8").read()
    for m in re.finditer(r"<!-- 같은 묶음: (\S+) ·", t):
        if m.group(1) in key_live:
            stale.append((os.path.basename(f), m.group(1)))
tick(not stale, "라이브가 된 묶음 편의 자리표시 없음", f"링크로 바꿀 자리표시: {stale}")

scout = glob.glob(f"작업/{today}/원천표*.md")
tick(bool(scout), "오늘 정찰 산출 있음", f"작업/{today}/원천표.md 없음 — scout.py 실행")

try:
    last = json.loads(open("운영/본사보고.jsonl", encoding="utf-8").read().strip().splitlines()[-1])
    print("  --   본사보고 마지막:", last.get("ts", "")[:16], last.get("kind"), last.get("text", "")[:50])
except Exception:
    print("  --   본사보고 마지막 줄을 읽지 못함")

print("\n" + ("할 일 없음" if not todo else f"할 일 {len(todo)}건"))
sys.exit(1 if todo else 0)
