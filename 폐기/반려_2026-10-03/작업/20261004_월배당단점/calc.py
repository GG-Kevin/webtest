"""월배당 ETF 단점 — JEPI·SCHD·SPY 같은 기간 맞대기. 원자료: Yahoo Finance chart API(2026-10-02 조회, 분할·배당 보정).
가격 = 종가(close, 분할 보정, 배당 미반영). 총수익 = 수정종가(adjclose, 배당 재투자). 분배금 = events.dividends."""
import json,datetime as dt
END=dt.date(2026,10,1)
def load(t):
    r=json.load(open(f"{t}.json"))["chart"]["result"][0]
    ts=r["timestamp"];q=r["indicators"]["quote"][0]["close"];a=r["indicators"]["adjclose"][0]["adjclose"]
    rows=[(dt.date.fromtimestamp(x),c,b) for x,c,b in zip(ts,q,a) if c and b and dt.date.fromtimestamp(x)<=END]
    dv=sorted((dt.date.fromtimestamp(int(k)),v["amount"]) for k,v in r.get("events",{}).get("dividends",{}).items() if dt.date.fromtimestamp(int(k))<=END)
    return rows,dv
D={t:load(t) for t in["JEPI","SCHD","SPY"]}
S=D["JEPI"][0][0][0]   # 공통 시작일 = JEPI 첫 거래일
print("기준일",END,"· 공통 시작일",S)
def win(t):
    rows,dv=D[t];return [x for x in rows if x[0]>=S],[x for x in dv if x[0]>=S]
yrs=(END-S).days/365.25
print("기간(년)",round(yrs,2))
INV=10000
print("\n[표1] 같은 기간 $10,000 한 번에 투자(분배금은 받아서 쓴 경우 vs 재투자 경우)")
print("종목|시작가|기말가|가격 변화|분배금 합계(주당)|받은 분배금($)|분배금 쓴 경우 합계($)|재투자 총수익|연평균(재투자)")
res={}
for t in D:
    rows,dv=win(t)
    p0,p1=rows[0][1],rows[-1][1]; a0,a1=rows[0][2],rows[-1][2]
    sh=INV/p0; divsum=sum(a for d,a in dv); cash=sh*divsum
    spent=sh*p1+cash; reinv=INV*a1/a0
    cagr=(a1/a0)**(1/yrs)-1
    res[t]=dict(p0=p0,p1=p1,pc=p1/p0-1,divsum=divsum,cash=cash,spent=spent,reinv=reinv,cagr=cagr)
    print(f"{t}|{p0:.2f}|{p1:.2f}|{(p1/p0-1)*100:.1f}%|{divsum:.2f}|{cash:,.0f}|{spent:,.0f}|{(reinv/INV-1)*100:.1f}% ({reinv:,.0f})|{cagr*100:.1f}%")
print("\n[표2] 연도별 주당 분배금(달러, 해당 연도 지급분) · 월 최저/최고(JEPI)")
for t in["JEPI","SCHD"]:
    rows,dv=win(t);by={}
    for d,a in dv: by.setdefault(d.year,[]).append(a)
    print(t,{y:(round(sum(v),3),len(v)) for y,v in by.items()})
rows,dv=win("JEPI");m=[a for d,a in dv if d.year>=2021 and d.year<=2025]
print("JEPI 2021~2025 월 분배금 최저 %.3f 최고 %.3f (배수 %.1f)"%(min(m),max(m),max(m)/min(m)))
mm=sorted((a,d) for d,a in dv);print("최저 3",mm[:3],"최고 3",mm[-3:])
print("\n[표3] 분배율(trailing 12M 분배금 ÷ 해당 시점 가격)")
for t in D:
    rows,dv=win(t)
    for y in (2021,2022,2023,2024,2025):
        end=dt.date(y,12,31)
        px=[c for d,c,b in rows if d<=end][-1]
        s=sum(a for d,a in dv if end-dt.timedelta(days=365)<d<=end)
        print(t,y,f"{s/px*100:.1f}%",end=" ")
    print()
print("\n[표4] 최대 낙폭(가격 기준 / 총수익 기준)·회복")
def mdd(rows,idx):
    pk=rows[0][idx];pkd=rows[0][0];best=(0,None,None)
    for r in rows:
        v=r[idx]
        if v>pk:pk=v;pkd=r[0]
        dd=v/pk-1
        if dd<best[0]:best=(dd,pkd,r[0])
    dd,pd,td=best;pv=[r[idx] for r in rows if r[0]==pd][0]
    rec=next((r[0] for r in rows if r[0]>td and r[idx]>=pv),None)
    return dd,pd,td,rec
for t in D:
    rows,_=win(t)
    print(t,"가격",[str(x) for x in mdd(rows,1)],"총수익",[str(x) for x in mdd(rows,2)])
print("\n[표5] 상승·하락장 동행(월간 총수익 수익률 기준, SPY 대비)")
def monthly(t):
    rows,_=win(t);m={}
    for d,c,b in rows: m[(d.year,d.month)]=b
    ks=sorted(m);return {ks[i]:m[ks[i]]/m[ks[i-1]]-1 for i in range(1,len(ks))}
mj,ms,mp=monthly("JEPI"),monthly("SCHD"),monthly("SPY")
up=[k for k in mp if mp[k]>0.03];dn=[k for k in mp if mp[k]<-0.03]
avg=lambda m,ks:sum(m[k] for k in ks)/len(ks)*100
print(f"SPY +3% 넘은 달 {len(up)}개: SPY 평균 {avg(mp,up):.1f}% · JEPI {avg(mj,up):.1f}% · SCHD {avg(ms,up):.1f}%")
print(f"SPY -3% 넘은 달 {len(dn)}개: SPY 평균 {avg(mp,dn):.1f}% · JEPI {avg(mj,dn):.1f}% · SCHD {avg(ms,dn):.1f}%")

print("\n[표1b] 다른 시작점 — 2022-01-03(S&P500 고점, 하락장 직전) 부터 $10,000")
S2=dt.date(2022,1,3);yrs2=(END-S2).days/365.25;print("기간(년)",round(yrs2,2))
for t in D:
    rows=[x for x in D[t][0] if x[0]>=S2];dv=[x for x in D[t][1] if x[0]>=S2]
    p0,p1=rows[0][1],rows[-1][1];a0,a1=rows[0][2],rows[-1][2]
    sh=INV/p0;cash=sh*sum(a for d,a in dv);spent=sh*p1+cash
    print(f"{t}|시작가 {p0:.2f}|기말가 {p1:.2f}|가격 {(p1/p0-1)*100:.1f}%|받은 분배금 ${cash:,.0f}|분배금 쓴 경우 ${spent:,.0f}|재투자 {(a1/a0-1)*100:.1f}% (${INV*a1/a0:,.0f})|연평균 {((a1/a0)**(1/yrs2)-1)*100:.1f}%")

print("\n[표6] 월 100만원(연 1,200만원) 분배금을 받으려면 필요한 원금 — 분배율은 [표3]와 같은 방식(최근 12개월 분배금 ÷ 가격), 기준일별")
for t in["JEPI","SCHD"]:
    rows,dv=win(t)
    for end in (dt.date(2025,12,31),END):
        px=[c for d,c,b in rows if d<=end][-1]
        s=sum(a for d,a in dv if end-dt.timedelta(days=365)<d<=end)
        y=s/px
        print(f"{t} {end} 최근12개월 분배금 ${s:.3f} / 가격 ${px:.2f} = {y*100:.2f}% → 필요 원금 {12_000_000/y/1e8:.2f}억원(분배율만 본 값, 세금·환율 제외)")
