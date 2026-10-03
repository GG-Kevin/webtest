#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""발행.html 조립 — 계산기 쪽(도구/계산기/틀.html의 틀: 감싸는 div·style·입력칸·calcCompute 스크립트)을 채운다.

본문 글은 원고.md 한 곳에만 쓰고, 문단·표·그림·목차·저자 박스의 꼴은 본사 변환 함수(convert_text)를 빌려 만든 뒤
틀 안에 넣는다. 계산기 입력칸은 두 번째 h2(계산기 절) 끝에 넣고, 스크립트 상수는 calc.py --js 출력을 그대로 쓴다.
실행: python3 조립.py  (같은 폴더의 발행.html을 새로 쓴다)
"""
import importlib.util
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("conv", os.path.join(ROOT, "도구", "원고_HTML변환.py"))
conv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(conv)

TPL = open(os.path.join(ROOT, "도구", "계산기", "틀.html"), encoding="utf-8").read()
STYLE = re.search(r"(?s)<style>.*?</style>", TPL).group(0)

body = conv.convert_text(open(os.path.join(HERE, "원고.md"), encoding="utf-8").read())
lines = body.split("\n")
head = [l for l in lines[:2] if l.startswith("<!--")]
rest = "\n".join(lines[len(head):])

FORM = """<form class="mp-form" id="mp-calc-form" onsubmit="return false">
  <label for="mp-in-1">연봉(원, 1년 세전 총액)</label><input id="mp-in-1" name="salary" type="number" inputmode="numeric" value="50000000">
  <label for="mp-in-2">한 달 비과세 금액(원, 식대 등)</label><input id="mp-in-2" name="nontax" type="number" inputmode="numeric" value="200000">
  <label for="mp-in-3">공제대상가족 수(본인 포함, 명)</label><input id="mp-in-3" name="family" type="number" inputmode="numeric" value="1">
  <label for="mp-in-4">그중 8세 이상 20세 이하 자녀 수(명)</label><input id="mp-in-4" name="kids" type="number" inputmode="numeric" value="0">
  <p><button type="button" id="mp-calc-go">계산하기</button></p>
  <div class="mp-out" id="mp-calc-out" aria-live="polite">스크립트가 돌지 않는 화면에서는 첫 표의 가까운 연봉 줄이 답입니다.</div>
</form>"""
assert '<h2 id="q3"' in rest
rest = rest.replace('<h2 id="q3"', FORM + '\n<h2 id="q3"', 1)

consts = subprocess.run([sys.executable, "calc.py", "--js"], cwd=HERE, capture_output=True, text=True, check=True).stdout

SCRIPT = """<script>
/* calcCompute: calc.py compute(**입력)과 같은 공식·같은 열쇠. document를 건드리지 않는 순수 함수(대조 스크립트가 node로 부른다). */
""" + consts + """var RATES = { pension: [95, 1000], pensionMin: 410000, pensionMax: 6590000, health: [719, 10000], care: [9448, 1000000], employ: [18, 1000],
  child1: 20830, child2: 45830, childMore: 33330, top: 10000000 };
var OVER = [[10000000, 14000000, 0, 3430, 10000, 25000], [14000000, 28000000, 1397000, 3724, 10000, 0], [28000000, 30000000, 6610600, 3920, 10000, 0],
  [30000000, 45000000, 7394600, 40, 100, 0], [45000000, 87000000, 13394600, 42, 100, 0], [87000000, null, 31034600, 45, 100, 0]];
