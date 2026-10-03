#!/usr/bin/env python3
"""실업급여(구직급여) 조건 — 180일 채우는 기간·신고 시점별 남는 수급기간·정당한 이직 사유 숫자 (표준 라이브러리만)

원문(모두 2026-10-03 국가법령정보센터에서 직접 열어 읽음 · 고용보험법 [시행 2026. 9. 18.] 법률 제21473호):
  - 고용보험법 제40조(구직급여의 수급 요건) ① 1호 「피보험 단위기간이 합산하여 180일 이상」 · ② 「기준기간은 이직일 이전 18개월」
      ② 1호 질병·부상 등으로 30일 이상 보수를 못 받으면 그 일수를 더함(3년 한도)
      ② 2호 1주 소정근로시간 15시간 미만·1주 소정근로일수 2일 이하 근로자 → 이직일 이전 24개월(24개월 중 90일 이상 그렇게 근로)
      https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=284449&joNo=0040&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  - 고용보험법 제41조(피보험 단위기간) ① 「보수 지급의 기초가 된 날을 합하여 계산」
      https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=284449&joNo=0041&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  - 고용보험법 제48조(수급기간) ① 이직일의 다음 날부터 12개월 내 · ② 임신·출산·육아 등 신고 시 연장(4년 한도)
      https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=284449&joNo=0048&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  - 고용보험법 제49조(대기기간) ① 실업의 신고일부터 7일간은 지급하지 않음
      https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=284449&joNo=0049&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  - 고용보험법 제10조(적용 제외) ② 65세 이후 고용(65세 전부터 유지하던 사람이 계속 고용된 경우 제외) → 실업급여 장 적용 안 함
      https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=284449&joNo=0010&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  - 고용보험법 시행령 제3조 ① 1개월 60시간 미만이거나 1주 15시간 미만 = 적용 제외 · ② 1호 3개월 이상 계속 근로하면 적용
      https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=288717&joNo=0003&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
  - 고용보험법 시행규칙 [별표 2] 근로자의 수급자격이 제한되지 아니하는 정당한 이직 사유(제101조제2항 관련, PDF)
      https://www.law.go.kr/LSW/flDownload.do?flSeq=169481947
  - 근로기준법 제55조 ① 1주에 평균 1회 이상의 유급휴일 · 제18조 ③ 1주 소정근로시간 15시간 미만이면 제55조 적용 안 함
      https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=290781&joNo=0055&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
      https://www.law.go.kr/LSW/lsSideInfoP.do?lsiSeq=290781&joNo=0018&joBrNo=00&docCls=jo&urlMode=lsScJoRltInfoR
기준일: 2026-10-03 국가법령정보센터 원문(현행 시행 2026-09-18판).

공식:
  - 한 주에 세는 날(k) = 소정근로일 수 + 유급 주휴일 1일(1주 소정근로시간 15시간 이상일 때만, 근로기준법 제55조·제18조③)
    · 「보수 지급의 기초가 된 날」(제41조)을 개근·유급 주휴 1일 가정으로 셈. 무급 휴무일은 세지 않음(가정)
  - 180일 채우는 주 수 = ceil(180 / k) · 달력 일수 = 주 수 × 7 · 달 수 = 달력 일수 ÷ (365/12), 소수 첫째 자리 반올림
  - 기준기간 = 18개월(1주 15시간 미만·주 2일 이하이면 24개월) → 그 안에 달력 일수가 들어가면 「채울 수 있음」
    · 18개월 ≈ 18 × 365/12 일, 24개월 ≈ 24 × 365/12 일(달력 근사)
  - 수급기간 = 이직일 다음 날 ~ 이직일 12개월 뒤 같은 날(제48조①)
  - 대기기간 = 실업 신고일부터 7일(신고일 포함, 제49조①) → 지급 대상 첫날 = 신고일 + 7일
  - 수급기간 안에 남는 날 = 수급기간 끝날 - 지급 대상 첫날 + 1
같은 입력이면 같은 출력이다. 원고 표의 숫자는 모두 이 출력에서 가져온다.
"""
import datetime as dt
import math

