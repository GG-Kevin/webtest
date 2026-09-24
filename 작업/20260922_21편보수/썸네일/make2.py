# -*- coding: utf-8 -*-
"""/2 동전주 상장폐지 — 2026-09-24 회장 반려 재제작(2차).

반려 사유(회장): 「/2, /6 모두 별로」 + 공통사항 「가장 중요한 게 가장 크고 잘 보여야지」.
「지면」 진단: 구판은 이 장의 최대 글자가 숫자 「46」(h=230)이었고,
이 글이 무슨 글인지 말해주는 주제어 「동전주 상장폐지」는 32pt 킥커(h=24)였다.
비율 0.10. 숫자는 주제어를 대신하지 못한다(사장 §2).

이번 판이 바꾼 것 — 배치와 크기만. 문구는 한 글자도 건드리지 않았다(사장 §3).
  · 주제어 「동전주 / 상장폐지」를 250pt 2줄로 올려 이 장의 최대 글자로 만든다
  · 숫자 산식 「36+10=46」은 주제어보다 작은 보조 요소로 내린다
  · /5(주제어 상단 → 헤드라인 → 2패널 하단)와 상하가 반대인 하단 앵커형으로
    배치해 나란히 놓았을 때 같은 틀로 보이지 않게 한다

무수정 유지: 킥커·헤드라인·산식·라벨 문구 원문, 배경 RGB(230,214,178),
테라코타(178,61,33)·다크(26,23,21)·뮤트(120,112,100).
"""
from PIL import Image, ImageDraw, ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S, M = 1080, 72
BG    = (230, 214, 178)
DARK  = (26, 23, 21)
MUTED = (120, 112, 100)
TERRA = (178, 61, 33)

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)

def put(x, top, t, fo, col):
    """글리프 윗변을 top에 맞춰 찍고 (오른쪽끝, 아랫변)을 돌려준다."""
    bb = fo.getbbox(t)
    d.text((x - bb[0], top - bb[1]), t, font=fo, fill=col)
    return x + (bb[2] - bb[0]), top + (bb[3] - bb[1])

# ── 1. 헤드라인 (「포착」 확정 썸네일 문구, 무수정) — 상단, 중간 크기
hf = f("Bold", 62)
_, b = put(M, 96, "미달된 날이 아니라,", hf, DARK)
x = M
for seg, col in [("채운 날", TERRA), ("을 셉니다", DARK)]:
    x, b = put(x, 182, seg, hf, col)

# ── 2. 산식 (본문 11~12행 「36 더하기 10은 46」, 무수정) — 주제어보다 작게
d.rectangle([M, 262, M + 168, 268], fill=TERRA)

eqf = f("Bold", 84)
eqb = f("ExtraBold", 84)
lf  = f("Regular", 28)
EQ_TOP = 300
x = M
anchors = {}
for seg, fo, col in [("36", eqf, DARK), ("+", eqf, MUTED), ("10", eqf, DARK),
                     ("=", eqf, MUTED), ("46", eqb, TERRA), ("번째 거래일", eqf, DARK)]:
    anchors[seg] = x
    x, eq_bot = put(x, EQ_TOP, seg, fo, col)
    x += 20

# ── 3. 라벨 (기존 승인 문구 3개, 무수정 — 산식의 해당 항 아래로 재배치만)
lab_bot = eq_bot
for seg, lab in [("36", "경과일수"), ("10", "연속 필요"), ("46", "46번째 거래일")]:
    _, lab_bot = put(anchors[seg], eq_bot + 24, lab, lf, MUTED)

# ── 4. 주제어 — 이 장의 최대 글자. 하단 앵커 2줄
kf = f("ExtraBold", 250)
_, k1_bot = put(M, 524, "동전주", kf, DARK)
_, k2_bot = put(M, 524 + 252, "상장폐지", kf, TERRA)

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/2.png")
print("saved 2.png  headline_bot=%d eq_bot=%d lab_bot=%d k2_bot=%d" %
      (b, eq_bot, lab_bot, k2_bot))
