#!/usr/bin/env python3
"""그림 2장을 ImageMagick 그리기 명령(MVG)으로 그려 PNG(메타데이터 제거)로 쓴다. 숫자는 calc.py에서 가져온다."""
import os
import runpy
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
C = runpy.run_path(os.path.join(HERE, "..", "calc.py"), run_name="fig")
FONT = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"


def esc(s):
    return s.replace("\\", "\\\\").replace("'", "\\'")


def text(x, y, s, size=22, fill="#16212e", anchor="start", weight="normal"):
    sw = "stroke '%s' stroke-width 0.6 " % fill if weight == "bold" else "stroke none "
    return f"push graphic-context font '{FONT}' font-size {size} fill '{fill}' {sw}text-anchor {anchor} text {x},{y} '{esc(s)}' pop graphic-context"


def rect(x, y, w, h, fill):
    return f"push graphic-context fill '{fill}' stroke none rectangle {x:.1f},{y:.1f} {x + w:.1f},{y + h:.1f} pop graphic-context"


def fig1():
    W, H = 1200, 675
    _, rows = C["table_brackets"]()
    out = [text(40, 58, "주택청약 해지 때 추징 6%, 세율 구간마다 무게가 다릅니다", 33, weight="bold"),
           text(40, 98, "연 300만원 넣고 소득공제 120만원 받은 1년분 · 조세특례제한법 제87조 제2항·제7항", 20, "#3d4852")]
    base, top = 560, 150
    mx = max(max(r[3], r[4]) for r in rows)
    scale = (base - top - 40) / mx
    gx = [210, 560, 910]
    labels = ["세율 6% 구간", "세율 15% 구간", "세율 24% 구간"]
    for i, r in enumerate(rows):
        x = gx[i]
        for j, (v, col) in enumerate(((r[3], "#0a6350"), (r[4], "#b0413e"))):
            h = v * scale
            bx = x + j * 120
            out.append(rect(bx, base - h, 100, h, col))
            out.append(text(bx + 50, base - h - 12, f"{v // 10000:,}만 {v % 10000 // 1000}천원" if v % 10000 else f"{v // 10000:,}만원", 20, anchor="middle", weight="bold"))
        out.append(text(x + 110, base + 34, labels[i], 22, anchor="middle"))
    out.append(rect(40, 618, 22, 22, "#0a6350"))
    out.append(text(70, 636, "공제로 실제 줄어든 세금", 20))
    out.append(rect(330, 618, 22, 22, "#b0413e"))
    out.append(text(360, 636, "가입 5년 안 해지 때 추징세액", 20))
    out.append(text(1160, 636, "2026년 10월 3일 법령·국세청 원문 기준 계산", 17, "#5b6670", anchor="end"))
    return W, H, "\n".join(out)


def fig2():
    W, H = 1200, 600
    _, rows = C["table_cases"]()
    rows = [r for r in rows if r[0] == 100000]
    out = [text(40, 58, "월 10만원씩 넣다가 해지하면: 세전 이자와 추징세액", 31, weight="bold"),
           text(40, 96, "소득공제를 해마다 받았다고 가정 · 이자는 월 단위 단리 근사 · 주택도시기금 약정이율", 19, "#3d4852")]
    left, right, top, row = 200, 1080, 140, 100
    mx = max(max(r[4], r[5]) for r in rows)
    scale = (right - left - 140) / mx
    for i, r in enumerate(rows):
        y = top + i * row
        out.append(text(left - 16, y + 44, f"{r[1]}회 넣고", 22, anchor="end"))
        for j, (v, col, lab) in enumerate(((r[4], "#0a6350", "이자"), (r[5], "#b0413e", "추징"))):
            w = max(v * scale, 2)
            yy = y + 10 + j * 36
            out.append(rect(left, yy, w, 30, col))
            out.append(text(left + w + 10, yy + 23, f"{lab} {v:,}원", 19, weight="bold"))
    out.append(text(40, H - 20, "72회(가입 5년 지남) 해지는 추징 0원 · 2026년 10월 3일 원문 기준 계산", 18, "#5b6670"))
    return W, H, "\n".join(out)


for name, f in (("01_대표", fig1), ("02_해지시점", fig2)):
    W, H, mvg = f()
    pp = os.path.join(HERE, name + ".png")
    subprocess.run(["convert", "-size", f"{W}x{H}", "xc:white", "-draw", mvg, "-strip",
                    "-define", "png:exclude-chunks=date,time,tEXt,zTXt,iTXt", pp], check=True)
    print("썼다:", pp)
