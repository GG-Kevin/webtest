# -*- coding: utf-8 -*-
"""/13 형식적 상장폐지 vs 실질심사(가처분) — 2026-09-24 「지면」 신규 제작(12편 배치).

「포착」 지침(06_썸네일문구_13.md) 그대로 구현 — 문구 무수정.
  · 주제어 "상장폐지"를 이 장의 최대 글자로. 확정 제목("상장폐지 사유,
    숫자가 재는 것과...")에 이미 있는 말.
  · 킥커 "상장폐지 사유"는 확정 제목 앞부분을 그대로 잘라 옮긴 것.
  · 그래픽 장치: 「포착」 문서 [데이터 계열 판정]이 "오르내리는 그래프 금지,
    85 중 2를 강조하는 단순 비율 표시만"이라고 명시했다 — 그 지침대로
    두 막대(85건·2건)를 길이 비율 그대로 나란히 놓는다. 꺾은선·추세선 없음.
  · 헤드라인(확정 썸네일 문구) "가처분 85건 중, / 인용된 건 2건입니다" 무수정.

직전 두 장(/11 민트·중앙·감속바, /12 버넌엄버·우·화살표아이콘) 대조: /13은
웜 그레이지(색상축 무채색에 가까움)·좌측정렬·막대비율 장치로 셋 다 다르다.
"""
from PIL import Image, ImageDraw, ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S, M = 1080, 72
BG    = (236, 227, 214)   # 웜 그레이지 — /8 쿨그레이(237,240,245)와 색상축 다름(웜 vs 쿨)
INK   = (34, 28, 22)
RUST  = (150, 58, 40)
MUTED = (120, 108, 92)

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)

def put(x, top, t, fo, col):
    bb = fo.getbbox(t)
    d.text((x - bb[0], top - bb[1]), t, font=fo, fill=col)
    return x + (bb[2] - bb[0]), top + (bb[3] - bb[1])

# ── 1. 킥커 (확정 제목 앞부분, 무수정)
_, k_bot = put(M, 90, "상장폐지 사유", f("Bold", 36), MUTED)

# ── 2. 주제어 — 이 장의 최대 글자
_, key_bot = put(M, k_bot + 24, "상장폐지", f("ExtraBold", 250), INK)

# ── 3. 막대 비율 장치 — 85건 vs 2건, 길이 비율 그대로(꺾은선 아님)
bar_top = key_bot + 64
bar_h = 54
max_w = S - M * 2
w85 = max_w
w2 = int(max_w * 2 / 85)

d.rounded_rectangle([M, bar_top, M + w85, bar_top + bar_h], 12, fill=MUTED)
put(M + 20, bar_top + 10, "가처분 85건", f("Bold", 32), (250, 246, 240))

bar2_top = bar_top + bar_h + 20
d.rounded_rectangle([M, bar2_top, M + max(w2, 60), bar2_top + bar_h], 12, fill=RUST)
put(M + max(w2, 60) + 20, bar2_top + 8, "인용 2건", f("Bold", 32), RUST)
bars_bot = bar2_top + bar_h

# ── 4. 헤드라인 (「포착」 확정 썸네일 문구, 무수정) — 2줄, 주제어보다 작게
hf = f("Bold", 62)
_, h1_bot = put(M, bars_bot + 66, "가처분 85건 중,", hf, INK)
x = M
for seg, col in [("인용된 건 ", INK), ("2건", RUST), ("입니다", INK)]:
    x, h2_bot = put(x, h1_bot + 24, seg, hf, col)

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/13.png")
print("saved 13.png  k_bot=%d key_bot=%d bars_bot=%d h2_bot=%d w2=%d" %
      (k_bot, key_bot, bars_bot, h2_bot, w2))
