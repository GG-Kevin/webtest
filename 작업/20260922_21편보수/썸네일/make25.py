# -*- coding: utf-8 -*-
"""/25 유상증자 공시(권리락 조정) — 2026-09-24 「지면」 신규 제작(12편 배치).

「포착」 지침(06_썸네일문구_25.md) 그대로 구현 — 문구 무수정.
  · 주제어 "유상증자"를 이 장의 최대 글자로. 확정 제목("유상증자, 악재인지
    아닌지는...")에 이미 있는 말.
  · 킥커 "'자금 용도' 한 칸에 있습니다"는 확정 제목 뒷부분을 그대로 잘라
    옮긴 것(주제어와 겹치지 않는 다른 구절을 골랐다).
  · 그래픽 장치: 권리락 전/후 막대 2개(전: 높음, 후: 20% 낮음) + 점선으로
    "매도가 쏟아진 절벽"이 아니라 "제도가 미리 낮춘 기준선"임을 표시.
    본문 62행("인위적인 조정이지 매도가 쏟아진 결과가 아닙니다")의 구조를
    그린 것. 시세 계열 그래프 아님 — 단일 전/후 두 값만 비교.
  · 헤드라인(확정 썸네일 문구) "20% 급락, / 사실은 매도가 아니라
    조정입니다" 무수정.

직전 장들 색상축(아이보리앰버/버넌엄버/웜그레이지/딥플럼/스카이시안/다크
웜차콜/라벤더/차콜브라운/니어블랙/라이트피치/딥로즈) 대조: /25는 라이트
슬레이트블루그레이(밝은 쿨톤, 처음)·우측정렬·전후 막대+점선기준선 장치.
"""
from PIL import Image, ImageDraw, ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S, M = 1080, 72
BG    = (222, 230, 238)   # 라이트 슬레이트블루그레이
INK   = (26, 32, 44)
STEEL = (52, 92, 140)
RUST  = (196, 90, 60)
MUTED = (110, 122, 140)

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)
R = S - M

def put_r(right, top, t, fo, col):
    bb = fo.getbbox(t)
    w = bb[2] - bb[0]
    d.text((right - w - bb[0], top - bb[1]), t, font=fo, fill=col)
    return right - w, top + (bb[3] - bb[1])

# ── 1. 킥커 (확정 제목 뒷부분, 무수정)
_, k_bot = put_r(R, 88, "'자금 용도' 한 칸에 있습니다", f("Bold", 30), MUTED)

# ── 2. 주제어 — 이 장의 최대 글자
_, key_bot = put_r(R, k_bot + 24, "유상증자", f("ExtraBold", 230), INK)

# ── 3. 권리락 전/후 막대(도형) + 점선 기준선
dev_top = key_bot + 60
bw = 110
gap = 60
h_before = 180
h_after = int(h_before * 0.8)
x1 = R - 60 - bw
x0 = x1 - gap - bw
base_y = dev_top + h_before
d.rounded_rectangle([x0, base_y - h_before, x0 + bw, base_y], 10, fill=STEEL)
d.rounded_rectangle([x1, base_y - h_after, x1 + bw, base_y], 10, fill=RUST)
# 점선 기준선(전 고점에서 그대로 그은 선 — "매도로 뚫린 것 아님"을 보여줌)
xx = x0
top_line_y = base_y - h_before
while xx < x1 + bw + 20:
    d.line([(xx, top_line_y), (min(xx + 18, x1 + bw), top_line_y)], fill=MUTED, width=4)
    xx += 30
lf = f("Bold", 28)
bb = lf.getbbox("전")
d.text((x0 + bw / 2 - (bb[2] - bb[0]) / 2 - bb[0], base_y + 14 - bb[1]), "전", font=lf, fill=STEEL)
bb2 = lf.getbbox("후(-20%)")
d.text((x1 + bw / 2 - (bb2[2] - bb2[0]) / 2 - bb2[0], base_y + 14 - bb2[1]), "후(-20%)", font=lf, fill=RUST)
dev_bot = base_y + 14 + 34

_, lab_bot = put_r(R, dev_bot + 14, "제도가 낮춘 기준선(매도 아님)", f("Bold", 26), MUTED)

# ── 4. 헤드라인 (「포착」 확정 썸네일 문구, 무수정) — 2줄, 주제어보다 작게
hf = f("Bold", 58)
segs = [("20% ", RUST), ("급락,", INK)]
total_w = sum(hf.getbbox(t)[2] - hf.getbbox(t)[0] for t, _ in segs)
xL = R - total_w
h1_top = lab_bot + 56
h1_bot = h1_top
for seg, col in segs:
    bb = hf.getbbox(seg)
    d.text((xL - bb[0], h1_top - bb[1]), seg, font=hf, fill=col)
    xL += (bb[2] - bb[0])
    h1_bot = max(h1_bot, h1_top + (bb[3] - bb[1]))
_, h2_bot = put_r(R, h1_bot + 22, "사실은 매도가 아니라 조정입니다", hf, INK)

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/25.png")
print("saved 25.png  k_bot=%d key_bot=%d dev_bot=%d h2_bot=%d" %
      (k_bot, key_bot, dev_bot, h2_bot))
