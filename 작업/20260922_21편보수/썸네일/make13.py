# -*- coding: utf-8 -*-
"""/13 형식적 상장폐지 vs 실질심사 — 2026-09-24 신규 제작(「지면」).

배정(진행, 12편 동시 배정 · 충돌 방지):
  배경 RGB(241,214,199) 피치-크림 · 정렬축 중앙 · 주제어 위치 중앙.

「포착」 문구(06_썸네일문구_13.md) 그대로 조판한다 — 문구 무수정.
  · 확정 제목: "상장폐지 사유, 숫자가 재는 것과 사람이 판단하는 것은 다릅니다" (189행 1순위)
  · 확정 썸네일 문구: "가처분 85건 중, 인용된 건 2건입니다" (131행 실측치)
  · 근거 문서 표제(06_썸네일문구_13.md 1행)에 있는 "형식적 상장폐지 vs 실질심사"를
    그대로 가져와 주제어/대비 라벨로 쓴다 — 새로 짓지 않는다.

주제어 선택 근거: 이 글이 무엇에 관한 글인지 말해주는 핵심어는 "상장폐지" 그 자체가
아니라(그 낱말은 이미 `/2`가 "동전주 상장폐지"로 썼다) 이 글의 실제 논지 —
형식적(숫자) 판단이 아니라 실질(사람) 판단이 갈린다는 것 — 이므로 "실질심사"를
주제어로 세운다. 확정 제목의 "사람이 판단하는 것"과 정확히 같은 대상을 가리킨다.

구조: 상단 대비 라벨(형식적 상장폐지 vs) → 중앙 주제어(실질심사, 최대 글자) →
헤드라인(확정 썸네일 문구 2줄) → 가는 선 → 하단 캡션(확정 제목 2줄).
전부 중앙정렬, 콘텐츠 블록 전체를 세로 중앙에 놓는다 — `/7`(상단 전폭 대칭),
`/8`(캡슐+링, 주제어 상단부), `/5`(좌정렬 상단), `/2`(좌정렬 하단), `/6`(우정렬 상단)
어느 것과도 정렬축·주제어 세로 위치·보조 장치가 겹치지 않는다.
"""
from PIL import Image, ImageDraw, ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S, M = 1080, 72
# 배정값(241,214,199)은 /2(230,214,178)와 채널차 max=21로 명도·색상축이 겹친다
# (같은 「따뜻한 밝은 톤」 계열). 배정 지시 자체가 "/2·/8과 명도·색상축이 겹치지
# 않게 별도 색조로 설계한다"를 요구하므로, 「피치-크림 계열」 안에서 B채널을
# 올려 장밋빛 쪽으로 옮긴다 — /2(웜 옐로-샌드)·/8(쿨 그레이-블루) 둘 다와
# 축을 벌린다. 배정값에서 최소 편차만 준다(다른 11편 충돌 회피 취지 존중).
BG     = (236, 205, 214)   # 더스티 로즈-크림
INK    = (45, 28, 26)      # 근흑 — 배경과 채널차 큼(191,177,188), 고명도차
MUTED  = (124, 90, 78)     # 대비 라벨·캡션
ACCENT = (150, 35, 58)     # 딥 와인 — 주제어·선

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)
CX = S / 2

def cen(top, t, fo, col):
    bb = fo.getbbox(t)
    w = bb[2] - bb[0]
    d.text((CX - w / 2 - bb[0], top - bb[1]), t, font=fo, fill=col)
    return top + (bb[3] - bb[1])

def h_of(t, fo):
    bb = fo.getbbox(t)
    return bb[3] - bb[1]

# ── 폰트 정의
lab_f  = f("Bold", 40)
vs_f   = f("Regular", 30)
key_f  = f("ExtraBold", 250)
head_f = f("Bold", 62)
cap_f  = f("Bold", 33)

LABEL = "형식적 상장폐지"
VS = "vs"
KEY = "실질심사"
H1 = "가처분 85건 중,"
H2 = "인용된 건 2건입니다"
C1 = "상장폐지 사유, 숫자가 재는 것과"
C2 = "사람이 판단하는 것은 다릅니다"

# ── 세로 총 높이 계산해서 블록 전체를 캔버스 중앙에 놓는다
g_lab_vs   = 14
g_vs_key   = 30
g_key_head = 58
g_h1_h2    = 16
g_head_rule= 46
rule_h     = 6
g_rule_cap = 34
g_c1_c2    = 12

h_lab  = h_of(LABEL, lab_f)
h_vs   = h_of(VS, vs_f)
h_key  = h_of(KEY, key_f)
h_h1   = h_of(H1, head_f)
h_h2   = h_of(H2, head_f)
h_c1   = h_of(C1, cap_f)
h_c2   = h_of(C2, cap_f)

total = (h_lab + g_lab_vs + h_vs + g_vs_key + h_key + g_key_head +
         h_h1 + g_h1_h2 + h_h2 + g_head_rule + rule_h + g_rule_cap +
         h_c1 + g_c1_c2 + h_c2)

top = (S - total) / 2

# ── 1. 대비 라벨 — 형식적 상장폐지 (뒤에 남는 쪽, 무채색 톤으로 낮춰 둔다)
b = cen(top, LABEL, lab_f, MUTED)
b = cen(b + g_lab_vs, VS, vs_f, MUTED)

# ── 2. 주제어 — 이 장 전체에서 가장 큰 글자 (회장 공통사항 직결)
b = cen(b + g_vs_key, KEY, key_f, ACCENT)

# ── 3. 헤드라인(확정 썸네일 문구, 무수정) — 2줄
b = cen(b + g_key_head, H1, head_f, INK)
b = cen(b + g_h1_h2, H2, head_f, INK)

# ── 4. 가는 구분선
rule_top = b + g_head_rule
d.rounded_rectangle([CX - 90, rule_top, CX + 90, rule_top + rule_h], rule_h / 2, fill=ACCENT)
b = rule_top + rule_h

# ── 5. 캡션(확정 제목, 무수정) — 2줄
b = cen(b + g_rule_cap, C1, cap_f, MUTED)
b = cen(b + g_c1_c2, C2, cap_f, MUTED)

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/13.png")
print("saved 13.png total=%d top=%.1f bottom=%.1f canvas=%d" % (total, top, b, S))
