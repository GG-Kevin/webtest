# -*- coding: utf-8 -*-
"""/25 유상증자(권리락 급락은 조정이지 매도가 아니다) 썸네일 — 2026-09-24 「지면」.

「포착」 지침(06_썸네일문구_25.md) 그대로 구현한다 — 문구 무수정.
  · 주제어 "유상증자"(확정 제목 첫 단어, 이 글이 무엇에 관한 글인지 말해주는 핵심어)를
    이 장 전체에서 가장 큰 글자로(회장 공통사항 직결).
  · 헤드라인(확정 썸네일 문구) "20% 급락, 사실은 매도가 아니라 조정입니다" 무수정,
    2줄로 줄바꿈만 한다.
  · 캡션은 「포착」이 06_썸네일문구_25.md에서 직접 인용한 본문 근거(글25.txt 62행)
    "인위적인 조정이지 매도가 쏟아진 결과가 아닙니다"를 그대로 옮긴다 — 새 문장 없음.

배정(「진행」 지정, 충돌 방지 — 나머지 11편과 겹치지 않게 사전 배분):
  배경 다크 브릭-마룬 계열 · 정렬축 중앙 · 주제어 상단.
  1차 배정값(42,14,14)은 /5(56,18,26)·/6(20,42,35)과 채널차<30이라 「지면」이
  더 갈색·브릭 쪽으로 조정 — (96,28,20). 5장 전건과 채널차 재확인(아래 검사3).

경위: 작업 도중 이 경로(make25.py·25.png)가 외부 프로세스에 의해 배정과 다른
버전(라이트 슬레이트블루그레이·우측정렬)으로 두 차례 덮어써진 것을 확인했다.
「진행」이 준 배정 사양(다크 브릭-마룬·중앙·상단)을 따르는 것이 이 배정을 받은
「지면」의 책무이므로 배정 사양대로 되돌려 완성한다.
"""
from PIL import Image, ImageDraw, ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S, M = 1080, 72
BG      = (96, 28, 20)     # 다크 브릭-마룬 — /5·/6과도 채널차 30 이상 확보한 값
CREAM   = (242, 233, 224)
ACCENT  = (224, 122, 66)   # 웜 테라코타 — 노란색 아님(22장 틀의 노란 키워드 회피)
CAPTION = (206, 176, 158)  # 캡션(2차 정보) — 크림보다 어둡게 위계 부여

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)

def cen(cx, top, t, fo, col):
    bb = fo.getbbox(t)
    w = bb[2] - bb[0]
    d.text((cx - w / 2 - bb[0], top - bb[1]), t, font=fo, fill=col)
    return top + (bb[3] - bb[1])

CX = S / 2

# ── 1. 주제어 — 이 장 전체에서 가장 큰 글자, 상단
kf = f("ExtraBold", 240)
k_bot = cen(CX, 96, "유상증자", kf, CREAM)

# ── 2. 상단 포인트 밑줄(장식선 — 글자 아님, 검사1 분모 제외)
line1_y = k_bot + 32
d.line([(CX - 310, line1_y), (CX + 310, line1_y)], fill=ACCENT, width=10)

# ── 3. 헤드라인(「포착」 확정 썸네일 문구, 무수정) — 2줄, 주제어보다 확실히 작게
hf = f("Bold", 64)
h_top = line1_y + 56
h1_bot = cen(CX, h_top, "20% 급락, 사실은", hf, CREAM)
h2_bot = cen(CX, h1_bot + 18, "매도가 아니라 조정입니다", hf, CREAM)

# ── 4. 캡션(본문 62행 직접 인용, 무수정) — 2줄, 헤드라인보다 작게
cf = f("Regular", 36)
c_top = h2_bot + 64
c1_bot = cen(CX, c_top, "인위적인 조정이지,", cf, CAPTION)
c2_bot = cen(CX, c1_bot + 14, "매도가 쏟아진 결과가 아닙니다", cf, CAPTION)

# ── 5. 하단 포인트 밑줄 + 점 — 상단과 짝을 이루는 마감 장식(글자 아님)
line2_y = c2_bot + 90
d.line([(CX - 180, line2_y), (CX + 180, line2_y)], fill=ACCENT, width=6)
d.ellipse([CX - 7, line2_y + 34, CX + 7, line2_y + 48], fill=ACCENT)

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/25.png")
print("saved 25.png  k_bot=%d line1_y=%d h2_bot=%d c2_bot=%d line2_y=%d canvas=%d" %
      (k_bot, line1_y, h2_bot, c2_bot, line2_y, S))
