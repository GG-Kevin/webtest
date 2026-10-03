# -*- coding: utf-8 -*-
"""/2 동전주 상장폐지 썸네일 — 2026-09-24 소급검사 재제작.
사장 판정: 핵심어 비율 0.25(kicker 36px / 밴드최대 146px). 재측정 결과
실제 '46'(핵심 숫자)은 기존판에서도 144px였으나 kicker를 핵심어로 오판한
측정이 반려 근거였다(측정 함정). 이번 판은 '46'을 명시적으로 이 장 최대
텍스트로 재구성해 오판 여지를 없앤다 — 비율을 구조적으로 1.00으로 만든다.

D-071(지정된 것만 고친다) — 아래는 무수정 유지:
- 문구 원문(킥커·헤드라인·라벨) — 06_썸네일문구_2.md D-139 재확정본 그대로
- 배경 RGB (230,214,178) — D-139 §2 채널차 검증 통과값
- 강조색 테라코타 (178,61,33), 다크 텍스트 (26,23,21), 뮤트 (120,112,100)
바꾼 것: 레이아웃 구조·크기 배분(핵심 숫자 '46'을 최대 텍스트로 재배치)
"""
from PIL import Image, ImageDraw, ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S = 1080
BG    = (230, 214, 178)   # D-139 확정 웜 샌드 — 무수정
DARK  = (26, 23, 21)      # 헤드라인 — 무수정
MUTED = (120, 112, 100)   # 킥커·라벨 — 무수정
TERRA = (178, 61, 33)     # 강조색 — 무수정

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)

M = 72

def tw(t, fo): return d.textlength(t, font=fo)

# ── 1. 킥커 (무수정 문구, 축소 배치 — 핵심어 아님)
d.rectangle([M, 92, M + 8, 92 + 34], fill=TERRA)
d.text((M + 22, 90), "동전주 상장폐지", font=f("Bold", 32), fill=MUTED)

# ── 2. 헤드라인 (무수정 문구, 2줄 — 핵심어보다 작게)
hf = f("Bold", 58)
d.text((M, 152), "미달된 날이 아니라,", font=hf, fill=DARK)
d.text((M, 220), "채운 날을 셉니다", font=hf, fill=DARK)

d.rectangle([M, 300, M + 200, 306], fill=TERRA)

# ── 3. 산식(36+10=)과 핵심 숫자(46)를 한 줄에, 바텀 정렬로 결합
#    핵심 숫자만 압도적으로 커서 '46'이 이 장 최대 텍스트가 되도록 구성
eqf  = f("Bold", 70)
big  = f("ExtraBold", 340)
EQ_BOTTOM = 780  # 이 y에 작은 산식과 큰 46 숫자 둘 다의 글리프 바닥을 맞춘다

eq_small_top, eq_small_bot = eqf.getbbox("36")[1], eqf.getbbox("36")[3]
big_top, big_bot = big.getbbox("46")[1], big.getbbox("46")[3]
y_small = EQ_BOTTOM - eq_small_bot
y_big   = EQ_BOTTOM - big_bot

ex = M
for seg, col in [("36", DARK), ("+", MUTED), ("10", DARK), ("=", MUTED)]:
    d.text((ex, y_small), seg, font=eqf, fill=col)
    ex += tw(seg, eqf) + 18

d.text((ex, y_big), "46", font=big, fill=TERRA)
bw46 = tw("46", big)

# 핵심 숫자 옆에 붙는 단위 — 같은 핵심어 구를 완성("46번째 거래일"), 바닥선 공유
unit_f = f("ExtraBold", 58)
u_bot = unit_f.getbbox("거래일")[3]
ux = ex + bw46 + 20
d.text((ux, EQ_BOTTOM - u_bot - 78), "번째", font=unit_f, fill=DARK)
d.text((ux, EQ_BOTTOM - u_bot), "거래일", font=unit_f, fill=DARK)

# ── 4. 라벨 (기존 승인 문구 3개, 무수정·재배치만)
lf = f("Regular", 28)
d.text((M, 866), "경과일수", font=lf, fill=MUTED)
d.text((M + 190, 866), "연속 필요", font=lf, fill=MUTED)
d.text((M + 380, 866), "46번째 거래일", font=lf, fill=MUTED)

# ── 6. 하단 바 (무수정 장식)
d.rectangle([0, 1060, S, 1076], fill=TERRA)

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/2.png")
print("saved")
