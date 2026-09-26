# -*- coding: utf-8 -*-
"""/19 해외주식 양도소득세(환율) — 2026-09-24 「지면」 신규 제작(12편 배치).

「포착」 지침(06_썸네일문구_19.md) 그대로 구현 — 문구·제목 무수정, 새로 짓지 않는다.
  · 주제어 "해외주식 / 양도소득세" — 06_썸네일문구_19.md 첫 줄(문서 제목)에
    그대로 있는 말("/19 해외주식 양도소득세")을 2행으로 나눠 이 장 전체에서
    가장 큰 글자로 세운다(회장 공통사항 — 가장 중요한 게 가장 커야 한다).
  · 킥커 "해외주식 250만원까지는" — 확정 제목("해외주식 250만원까지는 세금이
    없습니다, 그 다음이 문제입니다") 앞부분을 그대로 잘라 옮긴 것. 새 문장 아님.
  · 그래픽 장치: 수평 점선(주가 — "그대로")과 계단형 상승선(환율 — "오름")의
    대비. 실제 시세 계열이 아니라 본문 35행의 메커니즘(주가는 그대로인데
    환율이 오르면 원화환산 매도금액이 커진다)을 은유하는 추상 도형이다.
    라벨 "주가"·"환율"만 있고 눈금·단위는 없다 — 데이터로 오인될 요소 없음.
  · 헤드라인(확정 썸네일 문구, 무수정) "주가는 그대로인데, / 세금은 환율
    때문에 달라집니다" — 주제어보다 확실히 작게.

배정(「진행」): 배경 페일 라일락 계열·밝은 톤, 정렬축 좌측(킥커·헤드라인·장치
라벨), 주제어 위치 중앙. 다만 배정 원안 RGB(233,218,236)는 완료본 `/8`
(237,240,245)과 채널차 최대 22 <30이라 「지면」이 자체 검사3 기준(≥30)에
맞춰 (224,198,236)으로 조정했다 — 같은 "페일 라일락 계열, 밝은 톤"을 유지한
채 값만 옮긴 것이다(검사 3 섹션에서 재현 가능하게 계산).

직전 6장 색상축(다른 손, 참고): /11 아이보리앰버 /12 버넌엄버 /13 웜그레이지
/16 초콜릿골드 /17 스카이시안 /18 다크올리브. /19는 라이트 라벤더(보라 계열,
이 배치에서 처음)·좌측정렬+중앙 주제어·점선+계단선 대비 장치.
"""
from PIL import Image, ImageDraw, ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S, M = 1080, 72
BG     = (224, 198, 236)   # 페일 라일락(밝은 톤) — /8과 채널차 확보 위해 원안에서 조정
INK    = (32, 24, 50)      # 짙은 보라잉크 — 밝은 배경 대비용(고대비)
VIOLET = (94, 54, 150)     # 환율(상승) 계열
MUTED  = (120, 104, 140)   # 킥커·주가 라벨
CORAL  = (176, 70, 46)     # 헤드라인 2행 포인트

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)
CX = S / 2

def left(x, top, t, fo, col):
    bb = fo.getbbox(t)
    d.text((x - bb[0], top - bb[1]), t, font=fo, fill=col)
    return top + (bb[3] - bb[1])

def cen(top, t, fo, col):
    bb = fo.getbbox(t)
    w = bb[2] - bb[0]
    d.text((CX - w / 2 - bb[0], top - bb[1]), t, font=fo, fill=col)
    return top + (bb[3] - bb[1])

# ── 1. 킥커 (확정 제목 앞부분, 무수정) — 좌측 정렬
kf = f("Bold", 36)
k_bot = left(M, 60, "해외주식 250만원까지는", kf, MUTED)

# ── 2. 주제어 — 이 장의 최대 글자, 중앙 정렬(배정)
kw_f = f("ExtraBold", 215)
kw1_bot = cen(k_bot + 30, "해외주식", kw_f, INK)
kw2_bot = cen(kw1_bot + 16, "양도소득세", kw_f, INK)

# ── 3. 점선(주가·그대로) + 계단선(환율·오름) 대비 장치 — 좌측 정렬 틀 안
dev_top = kw2_bot + 50
x0, x1 = M, S - M
flat_y = dev_top + 100
xx = x0
while xx < x1:
    d.line([(xx, flat_y), (min(xx + 22, x1), flat_y)], fill=MUTED, width=6)
    xx += 36
lab_f = f("Bold", 30)
left(x0, flat_y + 16, "주가 — 그대로", lab_f, MUTED)

steps = 4
step_w = (x1 - x0) // steps
prev_sy = flat_y
for i in range(steps):
    sx0 = x0 + i * step_w
    sx1 = sx0 + step_w
    sy = flat_y - (i + 1) * 22
    d.line([(sx0, prev_sy), (sx0, sy)], fill=VIOLET, width=8)
    d.line([(sx0, sy), (sx1, sy)], fill=VIOLET, width=8)
    prev_sy = sy
env_lab = "환율 — 오르면"
bb = lab_f.getbbox(env_lab)
left(x1 - (bb[2] - bb[0]), prev_sy - (bb[3]-bb[1]) - 14, env_lab, lab_f, VIOLET)
dev_bot = flat_y + 40

# ── 4. 헤드라인(「포착」 확정 썸네일 문구, 무수정) — 좌측 정렬, 2줄
hf = f("Bold", 70)
h1_bot = left(M, dev_bot + 55, "주가는 그대로인데,", hf, INK)
h2_bot = left(M, h1_bot + 22, "세금은 환율 때문에 달라집니다", hf, CORAL)

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/19.png")
print("saved 19.png  k_bot=%d kw2_bot=%d dev_bot=%d h2_bot=%d canvas=%d" %
      (k_bot, kw2_bot, dev_bot, h2_bot, S))
