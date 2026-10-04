#!/usr/bin/env python3
"""1080×1080 썸네일 — 편마다 다른 색·구성. 새 정보(숫자)를 가장 크게, 제목을 반복하지 않는다.
사용: python3 도구/썸네일_만들기.py  → 발행/패키지/<슬러그>/썸네일.png
폰트: 자산/폰트/Pretendard (OFL). 렌더: 설치된 Chromium."""
import os, subprocess, glob, html

ROOT = os.getcwd()
FONT = f"file://{ROOT}/자산/폰트/Pretendard"

# kind: bars(가로 막대 비교) | stack(한 줄 쌓기)
SPECS = [
 dict(slug="2026-10-04_혼인증여공제", bg="#EEE6D8", ink="#2A2418", c=["#1F6B4F", "#B24B3A"],
      big="485만원", phrase="2억을 받아도 내는 세금", kind="stack",
      items=[("면제 1억 5천만원", 150, "#1F6B4F"), ("과세 5천만원", 50, "#B24B3A")],
      cap="부모에게 받은 2억원 · 신고세액공제 뒤 · 받은 돈의 2.4%"),
 dict(slug="2026-10-04_순자산상위10", bg="#DCE6F1", ink="#14233A", c=["#9AAFC8", "#1F3A5F"],
      big="4.6배", phrase="상위 10% 문턱은 한가운데 가구의", kind="bars",
      items=[("한가운데 가구  2억 3,860만원", 23860, "#8EA6C4"), ("상위 10% 문턱  11억 20만원", 110020, "#1F3A5F")],
      cap="가계금융복지조사 · 2025년 3월 31일 기준"),
 dict(slug="2026-10-05_구직급여상한액", bg="#F4E4D1", ink="#2B1D10", c=["#0E6A63"],
      big="2,052원", phrase="월급 300만과 500만의 하루 차이", kind="bars",
      items=[("월급 300만원  66,048원", 66048, "#7FB5AE"), ("월급 500만원  68,100원", 68100, "#0E6A63")],
      cap="구직급여 하루치 · 하한과 상한 · 2026년 이직 기준"),
 dict(slug="2026-10-05_실업급여조건", bg="#E4E0F1", ink="#1F1838", c=["#5B45A8"],
      big="20.7개월", phrase="주 2일 근무로 180일을 채우려면", kind="bars", bigsize=200,
      items=[("주 5일 근무  6.9개월", 6.9, "#B7ABE0"), ("주 2일 근무  20.7개월", 20.7, "#5B45A8")],
      cap="근무한 날 180일 기준 · 개근 가정"),
 dict(slug="2026-10-05_퇴직소득세계산", bg="#D8E9E4", ink="#10302B", c=["#0F6B5E"],
      big="8.4배", phrase="같은 퇴직금 1억원, 세금 차이", kind="bars",
      items=[("근속 5년  1,036만원", 1036, "#0F6B5E"), ("근속 10년  426만원", 426, "#4E9D90"), ("근속 20년  123만원", 123, "#9CCBC2")],
      cap="지방소득세 포함 · 2026년 소득세법 기준"),
 dict(slug="2026-10-05_퇴직연금수령", bg="#F3DDD6", ink="#33150F", c=["#8C3B2E"],
      big="86만원", phrase="일시금 123만원이 10년 연금이면", kind="bars",
      items=[("일시금  123만 2,000원", 123.2, "#D79C8E"), ("10년 연금  86만 2,400원", 86.24, "#8C3B2E")],
      cap="근속 20년 · 퇴직금 1억원 · 지방소득세 포함"),
 dict(slug="2026-10-06_4대보험계산", bg="#E7EDD4", ink="#1F2A0E", c=["#4F6B1B"],
      big="291,522원", phrase="월급 300만원, 매달 빠지는 돈", kind="stack", bigsize=190,
      items=[("국민연금 142,500", 142500, "#4F6B1B"), ("건강 107,850", 107850, "#7E9B3E"), ("고용 27,000", 27000, "#B2C77A"), ("요양 14,172", 14172, "#D5E0A9")],
      cap="근로자 몫 4개 항목 · 2026년 10월 3일 요율 기준"),
 dict(slug="2026-10-06_보금자리론신혼", bg="#F7ECC9", ink="#35290A", c=["#8A6400"],
      big="7천만원", phrase="10월 19일부터 부부 중 1명 소득 기준", kind="bars", bigsize=190,
      items=[("10월 18일까지  부부 합산 8,500만원", 8500, "#D6B766"), ("10월 19일부터  1명 7,000만원", 7000, "#8A6400")],
      cap="신혼부부 소득 요건 · 2026년 10월 3일 공사 보도자료 기준"),
 dict(slug="2026-10-06_연봉실수령액", bg="#E1E6EC", ink="#162033", c=["#2B4C7E", "#B24B3A"],
      big="약 60만원", phrase="연봉 5천만원에서 매달 빠지는 돈", kind="stack", bigsize=150,
      items=[("실수령 3,571,586", 3571586, "#2B4C7E"), ("공제 595,080", 595080, "#B24B3A")],
      cap="세전 월 4,166,666원 · 4대보험과 소득세·지방소득세"),
 dict(slug="2026-10-06_주택청약해지", bg="#EBDDE9", ink="#2E1429", c=["#6B2D5C"],
      big="18만원", phrase="5년 안에 해지하면 내는 추징세액", kind="bars",
      items=[("받은 소득공제 효과  7만 2천원", 72, "#C7A3BE"), ("추징  18만원", 180, "#6B2D5C")],
      cap="연 300만원 납입 · 소득세율 6% 구간 · 조특법 제87조"),
 dict(slug="2026-10-08_금통위일정", bg="#E3E9F3", ink="#14233A", c=["#1F3A5F"],
      big="2번", phrase="남은 기준금리 결정, 10월과 11월", kind="stack", bigsize=250,
      items=[("10월 22일(목)", 1, "#1F3A5F"), ("11월 26일(목)", 1, "#6F8DB8")],
      cap="한국은행 일정 · 기준금리 연 3.00% · 10월 4일 기준"),
 dict(slug="2026-10-10_부가세예정신고", bg="#F5E8D6", ink="#2E1F0C", c=["#9A5B12"],
      big="10월 26일", phrase="2기 부가세 예정신고·납부 마감", kind="bars", bigsize=200,
      items=[("법인  예정신고서 직접 제출", 100, "#9A5B12"), ("개인 일반과세  1기 납부세액의 절반을 고지", 50, "#D9AE74")],
      cap="25일이 일요일이라 26일 월요일 · 국세청 세무일정"),
 dict(slug="2026-10-12_중간예납", bg="#DDEBE3", ink="#0F2D22", c=["#14684A"],
      big="2월 1일", phrase="11월 30일에 다 못 내면 분납 마감은", kind="bars", bigsize=230,
      items=[("납부기한  11월 30일 (10월 4일부터 57일)", 57, "#7DB79E"), ("분납 기한  2027년 2월 1일 (120일)", 120, "#14684A")],
      cap="종합소득세 중간예납 · 1천만원 초과분 분납"),
 dict(slug="2026-10-14_종부세납부", bg="#F0E1E1", ink="#341515", c=["#8A2F2F"],
      big="250만원", phrase="넘으면 6개월 나눠 낼 수 있습니다", kind="stack", bigsize=230,
      items=[("12월 15일까지 300만원", 300, "#8A2F2F"), ("2027년 6월 15일까지 180만원", 180, "#D39A9A")],
      cap="고지세액 400만원 가정 · 농어촌특별세 20% 포함"),
 dict(slug="2026-10-07_월세공제", bg="#E6EFE0", ink="#16301A", c=["#2F6B35"],
      big="102만원", phrase="월세 월 50만원이면 줄어드는 세금", kind="bars", bigsize=220,
      items=[("총급여 5,500만원 이하  17%  102만원", 102, "#2F6B35"), ("5,500만~8,000만원  15%  90만원", 90, "#93BE8F")],
      cap="월세 월 50만원 × 12개월 · 조세특례제한법 제95조의2"),
 dict(slug="2026-10-07_디딤돌조건", bg="#E2ECF4", ink="#12293D", c=["#1D5C8C"],
      big="5억원", phrase="디딤돌대출 집값 상한, 소득은 6천만원 이하", kind="bars", bigsize=240,
      items=[("일반  한도 2억원", 20000, "#9DBFD8"), ("생애최초  한도 2억 4천만원", 24000, "#5C93BC"), ("2자녀·신혼  한도 3억 2천만원", 32000, "#1D5C8C")],
      cap="기본형 기준 · 주택도시기금 · 2026년 10월 5일"),
 dict(slug="2026-10-07_전세보증보험", bg="#F3E7D8", ink="#33200E", c=["#9A5A1C"],
      big="90%", phrase="계약기간 절반 전에 가입, 주택가격 이내", kind="bars", bigsize=250,
      items=[("주택가격  100%", 100, "#E0BF98"), ("보증 가능 범위  90% 이내", 90, "#9A5A1C")],
      cap="HUG 전세보증금반환보증 · 2026년 10월 5일 기준"),
 dict(slug="2026-10-07_전세대출한도", bg="#E8E4F2", ink="#241B3D", c=["#54409A"],
      big="2억원", phrase="수도권 1주택자 전세대출 한도", kind="bars", bigsize=240,
      items=[("1주택자 상한  2억원", 20000, "#54409A"), ("신혼 버팀목  2억 5천만원", 25000, "#A99BD6"), ("HUG 일반(전세 4억)  3억 2천만원", 32000, "#CFC6E9")],
      cap="무주택자 보증금 80% 기준 · 2026년 10월 5일"),
]


