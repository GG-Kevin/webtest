# -*- coding: utf-8 -*-
"""/6 정리매매 7거래일 — 오답↔정답 대비형(2요소 병치, 위아래 겹침).
핵심어 「14」(거래소 원문 확정값)를 이 장의 최대 글자로 올린다.
좌표는 사전 textbbox 실측값을 그대로 대입한 것 — 임의 추정 없음."""
from PIL import Image, ImageDraw, ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S = 1080
M = 72

INK    = (26, 24, 22)      # 웜 뉴트럴 니어블랙 — 남색 아님(R>=G>=B, 블루 편향 없음)
SLATE  = (150, 146, 138)   # 「13」(오답·계산) — 무채색에 가까운 흐린 회갈색
LABEL1 = (128, 122, 112)   # 「계산」 라벨
STRIKE = (176, 92, 82)     # 취소선 — 오답 표시
DIV    = (70, 66, 60)      # 구분선
GREEN  = (72, 202, 140)    # 「14」(정답·원문) — 이 배치 미사용 색상(에메랄드)
LABEL2 = (150, 214, 182)   # 「원문」 라벨
CREAM  = (236, 230, 220)   # 헤드라인(썸네일 문구)

img = Image.new("RGB", (S, S), INK)
d = ImageDraw.Draw(img)

F13   = f("Bold", 150)       # 13 — pt 150
FLAB1 = f("Bold", 40)        # 계산 — pt 40
F14   = f("ExtraBold", 600)  # 14 — pt 600 (이 장 최대)
FLAB2 = f("Bold", 40)        # 원문 — pt 40
FH1   = f("Bold", 66)        # 헤드라인 1행 — pt 66
FH2   = f("Bold", 66)        # 헤드라인 2행 — pt 66

# ── 1. 「13」(오답·계산) — 상단, 작게, 취소선
b13 = d.textbbox((0, 0), "13", font=F13)          # (0,35,166,145)
x13, y13 = M, 100 - b13[1]
d.text((x13, y13), "13", font=F13, fill=SLATE)
strike_y = 100 + (b13[3] - b13[1]) // 2           # 13의 세로 중앙
d.line([(M - 16, strike_y), (M + b13[2] + 16, strike_y)], fill=STRIKE, width=7)

blab1 = d.textbbox((0, 0), "계산", font=FLAB1)
lab1_top = 100 + (b13[3] - b13[1]) + 14
d.text((M, lab1_top - blab1[1]), "계산", font=FLAB1, fill=LABEL1)
lab1_bottom = lab1_top + (blab1[3] - blab1[1])

# ── 2. 구분선
div_y = lab1_bottom + 40
d.line([(M, div_y), (S - M, div_y)], fill=DIV, width=2)

# ── 3. 「14」(정답·원문) — 이 장의 최대 글자, 우측정렬, 하단으로 겹쳐 배치
b14 = d.textbbox((0, 0), "14", font=F14)          # (0,146,688,571)
top14 = div_y + 60
x14 = (S - M) - b14[2]
y14 = top14 - b14[1]
d.text((x14, y14), "14", font=F14, fill=GREEN)
bottom14 = top14 + (b14[3] - b14[1])

blab2 = d.textbbox((0, 0), "원문", font=FLAB2)
lab2_top = bottom14 + 20
x_lab2 = (S - M) - blab2[2]
d.text((x_lab2, lab2_top - blab2[1]), "원문", font=FLAB2, fill=LABEL2)

# ── 4. 헤드라인(「포착」 확정 썸네일 문구, 무수정) — 우측정렬, 하단
h2 = "원문을 확인했습니다"
h1 = "계산이 아니라,"
bh2 = d.textbbox((0, 0), h2, font=FH2)
bh1 = d.textbbox((0, 0), h1, font=FH1)

h2_bottom = S - M
h2_top = h2_bottom - (bh2[3] - bh2[1])
d.text(((S - M) - bh2[2], h2_top - bh2[1]), h2, font=FH2, fill=CREAM)

h1_bottom = h2_top - 14
h1_top = h1_bottom - (bh1[3] - bh1[1])
d.text(((S - M) - bh1[2], h1_top - bh1[1]), h1, font=FH1, fill=CREAM)

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/6.png")
print("saved")
print("13 top/bottom", 100, 100 + (b13[3]-b13[1]), "h13=", b13[3]-b13[1])
print("14 top/bottom", top14, bottom14, "h14=", bottom14-top14)
print("headline1 top/bottom", h1_top, h1_bottom)
print("headline2 top/bottom", h2_top, h2_bottom)
print("label2 right edge", x_lab2 + blab2[2], "canvas right margin", S - M)
