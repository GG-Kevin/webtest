#!/usr/bin/env python3
"""그림 2장을 ImageMagick 그리기 명령(MVG)으로 그려 PNG(메타데이터 제거)로 쓴다. 숫자는 calc.py에서 가져온다."""
import os
import runpy
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
C = runpy.run_path(os.path.join(HERE, "..", "calc.py"), run_name="fig")
won = C["won"]
FONT = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"


def esc(s):
    return s.replace("\\", "\\\\").replace("'", "\\'")


def text(x, y, s, size=22, fill="#16212e", anchor="start", weight="normal"):
    sw = "stroke '%s' stroke-width 0.6 " % fill if weight == "bold" else "stroke none "
    ta = {"start": "start", "end": "end", "middle": "middle"}[anchor]
    return f"push graphic-context font '{FONT}' font-size {size} fill '{fill}' {sw}text-anchor {ta} text {x},{y} '{esc(s)}' pop graphic-context"


def rect(x, y, w, h, fill):
    return f"push graphic-context fill '{fill}' stroke none rectangle {x},{y} {x + w:.1f},{y + h} pop graphic-context"


def fig1():
    W, H = 1200, 675
    P = C["P2025"]
    ks = sorted(P)
    left, right, top, row = 150, 1010, 130, 52
    mx = P[90]
    out = [text(40, 58, "가구 순자산 분위 경계값 (2025년 3월 말)", 34, weight="bold"),
           text(40, 98, "P90 = 상위 10%가 시작하는 금액 · 국가데이터처 가계금융복지조사 부록 통계표 12", 20, "#3d4852")]
    for i, k in enumerate(reversed(ks)):
        y = top + i * row
        w = (right - left) * P[k] / mx
        color = "#0a6350" if k == 90 else ("#7fa99b" if k == 80 else "#c9d6d1")
        out.append(text(left - 16, y + 30, f"P{k}", 24, anchor="end", weight="bold" if k == 90 else "normal"))
        out.append(rect(left, y + 6, w, 34, color))
        out.append(text(left + w + 12, y + 31, won(P[k]), 23, "#0a6350" if k == 90 else "#16212e",
                        weight="bold" if k == 90 else "normal"))
    out.append(text(40, H - 22, "가구 단위(개인 아님) · 순자산 = 자산 - 부채", 18, "#5b6670"))
    return W, H, "\n".join(out)


def fig2():
    W, H = 1200, 620
    rows = C["AGE"]
    mx = max(m for _, m, _ in rows)
    left, right, top, row = 230, 980, 130, 72
    out = [text(40, 58, "가구주 연령대별 순자산 평균과 중앙값 (2025년 3월 말)", 32, weight="bold"),
           rect(40, 80, 22, 18, '#0a6350'), text(70, 96, "평균", 20),
           rect(140, 80, 22, 18, '#b8c7c1'), text(170, 96, "중앙값(가운데 가구)", 20)]
    for i, (name, mean, med) in enumerate(rows):
        y = top + i * row
        out.append(text(left - 16, y + 34, name, 22, anchor="end"))
        wm = (right - left) * mean / mx
        wd = (right - left) * med / mx
        out.append(rect(left, y + 4, wm, 26, '#0a6350'))
        out.append(text(left + wm + 10, y + 25, won(mean), 19))
        out.append(rect(left, y + 34, wd, 26, '#b8c7c1'))
        out.append(text(left + wd + 10, y + 55, won(med), 19, "#3d4852"))
    out.append(text(40, H - 18, "국가데이터처 가계금융복지조사 부록 통계표 8 · 연령대별 상위 10% 경계값은 공개 통계표에 없음", 18, "#5b6670"))
    return W, H, "\n".join(out)


for name, f in (("01_대표", fig1), ("02_연령대", fig2)):
    W, H, mvg = f()
    pp = os.path.join(HERE, name + ".png")
    subprocess.run(["convert", "-size", f"{W}x{H}", "xc:white", "-draw", mvg, "-strip",
                    "-define", "png:exclude-chunks=date,time,tEXt,zTXt,iTXt", pp], check=True)
    print("썼다:", pp)
