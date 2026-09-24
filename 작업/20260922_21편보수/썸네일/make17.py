# -*- coding: utf-8 -*-
"""/17 엔화 강세인데 원/엔은 그대로 — 2026-09-24 「지면」 신규 제작(12편 배치).

「포착」 지침(06_썸네일문구_17.md) 그대로 구현 — 문구 무수정.
  · 주제어 "원/엔"을 이 장의 최대 글자로. 확정 제목("...왜 원/엔은
    그대로일까요")에 이미 있는 말.
  · 킥커 "엔화가 강해졌는데"는 확정 제목 앞부분을 그대로 잘라 옮긴 것.
  · 그래픽 장치: 기울어진 저울대(시소) — ¥·₩ 두 통화를 양끝에 놓고 원화 쪽이
    무거운(=강세) 쪽으로 기울인 도형. 재정환율 구조(본문 20행)의 은유이지
    실제 환율 값을 그린 그래프가 아니다 — 데이터 계열 아님.
  · 헤드라인(확정 썸네일 문구) "엔화가 싸진 게 아니라, / 원화가 더
    세졌습니다" 무수정.

직전 네 장(/11 민트·중앙, /12 버넌엄버·우, /13 웜그레이지·좌, /16 초콜릿골드·좌)
대조: /17은 라이트 스카이시안(색상축 다름, /11 민트와도 채널차 큼)·우측정렬
(/12뿐 — /12는 다크·아이콘장치, /17은 라이트·저울대로 전혀 다름).
"""
from PIL import Image, ImageDraw, ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S, M = 1080, 72
BG    = (206, 230, 236)   # 라이트 스카이시안
INK   = (18, 42, 48)
TEAL  = (28, 110, 120)
RUST  = (176, 70, 46)
MUTED = (96, 132, 140)

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)
R = S - M

def put_r(right, top, t, fo, col):
    bb = fo.getbbox(t)
    w = bb[2] - bb[0]
    d.text((right - w - bb[0], top - bb[1]), t, font=fo, fill=col)
    return right - w, top + (bb[3] - bb[1])

# ── 1. 킥커 (확정 제목 앞부분, 무수정)
_, k_bot = put_r(R, 88, "엔화가 강해졌는데", f("Bold", 34), MUTED)

# ── 2. 주제어 — 이 장의 최대 글자
_, key_bot = put_r(R, k_bot + 22, "원/엔", f("ExtraBold", 300), TEAL)

# ── 3. 저울대(시소) 도형 — 원화 쪽이 무거운(강세) 쪽으로 기움
beam_cx, beam_cy = S - M - 300, key_bot + 130
tilt = 26
lx, ly = beam_cx - 220, beam_cy - tilt
rx, ry = beam_cx + 220, beam_cy + tilt
d.line([(lx, ly), (rx, ry)], fill=MUTED, width=10)
d.polygon([(beam_cx - 22, beam_cy + 46), (beam_cx + 22, beam_cy + 46), (beam_cx, beam_cy - 8)], fill=MUTED)
d.ellipse([lx - 46, ly - 46, lx + 46, ly + 46], fill=(255, 255, 255), outline=RUST, width=6)
d.ellipse([rx - 54, ry - 54, rx + 54, ry + 54], fill=TEAL, outline=TEAL, width=6)

yenf = f("ExtraBold", 44)
wonf = f("ExtraBold", 50)
bb = yenf.getbbox("¥")
d.text((lx - (bb[2] - bb[0]) / 2 - bb[0], ly - (bb[3] - bb[1]) / 2 - bb[1]), "¥", font=yenf, fill=RUST)
bb2 = wonf.getbbox("₩")
d.text((rx - (bb2[2] - bb2[0]) / 2 - bb2[0], ry - (bb2[3] - bb2[1]) / 2 - bb2[1]), "₩", font=wonf, fill=(255, 255, 255))
beam_bot = max(ly + 46, ry + 54)

# ── 4. 헤드라인 (「포착」 확정 썸네일 문구, 무수정) — 2줄, 주제어보다 작게
hf = f("Bold", 60)
_, h1_bot = put_r(R, beam_bot + 60, "엔화가 싸진 게 아니라,", hf, INK)
_, h2_bot = put_r(R, h1_bot + 22, "원화가 더 세졌습니다", hf, TEAL)

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/17.png")
print("saved 17.png  k_bot=%d key_bot=%d beam_bot=%d h2_bot=%d" %
      (k_bot, key_bot, beam_bot, h2_bot))
