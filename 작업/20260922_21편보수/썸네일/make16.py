# -*- coding: utf-8 -*-
"""/16 생산적금융 ISA — 2026-09-24 「지면」 재제작(D-146 12편 동시배정, 충돌방지 배정값 준수).

배정(「진행」, 충돌 방지): 배경 딥 플럼(자주빛으로 색상축 분리) · 정렬축 좌측 ·
주제어 위치 하단. 구판 make16.py(다크초콜릿골드·주제어 상단)는 이 배정 이전에
만들어진 것이라 폐기하고 이 배정값으로 다시 그린다.

「포착」 지침(06_썸네일문구_16.md) 그대로 — 문구 무수정.
  · 확정 제목 "생산적금융 ISA, 아직 국회를 통과하지 못했습니다"(무수정, 209행 1순위)
    에 이미 있는 두 단어를 킥커/주제어로 그대로 쓴다 — 새로 짓지 않는다.
    킥커 "생산적금융"(제목 첫 단어) · 주제어 "ISA"(제목 두 번째 단어).
  · 헤드라인(확정 썸네일 문구) "비과세 한도, / 이번엔 없습니다" 무수정, 2줄.
  · 보조 태그 "한도 없이 전액 비과세" — 본문 1행·19행 원문 그대로 인용
    (「지면」이 새로 지은 문장 아님). ISA 위, 주제어를 뒷받침하는 위치.
  · 주제어 "ISA"를 이 장 전체에서 가장 큰 글자로 하단에 배치(회장 공통사항 직결).
  · 노란 계열 전혀 안 씀 — 22장 틀의 "노란 배지·노란 키워드 강조"와 분리.
"""
from PIL import Image, ImageDraw, ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S, M = 1080, 72
BG     = (90, 10, 60)     # 딥 마젠타 플럼 — /7(40,20,70)과 색상축 분리(채널차 최소34)
CREAM  = (245, 235, 240)
MUTED  = (188, 140, 168)
TAG_BG = (245, 235, 240)
TAG_TX = (90, 10, 60)

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)

def put(x, top, t, fo, col):
    bb = fo.getbbox(t)
    d.text((x - bb[0], top - bb[1]), t, font=fo, fill=col)
    return x + (bb[2] - bb[0]), top + (bb[3] - bb[1])

# ── 1. 킥커 (확정 제목 첫 단어, 무수정) — 좌측정렬 상단
_, k_bot = put(M, 84, "생산적금융", f("Bold", 42), MUTED)

# ── 2. 헤드라인(확정 썸네일 문구, 무수정) — 2줄, 좌측정렬
hf = f("Bold", 68)
_, h1_bot = put(M, k_bot + 44, "비과세 한도,", hf, CREAM)
_, h2_bot = put(M, h1_bot + 18, "이번엔 없습니다", hf, CREAM)

# ── 3. 얇은 밑줄(도형) — 헤드라인과 하단부 분리
div_y = h2_bot + 70
d.rectangle([M, div_y, M + 160, div_y + 6], fill=MUTED)

# ── 4. 보조 태그(본문 1행·19행 직접 인용) — 필 배지, ISA 바로 위
tag_f = f("Bold", 34)
tag_t = "한도 없이 전액 비과세"
tb = tag_f.getbbox(tag_t)
tw, th = tb[2] - tb[0], tb[3] - tb[1]
pad_x, pad_y = 24, 14
tag_w, tag_h = tw + pad_x * 2, th + pad_y * 2
tag_top = div_y + 54
d.rounded_rectangle([M, tag_top, M + tag_w, tag_top + tag_h], tag_h / 2, fill=TAG_BG)
d.text((M + pad_x - tb[0], tag_top + pad_y - tb[1]), tag_t, font=tag_f, fill=TAG_TX)
tag_bot = tag_top + tag_h

# ── 5. 주제어 "ISA" — 이 장 전체에서 가장 큰 글자, 하단, 좌측정렬
kf = f("ExtraBold", 400)
isa_bb = kf.getbbox("ISA")
isa_h = isa_bb[3] - isa_bb[1]
bottom_margin = 90
isa_top = S - bottom_margin - isa_h
put(M, isa_top, "ISA", kf, CREAM)

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/16.png")
print("saved 16.png  k_bot=%d h2_bot=%d div=%d tag_bot=%d isa_top=%d isa_h=%d canvas=%d" %
      (k_bot, h2_bot, div_y, tag_bot, isa_top, isa_h, S))
