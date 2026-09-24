# -*- coding: utf-8 -*-
"""/18 연금저축 세액공제 중도해지 — 2026-09-24 「지면」 신규 제작(12편 배치).

「포착」 지침(06_썸네일문구_18.md) 그대로 구현 — 문구 무수정.
  · 주제어 "연금저축"을 이 장의 최대 글자로. 확정 제목("연금저축 900만원
    채우면...")에 이미 있는 말.
  · 킥커 "연금저축 900만원 채우면"은 확정 제목 앞부분을 그대로 잘라 옮긴 것.
  · 그래픽 장치: 링(도형) 안에 "16.5%"(본문 65행 실측치) — 중도해지 시
    다시 뱉어내는 기타소득세율 하나를 강조하는 단일 원형 표시. 오르내리는
    그래프 아님(시점별 계열이 없는 단일 세율값).
  · 헤드라인(확정 썸네일 문구) "빼는 순간, / 16.5%를 다시 뱉어냅니다" 무수정.

직전 다섯 장(/11 아이보리앰버·좌, /12 버넌엄버·우, /13 웜그레이지·좌,
/16 초콜릿골드·좌, /17 스카이시안·우) 대조: /18은 다크 올리브(색상축 다름)·
좌측정렬(글자 배치는 /13·/16과 같은 좌측이나 배경 명도·장치가 다르다 —
/13은 라이트+막대비율, /16은 다크초콜릿+무한고리, /18은 다크올리브+퍼센트링)·
그래픽 장치가 여섯 장 중 유일한 "퍼센트 링".
"""
from PIL import Image, ImageDraw, ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S, M = 1080, 72
BG     = (40, 44, 18)     # 다크 올리브 — 남색 아님(G가 최대 채널, 옐로그린 계열)
CREAM  = (238, 240, 220)
GREEN  = (90, 180, 150)   # 링 강조색 — 라임/노랑 아님(청록 쪽으로 당김)
RUST   = (214, 120, 70)
MUTED  = (150, 152, 110)

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)

def put(x, top, t, fo, col):
    bb = fo.getbbox(t)
    d.text((x - bb[0], top - bb[1]), t, font=fo, fill=col)
    return x + (bb[2] - bb[0]), top + (bb[3] - bb[1])

# ── 1. 킥커 (확정 제목 앞부분, 무수정)
_, k_bot = put(M, 88, "연금저축 900만원 채우면", f("Bold", 34), MUTED)

# ── 2. 주제어 — 이 장의 최대 글자
_, key_bot = put(M, k_bot + 24, "연금저축", f("ExtraBold", 230), CREAM)

# ── 3. 퍼센트 링(도형) — 본문 65행 세율(16.5%), 키워드 아래 줄에 배치(겹침 방지)
ring_cx = M + 150
ring_cy = key_bot + 56 + 128
rad = 128
d.ellipse([ring_cx - rad, ring_cy - rad, ring_cx + rad, ring_cy + rad], outline=(70, 74, 40), width=22)
# 진행 호(16.5% 분만 강조 — 360*0.165=59.4도)
d.arc([ring_cx - rad, ring_cy - rad, ring_cx + rad, ring_cy + rad], -90, -90 + 360 * 0.165, fill=RUST, width=22)
pf = f("ExtraBold", 62)
bb = pf.getbbox("16.5%")
d.text((ring_cx - (bb[2] - bb[0]) / 2 - bb[0], ring_cy - (bb[3] - bb[1]) / 2 - bb[1]), "16.5%", font=pf, fill=CREAM)
ring_bot = ring_cy + rad + 22

body_bot = max(key_bot, ring_bot)

# ── 4. 헤드라인 (「포착」 확정 썸네일 문구, 무수정) — 2줄, 주제어보다 작게
hf = f("Bold", 62)
_, h1_bot = put(M, body_bot + 56, "빼는 순간,", hf, CREAM)
x = M
for seg, col in [("16.5%", RUST), ("를 다시 뱉어냅니다", CREAM)]:
    x, h2_bot = put(x, h1_bot + 22, seg, hf, col)

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/18.png")
print("saved 18.png  k_bot=%d key_bot=%d ring_bot=%d h2_bot=%d" %
      (k_bot, key_bot, ring_bot, h2_bot))
