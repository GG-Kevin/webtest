#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""그림 2장을 코드로 그린다(ImageMagick convert 그리기 명령, 숫자는 calc.py compute에서 가져온다). 메타데이터는 -strip으로 지운다."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.dont_write_bytecode = True
from calc import compute, MAN, EOK  # noqa: E402

FONT = "WenQuanYi-Zen-Hei"
INK, MUTED, A, B, GRID = "#16212e", "#5b6670", "#b7c0c8", "#0a6350", "#e3e7ea"


def run(args, out):
    cmd = ["convert"] + args + ["-strip", "-define", "png:exclude-chunks=date,time,tEXt,zTXt,iTXt", out]
    subprocess.run(cmd, check=True)


def text(x, y, s, size=24, color=INK, gravity="NorthWest"):
    return ["-gravity", gravity, "-fill", color, "-pointsize", str(size), "-annotate", f"+{x}+{y}", s, "-gravity", "NorthWest"]


def fig1():
    W, H = 1200, 675
    amounts = [5_000 * MAN, 1 * EOK, 15_000 * MAN, 2 * EOK, 3 * EOK]
    labels = ["5,000만원", "1억원", "1억 5,000만원", "2억원", "3억원"]
    no = [compute(a, in_window=False)["납부세액"] for a in amounts]
    yes = [compute(a)["납부세액"] for a in amounts]
    top = 40_000_000
    x0, y0, x1, y1 = 110, 560, 1150, 170  # 그래프 틀(y0 = 바닥)
    a = ["-size", f"{W}x{H}", "xc:white", "-font", FONT]
    a += text(60, 40, "부모에게 받은 금액별 증여세(성년 자녀, 신고세액공제 3% 반영)", 34)
    a += text(60, 92, "회색: 혼인 공제 없음 · 초록: 혼인신고일 앞뒤 2년 안(공제 1억원 추가)", 24, MUTED)
    for t in range(0, top + 1, 10_000_000):
        y = y0 - (y0 - y1) * t / top
        a += ["-stroke", GRID, "-strokewidth", "1", "-draw", f"line {x0},{y:.0f} {x1},{y:.0f}", "-stroke", "none"]
        a += text(20, int(y) - 12, f"{t // MAN:,}만", 18, MUTED)
    gw = (x1 - x0) / len(amounts)
    bw = 62
    for i, (lab, n, ycv) in enumerate(zip(labels, no, yes)):
        cx = x0 + gw * i + gw / 2
        for j, (v, col) in enumerate([(n, A), (ycv, B)]):
            bx = cx - bw - 4 if j == 0 else cx + 4
            h = (y0 - y1) * v / top
            if v > 0:
                a += ["-fill", col, "-draw", f"rectangle {bx:.0f},{y0 - h:.0f} {bx + bw:.0f},{y0}"]
            vs = "0원" if v == 0 else f"{v / MAN:,.0f}만원"
            a += text(int(bx) - 6, int(y0 - h) - 30, vs, 18, INK if j else MUTED)
        a += text(int(cx - len(lab) * 9.5), y0 + 14, lab, 22)
    a += ["-stroke", INK, "-strokewidth", "2", "-draw", f"line {x0},{y0} {x1},{y0}", "-stroke", "none"]
    a += text(60, 630, "상속세 및 증여세법 제26조·제53조·제53조의2·제69조, 2026년 10월 3일 원문 기준 계산", 20, MUTED)
    run(a, os.path.join(HERE, "01_대표.png"))


def fig2():
    W, H = 1200, 520
    a = ["-size", f"{W}x{H}", "xc:white", "-font", FONT]
    a += text(60, 36, "혼인 공제 기간과 기한 — 혼인신고일 2026년 10월 24일인 경우(예시)", 32)
    x0, x1, y = 100, 1100, 250
    # 4년 구간: 2024-10 ~ 2028-10
    a += ["-fill", "#d6ebe5", "-draw", f"rectangle {x0},{y - 40} {x1},{y + 40}"]
    a += ["-stroke", INK, "-strokewidth", "3", "-draw", f"line {x0},{y + 40} {x1},{y + 40}", "-stroke", "none"]
    mid = (x0 + x1) // 2
    a += ["-fill", B, "-draw", f"rectangle {mid - 3},{y - 40} {mid + 3},{y + 60}"]
    a += text(mid - 90, y - 110, "혼인신고일", 26, B)
    a += text(mid - 120, y - 80, "2026년 10월 24일", 22, B)
    a += text(x0 - 20, y + 60, "2024년 10월 무렵", 22)
    a += text(x1 - 170, y + 60, "2028년 10월 무렵", 22)
    a += text(x0 + 90, y - 15, "앞 2년", 26, INK)
    a += text(x1 - 230, y - 15, "뒤 2년", 26, INK)
    a += text(60, 380, "· 이 4년 사이에 직계존속에게 받은 증여에서 1억원을 더 뺍니다(제53조의2 제1항).", 22)
    a += text(60, 418, "· 신고기한은 받은 날이 속한 달의 말일부터 3개월 안입니다(제68조 제1항).", 22)
    a += text(60, 456, "· 혼인 전에 공제받고 2년 안에 혼인하지 않으면 수정신고 기한이 따로 있습니다(같은 조 제6항).", 22)
    run(a, os.path.join(HERE, "02_기간.png"))


if __name__ == "__main__":
    fig1()
    fig2()
    print("그림 2장 저장")
