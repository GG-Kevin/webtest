# -*- coding: utf-8 -*-
"""/6 정리매매 7거래일 — 2026-09-24 회장 반려 재제작(2차).

반려 사유(회장): 「/2, /6 모두 별로」 + 공통사항 「가장 중요한 게 가장 크고 잘 보여야지」.
「지면」 진단: 구판은 숫자 「14」가 h=425로 화면 절반을 먹었고, 이 글의 주제어
「정리매매」는 카드에 **한 번도 나오지 않았다**. 썸네일만 보고 무슨 글인지 알 수 없다.
게다가 구판 /2도 초대형 숫자 1개 구조여서 두 장이 같은 틀로 보였다(D-105 §8).

이번 판이 바꾼 것:
  · 주제어 「정리매매」를 250pt로 올려 이 장의 최대 글자로 만든다.
    출처는 「포착」 확정 제목 89행 「정리매매 하루 체결 횟수, 13회 아니라 14회입니다」.
    부제 「하루 체결 횟수」도 같은 제목의 구를 그대로 옮긴 것 — 새 문구 창작 아님.
  · 숫자 대비쌍 13↔14는 주제어보다 작은 보조 장치로 내린다(「포착」 지침의 대비형은 유지).
  · 우측정렬축 — /2(좌정렬 하단앵커)·/5(좌정렬 상단주제어)와 정렬축 자체가 다르다.
  · 배경을 딥 포레스트로 — /5 버건디(적)와 색상축이 반대, /2 웜샌드와 명도축이 반대.

무수정 유지: 헤드라인(썸네일 문구) 원문, 라벨 「계산」·「원문」, 13/14 대비 장치.
"""
from PIL import Image, ImageDraw, ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S, M = 1080, 72
BG     = (20, 42, 35)      # 딥 포레스트 — 남색 아님(G가 최대 채널)
CREAM  = (236, 233, 224)
MOSS   = (126, 152, 136)   # 부제·라벨
SLATE  = (112, 130, 120)   # 「13」 오답
STRIKE = (214, 106, 88)    # 취소선
EMER   = (74, 214, 146)    # 「14」 정답
DIV    = (48, 74, 63)

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)
R = S - M   # 우측 정렬 기준선

def put_r(right, top, t, fo, col):
    """글리프 오른끝을 right에, 윗변을 top에 맞춰 찍고 (왼끝, 아랫변)을 돌려준다."""
    bb = fo.getbbox(t)
    w = bb[2] - bb[0]
    d.text((right - w - bb[0], top - bb[1]), t, font=fo, fill=col)
    return right - w, top + (bb[3] - bb[1])

# ── 1. 주제어 — 이 장의 최대 글자
kf = f("ExtraBold", 250)
kx, k_bot = put_r(R, 108, "정리매매", kf, CREAM)

# ── 2. 부제 (확정 제목의 구, 무수정)
sf = f("Bold", 54)
_, s_bot = put_r(R, k_bot + 22, "하루 체결 횟수", sf, MOSS)

# ── 3. 구분선
div_y = s_bot + 76
d.line([(M, div_y), (R, div_y)], fill=DIV, width=3)

# ── 4. 숫자 대비쌍 13 ↔ 14 (「포착」 지침 유지) — 주제어보다 작게
f14 = f("ExtraBold", 222)
f13 = f("Bold", 152)
flab = f("Bold", 36)
TOP14 = div_y + 80
x14, bot14 = put_r(R, TOP14, "14", f14, EMER)
_, lab14_bot = put_r(R, bot14 + 14, "원문", flab, MOSS)

# 13은 14의 왼쪽에, 바닥선을 14와 맞춰 작게
bb13 = f13.getbbox("13")
h13 = bb13[3] - bb13[1]
top13 = bot14 - h13
x13, _ = put_r(x14 - 72, top13, "13", f13, SLATE)
sy = top13 + h13 // 2
d.line([(x13 - 16, sy), (x14 - 56, sy)], fill=STRIKE, width=8)
put_r(x14 - 72, bot14 + 14, "계산", flab, SLATE)

# ── 5. 헤드라인 (「포착」 확정 썸네일 문구, 무수정)
hf = f("Bold", 62)
put_r(R, 872, "계산이 아니라,", hf, CREAM)
_, h_bot = put_r(R, 872 + 82, "원문을 확인했습니다", hf, CREAM)

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/6.png")
print("saved 6.png  k_bot=%d s_bot=%d div=%d bot14=%d h_bot=%d" %
      (k_bot, s_bot, div_y, bot14, h_bot))
