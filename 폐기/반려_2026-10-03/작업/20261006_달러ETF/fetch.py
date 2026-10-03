import json,subprocess,time,datetime as dt
T={"KRW=X":"USDKRW","261240.KS":"KODEX_USD선물","138230.KS":"KOSEF_USD선물","329750.KS":"TIGER_USD단기채권","261250.KS":"TIGER_USD선물레버리지"}
for t,n in T.items():
    for k in range(4):
        o=subprocess.run(["curl","-sS","-m","90","-A","Mozilla/5.0",f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?period1=1000000000&period2=1790900000&interval=1d&includeAdjustedClose=true&events=div"],capture_output=True,text=True).stdout
        if '"result":[' in o: break
        time.sleep(5*(k+1))
    open(f"{n}.json","w").write(o)
    try:
        r=json.loads(o)["chart"]["result"][0];ts=r["timestamp"]
        print(t,n,len(ts),dt.date.fromtimestamp(ts[0]),dt.date.fromtimestamp(ts[-1]),r["meta"].get("longName") or r["meta"].get("shortName"),len(r.get("events",{}).get("dividends",{})))
    except Exception as e: print(t,n,"실패",o[:120])
