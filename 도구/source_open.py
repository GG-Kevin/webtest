#!/usr/bin/env python3
"""source_open — 1차 원문이 오늘 열리는지 본다(0토큰, 표준 라이브러리만).

사용:
  python3 도구/source_open.py <URL> [<URL> ...]
  python3 도구/source_open.py --file urls.txt      (줄마다 URL, 탭 뒤는 메모, # 줄은 건너뜀)
  옵션: --json(스크립트용) · --min-text N(본문 글자 하한, 기본 300) · --timeout 초(기본 25)
출력 줄: 판정<TAB>HTTP 상태<TAB>본문 길이<TAB>최종 URL<TAB>입력 URL
  판정 = 「열림」 또는 「못 열림(이유)」. 이유: HTTP 403·404·429·5xx / 시간 초과 / 연결 실패 / 본문 짧음(JS 화면일 수 있음) / 로그인 화면
종료코드: 0 = 모두 열림 · 1 = 못 연 것 있음 · 2 = 사용 오류

규칙
- 403·429는 「못 열었다」로 적고 끝낸다. 다른 머리글·다른 주소로 우회하지 않는다(본사 공통 규칙).
- 네트워크는 환경의 HTTPS_PROXY를 그대로 쓴다. CA는 SSL_CERT_FILE(없으면 시스템 기본).
- 본문 길이 = <script>·<style>·태그를 지운 뒤 공백을 뺀 글자 수.
- 다른 정찰 스크립트(scout·calendar_build·wp_collect·counter_log·calc_check)가 fetch()·visible_text()를 가져다 쓴다.
"""
import argparse
import html
import json
import os
import re
import socket
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
_CTX = None


def _ctx():
    global _CTX
    if _CTX is None:
        caf = os.environ.get("SSL_CERT_FILE")
        if not caf and os.path.exists("/root/.ccr/ca-bundle.crt"):
            caf = "/root/.ccr/ca-bundle.crt"
        _CTX = ssl.create_default_context(cafile=caf) if caf else ssl.create_default_context()
    return _CTX


def _decode(raw, ctype):
    m = re.search(r"charset=([\w-]+)", ctype or "", re.I)
    cands = []
    if m:
        cands.append(m.group(1))
    head = raw[:4000].decode("ascii", "ignore")
    m2 = re.search(r"<meta[^>]+charset=[\"']?([\w-]+)", head, re.I)
    if m2:
        cands.append(m2.group(1))
    cands += ["utf-8", "cp949"]
    for c in cands:
        try:
            return raw.decode(c)
        except (LookupError, UnicodeDecodeError):
            continue
    return raw.decode("utf-8", "replace")


def iri(url):
    """한글이 든 주소(예: law.go.kr/법령/…)를 퍼센트 인코딩한다. 이미 인코딩된 %xx는 그대로 둔다."""
    p = urllib.parse.urlsplit(url)
    host = p.hostname.encode("idna").decode("ascii") if p.hostname else ""
    netloc = host + (f":{p.port}" if p.port else "")
    if p.username:
        netloc = p.username + (":" + p.password if p.password else "") + "@" + netloc
    path = urllib.parse.quote(p.path, safe="/%:@!$&'()*+,;=-._~")
    query = urllib.parse.quote(p.query, safe="=&%:@!$'()*+,;/?-._~")
    return urllib.parse.urlunsplit((p.scheme, netloc, path, query, p.fragment))


