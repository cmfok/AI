#!/usr/bin/env python3
"""
旅行 Agent v4 — 全自动 Loop，自主填补空缺
=============================================
Loop: 查 → 验 → 缺则换策略补 → 再验 → 出方案
不达标自动降级/换关键词/换数据源，不问人。
"""

import subprocess, json, re, sys, time, os
from datetime import datetime, timedelta

MAX_LOOP = 6
FLYAI = "npx --yes @fly-ai/flyai-cli"

def flyai(cmd: str, timeout: int = 25) -> dict:
    try:
        r = subprocess.run(f'{FLYAI} {cmd}', shell=True, capture_output=True, text=True, timeout=timeout)
        return json.loads(r.stdout) if r.stdout.strip() else {"error": "empty"}
    except: return {"error": "fail"}

def get_items(d, key='itemList'):
    data = d.get('data',{}) or {}
    if isinstance(data, dict):
        if key in data:
            items = data[key]
            # flyai train: itemList items wrap journeys
            flat = []
            for item in items:
                if isinstance(item, dict) and 'journeys' in item:
                    for j in item['journeys']:
                        for s in j.get('segments',[]):
                            s['_price'] = j.get('priceInfo',{}).get('minPrice','?')
                            s['_name'] = f"{s.get('marketingTransportName','')}{s.get('marketingTransportNo','')} {s.get('depStationName','')}-{s.get('arrStationName','')} {s.get('depDateTime','')[:10]}"
                            flat.append(s)
                else:
                    flat.append(item)
            return flat
        if 'journeys' in data:
            items = []
            for j in data['journeys']:
                for s in j.get('segments',[]):
                    s['_price'] = j.get('priceInfo',{}).get('minPrice','?')
                    s['_name'] = f"{s.get('marketingTransportName','')}{s.get('marketingTransportNo','')}"
                    items.append(s)
            return items
    return [] if isinstance(d.get("data",{}),dict) else (d.get("data",[]) if isinstance(d.get("data"),list) else [])

def parse(q):
    info={"dest":"大理","days":5,"budget":10000,"from":"广州","prefer":"高铁","guests":"2人","style":"","needs":[],"date":(datetime.now()+timedelta(days=7)).strftime("%Y-%m-%d")}
    C=["昆明","丽江","大理","西双版纳","香格里拉","腾冲","普洱","北京","上海","广州","深圳","杭州","成都","重庆","西安","三亚","海口","厦门","青岛","大连","桂林","张家界","黄山","南京","武汉","长沙","苏州","贵阳","拉萨"]
    for c in C:
        if c in q: info["dest"]=c; break
    m=re.search(r'(\d+)\s*天',q)
    if m: info["days"]=int(m.group(1))
    m=re.search(r'预算\s*(\d+)\s*万',q)
    if m: info["budget"]=int(m.group(1))*10000
    for c in C:
        if f"从{c}" in q or f"{c}出发" in q: info["from"]=c; break
    if "飞机" in q or "机票" in q: info["prefer"]="飞机"
    if "自驾" in q or "开车" in q: info["prefer"]="自驾"
    if "一家三口" in q: info["guests"]="一家三口(2大1小)"
    return info

def run(info):
    """全自动执行，不中断"""
    results = {}
    gaps = ["hotel","train","poi","flight"]
    plan = ""
    
    print(f"🎯 {info['dest']} {info['days']}天 ¥{info['budget']:,} {info['guests']} | {info['prefer']}优先 | 从{info['from']}出发")
    
    for loop in range(1, MAX_LOOP+1):
        fixed = 0
        
        # ── 查酒店 ──
        if "hotel" in gaps and not get_items(results.get("hotel",{})):
            r = flyai(f'search-hotel --dest-name "{info["dest"]}" --check-in-date {info["date"]}')
            if get_items(r): results["hotel"] = r; gaps.remove("hotel"); fixed+=1
        
        # ── 查火车 ──
        if "train" in gaps and not get_items(results.get("train",{})):
            r = flyai(f'search-train --origin "{info["from"]}" --dest "{info["dest"]}" --date {info["date"]}')
            if get_items(r): results["train"] = r; gaps.remove("train"); fixed+=1
            else:
                # 策略2: 关键词搜索
                r2 = flyai(f'keyword-search --query "{info["from"]}到{info["dest"]}高铁火车票 {info["date"]}"')
                if get_items(r2): results["train"] = r2; gaps.remove("train"); fixed+=1
        
        # ── 查景点 ──
        if "poi" in gaps and not get_items(results.get("poi",{})):
            r = flyai(f'search-poi --city-name "{info["dest"]}"')
            if get_items(r): results["poi"] = r; gaps.remove("poi"); fixed+=1
            else:
                r2 = flyai(f'keyword-search --query "{info["dest"]}必去景点攻略门票"')
                if get_items(r2): results["poi"] = r2; gaps.remove("poi"); fixed+=1
        
        # ── 查机票 ──
        if "flight" in gaps and not get_items(results.get("flight",{})):
            r = flyai(f'search-flight --origin "{info["from"]}" --destination "{info["dest"]}" --dep-date {info["date"]}')
            if get_items(r): results["flight"] = r; gaps.remove("flight"); fixed+=1
        
        # ── 自驾估算 ──
        if "drive" not in results:
            dist = {"广州-大理":1600,"广州-丽江":1750,"广州-桂林":500,"广州-昆明":1400,"昆明-大理":320,"成都-大理":800}.get(f'{info["from"]}-{info["dest"]}',800)
            results["drive"] = {"km":dist,"h":round(dist/100,1),"gas":f"¥{int(dist*0.7)}","toll":f"¥{int(dist*0.5)}","total":int(dist*1.2)}
        
        # ── 打印进展 ──
        icons = {"hotel":"🏨","train":"🚄","poi":"🎯","flight":"✈️"}
        status = " ".join([f"{'✅' if k not in gaps else '⏳'}{icons.get(k,'')}" for k in ["hotel","train","poi","flight"]])
        print(f"  Loop {loop}: {status} | 修复{fixed} | 剩余缺口{len(gaps)}")
        
        if not gaps: break
    
    # ── 生成方案 ──
    info["loops"] = loop
    print(gen_plan(info, results, gaps))
    return results

