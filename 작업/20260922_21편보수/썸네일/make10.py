# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S = 1080
BG      = (214, 230, 209)   # 소프트 세이지 — 안심 톤. 직전 3편(마룬/올리브/라일락)과 다른 계열
TEXT    = (30, 46, 32)      # 짙은 포레스트블랙 — 배경과 명도차 크게
SEG1    = (44, 96, 66)      # 진 포레스트그린 — 첫 칸(705건, 62.7%)
SEG2    = (198, 156, 90)    # 머스터드탠 — 둘째 칸(296건, 26.3%)
SEG3    = (176, 78, 60)     # 테라코타레드 — 셋째 칸(116건, 10.3%, 퇴출로 가는 칸)

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)

MARGIN = 90
LEFT = MARGIN

def left_text(x, top, t, fo, col):
    bb = fo.getbbox(t)
    d.text((x - bb[0], top - bb[1]), t, font=fo, fill=col)
    return top + (bb[3] - bb[1]), bb[2]-bb[0]

# 1. 헤드라인 1행(핵심어+조사) — 이 장 최대 글자
hf = f("ExtraBold", 210)
y = 172  # 전체 콘텐츠(737px) 상하 여백 균형 — (1080-737)/2 ≈ 171
y, w1 = left_text(LEFT, y, "63%는", hf, TEXT)

# 2. 헤드라인 2행(나머지) — 확정 문구 원문 그대로
h2f = f("Bold", 96)
y2, w2 = left_text(LEFT, y + 22, "장부 정리 때문입니다", h2f, TEXT)
y = y2

# 3. 세 칸 — 본문 705:296:116(62.7%:26.3%:10.3%) 비례 3박스
bar_top = y + 70
bar_h = 160
gap = 18
bar_w = S - 2*MARGIN
usable = bar_w - 2*gap
c1, c2, c3 = 705, 296, 116
tot = c1+c2+c3
w_seg1 = usable * c1 / tot
w_seg2 = usable * c2 / tot
w_seg3 = usable * c3 / tot

x = LEFT
r = 22
d.rounded_rectangle([x, bar_top, x+w_seg1, bar_top+bar_h], r, fill=SEG1)
x += w_seg1 + gap
d.rounded_rectangle([x, bar_top, x+w_seg2, bar_top+bar_h], r, fill=SEG2)
x += w_seg2 + gap
d.rounded_rectangle([x, bar_top, x+w_seg3, bar_top+bar_h], r, fill=SEG3)

bar_bottom = bar_top + bar_h

# 4. 캡션 — 확정 문구 원문
capf = f("Bold", 78)
cap_top = bar_bottom + 66
cy, cw = left_text(LEFT, cap_top, "회사가 무너진 게", capf, TEXT)
cy2, cw2 = left_text(LEFT, cy + 14, "아닙니다", capf, TEXT)

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/10.png")
print("w1=%d w2=%d bar_top=%d bar_bottom=%d cap_bottom=%d canvas=%d" % (w1, w2, bar_top, bar_bottom, cy2, S))
