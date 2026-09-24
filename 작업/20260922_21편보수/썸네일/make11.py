# -*- coding: utf-8 -*-
"""/11 VI(변동성완화장치) — 2026-09-24 「지면」 신규 제작(12편 배치).

「포착」 지침(06_썸네일문구_11.md) 그대로 구현 — 문구 무수정.
  · 주제어 "VI"를 이 장 전체에서 가장 큰 글자로(회장 공통사항).
    출처: 확정 제목 "VI가 떴다고 파는 게 맞을까요"에 이미 있는 말.
  · 킥커 "변동성완화장치"는 본문 20행("국내에서는 변동성완화장치라고 부릅니다")의
    그 단어를 그대로 가져온 것. 새로 지은 설명이 아니다.
  · 그래픽 장치: 수평 막대가 왼쪽에서 오른쪽으로 짧아지는 감속 바 —
    "막는 게 아니라 속도만 늦춘다"는 문구의 은유. 화살표·차트 아님(데이터 아님, 장식).
  · 캡션 "속도만 늦추는 장치"는 본문 8행(핵심요약)의 문장을 그대로 옮김.
  · 헤드라인(확정 썸네일 문구) "막는 게 아니라, / 늦추는 겁니다" 무수정 2줄.

기완료 5장·직전 없음(이 장이 2차 배치 1번) 대조:
  /2 샌드·좌·하단주제어 /5 버건디·좌·상단주제어 /6 포레스트·우·상단주제어
  /7 보라·중앙·상단주제어 /8 쿨그레이·중앙·중앙주제어(캡슐)
  → /11은 여섯째 색상축(민트, 라이트)·중앙정렬이지만 그래픽 장치(감속 바)가
    다섯 장 어디에도 없는 형태. 배지·캡슐·패널이 아니라 막대 그라데이션.
"""
from PIL import Image, ImageDraw, ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S, M = 1080, 72
BG    = (222, 238, 220)   # 라이트 민트 — 남색 아님, 기완료 5장 어디와도 다른 색상축
INK   = (24, 40, 30)
TEAL  = (32, 110, 92)
CORAL = (196, 90, 56)
MUTED = (108, 138, 120)

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)
CX = S // 2

def cen(top, t, fo, col):
    bb = fo.getbbox(t)
    w = bb[2] - bb[0]
    d.text((CX - w / 2 - bb[0], top - bb[1]), t, font=fo, fill=col)
    return top + (bb[3] - bb[1])

# ── 1. 킥커 (본문 20행의 용어, 무수정)
k_bot = cen(150, "변동성완화장치", f("Bold", 36), MUTED)

# ── 2. 주제어 — 이 장의 최대 글자
key_bot = cen(k_bot + 26, "VI", f("ExtraBold", 380), TEAL)

# ── 3. 감속 바 그래픽 — 왼쪽에서 오른쪽으로 짧아지는 5개 막대(장식, 도형)
bar_top = key_bot + 60
bar_h_max = 96
n = 5
gap = 22
bw = (S - M * 2 - gap * (n - 1)) // n
for i in range(n):
    bh = int(bar_h_max * (1 - i * 0.16))
    x0 = M + i * (bw + gap)
    y1 = bar_top + bar_h_max
    y0 = y1 - bh
    d.rounded_rectangle([x0, y0, x0 + bw, y1], 10, fill=CORAL if i == 0 else TEAL)
bar_bot = bar_top + bar_h_max

# 캡션 (본문 8행 핵심요약 문장, 무수정)
cap_bot = cen(bar_bot + 24, "속도만 늦추는 장치", f("Bold", 34), MUTED)

# ── 4. 헤드라인 (「포착」 확정 썸네일 문구, 무수정) — 2줄, 주제어보다 확실히 작게
hf = f("Bold", 66)
h1_bot = cen(cap_bot + 60, "막는 게 아니라,", hf, INK)
h2_bot = cen(h1_bot + 22, "늦추는 겁니다", hf, INK)

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/11.png")
print("saved 11.png  k_bot=%d key_bot=%d bar_bot=%d cap_bot=%d h2_bot=%d" %
      (k_bot, key_bot, bar_bot, cap_bot, h2_bot))
