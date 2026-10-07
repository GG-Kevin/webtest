# 보조 계산: 1999-04 적립식이 원금 아래였던 구간, 거치식(1999-04-01 일시 투입) 배수, MDD 회복 일수
import json,datetime
exec(open("calc.py").read().split("base=")[0])
def dca_path(rows,start,monthly=30):
    sh=0;inv=0;seen=set();out=[]
    for d,p in rows:
        if d<start or d>END: continue
        k=(d.year,d.month)
        if k not in seen: seen.add(k);sh+=monthly/p;inv+=monthly
        out.append((d,inv,sh*p))
    return out
s=datetime.date(1999,4,1)
for t in D:
    path=dca_path(D[t],s)
    worst=min(path,key=lambda x:x[2]/x[1])
    under=[d for d,i,v in path if v<i]
    print(t,"DCA1999 최저 평가/투입",worst[0],round(worst[2]/worst[1],3),"원금아래 마지막날",under[-1] if under else None)
    r=[x for x in D[t] if s<=x[0]<=END]
    print(t,"거치식 1999-04 첫거래일",r[0][0],"배수",round(r[-1][1]/r[0][1],2))
for t,pk,rec in [("QQQ",datetime.date(2000,3,27),datetime.date(2015,2,20)),("SPY",datetime.date(2007,10,9),datetime.date(2012,8,16)),("QQQ",datetime.date(2020,2,19),datetime.date(2020,6,3)),("SPY",datetime.date(2020,2,19),datetime.date(2020,8,10)),("QQQ",datetime.date(2021,12,27),datetime.date(2023,12,13)),("SPY",datetime.date(2022,1,3),datetime.date(2023,12,13))]:
    print(t,pk,rec,"고점→회복 일수",(rec-pk).days)
