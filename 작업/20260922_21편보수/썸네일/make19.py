# -*- coding: utf-8 -*-
"""/19 해외주식 양도소득세(환율) — 2026-09-24 「지면」 신규 제작(12편 배치).

「포착」 지침(06_썸네일문구_19.md) 그대로 구현 — 문구 무수정.
  · 주제어 "해외주식"을 이 장의 최대 글자로. 확정 제목("해외주식 250만원
    까지는...")에 이미 있는 말.
  · 킥커 "해외주식 250만원까지는"은 확정 제목 앞부분을 그대로 잘라 옮긴 것.
  · 그래픽 장치: 수평 점선(주가 — "그대로") 위로 계단형 선(환율 — 오름)을
    교차시킨 도형. 본문 35행(주가는 그대로인데 환율이 오르면 양도차익 발생)의
    구조를 그린 것. 실제 시세 계열이 아니라 두 상태(그대로/오름)의 대비 도형.
  · 헤드라인(확정 썸네일 문구) "주가는 그대로인데, / 세금은 환율 때문에
    달라집니다" 무수정.

직전 여섯 장 대조(색상축): /11 아이보리앰버 /12 버넌엄버 /13 웜그레이지
/16 초콜릿골드 /17 스카이시안 /18 다크올리브 → /19는 라이트 라벤더(보라,
전부 처음)·중앙정렬·계단선+점선 교차 장치(여섯 장 누구에게도 없음).
"""
from PIL import Image, ImageDraw, ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S, M = 1080, 72
BG     = (230, 222, 242)   # 라이트 라벤더 — 남색 아님(밝음, R·G·B 근접한 파스텔)
INK    = (30, 24, 46)
VIOLET = (94, 64, 150)
CORAL  = (200, 92, 60)
MUTED  = (120, 108, 140)

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)
CX = S // 2

def cen(top, t, fo, col):
    bb = fo.getbbox(t)
    w = bb[2] - bb[0]
    d.text((CX - w / 2 - bb[0], top - bb[1]), t, font=fo, fill=col)
    return top + (bb[3] - bb[1])

# ── 1. 킥커 (확정 제목 앞부분, 무수정)
k_bot = cen(88, "해외주식 250만원까지는", f("Bold", 32), MUTED)

# ── 2. 주제어 — 이 장의 최대 글자
key_bot = cen(k_bot + 26, "해외주식", f("ExtraBold", 230), INK)

# ── 3. 점선(주가·그대로) + 계단선(환율·오름) 교차 도형
dev_top = key_bot + 56
dev_h = 160
x0, x1 = M + 40, S - M - 40
flat_y = dev_top + dev_h - 30
# 점선(주가)
xx = x0
while xx < x1:
    d.line([(xx, flat_y), (min(xx + 22, x1), flat_y)], fill=MUTED, width=6)
    xx += 36
put_lab = f("Bold", 26)
d.text((x0, flat_y + 14), "주가", font=put_lab, fill=MUTED)

# 계단선(환율) — 4단 상승
steps = 4
step_w = (x1 - x0) // steps
py = dev_top + dev_h
for i in range(steps):
    sx0 = x0 + i * step_w
    sx1 = sx0 + step_w
    sy = dev_top + dev_h - 30 - (i + 1) * 34
    d.line([(sx0, py if i == 0 else prev_sy), (sx0, sy)], fill=VIOLET, width=8)
    d.line([(sx0, sy), (sx1, sy)], fill=VIOLET, width=8)
    prev_sy = sy
d.text((x1 - 70, prev_sy - 40), "환율", font=put_lab, fill=VIOLET)
dev_bot = flat_y + 46

# ── 4. 헤드라인 (「포착」 확정 썸네일 문구, 무수정) — 2줄, 주제어보다 작게
hf = f("Bold", 58)
h1_bot = cen(dev_bot + 60, "주가는 그대로인데,", hf, INK)
h2_bot = cen(h1_bot + 22, "세금은 환율 때문에 달라집니다", hf, CORAL)

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/19.png")
print("saved 19.png  k_bot=%d key_bot=%d dev_bot=%d h2_bot=%d" %
      (k_bot, key_bot, dev_bot, h2_bot))
