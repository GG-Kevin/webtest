# -*- coding: utf-8 -*-
"""/22 추석 주식시장 휴장(정산지연) 썸네일 — 2026-09-24 「지면」 신규 제작.

「포착」 지침(06_썸네일문구_22.md) 그대로 구현한다 — 제목·썸네일 문구 무수정.
  · 확정 제목: "추석 주식시장 휴장은 24일·25일 — 28일 월요일은 정상 개장합니다"
    → 「휴장」이 이 글의 주제어(무엇에 관한 글인지). 이 장 전체에서 가장 큰 글자.
  · 확정 썸네일 문구(무수정): "9월 23일에 팔아도, 돈은 29일에야 들어옵니다"
    → 헤드라인 2줄로 줄바꿈만.
  · 본문 66행 직접 인용 3구간("9월 23일(수) 매도 → 다음 영업일은 9월 28일(월)
    → 출금 가능일 9월 29일(화)")을 하단 타임라인 다이어그램으로 시각화.
    라벨(매도/다음 영업일/출금 가능일) 전부 66행 원문 그대로 — 「지면」이 새로 지은
    문장 없음.

배정(진행, 충돌 방지):
  배경 다크 차콜-퍼플, 좌측 정렬, 주제어 상단.
  기존 5장((2,5,6,7,8))과 채널차 30↑ 확보 위해 (26,20,32) 원안에서
  G채널을 더 낮춰 (18,8,30)으로 조정 — /6(20,42,35)과의 diff가 원안대로면
  max=24로 미달이라 "안 되면 더 무채색·검정에 가깝게" 지침대로 낮췄다.

직전 5장과 구조 대조: /2 단일수식형(좌·하단) / /5 2패널병치(좌·상단, 경계선 없음)
/6 숫자대비쌍(우·상단, 시간축 없음) / /7 2블록+세로시간경계선(대칭·상단)
/8 단일캡슐(중앙·중앙) → /22는 **가로 3점 타임라인**(좌·상단) — 어느 것과도
다른 구조(점 3개+연결선, 대칭 아닌 좌측기준 가로 배열).
"""
from PIL import Image, ImageDraw, ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S, M = 1080, 72
BG      = (18, 8, 30)      # 다크 차콜-퍼플(무채색에 가깝게 조정) — 기존 5장과 채널차 34↑
CREAM   = (240, 234, 226)
MUTE    = (150, 138, 168)  # 보조 라벨(다음 영업일)
CORAL   = (224, 122, 95)   # 강조 — 출금 가능일(핵심 정보)
LINE_C  = (86, 74, 104)    # 타임라인 연결선(무채색에 가까운 보조색)

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)

def left(x, top, t, fo, col):
    bb = fo.getbbox(t)
    d.text((x - bb[0], top - bb[1]), t, font=fo, fill=col)
    return top + (bb[3] - bb[1]), x + (bb[2] - bb[0])

def cen_mid(cx, cy, t, fo, col):
    bb = fo.getbbox(t)
    w = bb[2] - bb[0]; h = bb[3] - bb[1]
    d.text((cx - w / 2 - bb[0], cy - h / 2 - bb[1]), t, font=fo, fill=col)
    return w

# ── 1. 주제어 — 상단·좌측, 이 장 전체에서 가장 큰 글자
kf = f("ExtraBold", 300)
k_bot, _ = left(M, 96, "휴장", kf, CREAM)

# ── 2. 헤드라인(확정 썸네일 문구, 무수정) — 좌측 정렬 2줄
hf = f("Bold", 66)
hy0 = k_bot + 70
h1_bot, _ = left(M, hy0, "9월 23일에 팔아도,", hf, CREAM)
h2_bot, _ = left(M, h1_bot + 18, "돈은 29일에야 들어옵니다", hf, CREAM)

# ── 3. 타임라인(본문 66행 직접 인용 3구간) — 가로 3점 다이어그램
tl_y = h2_bot + 200          # 연결선 y좌표(여백을 넉넉히 두어 하단까지 균형)
x1, x2, x3 = M + 46, S / 2, S - M - 46

d.line([(x1, tl_y), (x3, tl_y)], fill=LINE_C, width=4)
r = 12
for x, col in ((x1, CREAM), (x2, MUTE), (x3, CORAL)):
    d.ellipse([x - r, tl_y - r, x + r, tl_y + r], fill=col)

df = f("Bold", 44)
lf = f("Regular", 27)

def anchored(x, top, t, fo, col, align):
    """align: 'l'=왼쪽 끝을 x에, 'c'=x가 중심, 'r'=오른쪽 끝을 x에.
    캔버스 좌우 끝점의 점(dot)에 붙는 라벨이 폭 때문에 화면 밖으로
    밀려나 잘리는 것을 막기 위해 끝점은 안쪽으로만 자라게 정렬한다."""
    bb = fo.getbbox(t)
    tw = bb[2] - bb[0]
    if align == 'l':
        x0 = x
    elif align == 'r':
        x0 = x - tw
    else:
        x0 = x - tw / 2
    d.text((x0 - bb[0], top - bb[1]), t, font=fo, fill=col)
    return x0 + tw / 2  # 실제 중심(밑줄 등 후속 정렬용)

def point(x, date, label, col, lab_col, align):
    dy = tl_y + 34
    anchored(x, dy + 2, date, df, col, align)
    ly = dy + 2 + 44 + 26
    anchored(x, ly, label, lf, lab_col, align)

# 좌측 끝점: 텍스트를 점 기준 오른쪽으로만(왼쪽정렬) — 캔버스 밖으로 안 나감
# 우측 끝점: 텍스트를 점 기준 왼쪽으로만(오른쪽정렬) — 캔버스 밖으로 안 나감
# 중앙: 그대로 중앙정렬
point(x1, "9월 23일(수)", "매도", CREAM, MUTE, 'l')
point(x2, "9월 28일(월)", "다음 영업일", MUTE, MUTE, 'c')
point(x3, "9월 29일(화)", "출금 가능일", CORAL, CORAL, 'r')

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/22.png")
print("saved 22.png  k_bot=%d h2_bot=%d tl_y=%d canvas=%d" % (k_bot, h2_bot, tl_y, S))
