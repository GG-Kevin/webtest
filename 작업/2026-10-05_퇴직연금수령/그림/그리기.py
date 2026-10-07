#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""그림 2장을 코드로 그린다(ImageMagick convert 그리기 명령, 숫자는 calc.py에서 가져온다). 메타데이터는 -strip으로 지운다."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.dont_write_bytecode = True
from calc import retirement_tax, pension_tax, with_local, EOK, MAN  # noqa: E402

FONT = "WenQuanYi-Zen-Hei"
INK, MUTED, A, B, GRID = "#16212e", "#5b6670", "#b7c0c8", "#0a6350", "#e3e7ea"


def run(args, out):
    cmd = ["convert"] + args + ["-strip", "-define", "png:exclude-chunks=date,time,tEXt,zTXt,iTXt", out]
    subprocess.run(cmd, check=True)


def text(x, y, s, size=24, color=INK):
    return ["-gravity", "NorthWest", "-fill", color, "-pointsize", str(size), "-annotate", f"+{x}+{y}", s]


def fig1():
    W, H = 1200, 675
    p = 3 * EOK
    vals = [with_local(retirement_tax(p)["퇴직소득세"]), pension_tax(p, 10, local=True),
            pension_tax(p, 20, local=True), pension_tax(p, 30, local=True)]
    labels = ["일시금", "10년 연금", "20년 연금", "30년 연금"]
    top = 25_000_000
    x0, y0, x1, y1 = 120, 560, 1150, 170
    a = ["-size", f"{W}x{H}", "xc:white", "-font", FONT]
    a += text(60, 40, "퇴직급여 3억원(근속 20년)을 받는 방법별 세금 합계", 36)
    a += text(60, 94, "지방소득세 포함 · 운용수익 0 가정 · 연금은 해마다 같은 금액", 24, MUTED)
    for t in range(0, top + 1, 5_000_000):
        y = y0 - (y0 - y1) * t / top
        a += ["-stroke", GRID, "-strokewidth", "1", "-draw", f"line {x0},{y:.0f} {x1},{y:.0f}", "-stroke", "none"]
        a += text(24, int(y) - 12, f"{t // MAN:,}만", 18, MUTED)
    gw = (x1 - x0) / len(vals)
    bw = 130
    for i, (lab, v) in enumerate(zip(labels, vals)):
        cx = x0 + gw * i + gw / 2
        h = (y0 - y1) * v / top
        col = A if i == 0 else B
        a += ["-fill", col, "-draw", f"rectangle {cx - bw / 2:.0f},{y0 - h:.0f} {cx + bw / 2:.0f},{y0}"]
        a += text(int(cx - 70), int(y0 - h) - 34, f"{v:,}원", 20, INK)
        a += text(int(cx - len(lab) * 12), y0 + 14, lab, 24)
    a += ["-stroke", INK, "-strokewidth", "2", "-draw", f"line {x0},{y0} {x1},{y0}", "-stroke", "none"]
    a += text(60, 628, "소득세법 제129조 제1항 제5호의3·지방세법 제103조의13, 2026년 10월 3일 원문 기준 계산", 20, MUTED)
    run(a, os.path.join(HERE, "01_대표.png"))


def fig2():
    W, H = 1200, 560
    a = ["-size", f"{W}x{H}", "xc:white", "-font", FONT]
    a += text(60, 36, "55세에 받을 수 있게 된 IRP를 60세에 처음 받을 때 — 두 가지 연차", 32)
    x0, cell = 230, 85
    ages = list(range(55, 66))
    for i, age in enumerate(ages):
        a += text(x0 + i * cell + 22, 110, f"{age}세", 20, MUTED)
    rows = [("연금수령연차", "한도를 정함", [i + 1 for i in range(len(ages))], A),
            ("실제 수령연차", "감면 비율을 정함", [None] * 5 + [i + 1 for i in range(len(ages) - 5)], B)]
    for r, (name, role, nums, col) in enumerate(rows):
        y = 160 + r * 130
        a += text(40, y + 12, name, 24)
        a += text(40, y + 46, role, 18, MUTED)
        for i, n in enumerate(nums):
            bx = x0 + i * cell
            if n is None:
                a += ["-fill", "#f3f4f5", "-draw", f"rectangle {bx + 4},{y} {bx + cell - 4},{y + 70}"]
                a += text(bx + 16, y + 22, "안 받음", 16, MUTED)
            else:
                a += ["-fill", col, "-draw", f"rectangle {bx + 4},{y} {bx + cell - 4},{y + 70}"]
                a += text(bx + 26, y + 18, f"{n}", 26, "white" if col == B else INK)
    a += text(60, 438, "· 60세 첫해: 한도는 6년차로 평가액의 24%, 감면은 1년차로 퇴직소득세의 70%", 22)
    a += text(60, 474, "· 연금수령연차는 시행령 제40조의2 제4항, 실제 수령연차는 시행령 제187조의3 제1항", 22)
    a += text(60, 510, "· 2026년 10월 3일 국가법령정보센터 원문 기준", 20, MUTED)
    run(a, os.path.join(HERE, "02_연차.png"))


if __name__ == "__main__":
    fig1()
    fig2()
    print("그림 2장 저장")
