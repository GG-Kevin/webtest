#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""그림 2장을 코드로 그린다(ImageMagick convert 그리기 명령, 숫자는 calc.py compute에서 가져온다). 메타데이터는 -strip으로 지운다."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.dont_write_bytecode = True
from calc import compute, man, MAN, EOK  # noqa: E402

FONT = "WenQuanYi-Zen-Hei"
INK, MUTED, GRID = "#16212e", "#5b6670", "#e3e7ea"
COLS = ["#b7c0c8", "#5f9f8f", "#0a6350"]


def run(args, out):
    cmd = ["convert"] + args + ["-strip", "-define", "png:exclude-chunks=date,time,tEXt,zTXt,iTXt", out]
    subprocess.run(cmd, check=True)


def text(x, y, s, size=24, color=INK):
    return ["-gravity", "NorthWest", "-fill", color, "-pointsize", str(size), "-annotate", f"+{x}+{y}", s]


def fig1():
    W, H = 1200, 675
    pays = [5_000 * MAN, 1 * EOK, 3 * EOK]
    labels = ["퇴직급여 5,000만원", "퇴직급여 1억원", "퇴직급여 3억원"]
    years = [5, 10, 20]
    top = 70_000_000
    x0, y0, x1, y1 = 120, 545, 1150, 170
    a = ["-size", f"{W}x{H}", "xc:white", "-font", FONT]
    a += text(60, 36, "퇴직소득세 계산 결과 — 같은 퇴직급여도 근속연수가 길수록 세금이 줄어듭니다", 30)
    a += text(60, 88, "막대: 퇴직소득세 + 지방소득세 10% 합계(비과세 소득 없음) · 왼쪽부터 근속 5년·10년·20년", 22, MUTED)
    for t in range(0, top + 1, 10_000_000):
        y = y0 - (y0 - y1) * t / top
        a += ["-stroke", GRID, "-strokewidth", "1", "-draw", f"line {x0},{y:.0f} {x1},{y:.0f}", "-stroke", "none"]
        a += text(20, int(y) - 12, f"{t // MAN:,}만", 18, MUTED)
    gw = (x1 - x0) / len(pays)
    bw = 78
    for i, (p, lab) in enumerate(zip(pays, labels)):
        cx = x0 + gw * i + gw / 2
        for j, (n, col) in enumerate(zip(years, COLS)):
            v = compute(n, p)["합계"]
            bx = cx - 1.5 * bw - 6 + j * (bw + 6)
            h = (y0 - y1) * v / top
            if v > 0:
                a += ["-fill", col, "-draw", f"rectangle {bx:.0f},{y0 - h:.0f} {bx + bw:.0f},{y0}"]
            vs = "0원" if v == 0 else f"{v / MAN:,.0f}만원"
            a += text(int(bx) + 2, int(y0 - h) - 28, vs, 18)
            a += text(int(bx) + 22, y0 + 8, f"{n}년", 18, MUTED)
        a += text(int(cx - len(lab) * 10), y0 + 40, lab, 22)
    a += ["-stroke", INK, "-strokewidth", "2", "-draw", f"line {x0},{y0} {x1},{y0}", "-stroke", "none"]
    a += text(60, 630, "소득세법 제48조·제55조, 지방세법 제103조의13, 2026년 10월 3일 원문 기준 계산(원 미만 버림)", 20, MUTED)
    run(a, os.path.join(HERE, "01_대표.png"))


def fig2():
    W, H = 1200, 560
    r = compute(10, 1 * EOK)
    steps = [("퇴직소득금액", 1 * EOK), ("근속연수공제", r["근속연수공제"]), ("환산급여", r["환산급여"]), ("환산급여공제", r["환산급여공제"]),
             ("과세표준", r["과세표준"]), ("환산산출세액", r["환산산출세액"]), ("퇴직소득세", r["퇴직소득세"])]
    a = ["-size", f"{W}x{H}", "xc:white", "-font", FONT]
    a += text(60, 34, "퇴직소득세 계산 순서 7단계 — 근속 10년·퇴직급여 1억원 예시", 30)
    a += text(60, 82, "공제를 빼고, 1년 치로 늘리고(× 12 ÷ 근속연수), 세율을 곱한 뒤, 근속연수만큼 되돌립니다(÷ 12 × 근속연수)", 20, MUTED)
    bx, by, bw, bh, gap = 40, 150, 146, 150, 12
    for i, (name, v) in enumerate(steps):
        x = bx + i * (bw + gap)
        fill = "#d6ebe5" if i in (0, 2, 4) else ("#0a6350" if i == 6 else "#f1f3f4")
        a += ["-fill", fill, "-stroke", "#9aa5ae", "-strokewidth", "1", "-draw", f"roundrectangle {x},{by} {x + bw},{by + bh} 10,10", "-stroke", "none"]
        col = "white" if i == 6 else INK
        a += text(x + 12, by + 22, name, 20, col)
        a += text(x + 12, by + 70, man(v) if int(round(v)) % MAN == 0 else f"{int(round(v)):,}원", 20, col)
    notes = ["· 근속연수공제·환산급여공제: 소득세법 제48조 제1항 제1호·제2호", "· 환산급여 = (퇴직소득금액 - 근속연수공제) × 12 ÷ 근속연수",
             "· 세율은 종합소득과 같은 기본세율 6~45%(제55조 제1항), 마지막에 ÷ 12 × 근속연수(같은 조 제2항)",
             "· 개인지방소득세는 퇴직소득세의 10%를 따로 뗍니다(지방세법 제103조의13)"]
    for k, s in enumerate(notes):
        a += text(60, 340 + k * 40, s, 21)
    run(a, os.path.join(HERE, "02_순서.png"))


if __name__ == "__main__":
    fig1()
    fig2()
    print("그림 2장 저장")
