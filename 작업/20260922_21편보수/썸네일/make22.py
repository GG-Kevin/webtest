# -*- coding: utf-8 -*-
"""/22 추석 주식시장 휴장 — 2026-09-24 「지면」 신규 제작(12편 배치).

「포착」 지침(06_썸네일문구_22.md) 그대로 구현 — 문구 무수정.
  · 주제어 "휴장"을 이 장의 최대 글자로. 확정 제목("추석 주식시장 휴장은
    24일·25일...")에 이미 있는 말.
  · 킥커 "추석 주식시장 휴장은 24일·25일"은 확정 제목 앞부분을 그대로 잘라 옮긴 것.
  · 그래픽 장치: 9.23~9.29 달력 스트립 — 24·25일을 휴장(회색 처리)으로,
    29일을 입금일(강조)로 표시. 본문 66행의 날짜(23일 매도 → 28일 다음
    영업일 → 29일 출금)를 그대로 옮긴 것, 새 날짜 아님.
  · 헤드라인(확정 썸네일 문구) "9월 23일에 팔아도, / 돈은 29일에야
    들어옵니다" 무수정.

직전 여덟 장 색상축(아이보리앰버/버넌엄버/웜그레이지/초콜릿골드/스카이시안
/올리브/라벤더/니어블랙) 대조: /22는 라이트 피치(웜 파스텔, 처음)·좌측정렬·
7칸 달력 스트립 장치(아홉 장 누구에게도 없음).
"""
from PIL import Image, ImageDraw, ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S, M = 1080, 72
BG     = (250, 224, 198)   # 라이트 피치
INK    = (42, 28, 20)
TERRA  = (176, 62, 40)
OLIVE  = (100, 116, 72)
MUTED  = (150, 122, 100)
BOXBG  = (240, 206, 174)

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)

def put(x, top, t, fo, col):
    bb = fo.getbbox(t)
    d.text((x - bb[0], top - bb[1]), t, font=fo, fill=col)
    return x + (bb[2] - bb[0]), top + (bb[3] - bb[1])

# ── 1. 킥커 (확정 제목 앞부분, 무수정)
_, k_bot = put(M, 88, "추석 주식시장 휴장은 24일·25일", f("Bold", 30), MUTED)

# ── 2. 주제어 — 이 장의 최대 글자
_, key_bot = put(M, k_bot + 24, "휴장", f("ExtraBold", 340), TERRA)

# ── 3. 달력 스트립(도형) — 23~29일, 24·25 휴장 / 29 입금 강조
days = [("23", "수"), ("24", "목"), ("25", "금"), ("26", "토"), ("27", "일"), ("28", "월"), ("29", "화")]
n = len(days)
gap = 14
cw = (S - M * 2 - gap * (n - 1)) // n
cal_top = key_bot + 56
cal_h = 110
df_num = f("ExtraBold", 34)
df_lab = f("Bold", 22)
for i, (num, wd) in enumerate(days):
    x0 = M + i * (cw + gap)
    x1 = x0 + cw
    if num in ("24", "25"):
        fill, tcol = (222, 196, 170), MUTED
    elif num == "29":
        fill, tcol = TERRA, (255, 250, 244)
    else:
        fill, tcol = BOXBG, INK
    d.rounded_rectangle([x0, cal_top, x1, cal_top + cal_h], 14, fill=fill)
    bb = df_num.getbbox(num)
    d.text((x0 + (cw - (bb[2] - bb[0])) / 2 - bb[0], cal_top + 18 - bb[1]), num, font=df_num, fill=tcol)
    bb2 = df_lab.getbbox(wd)
    d.text((x0 + (cw - (bb2[2] - bb2[0])) / 2 - bb2[0], cal_top + 66 - bb2[1]), wd, font=df_lab, fill=tcol)
cal_bot = cal_top + cal_h
_, lab_bot = put(M, cal_bot + 18, "휴장(회색) · 입금일 29일(강조)", f("Bold", 26), OLIVE)

# ── 4. 헤드라인 (「포착」 확정 썸네일 문구, 무수정) — 2줄, 주제어보다 작게
hf = f("Bold", 58)
_, h1_bot = put(M, lab_bot + 46, "9월 23일에 팔아도,", hf, INK)
x = M
for seg, col in [("돈은 ", INK), ("29일", TERRA), ("에야 들어옵니다", INK)]:
    x, h2_bot = put(x, h1_bot + 22, seg, hf, col)

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/22.png")
print("saved 22.png  k_bot=%d key_bot=%d cal_bot=%d h2_bot=%d" %
      (k_bot, key_bot, cal_bot, h2_bot))
