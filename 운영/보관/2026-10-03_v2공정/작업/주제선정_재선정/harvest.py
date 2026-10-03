import json,subprocess,urllib.parse,time,sys
SEEDS="""연금저축 연말정산|연금저축 IRP 한도|연말정산 미리보기|연말정산 환급|ISA 만기|ISA 중개형|ISA 해외주식|배당소득 분리과세|금융소득 종합과세|피부양자 금융소득|해외주식 양도세|해외주식 양도세 신고|배당락|월배당 ETF|커버드콜 ETF|SCHD|JEPI|TQQQ|QQQ 적립식|나스닥100 ETF|S&P500 ETF 추천|환헤지|달러 투자|원달러 환율 전망|엔화 투자|금통위 금리|기준금리 인하 예금|삼성전자 배당|삼성전자 실적|수능 증시|증시 휴장 10월|한글날 증시|공모주 청약|공모주 환불일|상장폐지 정리매매|대주주 양도세|종부세|주식 양도세 대주주|퇴직연금 IRP|국민연금 수령|청년도약계좌|파킹통장|CMA 금리|국채 ETF|미국 국채 투자|금 투자 ETF|비트코인 ETF|리츠 배당|연말 배당 투자|FOMC 투자""".split("|")
SUF=["",""," 방법"," 얼마"," 언제"," 후기"," 세금"," 추천"," 비교"," 마감"]
def sug(q):
    u="https://suggestqueries.google.com/complete/search?client=firefox&hl=ko&gl=kr&q="+urllib.parse.quote(q)
    o=subprocess.run(["curl","-sS","-m","15","-A","Mozilla/5.0",u],capture_output=True,text=True).stdout
    try: return json.loads(o)[1]
    except: return []
res={}
for s in SEEDS:
    seen=[]
    for suf in SUF[1:]:
        for r in sug(s+suf):
            if r not in seen: seen.append(r)
        time.sleep(0.25)
    res[s]=seen
    print(s,len(seen),"|",", ".join(seen[:4]),flush=True)
json.dump(res,open("questions_1003.json","w"),ensure_ascii=False,indent=1)
