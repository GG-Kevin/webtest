# -*- coding: utf-8 -*-
"""/5 관리종목 썸네일 — 2026-09-24 회장 반려 재제작.
핵심어 「관리종목」을 그 장의 최대 글자로 올린다."""
from PIL import Image, ImageDraw
from PIL import ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S = 1080
BG      = (56, 18, 26)       # 짙은 버건디
CREAM   = (244, 236, 228)
MUTED   = (186, 142, 146)
CORAL   = (255, 122, 96)
PANEL   = (76, 30, 38)

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)

M = 72

# ── 1. 핵심어 — 이 장에서 가장 큰 글자
d.text((M, 96), "관리종목", font=f("ExtraBold", 188), fill=CREAM)
# 부속어는 핵심어보다 확실히 작게, 같은 줄 아래
d.text((M + 6, 300), "지정되면", font=f("Bold", 64), fill=MUTED)

# ── 2. 헤드라인 (「포착」 확정 문구, 무수정)
d.text((M, 418), "정작 청산당하는 건,", font=f("Bold", 82), fill=CREAM)
y2 = 522
x = M
for seg, col in [("멀쩡한 다른 종목", CORAL), ("입니다", CREAM)]:
    d.text((x, y2), seg, font=f("Bold", 82), fill=col)
    x += d.textlength(seg, font=f("Bold", 82))

# ── 3. 본문 34행 결론 — 두 블록 가로 병치
by, bh = 700, 210
gap = 36
bw = (S - M * 2 - gap) // 2
d.rounded_rectangle([M, by, M + bw, by + bh], 20, fill=PANEL)
d.rounded_rectangle([M + bw + gap, by, S - M, by + bh], 20, fill=CORAL)

def cen(cx, cy, t, fo, col):
    w = d.textlength(t, font=fo)
    d.text((cx - w / 2, cy), t, font=fo, fill=col)

c1 = M + bw / 2
c2 = M + bw + gap + bw / 2
cen(c1, by + 44, "문제는", f("Bold", 46), MUTED)
cen(c1, by + 104, "A종목", f("ExtraBold", 72), CREAM)
cen(c2, by + 44, "청산은", f("Bold", 46), (92, 26, 22))
cen(c2, by + 104, "B종목", f("ExtraBold", 72), (36, 12, 14))

d.text((M, 962), "담보가치가 사라지면 계좌 전체가 흔들립니다",
       font=f("Regular", 40), fill=MUTED)

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/5.png")
print("saved")