# ---- 원문 숫자 ----
UNIT_DAYS = 180          # 제40조①1 피보험 단위기간 180일 이상
BASE_MONTHS = 18         # 제40조② 기준기간 이직일 이전 18개월
SHORT_BASE_MONTHS = 24   # 제40조②2 초단시간 근로자 24개월
SHORT_MIN_DAYS = 90      # 제40조②2나 24개월 중 90일 이상
SHORT_HOURS = 15         # 제40조②2가 · 근로기준법 제18조③ 1주 15시간 미만
SHORT_DAYS = 2           # 제40조②2가 1주 소정근로일수 2일 이하
SICK_DAYS = 30           # 제40조②1 계속 30일 이상 보수 못 받음
SICK_CAP_YEARS = 3       # 제40조②1 3년 한도
CLAIM_MONTHS = 12        # 제48조① 12개월
CLAIM_CAP_YEARS = 4      # 제48조② 4년 한도
WAIT_DAYS = 7            # 제49조① 대기기간 7일
AGE = 65                 # 제10조② 65세
EXCL_MONTH_HOURS = 60    # 시행령 제3조① 1개월 60시간 미만
EXCL_CONT_MONTHS = 3     # 시행령 제3조②1 3개월 이상 계속 근로
MONTH_DAYS = 365 / 12
EX_JOIN_AGE, EX_LEAVE_AGE = 64, 66   # 가정
B2_ITEMS = 13            # 별표 2 마지막 호 번호
DAY_LABORER_RATIO = "3분의 1"  # 제40조①5가 근로일 수 3분의 1 미만

# 시행규칙 별표 2 숫자
B2 = {"기간_년": 1, "기간_개월": 2, "휴업_퍼센트": 70, "통근_시간": 3, "간호_일": 30, "자녀_세": 8, "자녀_학년": 2}

# ---- 독자 대입(가정) ----
SCHEDULES = [  # (근무 형태, 1주 소정근로일, 1주 소정근로시간)
    ("주 6일 · 하루 7시간", 6, 42),
    ("주 5일 · 하루 8시간", 5, 40),
    ("주 4일 · 하루 6시간", 4, 24),
    ("주 3일 · 하루 6시간", 3, 18),
    ("주 2일 · 하루 7시간", 2, 14),
]
LEAVE_DATE = dt.date(2026, 10, 31)   # 가정한 이직일(마지막 근무일)
REPORT_AFTER = [  # (설명, 실업 신고일)
    ("이직 3일 뒤", dt.date(2026, 11, 3)),
    ("이직 1개월 뒤", dt.date(2026, 11, 30)),
    ("이직 3개월 뒤", dt.date(2027, 1, 31)),
    ("이직 6개월 뒤", dt.date(2027, 4, 30)),
    ("이직 9개월 뒤", dt.date(2027, 7, 31)),
]


