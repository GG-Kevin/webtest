# -*- coding: utf-8 -*-
"""/25 유상증자(권리락 급락은 조정이지 매도가 아니다) 썸네일 — 2026-09-25 「지면」 재제작.

D-149 집행(사장·회장 지시):
  1. 낡은 비율식 검사(핵심어÷최대 ≥0.8) 폐기 — 이 산출물에서 안 쓴다.
  2. 새 검사는 165px 축소 실물 육안판정(아래 06_지면_25.md 참조). 비율식으로 안 돌아간다.
  3. 재제작 1장 — /25만. 문구(제목·썸네일 문구·본문 인용)는 「포착」 확정본에서
     한 글자도 새로 짓지 않는다. 06_썸네일문구_25.md의 [썸네일 문구]와
     18_제목_썸네일문구.md 391행 확정 제목만 원문으로 쓴다.
  5. 범주어 단독 금지 — "유상증자"만 있으면 정보 0(회장 지적: "유상증자 뭐?").
     확정 제목 "유상증자, 악재인지 아닌지는 '자금 용도' 한 칸에 있습니다"에서
     이미 있는 연결어 "악재인지 아닌지는"을 그대로 잘라 붙여 "유상증자, 악재인지
     아닌지는"이 한 문장처럼 읽히게 한다(/5 "관리종목 지정되면"과 같은 원리,
     새 카피 아님 — 확정 제목 원문을 그대로 옮긴 것).

레이아웃 재설계 이유:
  구판(9/24)은 유상증자(240pt) 바로 아래 64pt 헤드라인 2줄로 점프했다.
  165px 실물에서 유상증자만 읽히고 나머지는 뭉개졌다 — 회장이 지적한 것과 동일 병.
  이번 판은 4단으로 나눈다.
    1) 유상증자(핵심어, 최대 글자)
    2) 악재인지 아닌지는(연결어, 확정 제목 원문) — 1)과 이어 읽는 한 문장
    3) "20%"를 확정 썸네일 문구 첫 세그먼트로 분리해 색 배지에 크게(짧은 숫자라
       165px에서도 형태가 뭉개지지 않는다 — /5의 "50개/150개" 박스와 같은 원리)
    4) 나머지 확정 문구("급락, 사실은 매도가 아니라 조정입니다")를 문장 그대로,
       배지보다 작지만 연결어와 비슷한 크기로 둬 읽는 흐름을 끊지 않는다.
  구판의 캡션(본문 62행 인용)은 뺀다 — 헤드라인이 이미 "조정입니다"로 같은 내용을
  말하고 있어 165px에서는 중복인 채로 안 읽히기만 했다(지면 재량, 확정 문구 자체는
  건드리지 않음).
"""
from PIL import Image, ImageDraw, ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S = 1080
BG      = (96, 28, 20)     # 다크 브릭-마룬 — /5·/6과 채널차 30 이상 확보(구판과 동일 유지, 색 문제 아니었음)
CREAM   = (242, 233, 224)
ACCENT  = (224, 122, 66)   # 웜 테라코타
MUTED   = (216, 176, 152)  # 연결어용 — 크림보다 한 단 낮은 위계, 배경 대비는 유지
DARKTXT = (52, 20, 12)     # 배지(밝은 주황) 위에 올릴 어두운 글자

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)

def cen(cx, top, t, fo, col):
    bb = fo.getbbox(t)
    w = bb[2] - bb[0]
    d.text((cx - w / 2 - bb[0], top - bb[1]), t, font=fo, fill=col)
    return top + (bb[3] - bb[1])

CX = S / 2

# 구판(9/24)은 세로 717px만 채우고 아래 300px가 비어 165px 축소 시 글자가
# 실제보다 더 작게 눌렸다(캔버스 대비 콘텐츠 비율이 낮을수록 165px 환산 크기도
# 작아진다). 1.16배로 키워 캔버스를 채우고, 그만큼 165px에서의 실제 픽셀 크기도 키운다.
SC = 1.16
def sz(n): return int(round(n * SC))

# ── 1. 핵심어 "유상증자" — 이 장 전체에서 가장 큰 글자, 최상단
kf = f("ExtraBold", sz(172))
k_bot = cen(CX, sz(60), "유상증자", kf, CREAM)

# ── 2. 연결어 "악재인지 아닌지는" — 확정 제목(391행 1순위) 원문에서 그대로 옮김.
#       1)과 이어 "유상증자, 악재인지 아닌지는"으로 한 문장처럼 읽힌다.
cf = f("Bold", sz(58))
c_bot = cen(CX, k_bot + sz(14), "악재인지 아닌지는", cf, MUTED)

# 구분선(장식 — 글자 아님)
ly = c_bot + sz(34)
d.line([(CX - sz(250), ly), (CX + sz(250), ly)], fill=ACCENT, width=sz(8))

# ── 3. 통계 배지 "20%" — 확정 썸네일 문구("20% 급락, 사실은 매도가 아니라
#       조정입니다")의 첫 세그먼트. 짧은 숫자라 165px에서도 뭉개지지 않는다.
bf = f("ExtraBold", sz(148))
bb = bf.getbbox("20%")
bw = bb[2] - bb[0]
pad_x, pad_y = sz(52), sz(24)
panel_w = bw + pad_x * 2
panel_h = (bb[3] - bb[1]) + pad_y * 2
py0 = ly + sz(46)
px0 = CX - panel_w / 2
d.rounded_rectangle([px0, py0, px0 + panel_w, py0 + panel_h], sz(30), fill=ACCENT)
cen(CX, py0 + pad_y - bb[1], "20%", bf, DARKTXT)
badge_bot = py0 + panel_h

# ── 4. 나머지 확정 문구 — "급락, 사실은 매도가 아니라 조정입니다" 무수정,
#       배지 바로 아래, 2줄
hf = f("Bold", sz(56))
h_top = badge_bot + sz(44)
h1_bot = cen(CX, h_top, "급락, 사실은 매도가", hf, CREAM)
h2_bot = cen(CX, h1_bot + sz(16), "아니라 조정입니다", hf, CREAM)

# 하단 마감 점(장식)
dot_y = h2_bot + sz(70)
d.ellipse([CX - sz(7), dot_y, CX + sz(7), dot_y + sz(14)], fill=ACCENT)

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/25.png")
print("saved 25.png  k_bot=%d c_bot=%d ly=%d badge_bot=%d h2_bot=%d dot_y=%d canvas=%d" %
      (k_bot, c_bot, ly, badge_bot, h2_bot, dot_y, S))
