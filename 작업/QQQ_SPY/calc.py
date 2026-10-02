import json,datetime
def load(t):
    d=json.loads(open(f"{t}.json").read())["chart"]["result"][0]
    return [(datetime.date.fromtimestamp(x),a) for x,a in zip(d["timestamp"],d["indicators"]["adjclose"][0]["adjclose"]) if a]
D={t:load(t) for t in["QQQ","SPY"]}
END=datetime.date(2026,10,1)
def dca(rows,start,monthly=30):
    # buy on first trading day of each month from start month, adj close (total return)
    sh=0;n=0;seen=set();last=None
    for d,p in rows:
        if d<start or d>END: continue
        k=(d.year,d.month)
        if k not in seen: seen.add(k);sh+=monthly/p;n+=1
        last=p
    return n,n*monthly,sh*last
def mdd(rows,start):
    pk=0;m=0;pkd=None;res=None;tr=None
    r=[x for x in rows if start<=x[0]<=END]
    pk=r[0][1];pkd=r[0][0];best=(0,None,None)
    for d,p in r:
        if p>pk: pk=p;pkd=d
        dd=p/pk-1
        if dd<best[0]: best=(dd,pkd,d)
    dd,pd,td=best;pkp=dict(r)[pd]
    rec=next((d for d,p in r if d>td and p>=pkp),None)
    return dd,pd,td,rec
base=datetime.date(1999,4,1)
for label,s in [("1999-04",datetime.date(1999,4,1)),("2006-01",datetime.date(2006,1,1)),("2011-10",datetime.date(2011,10,1)),("2016-10",datetime.date(2016,10,1)),("2021-10",datetime.date(2021,10,1)),("2023-10",datetime.date(2023,10,1))]:
    for t in D:
        n,inv,val=dca(D[t],s);print(label,t,n,inv,round(val,1),round(val/inv,2))
for t in D:
    print(t,"MDD all(1999-)",mdd(D[t],base))
    print(t,"MDD 2020",mdd([x for x in D[t] if x[0]<datetime.date(2021,1,1)],datetime.date(2020,1,1)))
    print(t,"MDD 2022",mdd(D[t],datetime.date(2021,6,1)))
