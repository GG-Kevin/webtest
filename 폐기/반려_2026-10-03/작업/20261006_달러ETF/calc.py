"""달러 투자 ETF vs 환전 — 원/달러(Yahoo KRW=X)와 국내 상장 달러 ETF 3종을 같은 기간에 맞댄다.
원자료: Yahoo Finance chart API, 2026-10-02 조회, 기준일 2026-10-01. 수수료·환전 스프레드·세금·이자는 계산에 넣지 않았다.
ETF 수익 = 수정종가(adjclose, 분배금 재투자). 환율 수익 = 달러를 그대로 들고 있을 때(이자 0)."""
import json,datetime as dt
END=dt.date(2026,10,1)
def load(n):
    r=json.load(open(f"{n}.json"))["chart"]["result"][0]
    return [(dt.date.fromtimestamp(x),c,a) for x,c,a in zip(r["timestamp"],r["indicators"]["quote"][0]["close"],r["indicators"]["adjclose"][0]["adjclose"]) if c and a and dt.date.fromtimestamp(x)<=END]
FX=load("USDKRW");E={"KODEX 미국달러선물":load("KODEX_USD선물"),"KOSEF 미국달러선물":load("KOSEF_USD선물"),"TIGER 미국달러단기채권액티브":load("TIGER_USD단기채권")}
fxd={d:c for d,c,a in FX}
def fx_at(d):
    ks=[k for k in fxd if k<=d];return fxd[max(ks)]
def ret_etf(rows,s,e):
    a=[x for x in rows if x[0]>=s][0];b=[x for x in rows if x[0]<=e][-1];return a[0],b[0],b[2]/a[2]-1
print("기준일",END)
print("\n[표1] 원/달러 환율 기록(Yahoo KRW=X 종가)")
r=[x for x in FX if x[0]>=dt.date(2019,7,24)]
hi=max(r,key=lambda x:x[1]);lo=min(r,key=lambda x:x[1])
print("2019-07-24 이후 최고",hi[0],round(hi[1],1),"최저",lo[0],round(lo[1],1),"기말",END,round(fx_at(END),1),"시작",r[0][0],round(r[0][1],1))
print("\n[표2] 같은 기간 1,000만원 — 달러 보유(환율) vs 달러 ETF 3종 (기간별 시작일 다름: 각 ETF 상장 이후 가장 이른 날, 같은 기간 맞댐)")
S0=dt.date(2019,7,24)  # TIGER 상장 이후 공통
for lab,s in [("2019-07-24",S0),("2022-01-03",dt.date(2022,1,3)),("2024-01-02",dt.date(2024,1,2)),("2025-01-02",dt.date(2025,1,2))]:
    s2=[d for d,_,_ in FX if d>=s][0];fx=fx_at(END)/fxd[s2]-1
    print(f"시작 {lab}({s2}) 환율 {fxd[s2]:.1f}→{fx_at(END):.1f} 달러 보유 {fx*100:+.1f}% (1,000만원→{10_000_000*(1+fx):,.0f}원)")
    for n,rows in E.items():
        try:
            a,b,rr=ret_etf(rows,s,END)
            if a-s>dt.timedelta(days=10): print("  ",n,"상장 전 시작 불가");continue
            print(f"   {n}: {rr*100:+.1f}% (1,000만원→{10_000_000*(1+rr):,.0f}원) · 환율과 차이 {(rr-fx)*100:+.1f}%p")
        except Exception as e: print("  ",n,"계산 불가",e)
print("\n[표3] 연도별 원/달러 변화와 달러 ETF(KODEX 미국달러선물) — 연초 첫 거래일~연말(2026은 10-01) 수익률")
K=E["KODEX 미국달러선물"];T=E["TIGER 미국달러단기채권액티브"]
for y in range(2017,2027):
    s=dt.date(y,1,1);e=dt.date(y,12,31) if y<2026 else END
    fs=[d for d,_,_ in FX if d>=s][0];fe=[d for d,_,_ in FX if d<=e][-1]
    fxr=fxd[fe]/fxd[fs]-1
    try:
        a,b,kr=ret_etf(K,s,e);ks=f"{kr*100:+.1f}%"
    except: ks="-"
    try:
        a,b,tr=ret_etf(T,s,e);ts=f"{tr*100:+.1f}%" if a<=s+dt.timedelta(days=10) else "-"
    except: ts="-"
    print(f"{y}|환율 {fxd[fs]:.0f}→{fxd[fe]:.0f} ({fxr*100:+.1f}%)|KODEX선물 {ks}|TIGER단기채권 {ts}")
print("\n[표4] 일간 움직임을 얼마나 따라가나 — KODEX 미국달러선물 vs 원/달러 (2017-01 이후, 일간 수익률 상관계수·평균 절대 차이)")
import statistics as st
def daily(rows):
    return {rows[i][0]:rows[i][2]/rows[i-1][2]-1 for i in range(1,len(rows))}
dk=daily(K);dfx=daily([(d,c,c) for d,c,a in FX])
common=[d for d in dk if d in dfx and d>=dt.date(2017,1,1)]
x=[dfx[d] for d in common];y=[dk[d] for d in common]
mx,my=st.mean(x),st.mean(y)
cov=sum((a-mx)*(b-my) for a,b in zip(x,y))/len(x);cor=cov/(st.pstdev(x)*st.pstdev(y))
print("공통 거래일",len(common),"상관계수",round(cor,3),"평균 절대 차이(%p)",round(st.mean(abs(a-b) for a,b in zip(x,y))*100,3))
# 주간(5거래일 묶음) 상관
import itertools
wk=[(sum(x[i:i+5]),sum(y[i:i+5])) for i in range(0,len(x)-4,5)]
wx=[a for a,b in wk];wy=[b for a,b in wk];mwx,mwy=st.mean(wx),st.mean(wy)
wc=sum((a-mwx)*(b-mwy) for a,b in wk)/len(wk)/(st.pstdev(wx)*st.pstdev(wy))
print("5거래일 묶음 상관계수",round(wc,3),"표본",len(wk))
print("\n[표5] 월 적립 비교 — 매달 첫 거래일 100만원, 2019-07-24~2026-10-01 (달러 환전 보유 vs KODEX 미국달러선물 총수익 vs TIGER 단기채권)")
def dca(series,s,mon=1_000_000):
    seen=set();sh=0;n=0;last=None
    for d,c in series:
        if d<s or d>END:continue
        k=(d.year,d.month)
        if k not in seen: seen.add(k);sh+=mon/c;n+=1
        last=c
    return n,n*mon,sh*last
fxs=[(d,c) for d,c,a in FX];ks=[(d,a) for d,c,a in K];ts=[(d,a) for d,c,a in T]
for nm,sr,st0 in [("달러 환전 보유(이자 0)",fxs,S0),("KODEX 미국달러선물",ks,dt.date(2019,7,24)),("TIGER 미국달러단기채권액티브",ts,dt.date(2019,7,24))]:
    n,inv,val=dca(sr,st0);print(f"{nm}: {n}회 납입 {inv:,.0f}원 → {val:,.0f}원 ({(val/inv-1)*100:+.1f}%)")
