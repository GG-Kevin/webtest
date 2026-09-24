# -*- coding: utf-8 -*-
"""/23 관리종목 36개(거래소 예상 50개 vs 실제 추산 150개) 썸네일 — 2026-09-24 「지면」.

「포착」 지침(06_썸네일문구_23.md) 그대로 구현한다 — 문구·구조 무수정.
  · 헤드라인(확정 썸네일 문구) "거래소 예상 50개, 실제 추산은 150개입니다"를
    쉼표 기준 2줄로 줄바꿈만 했다. 문구 자체는 무수정.
  · 데이터 계열 없음(전망치 두 점) → 오르내리는 그래프 금지. "두 숫자를
    나란히 놓고 대비하는 장치만 쓴다"(포착 지침 원문) → 2블록 비교(막대/선 아님).
  · 주제어 "관리종목"(확정 제목 "관리종목 36개, 2027년 1월엔 더 늘어납니다"의
    첫 단어)을 이 장 전체에서 가장 큰 글자로(회장 공통사항 직결).
  · 캡션 "당초 예상의 3배"는 06_썸네일문구_23.md의 [본문 근거]가 본문 92행에서
    직접 인용한 표현 그대로 — 「지면」이 새로 지은 문장이 아니다.

배정(「진행」, 충돌 방지):
  배경 페일 스카이-틸 계열(밝은 톤) · 정렬축 우측 · 주제어 위치 하단.
  기존 5장(/2 /5 /6 /7 /8)과 채널차 확보 위해 (206,231,236)에서
  (176,218,226)으로 더 진하게 조정 — /8 쿨그레이(237,240,245)와의
  채널차가 31로 30 턱걸이였던 문제를 61로 확보.

make7.py의 좌표·레이아웃 함수는 복사하지 않았다 — 우측 정렬 비대칭
2블록 + 하단 주제어는 이 장에서 새로 짠 구조다.
"""
from PIL import Image, ImageDraw, ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S, M = 1080, 72
RIGHT = S - M  # 1008 — 정렬축(우측) 기준선

BG          = (176, 218, 226)   # 페일 스카이-틸, 밝은 톤
TEXT_DARK   = (14, 40, 48)      # 헤드라인·주제어·패널1 텍스트 — 배경 대비 큼
MUTED       = (86, 118, 126)    # 패널1 라벨(거래소 예상)
ACCENT_RUST = (176, 64, 28)     # 패널2 배경·캡션 — 경고색
PEACH       = (240, 214, 198)   # 패널2 라벨(실제 추산)
CREAM       = (250, 248, 244)   # 패널1 배경 / 패널2 숫자 텍스트

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)

def right(x_right, top, t, fo, col):
    """오른쪽 끝 x_right에 텍스트 우측을 맞춰 그린다. 아래쪽 y 좌표를 반환."""
    bb = fo.getbbox(t)
    w = bb[2] - bb[0]
    d.text((x_right - w - bb[0], top - bb[1]), t, font=fo, fill=col)
    return top + (bb[3] - bb[1])

def right_mid(x_right, cy, t, fo, col):
    bb = fo.getbbox(t)
    w = bb[2] - bb[0]; h = bb[3] - bb[1]
    d.text((x_right - w - bb[0], cy - h / 2 - bb[1]), t, font=fo, fill=col)
    return w

# ── 1. 헤드라인(확정 썸네일 문구, 쉼표에서 2줄 줄바꿈만) — 우측 정렬
hf = f("Bold", 58)
h1_bot = right(RIGHT, M, "거래소 예상 50개,", hf, TEXT_DARK)
h2_bot = right(RIGHT, h1_bot + 18, "실제 추산은 150개입니다", hf, TEXT_DARK)

# ── 2. 2블록 비교 — 패널1(거래소 예상/50개, 무채) vs 패널2(실제 추산/150개, 경고색)
lab_f = f("Bold", 36)
num1_f = f("ExtraBold", 60)
num2_f = f("ExtraBold", 92)
pad_x, pad_y, gap_in = 28, 24, 10

def panel_size(label, number, lab_f, num_f):
    lb = lab_f.getbbox(label); nb = num_f.getbbox(number)
    lw, lh = lb[2] - lb[0], lb[3] - lb[1]
    nw, nh = nb[2] - nb[0], nb[3] - nb[1]
    w = max(lw, nw) + pad_x * 2
    h = lh + gap_in + nh + pad_y * 2
    return w, h, lh, nh

w1, h1, lh1, nh1 = panel_size("거래소 예상", "50개", lab_f, num1_f)
w2, h2, lh2, nh2 = panel_size("실제 추산", "150개", lab_f, num2_f)
ph = max(h1, h2)
pgap = 28
group_w = w1 + pgap + w2

blocks_top = h2_bot + 66
p2_x0 = RIGHT - w2
p2_x1 = RIGHT
p1_x1 = p2_x0 - pgap
p1_x0 = p1_x1 - w1

d.rounded_rectangle([p1_x0, blocks_top, p1_x1, blocks_top + ph], 22, fill=CREAM,
                     outline=TEXT_DARK, width=3)
d.rounded_rectangle([p2_x0, blocks_top, p2_x1, blocks_top + ph], 22, fill=ACCENT_RUST)

def center_text(cx, top, t, fo, col):
    bb = fo.getbbox(t)
    w = bb[2] - bb[0]
    d.text((cx - w / 2 - bb[0], top - bb[1]), t, font=fo, fill=col)
    return top + (bb[3] - bb[1])

c1 = (p1_x0 + p1_x1) / 2
top1 = blocks_top + (ph - (lh1 + gap_in + nh1)) / 2
b = center_text(c1, top1, "거래소 예상", lab_f, MUTED)
center_text(c1, b + gap_in, "50개", num1_f, TEXT_DARK)

c2 = (p2_x0 + p2_x1) / 2
top2 = blocks_top + (ph - (lh2 + gap_in + nh2)) / 2
b = center_text(c2, top2, "실제 추산", lab_f, PEACH)
center_text(c2, b + gap_in, "150개", num2_f, CREAM)

blocks_bot = blocks_top + ph

# ── 3. 캡션(본문 92행 직접 인용, 포착 문서에 이미 인용돼 있는 표현) — 우측 정렬
cap_f = f("Bold", 34)
cap_bot = right(RIGHT, blocks_bot + 34, "당초 예상의 3배", cap_f, ACCENT_RUST)

# ── 4. 주제어 "관리종목" — 이 장 전체에서 가장 큰 글자, 하단·우측 정렬
kf = f("ExtraBold", 250)
kb = kf.getbbox("관리종목")
k_h = kb[3] - kb[1]
bottom_margin = 64
k_top = S - bottom_margin - k_h
right(RIGHT, k_top, "관리종목", kf, TEXT_DARK)

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/23.png")
print("saved 23.png  h2_bot=%d blocks_top=%d blocks_bot=%d cap_bot=%d k_top=%d k_h=%d canvas=%d"
      % (h2_bot, blocks_top, blocks_bot, cap_bot, k_top, k_h, S))