def fetch(url, timeout=25, headers=None, data=None, method=None, retries=1, max_bytes=12_000_000):
    """URL 하나를 받아 dict로 돌려준다. 403·429는 다시 시도하지 않는다.
    키: url · final_url · status(int, 실패면 0) · ctype · text · bytes · reason(None이면 받음) · elapsed"""
    h = {"User-Agent": UA, "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8"}
    if headers:
        h.update(headers)
    t0 = time.time()
    last = None
    req_url = iri(url)
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(req_url, headers=h, data=data, method=method)
            with urllib.request.urlopen(req, timeout=timeout, context=_ctx()) as r:
                raw = r.read(max_bytes)
                ctype = r.headers.get("Content-Type", "")
                return {"url": url, "final_url": r.geturl(), "status": r.status, "ctype": ctype,
                        "bytes": raw, "text": _decode(raw, ctype), "reason": None,
                        "headers": dict(r.headers), "elapsed": round(time.time() - t0, 2)}
        except urllib.error.HTTPError as e:
            body = b""
            try:
                body = e.read(200_000)
            except Exception:
                pass
            return {"url": url, "final_url": e.geturl() if hasattr(e, "geturl") else url, "status": e.code,
                    "ctype": e.headers.get("Content-Type", "") if e.headers else "", "bytes": body,
                    "text": _decode(body, e.headers.get("Content-Type", "") if e.headers else ""),
                    "reason": f"HTTP {e.code}", "headers": dict(e.headers or {}),
                    "elapsed": round(time.time() - t0, 2)}
        except (socket.timeout, TimeoutError) as e:
            last = "시간 초과"
        except urllib.error.URLError as e:
            r = getattr(e, "reason", e)
            last = "시간 초과" if isinstance(r, (socket.timeout, TimeoutError)) or "timed out" in str(r) else f"연결 실패({str(r)[:60]})"
        except Exception as e:  # noqa: BLE001 — 어떤 오류든 「못 열림」으로 적는다
            last = f"연결 실패({type(e).__name__}: {str(e)[:60]})"
        if attempt < retries:
            time.sleep(1.5)
    return {"url": url, "final_url": url, "status": 0, "ctype": "", "bytes": b"", "text": "",
            "reason": last, "headers": {}, "elapsed": round(time.time() - t0, 2)}


def visible_text(page):
    s = re.sub(r"(?is)<(script|style|noscript|template)[^>]*>.*?</\1>", " ", page or "")
    s = re.sub(r"(?s)<!--.*?-->", " ", s)
    s = re.sub(r"(?i)<br\s*/?>|</(p|div|li|tr|h\d|td|th)>", "\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t\r\f\v ]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


def judge(res, min_text=300):
    """fetch 결과 → (판정 문자열, 본문 길이)"""
    if res["reason"]:
        return f"못 열림({res['reason']})", 0
    txt = visible_text(res["text"]) if "html" in (res["ctype"] or "").lower() or "<html" in res["text"][:2000].lower() else res["text"]
    n = len(re.sub(r"\s", "", txt))
    if re.search(r"/(login|nidlogin|auth/login|member/login)", res["final_url"], re.I) and not re.search(r"/(login|auth)", res["url"], re.I):
        return "못 열림(로그인 화면)", n
    if "pdf" in (res["ctype"] or "").lower():
        return ("열림" if len(res["bytes"]) > 2000 else "못 열림(파일 짧음)"), len(res["bytes"])
    if n < min_text:
        return "못 열림(본문 짧음 — JS 화면일 수 있음)", n
    return "열림", n


def open_check(url, min_text=300, timeout=25):
    res = fetch(url, timeout=timeout, retries=2)  # 정부 누리집은 연결 끊김이 섞여 나온다(10/3) — 두 번 더 본다(403·429는 다시 안 봄)
    verdict, n = judge(res, min_text)
    return {"url": url, "status": res["status"], "final_url": res["final_url"], "length": n,
            "verdict": verdict, "elapsed": res["elapsed"]}


def main(argv=None):
    ap = argparse.ArgumentParser(description="1차 원문 열림 확인(0토큰)")
    ap.add_argument("urls", nargs="*")
    ap.add_argument("--file")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--min-text", type=int, default=300)
    ap.add_argument("--timeout", type=int, default=25)
    a = ap.parse_args(argv)
    urls = list(a.urls)
    if a.file:
        with open(a.file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    urls.append(line.split("\t")[0].strip())
    if not urls:
        ap.print_usage(sys.stderr)
        return 2
    out = []
    seen = {}
    for u in urls:
        if u not in seen:
            seen[u] = open_check(u, a.min_text, a.timeout)
        out.append(seen[u])
    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
    else:
        for r in out:
            print(f"{r['verdict']}\t{r['status']}\t{r['length']}\t{r['final_url']}\t{r['url']}")
        n_bad = sum(1 for r in out if r["verdict"] != "열림")
        print(f"# 합계 {len(out)} · 열림 {len(out) - n_bad} · 못 열림 {n_bad}")
    return 1 if any(r["verdict"] != "열림" for r in out) else 0


if __name__ == "__main__":
    sys.exit(main())