def gen_plan(info, res, gaps):
    d,days,budget=info["dest"],info["days"],info["budget"]
    hotels=get_items(res.get("hotel",{}))
    pois=get_items(res.get("poi",{}))
    trains=get_items(res.get("train",{}))
    flights=get_items(res.get("flight",{}))
    drive=res.get("drive",{})
    
    def price_sort(items):
        def p(h):
            try: return int(re.sub(r'[^0-9]','',str(h.get('price','0')).replace('xx','00').replace('9x','90').replace('1xx','100').replace('2xx','200').replace('3xx','300')))
            except: return 99999
        return sorted(items,key=p)
    
    hotels=price_sort(hotels)
    trains=price_sort(trains)
    flights=price_sort(flights)
    
    p=f"""
╔══════════════════════════════════════╗
║  🧭 {d} {days}天{days-1}夜 旅行方案
║  💰 ¥{budget:,} | 👥 {info['guests']}
║  📅 {info['date']} | 🚗 {info['prefer']}优先
║  🔄 {info.get('loops','?')}轮循环完成
╚══════════════════════════════════════╝
"""
    p+="\n🏨 住宿:\n"
    if hotels:
        for i,h in enumerate(hotels[:4],1):
            p+=f"  {i}. {h.get('name','?')} — {h.get('price','?')} {h.get('star','')} | {h.get('interestsPoi','')}\n"
    else: p+="  ⚠️ FlyAI无结果，建议飞猪APP查询\n"
    
    p+="\n🚄 交通:\n"
    if trains:
        for i,t in enumerate(trains[:3],1): p+=f"  {i}. {t.get('_name',t.get('trainNo',t.get('name','?')))} {t.get('_price',t.get('price','?'))}\n"
    elif flights:
        for i,f in enumerate(flights[:2],1): p+=f"  {i}. ✈️ {f.get('flightNo',f.get('name','?'))} {f.get('price','?')}\n"
    if drive:
        p+=f"  🚗 自驾备选: {drive.get('km','?')}km {drive.get('h','?')}h ¥{drive.get('total','?')}\n"
    if not trains and not flights:
        p+="  ⚠️ 火车/机票未获取到实时数据\n"
    
    p+="\n🎯 行程:\n"
    for day in range(1,days+1):
        if day-1<len(pois): p+=f"  D{day}: {pois[day-1].get('name','?')}\n"
        else: p+=f"  D{day}: 自由探索\n"
    
    # 预算
    hp=400
    try: hp=int(re.sub(r'[^0-9]','',str(hotels[0].get('price','400')).replace('xx','00').replace('9x','90').replace('1xx','100')) or '400')
    except: pass
    est=hp*days+2500
    p+=f"\n💰 预估: 住宿¥{hp}×{days}=¥{hp*days} + 交通门票¥2500 = ¥{est:,} "
    p+="✅ 预算内\n" if est<=budget else f"⚠️ 超¥{est-budget:,}\n"
    
    if gaps:
        p+=f"\n⚠️ 未获取: {', '.join(gaps)} (FlyAI接口限制)\n"
    
    return p

if __name__=='__main__':
    q=sys.argv[1] if len(sys.argv)>1 else "一家三口大理5天4夜 预算2万 高铁"
    print(f"\n🧭 Agent v4 启动 | {q}\n")
    run(parse(q))
    print("✅ 全自动执行完毕")
