# -*- coding: utf-8 -*-
"""/20 국민연금 조기수령 vs 연기연금 — 2026-09-24 「지면」 신규 제작(12편 배치).

「포착」 지침(06_썸네일문구_20.md) 그대로 구현 — 문구 무수정.
  · 주제어 "조기수령"을 이 장의 최대 글자로. 확정 제목("국민연금 조기수령,
    계산에 안 잡히는...")에 이미 있는 말.
  · 킥커 "국민연금 조기수령"은 확정 제목 앞부분을 그대로 잘라 옮긴 것.
  · 그래픽 장치: 수평 타임라인(도형) 위에 "숨은 변수" 지점을 원 마커로 표시 —
    본문 50행(소득 합계 연 2,000만원 초과 시 피부양자 자격 상실)의 "계산에
    안 잡히는 변수가 갑자기 나타난다"는 구조를 시각화. 시계열 그래프 아님.
  · 헤드라인(확정 썸네일 문구) "연 2,000만원 넘으면, / 건강보험 피부양자
    에서 빠집니다" 무수정.

직전 일곱 장 색상축(아이보리앰버/버넌엄버/웜그레이지/초콜릿골드/스카이시안/
올리브/라벤더) 대조: /20은 다크 차콜브라운(무채색에 가까운 중성 다크, 색상축
자체가 없음)·좌측정렬·수평 타임라인+마커 장치(여덟 장 누구에게도 없음).
"""
from PIL import Image, ImageDraw, ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S, M = 1080, 72
BG    = (36, 30, 26)     # 다크 차콜브라운 — 남색 아님(R이 최대, 무채색에 가까운 웜)
CREAM = (238, 230, 220)
TAN   = (196, 150, 90)
RUST  = (176, 96, 70)
MUTED = (140, 126, 112)

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)

def put(x, top, t, fo, col):
    bb = fo.getbbox(t)
    d.text((x - bb[0], top - bb[1]), t, font=fo, fill=col)
    return x + (bb[2] - bb[0]), top + (bb[3] - bb[1])

# ── 1. 킥커 (확정 제목 앞부분, 무수정)
_, k_bot = put(M, 88, "국민연금 조기수령", f("Bold", 36), MUTED)

# ── 2. 주제어 — 이 장의 최대 글자
_, key_bot = put(M, k_bot + 24, "조기수령", f("ExtraBold", 240), CREAM)

# ── 3. 타임라인(도형) + 숨은 변수 마커
line_y = key_bot + 92
x0, x1 = M, S - M
d.line([(x0, line_y), (x1, line_y)], fill=(70, 62, 54), width=8)
for i, (frac, lab) in enumerate([(0.12, "수령 개시"), (0.62, "연 2,000만원"), (1.0, "피부양자 상실")]):
    mx = x0 + (x1 - x0) * frac
    col = RUST if i == 1 else TAN
    r = 16 if i == 1 else 10
    d.ellipse([mx - r, line_y - r, mx + r, line_y + r], fill=col)
    lf = f("Bold", 26)
    bb = lf.getbbox(lab)
    lw = bb[2] - bb[0]
    lx = min(max(mx - lw / 2, x0), x1 - lw)
    d.text((lx - bb[0], line_y + 22 - bb[1]), lab, font=lf, fill=col)
dev_bot = line_y + 22 + 30

# ── 4. 헤드라인 (「포착」 확정 썸네일 문구, 무수정) — 2줄, 주제어보다 작게
hf = f("Bold", 58)
_, h1_bot = put(M, dev_bot + 66, "연 2,000만원 넘으면,", hf, CREAM)
_, h2_bot = put(M, h1_bot + 22, "건강보험 피부양자에서 빠집니다", hf, RUST)

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/20.png")
print("saved 20.png  k_bot=%d key_bot=%d dev_bot=%d h2_bot=%d" %
      (k_bot, key_bot, dev_bot, h2_bot))
