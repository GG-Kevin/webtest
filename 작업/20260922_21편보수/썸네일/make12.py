# -*- coding: utf-8 -*-
"""/12 단기과열종목 지정 — 2026-09-24 「지면」 신규 제작(12편 배치).

「포착」 지침(06_썸네일문구_12.md) 그대로 구현 — 문구 무수정.
  · 주제어 "단기과열종목"을 이 장의 최대 글자로. 확정 제목("단기과열종목
    지정됐는데...")에 이미 있는 말.
  · 킥커 "단기과열종목 지정"은 확정 제목의 앞부분을 그대로 잘라 옮긴 것.
  · 그래픽 장치: 상승 화살표가 "식힌다"는 원형 표시를 뚫고 올라가는 역설 아이콘
    (본문 4행 — 지정 소식이 오히려 화제 신호로 읽혀 매수세가 몰린다는 내용의 시각화).
    데이터 계열 아님 — 오르내리는 값이 없으므로 꺾은선 대신 단일 아이콘만 쓴다.
  · 헤드라인(확정 썸네일 문구) "식히려던 신호가, / 오히려 관심 신호로 읽힙니다" 무수정.

직전 장(/11 민트·라이트·중앙) 대조: /12는 다크 버넌엄버(색상축 전혀 다름)·
우측정렬(민트 장은 중앙)·아이콘 장치가 감속 바(막대)가 아니라 화살표+원.
기완료 5장과도 색상·정렬·장치 겹치지 않음(우측정렬은 /6뿐이나 /6은 포레스트·
숫자대비쌍이고 이번 장은 버넌엄버·화살표아이콘으로 다르다).
"""
from PIL import Image, ImageDraw, ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S, M = 1080, 72
BG     = (54, 28, 16)      # 다크 버넌엄버 — 남색 아님(R이 최대 채널, 웜)
CREAM  = (244, 230, 214)
ORANGE = (224, 120, 58)
MUTED  = (150, 110, 80)
RING   = (150, 110, 80)

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)
R = S - M

def put_r(right, top, t, fo, col):
    bb = fo.getbbox(t)
    w = bb[2] - bb[0]
    d.text((right - w - bb[0], top - bb[1]), t, font=fo, fill=col)
    return right - w, top + (bb[3] - bb[1])

# ── 1. 킥커 (확정 제목 앞부분, 무수정)
_, k_bot = put_r(R, 90, "단기과열종목 지정", f("Bold", 36), MUTED)

# ── 2. 주제어 — 이 장의 최대 글자
_, key_bot = put_r(R, k_bot + 24, "단기과열종목", f("ExtraBold", 160), ORANGE)

# ── 3. 역설 아이콘 — "식힌다"는 원(도형) + 그걸 뚫는 상승 화살표(도형)
icon_top = key_bot + 56
icon_h = 150
icon_cx = R - 210
icon_cy = icon_top + icon_h // 2
d.ellipse([icon_cx - 75, icon_cy - 75, icon_cx + 75, icon_cy + 75], outline=RING, width=6)
# 상승 화살표(원을 관통)
ax0, ay0 = icon_cx - 90, icon_cy + 60
ax1, ay1 = icon_cx + 95, icon_cy - 70
d.line([(ax0, ay0), (ax1, ay1)], fill=CREAM, width=14)
d.polygon([(ax1, ay1), (ax1 - 42, ay1 + 6), (ax1 - 6, ay1 + 42)], fill=CREAM)
icon_bot = icon_top + icon_h

# 라벨(본문 4행 표현 요약 — 새 문구 아님, 본문 그대로의 "화제 신호" 인용)
_, lab_bot = put_r(R, icon_bot + 20, "\"화제 신호\"로 읽힘", f("Bold", 30), MUTED)

# ── 4. 헤드라인 (「포착」 확정 썸네일 문구, 무수정) — 2줄, 주제어보다 작게
hf = f("Bold", 60)
_, h1_bot = put_r(R, lab_bot + 56, "식히려던 신호가,", hf, CREAM)
_, h2_bot = put_r(R, h1_bot + 22, "오히려 관심 신호로 읽힙니다", hf, ORANGE)

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/12.png")
print("saved 12.png  k_bot=%d key_bot=%d icon_bot=%d lab_bot=%d h2_bot=%d" %
      (k_bot, key_bot, icon_bot, lab_bot, h2_bot))
