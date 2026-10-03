#!/usr/bin/env python3
"""발행/대기/*.html → 발행/패키지/<슬러그>/ (미리보기.html · 붙여넣기.txt · 썸네일.png · 발행.html · 그림/)
사용: python3 도구/패키지_만들기.py [슬러그 ...]   (없으면 대기 파일 전부)"""
import base64, html, os, re, shutil, subprocess, sys
from html.parser import HTMLParser

ROOT = os.getcwd()
QUEUE = "발행/대기"
OUT = "발행/패키지"
MIME = {".png": "image/png", ".svg": "image/svg+xml", ".jpg": "image/jpeg"}


class Txt(HTMLParser):
    BLOCK = {"p", "div", "h1", "h2", "h3", "li", "tr", "figure", "figcaption", "caption", "table", "ul", "ol", "section", "form"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.skip, self.href, self.row = [], 0, None, None

    def handle_starttag(self, t, a):
        a = dict(a)
        if t in ("script", "style", "head"):
            self.skip += 1
        elif t == "img":
            self.out.append(f"\n[그림: {a.get('alt','')}]\n")
        elif t == "a":
            self.href = a.get("href")
        elif t in ("h2", "h3"):
            self.out.append("\n\n" + ("## " if t == "h2" else "### "))
        elif t == "h1":
            self.out.append("# ")
        elif t == "tr":
            self.row = []
        elif t == "li":
            self.out.append("\n- ")
        elif t == "br":
            self.out.append("\n")
        elif t in self.BLOCK:
            self.out.append("\n")

    def handle_endtag(self, t):
        if t in ("script", "style", "head"):
            self.skip -= 1
        elif t == "a" and self.href:
            if self.href.startswith("http") or self.href.startswith("/"):
                self.out.append(f" ({self.href})")
            self.href = None
        elif t in ("td", "th") and self.row is not None:
            self.row.append("".join(self.cur).strip()); self.cur = []
        elif t == "tr" and self.row is not None:
            self.out.append("| " + " | ".join(self.row) + " |\n"); self.row = None
        elif t in ("p", "div", "h1", "h2", "h3", "figure", "caption", "table"):
            self.out.append("\n")

    cur = []

    def handle_starttag_td(self):
        pass

    def handle_data(self, d):
        if self.skip:
            return
        if self.row is not None:
            self.cur.append(d); return
        self.out.append(re.sub(r"\s+", " ", d))


def to_txt(src):
    p = Txt()
    # td/th 시작 때 셀 버퍼 초기화
    orig = p.handle_starttag
    def hs(t, a):
        if t in ("td", "th"):
            p.cur = []
        orig(t, a)
    p.handle_starttag = hs
    p.feed(src)
    s = "".join(p.out)
    s = re.sub(r"[ \t]+\n", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s).strip() + "\n"
    return s


def embed(src, folder):
    def rep(m):
        path = os.path.join(folder, m.group(2))
        if not os.path.isfile(path):
            return m.group(0)
        ext = os.path.splitext(path)[1].lower()
        b = base64.b64encode(open(path, "rb").read()).decode()
        return f'{m.group(1)}data:{MIME.get(ext,"application/octet-stream")};base64,{b}"'
    return re.sub(r'(<img[^>]*?src=")(그림/[^"]+)"', rep, src)


def main():
    names = sys.argv[1:] or sorted(f[:-5] for f in os.listdir(QUEUE) if f.endswith(".html"))
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for slug in names:
        qsrc = open(f"{QUEUE}/{slug}.html", encoding="utf-8").read()
        work = [d for d in os.listdir("작업") if d == slug or (d.startswith(slug.split("_")[0] + "_") and d.split("_", 1)[1] == slug.split("_", 1)[1])]
        if not work:
            print("작업 폴더 없음:", slug); continue
        wdir = f"작업/{work[0]}"
        dst = f"{OUT}/{slug}"
        os.makedirs(f"{dst}/그림", exist_ok=True)
        for f in os.listdir(f"{wdir}/그림"):
            if f.endswith((".png", ".svg")):
                shutil.copy(f"{wdir}/그림/{f}", f"{dst}/그림/{f}")
        shutil.copy(f"{QUEUE}/{slug}.html", f"{dst}/발행.html")
        title = re.search(r"<!-- 제목: (.*?) -->", qsrc).group(1).strip()
        disc = re.search(r"<!-- 디스커버 제목: (.*?) -->", qsrc)
        disc = disc.group(1).strip() if disc else ""
        pre = embed(qsrc, dst)
        pre = f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>body{{max-width:760px;margin:24px auto;padding:0 16px;font-family:system-ui,"Noto Sans KR",sans-serif;line-height:1.8;color:#222}}img{{max-width:100%;height:auto}}table{{border-collapse:collapse;max-width:100%;display:block;overflow-x:auto}}td,th{{border:1px solid #ccc;padding:6px 8px}}</style></head><body>\n<h1 style="font-size:1.6em;line-height:1.4">{html.escape(title)}</h1>\n{pre}\n</body></html>'
        open(f"{dst}/미리보기.html", "w", encoding="utf-8").write(pre)
        txt = to_txt(qsrc)
        head = f"[제목] {title}\n" + (f"[디스커버 제목] {disc}\n" if disc else "") + "=" * 40 + "\n\n"
        open(f"{dst}/본문_글자만.txt", "w", encoding="utf-8").write(head + txt)
        # 티스토리 HTML 모드에 붙이는 소스 — 이미지 자리는 그림/파일명 그대로(업로드 뒤 주소로 교체)
        open(f"{dst}/붙여넣기_HTML.txt", "w", encoding="utf-8").write(qsrc)
        # 시험용 — 그림을 파일 안에 넣은 판(티스토리가 받아 주는지 확인 필요)
        open(f"{dst}/붙여넣기_HTML_그림포함.txt", "w", encoding="utf-8").write(embed(qsrc, dst))
        rows.append((slug, title))
        print("만듦:", slug)
    idx = ['<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>발행 패키지 목록</title><style>body{max-width:900px;margin:24px auto;padding:0 16px;font-family:system-ui,sans-serif}li{margin:18px 0;display:flex;gap:14px;align-items:center}img{width:200px;border:1px solid #ddd}</style></head><body><h1>발행 패키지 목록</h1><ul>']
    for slug, title in rows:
        idx.append(f'<li><img src="{slug}/썸네일.png" alt=""><div><b>{html.escape(title)}</b><br><a href="{slug}/미리보기.html">미리보기</a> · <a href="{slug}/붙여넣기_HTML.txt">붙여넣기_HTML.txt</a> · <a href="{slug}/발행.html">발행.html</a></div></li>')
    idx.append("</ul></body></html>")
    open(f"{OUT}/목록.html", "w", encoding="utf-8").write("\n".join(idx))
    print("목록:", f"{OUT}/목록.html", len(rows), "편")
    subprocess.run([sys.executable, "도구/썸네일_만들기.py"], check=True)


main()
