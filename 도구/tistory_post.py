#!/usr/bin/env python3
"""티스토리 예약 게시(자동 브라우저). 회장 10/7 「서치 자동 게시로 바꿔」·「본사가 해」(본사 H-286).

로그인은 tistory_login_check.py 와 같다(환경변수 TISTORY_TSSESSION → 쿠키). 글쓰기 화면에서
제목·본문을 넣고 「완료」 → 발행 창에서 공개 + 발행일 「예약」(날짜·시·분) → 「공개 발행」을 누른다.
**즉시 발행은 하지 않는다** — 예약 칸이 켜졌고 날짜·시·분이 요청과 같을 때만 누르고, 하나라도 다르면
누르지 않고 멈춘다. 시각은 한국 시간이다(브라우저 시간대를 Asia/Seoul로 연다).

본문 입력 세 가지(--format): text(기본모드에 글자를 친다) · html(편집기 「HTML」 모드) · md(편집기 「마크다운」
모드) — html·md는 편집기 모드를 바꾸고 내용을 그대로 넣는다(티스토리가 직접 그린다). 사진(--image)은 편집기
「첨부 → 사진」으로 올린다. 태그(--tags). 대표 이미지 지정·카테고리는 다음 단계에서 시험한 뒤 넣는다.

사용법:
  python3 도구/tistory_post.py --title "제목" --text "본문 한 줄" --at "2026-10-07 22:40"
  python3 도구/tistory_post.py --title "제목" --body-file 발행/패키지/<폴더>/붙여넣기_HTML.txt --format html --at ...
  python3 도구/tistory_post.py --title "제목" --body-file 원고.md --format md --tags "태그1,태그2" --at ...
  python3 도구/tistory_post.py ... --dry      # 발행 창까지 채우고 「공개 발행」은 누르지 않는다
  --preview                                     # 「미리보기」 화면을 열어 본문이 그려졌는지 본다(--shot이면 캡처)
  --shot <git 밖 폴더>                         # 화면 캡처
10/7 본사 시험(공개 확인): text+사진 /48(22:40) · html+사진+태그 /49 · md+사진+태그 /50(22:31) — 표·목록·굵게·링크·태그
모두 그려짐. 주의: 이 컨테이너 브라우저에서는 사진이 가끔 「NO IMAGE」로 보인다(ERR_BLOCKED_BY_ORB, 다시 열면 뜸 —
글 안의 사진 주소는 정상). 예약은 지금+1분부터 된다(분 칸은 1분 단위).
종료코드: 0 예약 등록·목록 확인 · 2 입력 오류(지난 시각 등) · 3 로그인 필요 · 4 화면이 예상과 달라 멈춤(발행 안 함)
          · 5 접속 오류 · 6 「공개 발행」은 눌렀으나 예약 목록에서 확인 안 됨
쿠키 값은 출력하지 않는다(길이만). 카카오 보호조치·캡차·추가 인증 화면이 나오면 4로 멈춘다.
"""
import argparse
import datetime as dt
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

KST = dt.timezone(dt.timedelta(hours=9))
LOGIN_MARKS = ("/auth/login", "accounts.kakao.com", "logins.daum.net")
BLOCK_WORDS = ("보호조치", "자동입력 방지", "captcha", "보안문자", "추가 인증")


def launch_kwargs():
    kw = {}
    exe = os.environ.get("TISTORY_CHROME") or "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
    if os.path.exists(exe):
        kw["executable_path"] = exe
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    if proxy:
        kw["proxy"] = {"server": proxy}
    return kw


def where(url):
    u = urlparse(url)
    return f"{u.netloc}{u.path}"


def stop(code, msg):
    print(f"결과: 멈춤 · {msg}")
    return code


