# -*- coding: utf-8 -*-
"""/20 국민연금 조기수령 vs 피부양자(건강보험) — 2026-09-24 「지면」 신규 제작(2차 배치).

「포착」 확정문(06_썸네일문구_20.md) 그대로 구현 — 문구·제목 무수정, 새 문장 안 지음.
모든 텍스트는 확정 제목(289행 1순위) 또는 확정 썸네일 문구의 부분 발췌다.

「진행」 배정: 배경 RGB(24,36,18) 다크 올리브 계열 · 정렬축 우측 · 주제어 위치 중앙.
  → 배경 하나만 「지면」이 이 턴 안에서 자율 조정했다(회장 2026-09-23: "정방형 외에는
    모두 자율"). 배정값(24,36,18)을 실측해 보니 이미 완료된 /18(40,44,18)과
    max채널차 16, /16(52,40,14)과 28, /6(20,42,35)과 17로 검사3(≥30) 미달이었다
    (검사3 절 참조). 같은 "다크 올리브·어두운 톤" 성격은 유지하되 휘도를 더 낮추고
    G축을 더 지배적으로 만들어 (8,34,2)로 조정 — 근흑에 가까운 딥모스올리브.
    정렬축(우측)·주제어 위치(중앙) 배정은 그대로 지켰다.

구조:
  · 킥커(우측정렬, 작게) — 확정 제목 앞부분 발췌 "국민연금 조기수령"
  · 주제어(중앙정렬, 최대 글자) — 확정 썸네일 문구에 있는 "피부양자"
    (이 글의 클릭 유인은 "조기수령 자체"가 아니라 "피부양자 탈락"이라는 반전이므로
    이 반전 명사를 주제어로 세웠다. 확정 문구 원문에서 그대로 가져왔다.)
  · 숫자 배지(우측정렬, 캡슐) — 확정 문구의 기준 금액 발췌 "연 2,000만원"
  · 헤드라인(우측정렬, 2줄, 무수정) — "연 2,000만원 넘으면," / "건강보험 피부양자에서 빠집니다"
  · 우측 스파인(세로선) — 우측 정렬축을 시각으로 지지. 22장 틀의 좌측정렬·밑줄과
    다른 방향(우측)이라 그 틀과 헷갈리지 않는다.
"""
from PIL import Image, ImageDraw, ImageFont

F = "/home/user/webtest/자산/폰트/Pretendard-%s.otf"
def f(w, s): return ImageFont.truetype(F % w, s)

S, M = 1080, 72
BG     = (8, 34, 2)        # 근흑 딥모스올리브 — /6·/16·/18과 채널차 확보(검사3 참조)
CREAM  = (238, 232, 205)
MUTED  = (150, 168, 130)   # 킥커용 세이지
ACCENT = (214, 122, 58)    # 웜 테라코타 — 노란 배지 아님(22장 틀 회피)
SPINE  = ACCENT

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)
RX = S - M          # 우측정렬 기준선(텍스트 오른쪽 끝)
CX = S / 2           # 주제어 중앙정렬 기준

def right(top, t, fo, col):
    """오른쪽 끝을 RX에 맞춰 그린다."""
    bb = fo.getbbox(t)
    w = bb[2] - bb[0]
    d.text((RX - w - bb[0], top - bb[1]), t, font=fo, fill=col)
    return top + (bb[3] - bb[1])

def right_mixed(top, parts, fo_map):
    """parts=[(text,font,color),...]를 한 줄로, 전체를 RX에 우측정렬."""
    widths = []
    for t, fo, col in parts:
        bb = fo.getbbox(t)
        widths.append((bb[2] - bb[0], bb))
    total_w = sum(w for w, _ in widths)
    x = RX - total_w
    max_h = 0
    for (t, fo, col), (w, bb) in zip(parts, widths):
        d.text((x - bb[0], top - bb[1]), t, font=fo, fill=col)
        x += w
        max_h = max(max_h, bb[3] - bb[1])
    return top + max_h

def cen(cx, top, t, fo, col):
    bb = fo.getbbox(t)
    w = bb[2] - bb[0]
    d.text((cx - w / 2 - bb[0], top - bb[1]), t, font=fo, fill=col)
    return top + (bb[3] - bb[1])

def cen_mid(cx, cy, t, fo, col):
    bb = fo.getbbox(t)
    w = bb[2] - bb[0]; h = bb[3] - bb[1]
    d.text((cx - w / 2 - bb[0], cy - h / 2 - bb[1]), t, font=fo, fill=col)

# ── 세로 스파인(우측 정렬축 시각 지지) ───────────────────────────
SPINE_X = S - 40
d.line([(SPINE_X, 150), (SPINE_X, 900)], fill=SPINE, width=5)

# ── 1. 킥커 — 확정 제목 앞부분 발췌, 우측정렬 ──────────────────
kf = f("Bold", 34)
k_bot = right(150, "국민연금 조기수령", kf, MUTED)

# ── 2. 주제어 — 확정 썸네일 문구의 반전 명사, 중앙정렬·최대 글자 ─
subf = f("ExtraBold", 260)
sub_bot = cen(CX, k_bot + 44, "피부양자", subf, CREAM)

# ── 3. 숫자 배지 — 확정 문구의 기준 금액 발췌, 우측정렬 캡슐 ─────
badge_f = f("Bold", 50)
bt = "연 2,000만원"
bb = badge_f.getbbox(bt)
btw, bth = bb[2] - bb[0], bb[3] - bb[1]
pad_x, pad_y = 30, 18
bw_badge = btw + pad_x * 2
bh_badge = bth + pad_y * 2
badge_top = sub_bot + 46
d.rounded_rectangle(
    [RX - bw_badge, badge_top, RX, badge_top + bh_badge],
    bh_badge / 2, fill=ACCENT
)
cen_mid(RX - bw_badge / 2, badge_top + bh_badge / 2, bt, badge_f, (20, 12, 4))
badge_bot = badge_top + bh_badge

# ── 4. 헤드라인(확정 썸네일 문구, 무수정) — 2줄, 우측정렬 ────────
hf = f("Bold", 66)
h1_top = badge_bot + 58
h1_bot = right_mixed(h1_top, [
    ("연 ", hf, CREAM), ("2,000만원", hf, ACCENT), (" 넘으면,", hf, CREAM)
], None)
h2_bot = right(h1_bot + 24, "건강보험 피부양자에서 빠집니다", hf, CREAM)

img.save("/home/user/webtest/작업/20260922_21편보수/썸네일/20.png")
print("saved 20.png  k_bot=%d sub_bot=%d badge_bot=%d h2_bot=%d canvas=%d" %
      (k_bot, sub_bot, badge_bot, h2_bot, S))
