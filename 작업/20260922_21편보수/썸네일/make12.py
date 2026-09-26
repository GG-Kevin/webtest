# -*- coding: utf-8 -*-
"""/12 단기과열종목 지정 — 2026-09-24 「지면」 재제작(D-146 12편 동시 배정).

「진행」 배정값: 배경 딥 틸(어두운 톤) · 정렬축 우측 · 주제어 위치 하단.
배정 원안 RGB(18,48,42)는 기완료 `/6`(20,42,35)과 채널차 최대 7(≪30) —
검사3 기준(06_지면_전건판정_20260924.md, max채널차≥30) 미달이라 「지면」이
같은 "딥 틸 계열·어두운 톤" 안에서 블루 쪽으로 옮겨 RGB(8,52,72)로 조정했다
(정방형 외 전부 자율 — 회장 2026-09-23 지시, D-105 폐기).

「포착」 지침(06_썸네일문구_12.md) 그대로 구현 — 문구 무수정.
  · 주제어 "단기과열종목"— 확정 제목 앞부분 그대로(새로 짓지 않음), 이 장 최대 글자.
  · 킥커 "단기과열종목 지정"— 확정 제목의 앞부분 그대로.
  · 헤드라인(확정 썸네일 문구) "식히려던 신호가, / 오히려 관심 신호로 읽힙니다"
    무수정, 쉼표에서만 줄바꿈.
  · 그래픽: "식힌다"는 고리(도형)를 뚫고 올라가는 화살표(도형) — 본문 4행
    (지정 소식이 화제 신호로 읽혀 매수세가 몰린다는 역설)의 시각화. 새 문구 없음.

기완료 5장(`/2` `/5` `/6` `/7` `/8`) 대조: 색상축(테라코타+딥틸블루)·정렬(우측)·
주제어 위치(하단)에서 5장 누구와도 겹치지 않는다(우측정렬은 `/6`뿐이나 `/6`은
숫자대비쌍 구조로 이번 장의 킥커+아이콘+헤드라인+주제어 단일축 구조와 다르다).
"""
from PIL import Image, ImageDraw, ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S, M = 1080, 72
BG     = (8, 52, 72)      # 딥 틸-블루, 어두운 톤 (배정 원안에서 /6과 겹쳐 「지면」이 조정)
CREAM  = (232, 238, 236)  # 헤드라인 — BG 대비 명도차 최대
MUTED  = (110, 150, 158)  # 킥커·아이콘 고리 — 보조
ACCENT = (232, 140, 74)   # 주제어 — 테라코타(웜), BG(쿨) 대비 최대. 노란 배지·강조 아님

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)
R = S - M

def put_r(right, top, t, fo, col):
    bb = fo.getbbox(t)
    w = bb[2] - bb[0]
    d.text((right - w - bb[0], top - bb[1]), t, font=fo, fill=col)
    return right - w, top + (bb[3] - bb[1])

# ── 1. 킥커 (확정 제목 앞부분, 무수정)
_, k_bot = put_r(R, 80, "단기과열종목 지정", f("Bold", 34), MUTED)

# ── 2. 역설 아이콘 — "식힌다" 고리(도형)를 뚫는 상승 화살표(도형). 텍스트 없음.
icon_top = k_bot + 58
icon_h = 170
icon_cx = R - 220
icon_cy = icon_top + icon_h // 2
d.ellipse([icon_cx - 78, icon_cy - 78, icon_cx + 78, icon_cy + 78], outline=MUTED, width=7)
ax0, ay0 = icon_cx - 96, icon_cy + 66
ax1, ay1 = icon_cx + 100, icon_cy - 74
d.line([(ax0, ay0), (ax1, ay1)], fill=CREAM, width=15)
d.polygon([(ax1, ay1), (ax1 - 44, ay1 + 8), (ax1 - 8, ay1 + 44)], fill=CREAM)
icon_bot = icon_top + icon_h

# ── 3. 헤드라인(「포착」 확정 썸네일 문구, 무수정) — 쉼표에서만 줄바꿈
hf = f("Bold", 60)
h1_r, h1_bot = put_r(R, icon_bot + 90, "식히려던 신호가,", hf, CREAM)
h2_r, h2_bot = put_r(R, h1_bot + 14, "오히려 관심 신호로 읽힙니다", hf, CREAM)

# ── 4. 주제어 — 이 장 전체에서 가장 큰 글자, 하단 배치
kf = f("ExtraBold", 172)
sub_top = 822
_, sub_bot = put_r(R, sub_top, "단기과열종목", kf, ACCENT)

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/12.png")
print("saved 12.png  k_bot=%d icon_bot=%d h1_bot=%d h2_bot=%d sub_top=%d sub_bot=%d canvas=%d" %
      (k_bot, icon_bot, h1_bot, h2_bot, sub_top, sub_bot, S))