def pick_date(page, target):
    """예약 날짜 칸이 target(YYYY-MM-DD)과 다르면 달력에서 고른다. 고른 뒤 칸 글자로 다시 확인한다."""
    btn = page.locator("button.btn_reserve")
    if btn.inner_text().strip() == target:
        return True
    y, m, d = (int(x) for x in target.split("-"))
    btn.click()
    page.wait_for_timeout(800)
    for _ in range(14):  # 최대 14달 앞으로
        head = page.evaluate("""()=>{const e=[...document.querySelectorAll('*')].find(x=>x.offsetParent&&/^\\s*\\d{4}\\s*[.년-]\\s*\\d{1,2}/.test(x.innerText||'')&&x.children.length<4&&(x.innerText||'').length<20);return e?e.innerText:''}""")
        mm = re.search(r"(\d{4})\D+(\d{1,2})", head or "")
        if not mm:
            return False
        cy, cm = int(mm.group(1)), int(mm.group(2))
        if (cy, cm) == (y, m):
            break
        nxt = page.locator("button:visible", has_text=re.compile(r"^(다음|다음 달|>|›)$"))
        if nxt.count() == 0:
            nxt = page.locator("[class*=next]:visible")
        if nxt.count() == 0:
            return False
        nxt.first.click()
        page.wait_for_timeout(400)
    cell = page.locator("td:visible, button:visible, a:visible", has_text=re.compile(rf"^\s*{d}\s*$"))
    if cell.count() == 0:
        return False
    cell.first.click()
    page.wait_for_timeout(600)
    return btn.inner_text().strip() == target


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--blog", default="themoneyproducer")
    ap.add_argument("--title", required=True)
    ap.add_argument("--text", default="", help="본문 글자(줄바꿈은 \\n) — --body-file 대신")
    ap.add_argument("--body-file", default="", help="본문 파일(.html·.md·.txt)")
    ap.add_argument("--format", choices=("text", "html", "md"), default="", help="없으면 파일 확장자로 정한다")
    ap.add_argument("--tags", default="", help="쉼표로 이은 태그")
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--image", action="append", default=[], help="본문 끝에 넣을 사진 파일(여러 번 가능)")
    ap.add_argument("--at", required=True, help="예약 시각, 한국 시간 'YYYY-MM-DD HH:MM'")
    ap.add_argument("--min-lead", type=int, default=1, help="지금부터 최소 몇 분 뒤여야 하나")
    ap.add_argument("--dry", action="store_true", help="「공개 발행」을 누르지 않는다")
    ap.add_argument("--shot", default="")
    a = ap.parse_args()

    try:
        at = dt.datetime.strptime(a.at, "%Y-%m-%d %H:%M").replace(tzinfo=KST)
    except ValueError:
        print("결과: 입력 오류 · --at 형식은 'YYYY-MM-DD HH:MM'(한국 시간)")
        return 2
    if a.body_file:
        bf = Path(a.body_file)
        if not bf.is_file():
            print(f"결과: 입력 오류 · 본문 파일 없음 {bf}")
            return 2
        body = bf.read_text(encoding="utf-8")
        fmt = a.format or {".html": "html", ".htm": "html", ".md": "md"}.get(bf.suffix.lower(), "text")
        if bf.name.startswith("붙여넣기_HTML"):
            fmt = a.format or "html"
    else:
        body, fmt = a.text.replace("\\n", "\n"), (a.format or "text")
    if not body.strip():
        print("결과: 입력 오류 · 본문이 비었다(--text 또는 --body-file)")
        return 2
    now = dt.datetime.now(KST)
    if at < now + dt.timedelta(minutes=a.min_lead):
        print(f"결과: 입력 오류 · 예약 시각 {a.at}이 지금({now:%H:%M})+{a.min_lead}분보다 이르다 — 즉시 발행은 하지 않는다")
        return 2
    val = os.environ.get("TISTORY_TSSESSION", "")
    if not val:
        print("결과: 멈춤 · 로그인 필요 — 환경변수 TISTORY_TSSESSION 없음")
        return 3
    print(f"쿠키: TISTORY_TSSESSION(길이 {len(val)}) · 형식 {fmt} · 예약 {a.at} KST · {'시험(누르지 않음)' if a.dry else '등록'}")
    shot = Path(a.shot).resolve() if a.shot else None
    if shot:
        shot.mkdir(parents=True, exist_ok=True)

    from playwright.sync_api import sync_playwright, Error as PwError

    base = f"https://{a.blog}.tistory.com"
    dialogs = []
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(headless=True, **launch_kwargs())
            ctx = b.new_context(locale="ko-KR", timezone_id="Asia/Seoul", viewport={"width": 1280, "height": 900})
            ctx.add_cookies([{"name": "TSSESSION", "value": val, "domain": ".tistory.com", "path": "/",
                              "httpOnly": True, "secure": True, "sameSite": "Lax"}])
            page = ctx.new_page()

            def on_dialog(d):
                # 「작성 모드를 변경하시겠습니까?」만 「예」. 「저장된 글이 있습니다. 이어서 작성?」 등은 「아니요」(새 글)
                dialogs.append(d.message[:80])
                if "작성 모드" in d.message:
                    d.accept()
                else:
                    d.dismiss()
            page.on("dialog", on_dialog)

            page.goto(f"{base}/manage/newpost/", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(4000)
            if any(m in page.url for m in LOGIN_MARKS):
                b.close()
                return stop(3, f"로그인 필요 — 글쓰기 화면이 로그인으로 넘어감({where(page.url)})")
            body_txt = page.inner_text("body")[:3000]
            if any(w in body_txt for w in BLOCK_WORDS):
                b.close()
                return stop(4, "보호조치·추가 인증 화면 — 회장께 알린다")
            if page.locator("#post-title-inp").count() == 0:
                b.close()
                return stop(4, f"글쓰기 화면 요소(#post-title-inp) 없음({where(page.url)})")

            page.fill("#post-title-inp", a.title)
            if fmt == "text":
                page.frame_locator("#editor-tistory_ifr").locator("body").click()
                for i, ln in enumerate(body.split("\n")):
                    if i:
                        page.keyboard.press("Enter")
                    page.keyboard.type(ln)
            else:
                mode_id = {"html": "html", "md": "markdown"}[fmt]
                page.click("#editor-mode-layer-btn-open")
                page.wait_for_timeout(600)
                page.click(f"#editor-mode-{mode_id}")
                page.wait_for_timeout(2000)
                cm = page.locator(".CodeMirror:visible").first
                if cm.count() == 0:
                    b.close()
                    return stop(4, f"{fmt} 모드 편집기가 열리지 않음 — 「공개 발행」을 누르지 않음")
                cm.click()
                page.keyboard.insert_text(body)
                page.wait_for_timeout(800)
                got_body = page.evaluate("()=>{const c=[...document.querySelectorAll('.CodeMirror')].find(x=>x.offsetParent&&x.CodeMirror);return c?c.CodeMirror.getValue():''}")
                if got_body.strip() != body.strip():
                    b.close()
                    return stop(4, f"{fmt} 본문이 그대로 들어가지 않음(길이 {len(got_body)}/{len(body)}) — 「공개 발행」을 누르지 않음")
            page.wait_for_timeout(800)
            ifr = page.frame_locator("#editor-tistory_ifr")
            for img in a.image:
                pth = Path(img).resolve()
                if not pth.is_file():
                    b.close()
                    return stop(2, f"사진 파일 없음: {pth.name}")
                def n_img():
                    if fmt == "text":  # 올리기가 끝난 사진만 센다(주소가 http로 바뀐 것)
                        return ifr.locator("img").evaluate_all("els=>els.filter(e=>/^https?:/.test(e.getAttribute('src')||'')).length")
                    return page.evaluate("()=>{const c=[...document.querySelectorAll('.CodeMirror')].find(x=>x.offsetParent&&x.CodeMirror);return c?(c.CodeMirror.getValue().match(/\\[##_Image/g)||[]).length:0}")
                before = n_img()
                if fmt == "text":
                    page.keyboard.press("Enter")
                page.locator("[aria-label='첨부']:visible").first.click(timeout=10000)
                page.wait_for_timeout(600)
                with page.expect_file_chooser(timeout=10000) as fc:
                    page.click("#attach-image")
                fc.value.set_files(str(pth))
                for _ in range(30):
                    page.wait_for_timeout(1000)
                    busy = page.locator("text=/[1-9][0-9]*개의 파일을 업로드 중/").count()
                    if n_img() > before and not busy:
                        break
                else:
                    b.close()
                    return stop(4, f"사진 올리기 확인 안 됨({pth.name}) — 「공개 발행」을 누르지 않음")
            if shot:
                page.screenshot(path=str(shot / "01_본문.png"))

            for tg in [t.strip() for t in a.tags.split(",") if t.strip()]:
                page.click("#tagText")
                page.keyboard.type(tg)
                page.keyboard.press("Enter")
                page.wait_for_timeout(200)
            if a.preview:
                page.click("#preview-btn")
                page.wait_for_timeout(5000)
                pv = ""
                for f in page.frames:
                    if f.url.startswith("about:srcdoc"):
                        try:
                            pv = f.inner_text("body")
                        except PwError:
                            pass
                if shot:
                    page.screenshot(path=str(shot / "00_미리보기.png"))
                print(f"미리보기: 제목 {'있음' if a.title in pv else '없음'} · 본문 글자 {len(pv)}자")
                page.keyboard.press("Escape")
                close = page.locator("button:visible", has_text="닫기")
                if close.count():
                    close.first.click()
                page.wait_for_timeout(800)
            page.click("#publish-layer-btn")
            page.wait_for_timeout(2000)
            # 공개
            pub = page.locator("label:visible, span:visible, button:visible", has_text=re.compile(r"^\s*공개\s*$"))
            if pub.count():
                pub.first.click()
            page.locator("button.btn_date", has_text="예약").click()
            page.wait_for_timeout(1200)
            if "on" not in (page.locator("button.btn_date", has_text="예약").get_attribute("class") or ""):
                b.close()
                return stop(4, "예약 칸이 켜지지 않음 — 「공개 발행」을 누르지 않음")
            if not pick_date(page, at.strftime("%Y-%m-%d")):
                if shot:
                    page.screenshot(path=str(shot / "02_날짜실패.png"))
                b.close()
                return stop(4, f"예약 날짜 {at:%Y-%m-%d}를 고르지 못함 — 「공개 발행」을 누르지 않음")
            # fill()은 분 칸이 59로 바뀐다(10/7 실측) — 세 번 눌러 고른 뒤 친다
            for sel, v in (("#dateHour", at.hour), ("#dateMinute", at.minute)):
                page.click(sel, click_count=3)
                page.keyboard.type(str(v))
                page.locator(sel).press("Tab")
                page.wait_for_timeout(200)
            page.wait_for_timeout(500)
            got = (page.locator("button.btn_reserve").inner_text().strip(),
                   int(page.input_value("#dateHour") or -1), int(page.input_value("#dateMinute") or -1))
            want = (at.strftime("%Y-%m-%d"), at.hour, at.minute)
            if shot:
                page.screenshot(path=str(shot / "02_발행창.png"))
            if got != want:
                b.close()
                return stop(4, f"예약 칸 값 {got} ≠ 요청 {want} — 「공개 발행」을 누르지 않음")
            open_on = page.evaluate("""()=>{const r=[...document.querySelectorAll('input[type=radio]')].find(x=>x.checked);return r? (r.closest('label,div')||r).innerText.trim():''}""")
            if a.dry:
                b.close()
                print(f"결과: 시험 · 사진 {len(a.image)}장 · 발행 창 채움 — 공개 「{open_on or '?'}」 · 예약 {want[0]} {want[1]:02d}:{want[2]:02d} · 「공개 발행」 누르지 않음 · 질문 창 {len(dialogs)}")
                return 0
            page.click("#publish-btn")
            page.wait_for_timeout(5000)
            after = page.url

            # 확인: 글 관리 목록에서 제목과 「예약」 표시
            page.goto(f"{base}/manage/posts/", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(4000)
            row = page.evaluate("""(t)=>{const els=[...document.querySelectorAll('li,tr,div')].filter(e=>e.offsetParent&&(e.innerText||'').includes(t)&&(e.innerText||'').length<400);els.sort((x,y)=>x.innerText.length-y.innerText.length);return els.length?els[0].innerText.replace(/\\s+/g,' ').trim():''}""", a.title)
            if shot:
                page.screenshot(path=str(shot / "03_글목록.png"))
            b.close()
    except PwError as e:
        return stop(5, f"접속 오류 — {str(e).splitlines()[0][:160]}")

    if row and "예약" in row:
        print(f"결과: 성공 · 예약 등록 「{a.title}」 사진 {len(a.image)}장 {a.at} KST · 글 목록: {row[:160]}")
        return 0
    print(f"결과: 확인 필요 · 「공개 발행」 누름(이동 {where(after)}) · 글 목록에서 예약 표시 확인 안 됨: {row[:160] or '줄 없음'}")
    return 6


if __name__ == "__main__":
    sys.exit(main())
