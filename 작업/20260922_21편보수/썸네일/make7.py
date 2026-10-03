# -*- coding: utf-8 -*-
"""/7 병합·감자 썸네일 — 2026-09-24 신규 제작(「지면」).

「포착」 지침(06_썸네일문구_7.md) 그대로 구현한다 — 문구·구조 무수정.
  · 주제어 "병합"을 이 장 전체에서 가장 큰 글자로(회장 공통사항 직결).
  · 데이터 계열 없음 → 오르내리는 그래프 금지. 시점 전/후 대비형
    (2블록 + 시간 경계선)으로 그린다. 화살표 아님, 세로 경계선.
  · 좌측 블록 "지정 전 — 자유롭게 가능"(67~69행) / 우측 블록
    "지정 후 — 90거래일 금지"(71~77행). 경계선 위 배지에 "관리종목 지정".
  · 숫자(90거래일)는 블록 안 보조 숫자로만, 병합보다 작게.
  · 헤드라인(확정 썸네일 문구) "지정된 뒤엔, 이 카드가 사라집니다" 무수정.

직전 4장과 구조·색 대조(D-105 §8):
  /2 샌드(230,214,178) 좌·하단·단일수식형 / /5 버건디(56,18,26) 좌·상단·2패널(경계선 없음)
  /6 딥포레스트(20,42,35) 우·상단·숫자대비쌍(시간축 없음) / /8 쿨그레이(237,240,245) 중앙·중앙·캡슐
  → /7은 다섯째 색상축(보라)·전신 대칭 2블록+세로 경계선(넷 중 누구에게도 없는 시간축) 구조.
"""
from PIL import Image, ImageDraw, ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S, M = 1080, 72
BG     = (40, 20, 70)     # 짙은 보라 — /2·/5·/6·/8 어디에도 없는 색상축
CREAM  = (240, 233, 246)
LILAC  = (176, 158, 206)  # 보조 라벨
TEAL   = (58, 92, 98)     # 좌 패널 — "지정 전" 허용 상태
TEAL_TX= (214, 236, 236)
RED    = (176, 62, 46)    # 우 패널 — "지정 후" 금지 상태
RED_TX = (250, 226, 216)
GOLD_BADGE_BG = (240, 233, 246)
GOLD_BADGE_TX = (40, 20, 70)

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)

def cen(cx, top, t, fo, col):
    bb = fo.getbbox(t)
    w = bb[2] - bb[0]
    d.text((cx - w / 2 - bb[0], top - bb[1]), t, font=fo, fill=col)
    return top + (bb[3] - bb[1])

def cen_mid(cx, cy, t, fo, col):
    bb = fo.getbbox(t)
    w = bb[2] - bb[0]; h = bb[3] - bb[1]
    d.text((cx - w / 2 - bb[0], cy - h / 2 - bb[1]), t, font=fo, fill=col)

CX = S / 2

# ── 1. 주제어 — 이 장 전체에서 가장 큰 글자
kf = f("ExtraBold", 250)
k_bot = cen(CX, 66, "병합", kf, CREAM)

# ── 2. 부제(본문 82행 "카드" 표현) — 주제어보다 확실히 작게
sf = f("Bold", 42)
s_bot = cen(CX, k_bot + 20, "관리종목 지정 전 · 후, 같은 행위가 이렇게 갈립니다", sf, LILAC)

# ── 3. 2블록 + 세로 시간경계선
gap = 64
bw = (S - M * 2 - gap) // 2
by = s_bot + 56
bh = 300
lx0, lx1 = M, M + bw
rx0, rx1 = M + bw + gap, S - M

d.rounded_rectangle([lx0, by, lx1, by + bh], 26, fill=TEAL)
d.rounded_rectangle([rx0, by, rx1, by + bh], 26, fill=RED)

lab_f = f("Bold", 38)
main_f = f("ExtraBold", 58)
sub_f = f("Bold", 44)

# 블록마다 (라벨 + 간격14 + 본문2줄 간격10)을 블록 세로 중앙에 배치
def block(cx, label, l_col, line1, line2, t_col, sub_f2=None):
    lab_h = (lab_f.getbbox(label)[3] - lab_f.getbbox(label)[1])
    h1 = ((sub_f2 or main_f).getbbox(line1)[3] - (sub_f2 or main_f).getbbox(line1)[1])
    h2 = (main_f.getbbox(line2)[3] - main_f.getbbox(line2)[1])
    total = lab_h + 16 + h1 + 10 + h2
    top = by + (bh - total) / 2
    b1 = cen(cx, top, label, lab_f, l_col)
    b2 = cen(cx, b1 + 16, line1, sub_f2 or main_f, t_col)
    cen(cx, b2 + 10, line2, main_f, t_col)

block(lx0 + bw / 2, "지정 전", TEAL_TX, "자유롭게", "가능", CREAM)
block(rx0 + bw / 2, "지정 후", RED_TX, "90거래일", "금지", CREAM, sub_f)

# 세로 경계선(시간축) — 갭 중앙
div_x = (lx1 + rx0) / 2
d.line([(div_x, by - 18), (div_x, by + bh + 18)], fill=CREAM, width=4)

# 경계선 위 배지 — "관리종목 지정" (사건 지점)
badge_f = f("Bold", 30)
bt = "관리종목 지정"
bb = badge_f.getbbox(bt)
btw = bb[2] - bb[0]
pad_x, pad_y = 22, 14
bw_badge = btw + pad_x * 2
bh_badge = (bb[3] - bb[1]) + pad_y * 2
by_badge = by - 18 - bh_badge / 2
d.rounded_rectangle(
    [div_x - bw_badge / 2, by_badge, div_x + bw_badge / 2, by_badge + bh_badge],
    bh_badge / 2, fill=GOLD_BADGE_BG
)
cen_mid(div_x, by_badge + bh_badge / 2, bt, badge_f, GOLD_BADGE_TX)

# ── 4. 헤드라인(「포착」 확정 썸네일 문구, 무수정) — 2줄
hf = f("Bold", 66)
hy0 = by + bh + 74
h1_bot = cen(CX, hy0, "지정된 뒤엔,", hf, CREAM)
h2_bot = cen(CX, h1_bot + 20, "이 카드가 사라집니다", hf, CREAM)

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/7.png")
print("saved 7.png  k_bot=%d s_bot=%d by=%d bh_end=%d h2_bot=%d canvas=%d" %
      (k_bot, s_bot, by, by + bh, h2_bot, S))
