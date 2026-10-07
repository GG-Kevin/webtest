# -*- coding: utf-8 -*-
"""/8 근로장려금 반기신청 — 2026-09-24 재제작.

구판 문제(「지면」 진단): 이 장의 최대 글자가 날짜 스탬프 「2027.03」(h=97)이었고
주제어 「반기신청」은 헤드라인 안 h=88에 머물렀다. 날짜는 주제어를 대신하지 못한다(사장 §2).
게다가 스탬프가 원형 링과 어긋나게 겹쳐 있어 링이 숫자를 가로지르고,
상단 절반이 장식 하나로 비어 있었다 — 딱 봤을 때 읽히지 않는 구성이다.

이번 판이 바꾼 것 — 배치와 크기만. 문구는 한 글자도 건드리지 않았다(사장 §3).
  · 주제어 「반기신청」을 250pt로 올려 이 장의 최대 글자로 만든다.
    출처는 확정 제목 「근로장려금 반기신청 마감, 지금은 정기신청만 남았습니다」와
    확정 썸네일 문구 「다음 반기신청은 2027년 3월입니다」에 이미 있는 말.
  · 의미 없는 원형 링과 기울어진 스탬프를 버린다. 날짜는 헤드라인 안에서만 말한다.
  · 중앙정렬축 — /2·/5(좌정렬)·/6(우정렬) 어느 것과도 정렬축이 다르다.

무수정 유지: 킥커 「근로장려금」, 헤드라인 2줄, 캡슐 「지금은 정기신청만 남았습니다」,
배경 쿨 그레이·딥 블루 계열.
"""
from PIL import Image, ImageDraw, ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S, M = 1080, 72
BG    = (237, 240, 245)
INK   = (26, 32, 44)
BLUE  = (37, 99, 163)
MUTED = (122, 146, 176)

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)
CX = S // 2

def put_c(top, t, fo, col):
    bb = fo.getbbox(t)
    w = bb[2] - bb[0]
    d.text((CX - w / 2 - bb[0], top - bb[1]), t, font=fo, fill=col)
    return top + (bb[3] - bb[1])

def put_c_segs(top, segs, fo):
    """[(글자, 색)] 을 한 줄로 중앙정렬. 문구는 이어붙이기만 하고 바꾸지 않는다."""
    total = sum(fo.getbbox(t)[2] - fo.getbbox(t)[0] for t, _ in segs)
    x = CX - total / 2
    bot = top
    for t, col in segs:
        bb = fo.getbbox(t)
        d.text((x - bb[0], top - bb[1]), t, font=fo, fill=col)
        x += bb[2] - bb[0]
        bot = max(bot, top + (bb[3] - bb[1]))
    return bot

# ── 1. 킥커 (확정 제목 첫 단어, 무수정)
kick_bot = put_c(182, "근로장려금", f("Bold", 46), MUTED)

# ── 2. 주제어 — 이 장의 최대 글자
key_bot = put_c(256, "반기신청", f("ExtraBold", 250), BLUE)

# ── 3. 구분선
div_y = key_bot + 56
d.rectangle([CX - 96, div_y, CX + 96, div_y + 7], fill=BLUE)

# ── 4. 헤드라인 (「포착」 확정 썸네일 문구, 무수정)
hf = f("Bold", 74)
h1_bot = put_c(div_y + 62, "다음 반기신청은", hf, INK)
h2_bot = put_c_segs(h1_bot + 34, [("2027년 3월", BLUE), ("입니다", INK)], hf)

# ── 5. 캡슐 (기존 승인 문구, 무수정)
cf = f("Bold", 34)
cap = "지금은 정기신청만 남았습니다"
cb = cf.getbbox(cap)
cw, ch = cb[2] - cb[0], cb[3] - cb[1]
cap_top = h2_bot + 62
d.rounded_rectangle([CX - cw / 2 - 34, cap_top - 20, CX + cw / 2 + 34, cap_top + ch + 20],
                    (ch + 40) // 2, fill=BLUE)
d.text((CX - cw / 2 - cb[0], cap_top - cb[1]), cap, font=cf, fill=(255, 255, 255))

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/8.png")
print("saved 8.png  kick_bot=%d key_bot=%d div=%d h2_bot=%d cap_bot=%d" %
      (kick_bot, key_bot, div_y, h2_bot, cap_top + ch + 20))
