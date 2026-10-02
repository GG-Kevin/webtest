import json,subprocess,time
for t in ["SCHD","JEPI","SPY"]:
    for k in range(4):
        o=subprocess.run(["curl","-sS","-m","90","-A","Mozilla/5.0",f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?period1=1180000000&period2=1790900000&interval=1d&includeAdjustedClose=true&events=div"],capture_output=True,text=True).stdout
        if '"result":[' in o: break
        time.sleep(5*(k+1))
    open(f"{t}.json","w").write(o)
    d=json.loads(o)["chart"]["result"][0]
    print(t,len(d["timestamp"]),len(d.get("events",{}).get("dividends",{})))
