import json,subprocess,datetime,time
for t in ["TQQQ","QQQ"]:
    for k in range(4):
        out=subprocess.run(["curl","-sS","-m","90","-A","Mozilla/5.0",f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?period1=1267000000&period2=1790900000&interval=1d&includeAdjustedClose=true"],capture_output=True,text=True).stdout
        if out.startswith("{") and '"result":[' in out: break
        time.sleep(5*(k+1))
    open(f"{t}.json","w").write(out)
    d=json.loads(out)["chart"]["result"][0]
    ts=d["timestamp"];c=d["indicators"]["quote"][0]["close"];a=d["indicators"]["adjclose"][0]["adjclose"]
    rows=[(datetime.date.fromtimestamp(x),y,z) for x,y,z in zip(ts,c,a) if y and z]
    print(t,len(rows),rows[0],rows[-3:])
