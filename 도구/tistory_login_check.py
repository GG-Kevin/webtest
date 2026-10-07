#!/usr/bin/env python3
"""티스토리 로그인 확인(읽기 전용). 회장 10/7 22:0x 「로그인 확인 도구만 본사에 맡겨」(전략실 전달).

환경변수 TISTORY_TSSESSION(회장 티스토리 로그인 쿠키)을 자동 브라우저에 넣고
① 관리 화면(/manage)이 로그인 상태로 열리는지 ② 글쓰기 화면(/manage/newpost/)이 뜨는지만 본다.
네이버 도구(naver_draft state_from_env.py·session.py)와 같은 방식이다.

하지 않는 것: 글쓰기·저장·임시저장·설정 변경·로그아웃·버튼 누르기. 글쓰기 화면에서 「이어서
작성할까요」 같은 질문 창이 뜨면 답하지 않고 그대로 닫는다. 쿠키 값은 어디에도 출력·저장하지
않는다(이름과 길이만). 화면 캡처는 --shot 으로 git 밖 경로를 줄 때만 남긴다.

사용법:
  python3 도구/tistory_login_check.py                 # 기본 블로그 themoneyproducer
  python3 도구/tistory_login_check.py --blog <이름> --shot /tmp/tistory_shots
종료코드: 0 관리·글쓰기 모두 열림 · 3 로그인 필요(쿠키 없음·만료) · 4 관리는 열렸지만 글쓰기 확인 안 됨 · 5 접속 오류
"""
import argparse
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

LOGIN_MARKS = ("/auth/login", "accounts.kakao.com", "logins.daum.net")
EDITOR_SELECTORS = ("#post-title-inp", "textarea.textarea_tit", "#editor-tistory_ifr", "#editor-root", ".tt-editor")


def launch_kwargs():
    # 클라우드 컨테이너: 크로미움은 /opt/pw-browsers 에 있다(`playwright install` 금지).
    # 프록시 인증서는 컨테이너의 브라우저 인증서 저장소가 이미 믿는다 — 인증서 검사는 끄지 않는다.
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
    return f"{u.netloc}{u.path}"  # 질의 문자열(토큰이 섞일 수 있음)은 출력하지 않는다


def is_login(url):
    return any(m in url for m in LOGIN_MARKS)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--blog", default="themoneyproducer", help="티스토리 블로그 이름(<이름>.tistory.com)")
    ap.add_argument("--shot", default="", help="화면 캡처를 남길 git 밖 폴더(없으면 남기지 않음)")
    ap.add_argument("--wait", type=int, default=4000, help="화면마다 기다리는 밀리초")
    a = ap.parse_args()

    val = os.environ.get("TISTORY_TSSESSION", "")
    if not val:
        print("결과: 실패 · 로그인 필요 — 환경변수 TISTORY_TSSESSION 없음(이 컨테이너가 변수 추가 전에 떴다면 새 컨테이너 필요)")
        return 3
    print(f"쿠키: TISTORY_TSSESSION(길이 {len(val)})")

    shot = Path(a.shot).resolve() if a.shot else None
    if shot:
        shot.mkdir(parents=True, exist_ok=True)

    from playwright.sync_api import sync_playwright, Error as PwError

    base = f"https://{a.blog}.tistory.com"
    res = {}
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(headless=True, **launch_kwargs())
            ctx = b.new_context(locale="ko-KR")
            ctx.add_cookies([{"name": "TSSESSION", "value": val, "domain": ".tistory.com", "path": "/",
                              "httpOnly": True, "secure": True, "sameSite": "Lax"}])
            page = ctx.new_page()
            dialogs = []
            # 질문 창에는 답하지 않는다(누르면 서버 상태가 바뀔 수 있음) — 기록만 하고 브라우저를 닫는다.
            page.on("dialog", lambda d: dialogs.append(d.message[:60]))

            # ① 관리 화면
            page.goto(f"{base}/manage", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(a.wait)
            res["manage_url"] = page.url
            res["manage_title"] = page.title() if not dialogs else ""
            if shot and not dialogs:
                page.screenshot(path=str(shot / "01_manage.png"))
            if is_login(page.url):
                b.close()
                print(f"결과: 실패 · 로그인 필요 — 관리 화면이 로그인 화면으로 넘어감({where(res['manage_url'])})")
                return 3

            # ② 글쓰기 화면(열기만 한다)
            page.goto(f"{base}/manage/newpost/", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(a.wait)
            res["write_url"] = page.url
            found = []
            if not dialogs:
                for sel in EDITOR_SELECTORS:
                    try:
                        if page.locator(sel).count() > 0:
                            found.append(sel)
                    except PwError:
                        pass
                res["write_title"] = page.title()
                if shot:
                    page.screenshot(path=str(shot / "02_newpost.png"))
            b.close()
    except PwError as e:
        msg = str(e).splitlines()[0][:160]
        print(f"결과: 실패 · 접속 오류 — {msg}")
        return 5

    if is_login(res["write_url"]):
        print(f"결과: 실패 · 로그인 필요 — 글쓰기 화면이 로그인으로 넘어감 · 관리 화면 「{res['manage_title']}」")
        return 3
    write_ok = bool(found) or (bool(dialogs) and "/manage/newpost" in res["write_url"])
    tail = f" · 질문 창 {len(dialogs)}개(답하지 않음): {dialogs[0]}" if dialogs else ""
    if write_ok:
        print(f"결과: 성공 · 관리 화면 「{res['manage_title']}」({where(res['manage_url'])}) · "
              f"글쓰기 화면 열림({where(res['write_url'])}, 확인 요소 {', '.join(found) or '질문 창'}){tail}")
        return 0
    print(f"결과: 부분 · 관리 화면 「{res['manage_title']}」 열림 · 글쓰기 화면 요소 확인 안 됨"
          f"({where(res['write_url'])} 「{res.get('write_title', '')}」){tail}")
    return 4


if __name__ == "__main__":
    sys.exit(main())
