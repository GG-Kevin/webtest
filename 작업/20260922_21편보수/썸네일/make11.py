# -*- coding: utf-8 -*-
"""/11 VI(변동성완화장치) 썸네일 — 2026-09-24 「지면」 재제작(D-146 배정 반영).

「진행」 배정(충돌 방지): 배경 RGB(248,238,214) 아이보리-앰버 · 정렬축 좌측 ·
주제어 위치 상단. 기존 완료 5장 배경 /2(230,214,178) /5(56,18,26)
/6(20,42,35) /7(40,20,70) /8(237,240,245)과 채널차 확보.

텍스트는 전부 06_썸네일문구_11.md에 있는 표현만 쓴다 — 새로 짓지 않는다.
  · 확정 제목: "VI가 떴다고 파는 게 맞을까요" (149행 1순위, 무수정)
  · 확정 썸네일 문구: "막는 게 아니라, 늦추는 겁니다" (무수정, 2줄 줄바꿈만)
  · 킥커 "VI(변동성완화장치)": 문서 표제 자체의 표현("06_썸네일문구 — /11 VI(변동성완화장치)")
  · 캡션 "속도만 늦추는 장치": 본문 근거 8행 인용문 "VI는 방향을 바꾸는 장치가
    아니라 속도만 늦추는 장치입니다"의 부분 발췌(새 문장 아님)
  · 주제어 "VI": 제목·8행 인용문에 반복해서 나오는 그 단어. 숫자·날짜 아님.

그래픽 장치: 좌→우로 짧아지는 감속 바(장식, 데이터 아님) —
"막는 게 아니라 속도만 늦춘다"는 문구의 시각 은유. 화살표·차트 아님.
"""
from PIL import Image, ImageDraw, ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S, M = 1080, 72
BG     = (248, 238, 214)  # 아이보리-앰버 — 「진행」 배정값, 기완료 5장과 채널차 확보
INK    = (46, 34, 22)     # 짙은 커피브라운 — 밝은 배경 대비 명도차 최대화
SUBJECT= (24, 78, 70)     # 딥 틸 — 주제어 색
ACCENT = (196, 84, 40)    # 번트 오렌지 — 감속 바 첫 막대(사건 지점) 강조
MUTED  = (140, 116, 84)   # 킥커·캡션용 저채도 브라운

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)

def left(x, top, t, fo, col):
    bb = fo.getbbox(t)
    d.text((x - bb[0], top - bb[1]), t, font=fo, fill=col)
    return top + (bb[3] - bb[1])

def text_w(t, fo):
    bb = fo.getbbox(t)
    return bb[2] - bb[0]

X = M  # 좌측 정렬 기준선

# ── 1. 킥커 (문서 표제 표현 "VI(변동성완화장치)", 무수정) — 좌상단, 최상단 요소
kf = f("Bold", 36)
k_bot = left(X, 78, "VI(변동성완화장치)", kf, MUTED)

# ── 2. 주제어 "VI" — 이 장 전체에서 가장 큰 글자, 좌측정렬·상단
subj_f = f("ExtraBold", 420)
subj_bot = left(X, k_bot + 24, "VI", subj_f, SUBJECT)

# ── 3. 감속 바 그래픽 — 좌→우로 짧아지는 5개 막대(장식, 도형·데이터 아님)
bar_top = subj_bot + 56
bar_h_max = 108
n = 5
gap = 24
bw = (S - M * 2 - gap * (n - 1)) // n
for i in range(n):
    bh = int(bar_h_max * (1 - i * 0.17))
    x0 = M + i * (bw + gap)
    y1 = bar_top + bar_h_max
    y0 = y1 - bh
    d.rounded_rectangle([x0, y0, x0 + bw, y1], 12, fill=ACCENT if i == 0 else SUBJECT)
bar_bot = bar_top + bar_h_max

# 캡션 (8행 인용문 발췌, 무수정) — 좌측정렬
cap_f = f("Bold", 36)
cap_bot = left(X, bar_bot + 30, "속도만 늦추는 장치", cap_f, MUTED)

# ── 4. 헤드라인 (확정 썸네일 문구, 무수정) — 2줄, 좌측정렬, 주제어보다 확실히 작게
hf = f("Bold", 68)
hy0 = cap_bot + 52
h1_bot = left(X, hy0, "막는 게 아니라,", hf, INK)
h2_bot = left(X, h1_bot + 20, "늦추는 겁니다", hf, INK)

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/11.png")
print("saved 11.png  k_bot=%d subj_bot=%d bar_bot=%d cap_bot=%d h2_bot=%d canvas=%d" %
      (k_bot, subj_bot, bar_bot, cap_bot, h2_bot, S))
