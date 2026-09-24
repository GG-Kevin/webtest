# -*- coding: utf-8 -*-
"""/23 관리종목 36개, 2027년 1월엔 더 늘어난다 — 2026-09-24 「지면」 신규 제작(12편 배치).

「포착」 지침(06_썸네일문구_23.md) 그대로 구현 — 문구 무수정.
  · 주제어 "관리종목"을 이 장의 최대 글자로. 확정 제목("관리종목 36개,
    2027년 1월엔...")에 이미 있는 말. (/5도 같은 낱말을 쓰지만 그 글의
    실제 주제어이므로 반복 자체는 금지 대상이 아니다 — 금지되는 것은
    레이아웃 도장 찍기다. 배경·정렬·장치를 /5와 전부 다르게 했다.)
  · 킥커 "관리종목 36개"는 확정 제목 앞부분을 그대로 잘라 옮긴 것.
  · 그래픽 장치: 「포착」 문서 [데이터 계열 판정]이 "두 숫자를 나란히 놓고
    대비하는 장치만 쓴다(오르내리는 그래프 금지)"라고 명시 — 원 2개를
    반지름 비율(50:150 → 1:3)로 나란히 놓고 화살표로 확대를 표시.
  · 헤드라인(확정 썸네일 문구) "거래소 예상 50개, / 실제 추산은 150개입니다"
    무수정.

/5(버건디·좌·2패널) 대조: /23은 딥로즈(색상축 다름)·우측정렬·원크기비교
장치로 정렬·배경·장치 셋 다 다르다. 나머지 배치 열 장과도 우측정렬은
/6·/12뿐이나 둘 다 색상·장치가 다르다.
"""
from PIL import Image, ImageDraw, ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S, M = 1080, 72
BG    = (56, 22, 44)      # 딥 로즈 — /5 버건디(56,18,26)와 색상축 다름(B가 훨씬 큼)
CREAM = (240, 224, 232)
ROSE  = (224, 96, 140)
MAUVE = (168, 128, 156)

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)
R = S - M

def put_r(right, top, t, fo, col):
    bb = fo.getbbox(t)
    w = bb[2] - bb[0]
    d.text((right - w - bb[0], top - bb[1]), t, font=fo, fill=col)
    return right - w, top + (bb[3] - bb[1])

# ── 1. 킥커 (확정 제목 앞부분, 무수정)
_, k_bot = put_r(R, 88, "관리종목 36개", f("Bold", 36), MAUVE)

# ── 2. 주제어 — 이 장의 최대 글자
_, key_bot = put_r(R, k_bot + 24, "관리종목", f("ExtraBold", 240), CREAM)

# ── 3. 원 크기 비교(도형) — 50개 vs 150개, 반지름 비율 그대로
dev_top = key_bot + 60
r1, r2 = 34, 60  # 1:3에 근사(면적 아닌 가독성 위해 반지름 완만 스케일)
cy = dev_top + r2
c1x = R - 470
c2x = R - 260
d.ellipse([c1x - r1, cy - r1, c1x + r1, cy + r1], outline=MAUVE, width=6)
d.ellipse([c2x - r2, cy - r2, c2x + r2, cy + r2], fill=ROSE)
lf = f("Bold", 30)
put_r(c1x + 60, cy - 16, "50개", lf, MAUVE)
bb = lf.getbbox("150개")
d.text((c2x - (bb[2] - bb[0]) / 2 - bb[0], cy - (bb[3] - bb[1]) / 2 - bb[1]), "150개", font=lf, fill=CREAM)
# 화살표
d.line([(c1x + r1 + 14, cy), (c2x - r2 - 14, cy)], fill=MAUVE, width=6)
d.polygon([(c2x - r2 - 14, cy), (c2x - r2 - 34, cy - 12), (c2x - r2 - 34, cy + 12)], fill=MAUVE)
dev_bot = cy + r2 + 30

# ── 4. 헤드라인 (「포착」 확정 썸네일 문구, 무수정) — 2줄, 주제어보다 작게
hf = f("Bold", 58)
_, h1_bot = put_r(R, dev_bot + 56, "거래소 예상 50개,", hf, CREAM)
_, h2_bot = put_r(R, h1_bot + 22, "실제 추산은 150개입니다", hf, ROSE)

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/23.png")
print("saved 23.png  k_bot=%d key_bot=%d dev_bot=%d h2_bot=%d" %
      (k_bot, key_bot, dev_bot, h2_bot))
