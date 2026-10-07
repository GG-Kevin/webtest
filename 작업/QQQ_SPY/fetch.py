import json,subprocess,datetime
for t in ["QQQ","SPY"]:
    out=subprocess.run(["curl","-sS","-m","90","-A","Mozilla/5.0",f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?period1=728000000&period2=1790900000&interval=1d&includeAdjustedClose=true"],capture_output=True,text=True).stdout
    open(f"{t}.json","w").write(out)
    d=json.loads(out)["chart"]["result"][0]
    ts=d["timestamp"];c=d["indicators"]["quote"][0]["close"];a=d["indicators"]["adjclose"][0]["adjclose"]
    rows=[(datetime.date.fromtimestamp(x),y,z) for x,y,z in zip(ts,c,a) if y and z]
    print(t,len(rows),rows[0],rows[-3:])
