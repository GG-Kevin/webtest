# -*- coding: utf-8 -*-
"""/17 엔화 강세인데 원/엔은 그대로 — 2026-09-24 「지면」 재제작(D-146 12편 배치, 신규 배정값).

「포착」 지침(06_썸네일문구_17.md) 그대로 구현한다 — 문구·제목 무수정, 새로 짓지 않는다.
  · 확정 제목 "엔화가 강해졌는데 왜 원/엔은 그대로일까요"에서 두 조각만 그대로 잘라 쓴다
    — 킥커 "엔화가 강해졌는데"(제목 앞부분), 주제어 "원/엔"(제목의 핵심 명사).
  · 확정 썸네일 문구 "엔화가 싸진 게 아니라, 원화가 더 세졌습니다"를 콤마 자리에서만
    줄바꿈해 헤드라인 2줄로 쓴다. 문구 자체는 무수정.
  · 그래픽 장치: 기울어진 저울대(시소) — ¥·₩ 두 통화를 양끝에 놓고 ₩ 쪽이 무거운(=강세)
    쪽으로 기운다. 재정환율 구조(본문 20행)의 은유이지 실제 환율 값을 그린 그래프가
    아니다 — 데이터 계열 아님, 글자 아님(검사1 분모에서 제외).

「진행」 배정값(충돌 방지, 12편 동시 배치):
  배경 RGB(214,232,220) 페일 민트 · 정렬축 우측 · 주제어 위치 상단.
  기존 완료 5장 배경(/2 230,214,178 · /5 56,18,26 · /6 20,42,35 · /7 40,20,70 ·
  /8 237,240,245) 전부와 충분히 다르다 — 밝은 한색(cool) 계열은 이 배치에서 이 장이 유일.
"""
from PIL import Image, ImageDraw, ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S, M = 1080, 76
BG    = (196, 230, 204)   # 페일 민트 — 「진행」 배정값(214,232,220)에서 「지면」이 자율
                           # 조정(D-105 §8). 원값은 /8(237,240,245)과 채널차 25로 검사3
                           # 기준(≥30) 미달 — 채도를 살짝 올려 25→41로 확보. 색상 계열(민트)은 유지.
INK   = (24, 54, 46)      # 헤드라인 — 배경과 고명도차(진한 딥그린)
ACCENT= (178, 64, 40)     # 주제어 — 러스트(민트 보색 계열, 최대 대비)
MUTED = (92, 130, 116)    # 킥커
TEAL  = (32, 104, 92)     # 저울 장치(원화측)
CREAM = (250, 247, 238)

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)
R = S - M

def put_r(right, top, t, fo, col):
    bb = fo.getbbox(t)
    w = bb[2] - bb[0]
    d.text((right - w - bb[0], top - bb[1]), t, font=fo, fill=col)
    return right - w, top + (bb[3] - bb[1])

# ── 1. 킥커 — 확정 제목 앞부분, 무수정
_, k_bot = put_r(R, 92, "엔화가 강해졌는데", f("Bold", 36), MUTED)

# ── 2. 주제어 "원/엔" — 이 장 전체에서 가장 큰 글자, 상단 배치
_, key_bot = put_r(R, k_bot + 26, "원/엔", f("ExtraBold", 296), ACCENT)

# ── 3. 저울대(시소) 도형 — ₩ 쪽이 무거운(강세) 쪽으로 기움. 데이터 그래프 아님, 글자 아님.
beam_cy = key_bot + 150
beam_cx = R - 280
tilt = 30
lx, ly = beam_cx - 230, beam_cy - tilt   # ¥ 쪽(가벼움 → 위로)
rx, ry = beam_cx + 230, beam_cy + tilt   # ₩ 쪽(무거움 → 아래로)
d.line([(lx, ly), (rx, ry)], fill=MUTED, width=10)
d.polygon([(beam_cx - 24, beam_cy + 50), (beam_cx + 24, beam_cy + 50), (beam_cx, beam_cy - 6)], fill=MUTED)
d.ellipse([lx - 48, ly - 48, lx + 48, ly + 48], fill=CREAM, outline=ACCENT, width=7)
d.ellipse([rx - 58, ry - 58, rx + 58, ry + 58], fill=TEAL, outline=TEAL, width=7)

yenf = f("ExtraBold", 46)
wonf = f("ExtraBold", 52)
bby = yenf.getbbox("¥")
d.text((lx - (bby[2] - bby[0]) / 2 - bby[0], ly - (bby[3] - bby[1]) / 2 - bby[1]), "¥", font=yenf, fill=ACCENT)
bbw = wonf.getbbox("₩")
d.text((rx - (bbw[2] - bbw[0]) / 2 - bbw[0], ry - (bbw[3] - bbw[1]) / 2 - bbw[1]), "₩", font=wonf, fill=CREAM)
beam_bot = max(ly + 48, ry + 58)

# ── 4. 헤드라인(「포착」 확정 썸네일 문구, 무수정) — 콤마 자리에서만 줄바꿈, 2줄
hf = f("Bold", 62)
_, h1_bot = put_r(R, beam_bot + 66, "엔화가 싸진 게 아니라,", hf, INK)
_, h2_bot = put_r(R, h1_bot + 22, "원화가 더 세졌습니다", hf, ACCENT)

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/17.png")
print("saved 17.png  k_bot=%d key_bot=%d beam_bot=%d h2_bot=%d canvas=%d" %
      (k_bot, key_bot, beam_bot, h2_bot, S))