def page(s):
    big = s.get("bigsize", 250)
    rows = ""
    if s["kind"] == "bars":
        mx = max(v for _, v, _ in s["items"])
        for lab, v, col in s["items"]:
            rows += f'<div class="row"><div class="lab">{html.escape(lab)}</div><div class="bar" style="width:{100*v/mx:.1f}%;background:{col}"></div></div>'
    else:
        tot = sum(v for _, v, _ in s["items"])
        segs = "".join(f'<div class="seg" style="width:{100*v/tot:.2f}%;background:{col}"></div>' for _, v, col in s["items"])
        legend = "".join(f'<div class="lg"><i style="background:{col}"></i>{html.escape(lab)}</div>' for lab, _, col in s["items"])
        rows = f'<div class="stack">{segs}</div><div class="legend">{legend}</div>'
    return f'''<!doctype html><meta charset="utf-8"><style>
@font-face{{font-family:P;font-weight:400;src:url("{FONT}-Regular.otf")}}
@font-face{{font-family:P;font-weight:700;src:url("{FONT}-Bold.otf")}}
@font-face{{font-family:P;font-weight:800;src:url("{FONT}-ExtraBold.otf")}}
html,body{{margin:0;width:1080px;height:1080px;overflow:hidden}}
body{{background:{s["bg"]};color:{s["ink"]};font-family:P;box-sizing:border-box;padding:96px 90px 80px;display:flex;flex-direction:column}}
.big{{white-space:nowrap;font-weight:800;font-size:{big}px;line-height:1;letter-spacing:-.02em;color:{s["c"][0] if s["kind"]=="stack" and len(s["c"])>1 else s["ink"]}}}
.ph{{font-weight:700;font-size:62px;line-height:1.25;margin-top:26px}}
.g{{margin-top:auto;padding-top:44px}}
.row{{margin-bottom:26px}} .lab{{font-weight:700;font-size:40px;margin-bottom:10px}}
.bar{{height:62px;border-radius:14px}}
.stack{{display:flex;height:120px;gap:6px}} .seg{{border-radius:14px}}
.legend{{display:flex;flex-wrap:wrap;gap:12px 30px;margin-top:22px;font-weight:700;font-size:36px}}
.lg i{{display:inline-block;width:26px;height:26px;border-radius:7px;margin-right:10px;vertical-align:-3px}}
.cap{{font-weight:400;font-size:34px;opacity:.78;margin-top:34px;line-height:1.4;border-top:3px solid {s["ink"]}33;padding-top:24px}}
</style><div class="big">{html.escape(s["big"])}</div><div class="ph">{html.escape(s["phrase"])}</div>
<div class="g">{rows}</div><div class="cap">{html.escape(s["cap"])}</div>'''


def main():
    ch = glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome")[0]
    for s in SPECS:
        d = f"발행/패키지/{s['slug']}"
        if not os.path.isdir(d):
            print("폴더 없음", d); continue
        tmp = f"/tmp/_th_{s['slug']}.html"
        open(tmp, "w", encoding="utf-8").write(page(s))
        raw = f"/tmp/_th_{s['slug']}.png"
        subprocess.run([ch, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                        f"--screenshot={raw}", "--window-size=1080,1240", f"file://{tmp}"], check=True, capture_output=True)
        subprocess.run(["convert", raw, "-crop", "1080x1080+0+0", "+repage", f"{d}/썸네일.png"], check=True)
        print("썸네일:", s["slug"])


main()
