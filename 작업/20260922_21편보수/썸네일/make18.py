# -*- coding: utf-8 -*-
"""/18 연금저축 세액공제·중도해지 썸네일 — 2026-09-24 「지면」 재제작(D-146 재배정).

「포착」 지침(06_썸네일문구_18.md) 그대로 구현 — 문구 무수정, 모든 텍스트는
그 문서에 있는 표현(확정 제목·확정 썸네일 문구·본문 근거 직접 인용)만 쓴다.

배경색 재배정 사유(「지면」이 직접 처리, D-105 §「지면」 자율):
  「진행」의 최초 배정값은 RGB(48,32,18) 다크 엄버-브라운이었다. 그런데 같은
  배치에서 이미 완료된 `/12`(54,28,16 다크 버넌엄버)·`/16`(52,40,14 다크
  초콜릿골드)과 채널차 최대 6~8에 불과해 검사3(채널차≥30) 기준에 크게
  미달한다 — 사실상 같은 색을 세 번 찍는 꼴이다. 「지면」이 그 턴 안에서
  직접 후보를 재탐색해 기존 10장(`/2·5·6·7·8·11·12·13·16·17`) 전부와
  채널차 최소 46 이상을 확보하는 다크 웜차콜(78,70,62 — 무채색에 가까운
  중성 웜톤, R≈G>B로 남색과 무관)로 교체했다. 정렬축(중앙)·주제어 위치
  (상단) 배정은 그대로 따른다.

레이아웃(중앙정렬·주제어 상단):
  1. 킥커 — 확정 제목 앞부분("연금저축 900만원 채우면") 그대로.
  2. 주제어 "연금저축" — 이 장 전체에서 가장 큰 글자(회장 공통사항 직결).
  3. 퍼센트 링(도형) — 본문 65행 실측 세율 16.5%. 오르내리는 그래프가 아닌
     단일 세율값 강조(데이터 계열 없음).
  4. 캡션 — 본문 65행 직접 인용 구절("중도에 해지하거나 인출하면").
  5. 헤드라인(확정 썸네일 문구, 무수정) "빼는 순간, / 16.5%를 다시
     뱉어냅니다" — 2행, "16.5%"만 강조색.

직전 5장(`/11` 아이보리앰버·좌, `/12` 버넌엄버·좌, `/13` 웜그레이지·좌,
`/16` 초콜릿골드·좌, `/17` 스카이시안·우) 대조: 다섯 장 모두 좌/우 정렬인데
`/18`은 이 배치에서 유일한 **중앙 정렬**. 배경도 다크 웜차콜로 다섯 장 중
누구와도 겹치지 않는다(아래 검사3 계산 참조). 그래픽 장치(퍼센트 링)는
다섯 장에 없는 형태.
"""
from PIL import Image, ImageDraw, ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S, M = 1080, 72
BG     = (78, 70, 62)     # 다크 웜차콜(토프) — 재배정. 남색 아님(R≈G>B, 저채도)
CREAM  = (238, 233, 224)
MUTED  = (176, 168, 156)
RUST   = (214, 120, 70)   # 강조 — 세액공제 반환(16.5%) 경고색
RING_BG = (100, 92, 82)

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)
CX = S / 2

def cen(top, t, fo, col):
    bb = fo.getbbox(t)
    w = bb[2] - bb[0]
    d.text((CX - w / 2 - bb[0], top - bb[1]), t, font=fo, fill=col)
    return top + (bb[3] - bb[1])

def cen_multi(top, segs, fo):
    """segs: [(text, color), ...] 한 줄, 여러 색. 폭 합산 뒤 중앙정렬."""
    widths = []
    maxh = 0
    for t, _ in segs:
        bb = fo.getbbox(t)
        widths.append(bb[2] - bb[0])
        maxh = max(maxh, bb[3] - bb[1])
    gap = 6
    total = sum(widths) + gap * (len(segs) - 1)
    x = CX - total / 2
    bot = top
    for (t, col), w in zip(segs, widths):
        bb = fo.getbbox(t)
        d.text((x - bb[0], top - bb[1]), t, font=fo, fill=col)
        bot = max(bot, top + (bb[3] - bb[1]))
        x += w + gap
    return bot

# ── 1. 킥커(확정 제목 앞부분, 무수정)
kf = f("Bold", 34)
k_bot = cen(100, "연금저축 900만원 채우면", kf, MUTED)

# ── 2. 주제어 — 이 장의 최대 글자
qf = f("ExtraBold", 232)
q_bot = cen(k_bot + 26, "연금저축", qf, CREAM)

# ── 3. 퍼센트 링(도형) — 본문 65행 세율 16.5%
ring_cy = q_bot + 55 + 120
rad = 120
d.ellipse([CX - rad, ring_cy - rad, CX + rad, ring_cy + rad], outline=RING_BG, width=22)
d.arc([CX - rad, ring_cy - rad, CX + rad, ring_cy + rad], -90, -90 + 360 * 0.165, fill=RUST, width=22)
rf = f("ExtraBold", 58)
bb = rf.getbbox("16.5%")
d.text((CX - (bb[2] - bb[0]) / 2 - bb[0], ring_cy - (bb[3] - bb[1]) / 2 - bb[1]), "16.5%", font=rf, fill=CREAM)
ring_bot = ring_cy + rad + 45

# ── 4. 캡션(본문 65행 직접 인용)
cf = f("Bold", 36)
c_bot = cen(ring_bot, "중도에 해지하거나 인출하면", cf, MUTED)

# ── 5. 헤드라인(확정 썸네일 문구, 무수정) — 2행
hf = f("Bold", 64)
h1_bot = cen(c_bot + 36, "빼는 순간,", hf, CREAM)
h2_bot = cen_multi(h1_bot + 20, [("16.5%", RUST), ("를 다시 뱉어냅니다", CREAM)], hf)

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/18.png")
print("saved 18.png  k_bot=%d q_bot=%d ring_bot=%d c_bot=%d h2_bot=%d canvas=%d" %
      (k_bot, q_bot, ring_bot, c_bot, h2_bot, S))
