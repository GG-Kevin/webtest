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
    return f"push graphic-context fill '{fill}' stroke none rectangle {x},{y} {x + w:.1f},{y + h} pop graphic-context"


def vline(x, y1, y2, color, dash=True):
    d = "stroke-dasharray 8 6 " if dash else ""
    return f"push graphic-context stroke '{color}' stroke-width 2 {d}fill none line {x:.1f},{y1} {x:.1f},{y2} pop graphic-context"


def fig1():
    W, H = 1200, 675
    rows = [C["schedule_row"](n, d, h) for n, d, h in C["SCHEDULES"]]
    left, right, top, row = 250, 1080, 150, 78
    mx_m = 24
    scale = (right - left) / mx_m
    out = [text(40, 58, "실업급여 180일, 근무 형태별로 걸리는 기간", 34, weight="bold"),
           text(40, 98, "피보험 단위기간 = 보수를 받은 날(유급 주휴 포함) · 개근 가정 · 고용보험법 제40조·제41조", 20, "#3d4852")]
    bottom = top + row * len(rows) - 10
    for k, (m, label) in enumerate(((C["BASE_MONTHS"], "18개월: 기본 기준기간"), (C["SHORT_BASE_MONTHS"], "24개월: 주 15시간 미만·주 2일 이하"))):
        x = left + m * scale
        out.append(vline(x, top - 4, bottom + 8 + 30 * k, "#b0413e"))
        out.append(text(x - 8, bottom + 30 + 30 * k, label, 18, "#b0413e", anchor="end"))
    for i, r in enumerate(rows):
        y = top + i * row
        w = r["개월"] * scale
        color = "#0a6350" if r["기준기간"] == 18 else "#c08a2b"
        out.append(text(left - 16, y + 36, r["근무"], 21, anchor="end"))
        out.append(rect(left, y + 12, w, 36, color))
        out.append(text(left + w + 10, y + 38, f"{r['개월']}개월", 21, weight="bold"))
    out.append(text(40, H - 22, "2026년 10월 3일 국가법령정보센터 원문 기준 · 무급 휴무일·결근이 있으면 더 걸림", 18, "#5b6670"))
    return W, H, "\n".join(out)


def fig2():
    W, H = 1200, 600
    start, end, span, rows = C["claim_rows"]()
    left, right, top, row = 230, 1060, 140, 78
    scale = (right - left) / span
    out = [text(40, 58, "실업 신고가 늦으면 수급기간 안에 남는 날", 32, weight="bold"),
           text(40, 96, f"이직일 2026년 10월 31일 가정 · 수급기간 {span}일 · 대기기간 7일 반영 · 고용보험법 제48조·제49조", 19, "#3d4852")]
    for i, r in enumerate(rows):
        y = top + i * row
        w = r["남는날"] * scale
        out.append(text(left - 16, y + 36, r["시점"], 21, anchor="end"))
        out.append(rect(left, y + 12, w, 36, "#0a6350" if i == 0 else "#7fa99b"))
        out.append(text(left + w + 10, y + 38, f"{r['남는날']}일", 21, weight="bold"))
    out.append(text(40, H - 20, "2026년 10월 3일 국가법령정보센터 원문 기준 계산", 18, "#5b6670"))
    return W, H, "\n".join(out)


for name, f in (("01_대표", fig1), ("02_신고시점", fig2)):
    W, H, mvg = f()
    pp = os.path.join(HERE, name + ".png")
    subprocess.run(["convert", "-size", f"{W}x{H}", "xc:white", "-draw", mvg, "-strip",
                    "-define", "png:exclude-chunks=date,time,tEXt,zTXt,iTXt", pp], check=True)
    print("썼다:", pp)