def add_months(d, n):
    y, m = divmod(d.month - 1 + n, 12)
    y += d.year
    m += 1
    last = [31, 29 if (y % 4 == 0 and (y % 100 or y % 400 == 0)) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
    return dt.date(y, m, min(d.day, last))


def schedule_row(name, days, hours):
    paid_holiday = 1 if hours >= SHORT_HOURS else 0
    k = days + paid_holiday
    weeks = math.ceil(UNIT_DAYS / k)
    cal = weeks * 7
    months = round(cal / MONTH_DAYS, 1)
    short = hours < SHORT_HOURS and days <= SHORT_DAYS
    base = SHORT_BASE_MONTHS if short else BASE_MONTHS
    ok = cal <= base * MONTH_DAYS
    return {"근무": name, "주휴": paid_holiday, "k": k, "주": weeks, "달력일": cal, "개월": months,
            "기준기간": base, "충족": ok, "18개월이면": cal <= BASE_MONTHS * MONTH_DAYS}


def claim_rows():
    start = LEAVE_DATE + dt.timedelta(days=1)
    end = add_months(LEAVE_DATE, CLAIM_MONTHS)
    rows = []
    for name, rep in REPORT_AFTER:
        first = rep + dt.timedelta(days=WAIT_DAYS)
        left = (end - first).days + 1
        rows.append({"시점": name, "신고일": rep, "첫날": first, "남는날": left})
    return start, end, (end - start).days + 1, rows


def fmt(d):
    return f"{d.year}년 {d.month}월 {d.day}일"


def main():
    print("# calc.py 출력 — 실업급여 조건 (2026-10-03 국가법령정보센터 원문 기준)")
    print(f"원문 숫자: 피보험 단위기간 {UNIT_DAYS}일 · 기준기간 {BASE_MONTHS}개월 · 초단시간 {SHORT_BASE_MONTHS}개월(그중 {SHORT_MIN_DAYS}일 이상) · "
          f"1주 {SHORT_HOURS}시간 미만·{SHORT_DAYS}일 이하 · 질병 {SICK_DAYS}일 이상·{SICK_CAP_YEARS}년 한도 · 수급기간 {CLAIM_MONTHS}개월·{CLAIM_CAP_YEARS}년 한도 · "
          f"대기 {WAIT_DAYS}일 · {AGE}세 · 1개월 {EXCL_MONTH_HOURS}시간 · {EXCL_CONT_MONTHS}개월 이상")
    print(f"18개월 근사 {round(BASE_MONTHS * MONTH_DAYS)}일 · 24개월 근사 {round(SHORT_BASE_MONTHS * MONTH_DAYS)}일")
    print()
    print("표: 근무 형태별로 피보험 단위기간 180일을 채우는 데 걸리는 기간(개근·유급 주휴 1일 가정, 2026년 10월 3일 법령 원문 기준 계산)")
    print("| 근무 형태(가정) | 한 주에 세는 날 | 180일까지 | 달력으로 | 이직 전 살펴보는 기간 | 그 안에 채울 수 있나 |")
    print("|---|---|---|---|---|---|")
    for name, d, h in SCHEDULES:
        r = schedule_row(name, d, h)
        hol = "근무 {}일 + 유급 주휴 {}일".format(d, r["주휴"]) if r["주휴"] else "근무 {}일, 주휴 없음".format(d)
        okt = "채울 수 있음" if r["충족"] else "어려움"
        if r["기준기간"] == SHORT_BASE_MONTHS and not r["18개월이면"]:
            okt += f"({BASE_MONTHS}개월이었다면 어려움)"
        print(f"| {r['근무']} | {r['k']}일({hol}) | {r['주']}주 | 약 {r['달력일']}일 · {r['개월']}개월 | {r['기준기간']}개월 | {okt} |")
    six_weeks = int((6 * MONTH_DAYS) // 7)
    print(f"주 5일 근무로 6개월(약 {round(6 * MONTH_DAYS, 1)}일)만 일하면: 온전한 {six_weeks}주 × 6일 = {six_weeks * 6}일 → 180일에 {UNIT_DAYS - six_weeks * 6}일 모자람")
    print(f"나이 예시(가정): {EX_JOIN_AGE}세 입사·{EX_LEAVE_AGE}세 이직 → {AGE}세 전부터 피보험자격 유지 → 제10조② 제외 아님")
    print(f"별표 2 호 수: 1~{B2_ITEMS}호(3의2호 별도)")
    print()
    start, end, span, rows = claim_rows()
    print(f"가정 이직일 {fmt(LEAVE_DATE)} → 수급기간 {fmt(start)} ~ {fmt(end)} ({span}일)")
    print("표: 실업 신고 시점별로 수급기간 안에 남는 날(이직일 2026년 10월 31일 가정, 대기기간 7일 반영, 2026년 10월 3일 법령 원문 기준 계산)")
    print("| 실업 신고 | 신고일 | 지급 대상 첫날(대기 7일 뒤) | 수급기간 끝 | 수급기간 안에 남는 날 |")
    print("|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['시점']} | {fmt(r['신고일'])} | {fmt(r['첫날'])} | {fmt(end)} | {r['남는날']}일 |")
    print()
    print("표: 자기 사정으로 그만둬도 수급자격이 제한되지 않는 사유 가운데 숫자 조건이 있는 것(시행규칙 별표 2, 2026년 10월 3일 법령 원문 기준)")
    print("| 사유(별표 2) | 원문의 숫자 조건 | 원문의 다른 조건 |")
    print("|---|---|---|")
    print(f"| 임금체불·최저임금 미달·근로조건 저하·연장근로 제한 위반(1호) | 이직 전 {B2['기간_년']}년 안에 {B2['기간_개월']}개월 이상 발생 | 가~마목 가운데 하나 |")
    print(f"| 휴업으로 평균임금을 덜 받음(1호 마목) | 휴업 전 평균임금의 {B2['휴업_퍼센트']}% 미만 | 1호 본문의 기간 조건을 함께 봄 |")
    print(f"| 사업장 이전·다른 지역 전근·가족과 살려는 이사(6호) | 통근 왕복 {B2['통근_시간']}시간 이상 | 통상의 교통수단으로 잼 |")
    print(f"| 부모·동거 친족 간호(7호) | {B2['간호_일']}일 이상 본인이 간호 | 기업 사정상 휴가·휴직이 허용되지 않음 |")
    print(f"| 임신·출산·자녀 육아(10호) | {B2['자녀_세']}세 이하 또는 초등학교 {B2['자녀_학년']}학년 이하 자녀 | 사업주가 휴가·휴직을 허용하지 않음 |")

if __name__ == "__main__":
    main()
