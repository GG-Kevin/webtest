#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""그림 2장을 코드로 그린다(ImageMagick convert 그리기 명령, 숫자는 calc.py compute에서 가져온다). 메타데이터는 -strip으로 지운다."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.dont_write_bytecode = True
from calc import compute, fl10, PENSION_MAX, PENSION_MAX_OLD  # noqa: E402

FONT = "WenQuanYi-Zen-Hei"
INK, MUTED, GRID = "#16212e", "#5b6670", "#e3e7ea"
NET, INS, TAX = "#0a6350", "#8fd0bb", "#b7c0c8"


def run(args, out):
    cmd = ["convert"] + args + ["-strip", "-define", "png:exclude-chunks=date,time,tEXt,zTXt,iTXt", out]
    subprocess.run(cmd, check=True)


def text(x, y, s, size=24, color=INK):
    return ["-gravity", "NorthWest", "-fill", color, "-pointsize", str(size), "-annotate", f"+{x}+{y}", s]


def fig1():
    W, H = 1200, 675
    sal = [30, 40, 50, 60, 80, 100, 150]
    a = ["-size", f"{W}x{H}", "xc:white", "-font", FONT]
    a += text(50, 30, "연봉별 월 세전 급여가 실수령·4대보험·세금으로 나뉘는 모습(2026년 10월 3일 원문 기준)", 27)
    a += text(50, 76, "식대 비과세 월 20만원 · 공제대상가족 본인 1명 · 막대 길이는 월 세전 급여", 20, MUTED)
    lx, x0, x1, y, bh, gap = 50, 200, 900, 126, 50, 18
    top = compute(150_000_000, 200_000, 1, 0)["월세전"]
    for s in sal:
        r = compute(s * 1_000_000, 200_000, 1, 0)
        ins = r["국민연금"] + r["건강보험"] + r["장기요양"] + r["고용보험"]
        tax = r["소득세"] + r["지방소득세"]
        sc = (x1 - x0) / top
        w_net, w_ins, w_tax = r["월실수령"] * sc, ins * sc, tax * sc
        lab = "1억 5천만원" if s == 150 else ("1억원" if s == 100 else f"{s // 10}천만원")
        a += text(lx, y + 12, lab, 22)
        xa = x0
        for w, col in [(w_net, NET), (w_ins, INS), (w_tax, TAX)]:
            a += ["-fill", col, "-draw", f"rectangle {xa:.0f},{y} {xa + w:.0f},{y + bh}"]
            xa += w
        a += text(int(xa) + 14, y + 4, f"실수령 {r['월실수령'] // 10_000:,}만원", 21)
        a += text(int(xa) + 14, y + 30, f"공제 {r['공제합계'] // 10_000:,}만원", 17, MUTED)
        y += bh + gap
    ly = H - 42
    for k, (lab, col) in enumerate([("실수령", NET), ("4대보험 본인 부담", INS), ("소득세+지방소득세", TAX)]):
        x = 50 + k * 280
        a += ["-fill", col, "-draw", f"rectangle {x},{ly} {x + 26},{ly + 22}"]
        a += text(x + 36, ly - 2, lab, 20)
    a += text(900, ly - 2, "만원 아래는 버림", 18, MUTED)
    run(a, os.path.join(HERE, "01_대표.png"))


def fig2():
    W, H = 1200, 560
    vals = [("2025년 7~12월", fl10(PENSION_MAX_OLD * 90 // 2000), "요율 9% · 상한 637만원"),
            ("2026년 1~6월", fl10(PENSION_MAX_OLD * 95 // 2000), "요율 9.5% · 상한 637만원"),
            ("2026년 7월부터", fl10(PENSION_MAX * 95 // 2000), "요율 9.5% · 상한 659만원")]
    a = ["-size", f"{W}x{H}", "xc:white", "-font", FONT]
    a += text(50, 30, "기준소득월액 상한에 걸리는 사람의 국민연금 본인 부담(한 달)", 28)
    a += text(50, 78, "1월에는 보험료율이, 7월에는 기준소득월액 상한이 올랐습니다(국민연금공단 안내, 10원 미만 버림)", 20, MUTED)
    x0, y0, bw, gap, top = 170, 470, 220, 120, 330_000
    for i, (lab, v, note) in enumerate(vals):
        x = x0 + i * (bw + gap)
        h = 300 * v / top
        a += ["-fill", NET if i == 2 else INS, "-draw", f"rectangle {x},{y0 - h:.0f} {x + bw},{y0}"]
        a += text(x + 30, int(y0 - h) - 40, f"{v:,}원", 26)
        a += text(x + 20, y0 + 14, lab, 22)
        a += text(x + 10, y0 + 46, note, 17, MUTED)
    a += ["-stroke", INK, "-strokewidth", "2", "-draw", f"line 120,{y0} 1150,{y0}", "-stroke", "none"]
    run(a, os.path.join(HERE, "02_국민연금.png"))


if __name__ == "__main__":
    fig1()
    fig2()
    print("그림 2장 저장")
