# -*- coding: utf-8 -*-
"""4장 자기검사 — 핵심어 비율 + C58 축소 판독본 생성.
분모 정의(「지면」): 그 장에 그려진 **글자**의 잉크 행 높이 최댓값.
도형(밑줄·구분선·패널·캡슐)은 글자가 아니므로 분모에서 제외한다.
글자와 도형이 같은 행에 겹치는 경우(=/5 패널, /8 캡슐)는 글자색만 분리해 잰다."""
from PIL import Image
import os
D = "/home/user/webtest/작업/20260922_21편보수/썸네일/"
for n in ("2", "5", "6", "8"):
    im = Image.open(D + n + ".png").convert("RGB")
    for px in (58, 120):
        im.resize((px, px), Image.LANCZOS).save(D + "검사_C%d_%s.png" % (px, n))
    print(n, im.size)
