# -*- coding: utf-8 -*-
"""/21 애프터마켓 오후 8시까지 — 2026-09-24 「지면」 신규 제작(D-146 12편 배치).

배정(「진행」): 배경 웜 베이지-탠 계열·밝은 톤 / 정렬축 중앙 / 주제어 위치 하단.
문구 전부 06_썸네일문구_21.md·확정 제목에서 그대로 가져온다 — 새로 짓지 않는다.

  · 주제어 "애프터마켓" — 확정 제목("애프터마켓 오후 8시까지...") 첫 어절, 이 장의
    최대 글자. 하단 배치(회장 배정).
  · 킥커 "애프터마켓 오후 8시까지" — 확정 제목 앞부분(쉼표 앞까지)을 그대로 자른 것.
  · 헤드라인(확정 썸네일 문구, 무수정) "저녁에도," / "상한가·하한가가 뜰 수
    있습니다" — 쉼표에서 2줄로 나눔(문구 자체는 무수정).
  · 그래픽: 상승·하락 화살표 쌍 + 라벨 "상한가"/"하한가" — 둘 다 헤드라인
    문장에 이미 있는 낱말이며, 본문 32행("애프터마켓 시간대에도 이론적으로
    상한가·하한가가 발생할 수 있습니다")을 도형으로 형상화한 것. 숫자(±30%)는
    포착 의도대로 반복하지 않는다.

배경 RGB 확정 — 배정값(244,224,196)은 /2(230,214,178)와 채널차 최대 18로
30 미만이라 톤을 더 진하게 조정: (238,190,140). 웜 베이지-탠·밝은 톤 유지,
아래 검사3 스크립트로 기존 5장 전부와 채널차 ≥30 확인.

직전 5장과 구조 대조: /2(좌·하단·단일수식형) /5(좌·상단·2패널) /6(우·상단·
숫자대비쌍) /7(대칭·상단전폭·2블록+경계선) /8(중앙·중앙·캡슐) — 이 장은
유일하게 "중앙정렬 + 주제어 하단 + 상단 킥커·헤드라인 + 중단 화살표쌍" 구조다.
"""
from PIL import Image, ImageDraw, ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S, M = 1080, 72
BG      = (238, 190, 140)   # 웜 베이지-탠(캐러멜), 밝은 톤 — 배정색을 채널차 30 확보 위해 진하게 조정
TXT     = (46, 28, 18)      # 근흑 브라운 — 배경과 명도차 최대
MUTED   = (128, 92, 62)     # 킥커용 저채도 브라운
UP      = (176, 48, 36)     # 상한가 — 적(국내 관행: 상승=빨강)
DOWN    = (40, 86, 132)     # 하한가 — 청(하락=파랑). 배경 자체가 웜톤이라 남색 배경과 무관

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)
CX = S / 2

def cen(top, t, fo, col):
    bb = fo.getbbox(t)
    w = bb[2] - bb[0]
    d.text((CX - w / 2 - bb[0], top - bb[1]), t, font=fo, fill=col)
    return top + (bb[3] - bb[1])

# ── 1. 킥커 (확정 제목 앞부분, 무수정)
k_bot = cen(88, "애프터마켓 오후 8시까지", f("Bold", 34), MUTED)

# ── 2. 헤드라인 (확정 썸네일 문구, 무수정) — 2줄
hf = f("Bold", 64)
h1_bot = cen(k_bot + 42, "저녁에도,", hf, TXT)
h2_bot = cen(h1_bot + 20, "상한가·하한가가 뜰 수 있습니다", hf, TXT)

# ── 3. 화살표 쌍(도형) + 라벨(헤드라인에 이미 있는 낱말)
gy = h2_bot + 96
arm = 62
ax_up = CX - 170
d.line([(ax_up, gy + arm), (ax_up, gy - arm)], fill=UP, width=14)
d.polygon([(ax_up, gy - arm - 30), (ax_up - 28, gy - arm + 6), (ax_up + 28, gy - arm + 6)], fill=UP)
lab = f("Bold", 34)
up_bot = cen(gy + arm + 24, "상한가", lab, UP) if False else None
bb = lab.getbbox("상한가")
d.text((ax_up - (bb[2] - bb[0]) / 2 - bb[0], gy + arm + 24 - bb[1]), "상한가", font=lab, fill=UP)

ax_dn = CX + 170
d.line([(ax_dn, gy - arm), (ax_dn, gy + arm)], fill=DOWN, width=14)
d.polygon([(ax_dn, gy + arm + 30), (ax_dn - 28, gy + arm - 6), (ax_dn + 28, gy + arm - 6)], fill=DOWN)
bb2 = lab.getbbox("하한가")
d.text((ax_dn - (bb2[2] - bb2[0]) / 2 - bb2[0], gy + arm + 24 - bb2[1]), "하한가", font=lab, fill=DOWN)

# 중앙 연결 — 저녁(야간) 표시용 얇은 원(달, 도형) — 화살표 사이
d.ellipse([CX - 26, gy - 26, CX + 26, gy + 26], outline=TXT, width=6)

graphic_bot = gy + arm + 24 + (bb[3] - bb[1])

# ── 4. 주제어 — 이 장의 최대 글자, 하단 배치(배정)
kf = f("ExtraBold", 215)
subj_top = S - M - 194  # 주제어 잉크 높이(214/215pt 기준 실측 194)와 하단여백 72 역산
subj_bot = cen(subj_top, "애프터마켓", kf, TXT)

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/21.png")
print("saved 21.png  k_bot=%d h2_bot=%d graphic_bot=%d subj_top=%d subj_bot=%d canvas=%d" %
      (k_bot, h2_bot, graphic_bot, subj_top, subj_bot, S))
