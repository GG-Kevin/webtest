# -*- coding: utf-8 -*-
"""/21 애프터마켓 오후 8시까지 — 2026-09-24 「지면」 신규 제작(12편 배치).

「포착」 지침(06_썸네일문구_21.md) 그대로 구현 — 문구 무수정.
  · 주제어 "애프터마켓"을 이 장의 최대 글자로. 확정 제목("애프터마켓 오후
    8시까지...")에 이미 있는 말.
  · 킥커 "애프터마켓 오후 8시까지"는 확정 제목 앞부분을 그대로 잘라 옮긴 것.
  · 그래픽 장치: 달(초승달) 아이콘 + 위/아래 화살표 쌍 — 본문 32행("애프터
    마켓 시간대에도 이론적으로 상한가·하한가가 발생할 수 있습니다")을 밤 시간대
    + 극단적 등락 가능성으로 형상화한 것. 꺾은선 아님(단일 사실의 아이콘화).
  · 헤드라인(확정 썸네일 문구) "저녁에도, / 상한가·하한가가 뜰 수 있습니다"
    무수정.

배경을 니어블랙으로 잡은 것 자체가 이 글의 소재(저녁 시간대 거래)를 그대로
반영한다 — 남색(navy)이 아니라 R=G와 가까운 무채색 다크(22,22,26)다.
직전 여덟 장 대조: /21은 유일한 "니어블랙" 톤·중앙정렬·달+화살표쌍 장치.
"""
from PIL import Image, ImageDraw, ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S, M = 1080, 72
BG    = (22, 22, 26)     # 니어블랙 — R≈G≈B, 남색(navy) 아님
CREAM = (232, 232, 236)
BLUE  = (90, 160, 220)
RED   = (214, 96, 76)
MUTED = (140, 140, 150)

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)
CX = S // 2

def cen(top, t, fo, col):
    bb = fo.getbbox(t)
    w = bb[2] - bb[0]
    d.text((CX - w / 2 - bb[0], top - bb[1]), t, font=fo, fill=col)
    return top + (bb[3] - bb[1])

# ── 1. 킥커 (확정 제목 앞부분, 무수정)
k_bot = cen(90, "애프터마켓 오후 8시까지", f("Bold", 32), MUTED)

# ── 2. 주제어 — 이 장의 최대 글자
key_bot = cen(k_bot + 26, "애프터마켓", f("ExtraBold", 200), CREAM)

# ── 3. 달 아이콘(도형) + 위/아래 화살표 쌍
icy = key_bot + 130
moon_r = 64
mx = CX
d.ellipse([mx - moon_r, icy - moon_r, mx + moon_r, icy + moon_r], fill=CREAM)
d.ellipse([mx - moon_r + 30, icy - moon_r - 8, mx + moon_r + 30, icy + moon_r - 8], fill=BG)

ax_up = CX - 190
d.line([(ax_up, icy + 50), (ax_up, icy - 50)], fill=BLUE, width=12)
d.polygon([(ax_up, icy - 78), (ax_up - 26, icy - 34), (ax_up + 26, icy - 34)], fill=BLUE)
put_lab = f("Bold", 28)
bb = put_lab.getbbox("상한가")
d.text((ax_up - (bb[2] - bb[0]) / 2 - bb[0], icy + 66 - bb[1]), "상한가", font=put_lab, fill=BLUE)

ax_dn = CX + 190
d.line([(ax_dn, icy - 50), (ax_dn, icy + 50)], fill=RED, width=12)
d.polygon([(ax_dn, icy + 78), (ax_dn - 26, icy + 34), (ax_dn + 26, icy + 34)], fill=RED)
bb2 = put_lab.getbbox("하한가")
d.text((ax_dn - (bb2[2] - bb2[0]) / 2 - bb2[0], icy + 92 - bb2[1]), "하한가", font=put_lab, fill=RED)

dev_bot = icy + 92 + 34

# ── 4. 헤드라인 (「포착」 확정 썸네일 문구, 무수정) — 2줄, 주제어보다 작게
hf = f("Bold", 60)
h1_bot = cen(dev_bot + 64, "저녁에도,", hf, CREAM)
h2_bot = cen(h1_bot + 22, "상한가·하한가가 뜰 수 있습니다", hf, CREAM)

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/21.png")
print("saved 21.png  k_bot=%d key_bot=%d dev_bot=%d h2_bot=%d" %
      (k_bot, key_bot, dev_bot, h2_bot))
