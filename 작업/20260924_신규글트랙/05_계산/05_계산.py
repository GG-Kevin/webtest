# 05_원고 절 D 계산표 · 절 C 예시 재현용 (「서사」 2026-09-24)
# 입력 근거(전부 03_사실자료_원문/ 저장 원문):
#   조특법 §126의2① 최저사용금액 = 총급여 × 25/100            (M2)
#   §126의2② 4호 직불카드등사용분 ×30/100, 5호 신용카드사용분 ×15/100 (M2)
#   §126의2② 6호 가: 최저사용금액 ≤ 신용카드사용분 → 최저사용금액 ×15/100 을 뺀다
#   §126의2② 6호 나: 최저사용금액 > 신용카드사용분 이고 ≤ 신용+직불 → 신용×15/100 + (최저−신용)×30/100 을 뺀다
#   §126의2⑩ 본문 한도: 총급여 7천만원 이하 300만원, 초과 250만원 (자녀등 없는 경우. ⑩ 단서·⑪은 계산에 넣지 않음 — R6 미확보)
#   소득세법 §55① 세율표 구간 세율 6·15·24·35%                 (R1)
#   소득세법 §59의3① 연금계좌 12/100 (총급여 5,500만원 이하 15/100)  (R2)
#   소득세법 §61②③ 세액공제 합계가 산출세액 초과 → 초과분 없는 것   (R3)
# 가정: 전통시장·대중교통·문화체육 사용 0, 현금영수증은 직불과 같은 30%로 묶음. 단위 만원.

def limit(G):
    return 300 if G <= 7000 else 250

def raw_deduction(G, credit, debit):
    T = G * 0.25
    s = credit * 0.15 + debit * 0.30
    if credit + debit <= T:
        return 0.0
    if T <= credit:
        sub = T * 0.15                      # 6호 가
    else:
        sub = credit * 0.15 + (T - credit) * 0.30   # 6호 나
    return max(0.0, s - sub)

def deduction(G, credit, debit):
    return min(limit(G), raw_deduction(G, credit, debit))

print("== 절 D 계산표 ==")
print("총급여 | 25%문턱 | 기본한도 | 문턱 위 전부 신용일 때 한도 닿는 총사용액 | 문턱 위 전부 체크일 때 | 100만원 신용→체크 공제 증가")
for G in (3000, 5000, 8000):
    T = G * 0.25
    L = limit(G)
    S_credit = T + L / 0.15
    S_debit = T + L / 0.30
    # 검산: 문턱까지 신용, 그 위 전부 신용 / 전부 체크
    assert abs(deduction(G, S_credit, 0) - L) < 1e-6
    assert abs(deduction(G, T, S_debit - T) - L) < 1e-6
    # 문턱 위·한도 아래 한 지점에서 100만원 옮기기
    credit = T + 400; debit = 0
    d0 = deduction(G, credit, debit); d1 = deduction(G, credit - 100, debit + 100)
    print(f"{G} | {T:.0f} | {L} | {S_credit:.1f} | {S_debit:.1f} | {d1-d0:.1f}")

print()
print("== 0원 검산: 문턱 아래 / 신용이 문턱보다 적을 때 / 한도 위 ==")
G = 5000
print("문턱 아래(총 1,000 전부 신용→100 체크):", deduction(G,1000,0), "->", deduction(G,900,100))
print("신용 1,000·체크 800(신용<문턱 1,250) → 신용 100을 체크로:", deduction(G,1000,800), "->", deduction(G,900,900))
print("한도 위(신용 3,500):", deduction(G,3500,0), "->", deduction(G,3400,100))
G = 8000
print("총급여 8,000 신용 3,700:", round(raw_deduction(G,3700,0),1), "(한도 전)", deduction(G,3700,0), "->", deduction(G,3600,100))

print()
print("== 15만원 소득공제의 세금 가치 (§55 구간 세율, 구간 경계를 넘지 않는 경우) ==")
for r in (6, 15, 24, 35):
    print(f"{r}% → {150000*r/100:,.0f}원")

print()
print("== 절 C 예시: 총급여 5,000만원(15%), 연금 100만원 추가 ==")
for room in (30, 10, 0):
    credit = 100 * 0.15
    print(f"결정세액 {room}만원 → 받는 세액공제 {min(credit, room)}만원 (§61②: 초과분 없는 것)")
print("총급여 8,000만원(12%): 100만원 →", 100*0.12, "만원")

print()
print("== 절 C: 결정세액 10만원이 남았을 때 올해 세금이 되는 추가 납입 상한 ==")
print("15%:", round(10/0.15,1), "만원 / 12%:", round(10/0.12,1), "만원")
