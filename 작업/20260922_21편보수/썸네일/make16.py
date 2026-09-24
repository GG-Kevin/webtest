# -*- coding: utf-8 -*-
"""/16 생산적금융 ISA — 2026-09-24 「지면」 신규 제작(12편 배치).

「포착」 지침(06_썸네일문구_16.md) 그대로 구현 — 문구 무수정.
  · 주제어 "ISA"를 이 장의 최대 글자로. 확정 제목("생산적금융 ISA,
    아직 국회를...")에 이미 있는 말.
  · 킥커 "생산적금융"은 확정 제목 첫 단어. 무수정.
  · 그래픽 장치: 무한대 고리(∞) — 본문 1·19행 "한도 없이 전액 비과세"를
    형상화한 도형. 숫자·그래프 아님(한도가 없다는 것 자체를 그리는 것이라
    막대·선으로 오르내림을 지어낼 수 없다).
  · 헤드라인(확정 썸네일 문구) "비과세 한도, / 이번엔 없습니다" 무수정.
  · 키워드 색은 크림(밝은 무채색 계열)로 잡아 22장 틀의 "노란 키워드 강조"와
    분명히 다르게 했다 — 앰버는 보조 장치(고리)에만, 글자색에는 안 씀.

직전 세 장(/11 민트·중앙, /12 버넌엄버·우, /13 웜그레이지·좌) 대조: /16은
다크 초콜릿골드(색상축 다름)·좌측정렬(/13과 정렬은 같으나 명도가 반대 — 밝음↔어둠)·
무한대 고리 장치는 다섯 장 어디에도 없다.
"""
from PIL import Image, ImageDraw, ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S, M = 1080, 72
BG    = (52, 40, 14)     # 다크 초콜릿골드 — 남색 아님(R>G>B, 웜)
CREAM = (246, 238, 220)
AMBER = (214, 158, 54)
MUTED = (150, 130, 90)

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)

def put(x, top, t, fo, col):
    bb = fo.getbbox(t)
    d.text((x - bb[0], top - bb[1]), t, font=fo, fill=col)
    return x + (bb[2] - bb[0]), top + (bb[3] - bb[1])

# ── 1. 킥커 (확정 제목 첫 단어, 무수정)
_, k_bot = put(M, 88, "생산적금융", f("Bold", 40), MUTED)

# ── 2. 주제어 — 이 장의 최대 글자
_, key_bot = put(M, k_bot + 20, "ISA", f("ExtraBold", 380), CREAM)

# ── 3. 무한대 고리(도형) — "한도 없음"의 형상화, 오른쪽 여백에 배치
loop_cy = k_bot + 20 + 175
loop_cx = S - M - 150
rad = 78
off = 66
d.ellipse([loop_cx - off - rad, loop_cy - rad, loop_cx - off + rad, loop_cy + rad], outline=AMBER, width=14)
d.ellipse([loop_cx + off - rad, loop_cy - rad, loop_cx + off + rad, loop_cy + rad], outline=AMBER, width=14)

# ── 4. 밑줄(도형)
div_y = key_bot + 56
d.rectangle([M, div_y, M + 140, div_y + 8], fill=AMBER)

# ── 5. 헤드라인 (「포착」 확정 썸네일 문구, 무수정) — 2줄, 주제어보다 작게
hf = f("Bold", 66)
_, h1_bot = put(M, div_y + 56, "비과세 한도,", hf, CREAM)
x = M
for seg, col in [("이번엔 ", CREAM), ("없습니다", AMBER)]:
    x, h2_bot = put(x, h1_bot + 24, seg, hf, col)

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/16.png")
print("saved 16.png  k_bot=%d key_bot=%d div=%d h2_bot=%d" %
      (k_bot, key_bot, div_y, h2_bot))
