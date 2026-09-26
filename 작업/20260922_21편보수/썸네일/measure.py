#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D-136 1차 배치 3장 — 잉크 시작좌표(구조적 좌표) 실측.
18장 기각값(x=113, y=230-231, 레이아웃 함수 1개)과 대조.
재현: python3 measure.py
"""
from PIL import Image

FILES = {
    "27": "/home/user/webtest/작업/20261005_휴장/06_썸네일.png",
    "2":  "/home/user/webtest/작업/20260922_21편보수/썸네일/2.png",
    "8":  "/home/user/webtest/작업/20260922_21편보수/썸네일/8.png",
}

def ink_start(path):
    """배경색(2,2 픽셀 기준)과 다른 최초 픽셀의 (x,y) — 좌상단부터 스캔."""
    img = Image.open(path).convert("RGB")
    px = img.load()
    w, h = img.size
    bg = px[2, 2]
    for y in range(h):
        for x in range(w):
            if px[x, y] != bg:
                return (x, y)
    return None

def full_ink_bbox(path):
    img = Image.open(path).convert("RGB")
    px = img.load()
    w, h = img.size
    bg = px[2, 2]
    minx, miny, maxx, maxy = w, h, 0, 0
    found = False
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            if px[x, y] != bg:
                found = True
                if x < minx: minx = x
                if y < miny: miny = y
                if x > maxx: maxx = x
                if y > maxy: maxy = y
    return (minx, miny, maxx, maxy) if found else None

if __name__ == "__main__":
    print("| 글 | 잉크 시작(x,y) — 좌상단 첫 비배경 픽셀 | 전체 잉크 bbox |")
    print("|---|---|---|")
    for k, p in FILES.items():
        s = ink_start(p)
        b = full_ink_bbox(p)
        print(f"| /{k} | {s} | {b} |")
    print()
    print("18장 기각값(참고): x=113 (18/18 동일) · y=230-231 (18/18 동일)")
