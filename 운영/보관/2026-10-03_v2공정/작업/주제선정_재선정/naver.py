import json,subprocess,urllib.parse,time
C={
"ISA 만기 연금계좌 전환":["isa 만기 연금저축 전환","isa 만기"],
"월배당·커버드콜 ETF 단점":["월배당 etf","커버드콜 etf","schd 단점","jepi 단점"],
"IRP 중도해지 세금":["irp 중도해지","irp 해지 세금"],
"청년도약→미래적금 갈아타기":["청년미래적금 갈아타기","청년도약계좌 갈아타기"],
"금융소득 1천만원 피부양자":["금융소득 피부양자","피부양자 금융소득 1000만원"],
"TQQQ 장기투자":["tqqq 장기투자","qqq 적립식"],
"달러 투자 ETF vs 환전":["달러 투자 etf","달러 투자 방법"],
"파킹통장·CMA 금리":["파킹통장","cma 금리"],
"종부세":["종부세 납부","종부세 기준"],
"삼성전자 배당·실적":["삼성전자 배당","삼성전자 실적"],
"S&P500 환헤지 vs 일반":["환헤지 etf","s&p500 환헤지"],
"연금저축 ETF 20년 세후":["연금저축 etf 추천","연금저축 etf"],
"나스닥100 국내 ETF 비교":["나스닥100 etf 비교","나스닥100 etf 추천"],
"국채 ETF 세금":["국채 etf 세금","국채 etf 추천"],
"공모주 환불일":["공모주 환불일","공모주 청약 환불"],
"증시 휴장일":["증시 휴장일","10월 9일 증시"],
}
SUF=[""," 방법"," 비교"," 후기"," 세금"," 추천"]
def ac(q):
    o=subprocess.run(["curl","-s","-m","10","-A","Mozilla/5.0","-G","https://ac.search.naver.com/nx/ac","--data-urlencode","q="+q,"-d","con=1&frm=nx&ans=2&r_format=json&r_enc=UTF-8&r_unicode=0&t_koreng=1&run=2&rev=4&q_enc=UTF-8&st=100"],capture_output=True,text=True).stdout
    try: return [x[0] for x in json.loads(o)["items"][0]]
    except: return []
out={}
for k,qs in C.items():
    seen=[]
    for q in qs:
        for s in SUF:
            for r in ac(q+s):
                if r not in seen: seen.append(r)
            time.sleep(0.15)
    out[k]=seen; print(k,len(seen),seen[:3],flush=True)
json.dump(out,open("naver_1003.json","w"),ensure_ascii=False,indent=1)