var ROWS = null;
function rowsOf() {
  if (ROWS) return ROWS;
  ROWS = []; var lo = 0, prev = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
  TABLE.split(";").forEach(function (r) {
    var p = r.split(","), v = []; lo += parseInt(p[0], 36);
    for (var i = 0; i < 11; i++) { prev[i] += parseInt(p[i + 1], 36); v.push(prev[i] * 10); }
    ROWS.push([lo, v]);
  });
  return ROWS;
}
function fl10(x) { return Math.floor(x / 10) * 10; }
function tableTax(m, fam) {
  var R = rowsOf();
  if (m < R[0][0] * 1000) return 0;
  if (m < RATES.top) {
    for (var i = R.length - 1; i >= 0; i--) { if (R[i][0] * 1000 <= m) return R[i][1][fam - 1]; }
  }
  var base = TOPROW[fam - 1];
  if (m === RATES.top) return base;
  for (var k = 0; k < OVER.length; k++) {
    var o = OVER[k];
    if (o[1] === null || m <= o[1]) return fl10(base + o[2] + Math.floor((m - o[0]) * o[3] / o[4]) + o[5]);
  }
  return 0;
}
function childCut(kids) {
  if (kids <= 0) return 0;
  if (kids === 1) return RATES.child1;
  return RATES.child2 + (kids - 2) * RATES.childMore;
}
function calcCompute(input) {
  var salary = Math.floor(Number(input.salary) || 0), nontax = Math.floor(Number(input.nontax) || 0);
  var family = Math.floor(Number(input.family) || 0), kids = Math.floor(Number(input.kids) || 0);
  family = Math.min(Math.max(family, 1), 11);
  kids = Math.min(Math.max(kids, 0), family - 1);
  var gross = Math.floor(salary / 12);
  var m = Math.max(gross - Math.max(nontax, 0), 0);
  var pbase = m > 0 ? Math.min(Math.max(Math.floor(m / 1000) * 1000, RATES.pensionMin), RATES.pensionMax) : 0;
  var pension = fl10(Math.floor(pbase * RATES.pension[0] / (RATES.pension[1] * 2)));
  var health = fl10(Math.floor(m * RATES.health[0] / (RATES.health[1] * 2)));
  var care = fl10(Math.floor(health * RATES.care[0] * RATES.health[1] / (RATES.care[1] * RATES.health[0])));
  var employ = fl10(Math.floor(m * RATES.employ[0] / (RATES.employ[1] * 2)));
  var tax = Math.max(tableTax(m, family) - childCut(kids), 0);
  var local = fl10(Math.floor(tax / 10));
  var total = pension + health + care + employ + tax + local, net = gross - total;
  return { "월세전": gross, "국민연금": pension, "건강보험": health, "장기요양": care, "고용보험": employ,
           "소득세": tax, "지방소득세": local, "공제합계": total, "월실수령": net, "연실수령": net * 12 };
}
if (typeof document !== "undefined") {
  (function () {
    var go = document.getElementById("mp-calc-go"), out = document.getElementById("mp-calc-out");
    if (!go || !out) return;
    var NAMES = { "월세전": "월 세전", "국민연금": "국민연금", "건강보험": "건강보험", "장기요양": "장기요양보험", "고용보험": "고용보험",
                  "소득세": "소득세", "지방소득세": "지방소득세", "공제합계": "공제 합계", "월실수령": "월 실수령", "연실수령": "1년 실수령(월 × 12)" };
    function fmt(n) { return (Math.round(n)).toLocaleString("ko-KR") + "원"; }
    go.addEventListener("click", function () {
      var f = document.getElementById("mp-calc-form"), input = {};
      Array.prototype.forEach.call(f.querySelectorAll("input"), function (el) { input[el.name] = Number(el.value || 0); });
      var r = calcCompute(input), rows = [];
      for (var k in r) { if (Object.prototype.hasOwnProperty.call(r, k)) rows.push("<tr><td>" + (NAMES[k] || k) + "</td><td>" + fmt(r[k]) + "</td></tr>"); }
      out.innerHTML = rows.length ? "<table><caption>계산 결과(첫 표와 같은 식)</caption><tbody>" + rows.join("") + "</tbody></table>" : "첫 표의 가까운 연봉 줄이 답입니다.";
    });
  })();
}
</script>"""

page = "\n".join(head) + "\n<div class=\"mp-calc-page\">\n" + STYLE + "\n" + rest.rstrip("\n") + "\n" + SCRIPT + "\n</div>\n"
open(os.path.join(HERE, "발행.html"), "w", encoding="utf-8").write(page)
print(f"썼다: 발행.html ({len(page):,}자)")
