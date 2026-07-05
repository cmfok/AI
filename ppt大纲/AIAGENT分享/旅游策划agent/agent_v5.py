#!/usr/bin/env python3
"""
旅行 Agent v5 — 全自动 Loop + 酒店三方案对比 + Markdown 输出
==============================================================
新增:
- 酒店输出3档方案（经济型/舒适型/亲子精选），每个方案含优缺点分析
- 自动保存 Markdown 文件到输出目录
- 结构化日志与状态追踪
- 错误分类与降级策略
"""

import subprocess, json, re, sys, time, os
from datetime import datetime, timedelta

# ── 配置 ──
MAX_LOOP = 6
FLYAI = "npx --yes @fly-ai/flyai-cli"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
TIMEOUT = 25

# ══════════════════════════════════════════════════════════════
# 1. 状态管理
# ══════════════════════════════════════════════════════════════

class AgentState:
    """Agent 运行时状态追踪"""
    def __init__(self):
        self.loop = 0
        self.errors = []
        self.warnings = []
        self.gaps_filled = []
        self.gaps_remaining = []
        self.start_time = time.time()

    def log(self, msg, level="INFO"):
        ts = datetime.now().strftime("%H:%M:%S")
        icon = {"INFO": "ℹ️", "WARN": "⚠️", "ERROR": "❌"}.get(level, "")
        print(f"  [{ts}] {icon} {msg}")

    def add_error(self, ctx, detail):
        self.errors.append({"ctx": ctx, "detail": detail, "time": datetime.now().isoformat()})
        self.log(f"ERROR | {ctx}: {detail}", "ERROR")

    def add_warning(self, ctx, detail):
        self.warnings.append({"ctx": ctx, "detail": detail, "time": datetime.now().isoformat()})
        self.log(f"WARN | {ctx}: {detail}", "WARN")

state = AgentState()

# ══════════════════════════════════════════════════════════════
# 2. 工具调用层（FlyAI CLI 封装）
# ══════════════════════════════════════════════════════════════

def flyai(cmd: str, timeout: int = TIMEOUT) -> dict:
    """调用 FlyAI CLI 并解析 JSON 响应
    
    参数:
        cmd: FlyAI 子命令（如 search-hotel --dest-name "大理"）
        timeout: 超时秒数
    
    返回:
        dict: API 响应 JSON，失败时返回 {"error": "原因"}
    """
    full_cmd = f'{FLYAI} {cmd}'
    state.log(f"🔧 调用 {cmd[:60]}...")
    try:
        r = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        if r.returncode != 0:
            state.add_warning("FlyAI", f"退出码 {r.returncode}: {r.stderr[:100]}")
            return {"error": f"exit_code_{r.returncode}"}
        if not r.stdout.strip():
            state.add_warning("FlyAI", "空响应")
            return {"error": "empty"}
        return json.loads(r.stdout)
    except subprocess.TimeoutExpired:
        state.add_error("FlyAI", f"超时 ({timeout}s): {cmd[:60]}")
        return {"error": "timeout"}
    except json.JSONDecodeError:
        state.add_error("FlyAI", f"JSON解析失败: {r.stdout[:200]}")
        return {"error": "json_parse"}
    except Exception as e:
        state.add_error("FlyAI", str(e))
        return {"error": "fail"}


def get_items(d, key='itemList'):
    """从 FlyAI 嵌套响应中提取数据列表
    
    参数:
        d: FlyAI 响应 dict
        key: 提取的键名（itemList 或 data）
    
    返回:
        list: 提取后的数据列表
    """
    data = d.get('data', {}) or {}
    if isinstance(data, dict):
        if key in data:
            items = data[key]
            flat = []
            for item in items:
                if isinstance(item, dict) and 'journeys' in item:
                    for j in item['journeys']:
                        for s in j.get('segments', []):
                            s['_price'] = j.get('priceInfo', {}).get('minPrice', '?')
                            s['_name'] = f"{s.get('marketingTransportName', '')}{s.get('marketingTransportNo', '')} {s.get('depStationName', '')}-{s.get('arrStationName', '')} {s.get('depDateTime', '')[:10]}"
                            flat.append(s)
                else:
                    flat.append(item)
            return flat
        if 'journeys' in data:
            items = []
            for j in data['journeys']:
                for s in j.get('segments', []):
                    s['_price'] = j.get('priceInfo', {}).get('minPrice', '?')
                    s['_name'] = f"{s.get('marketingTransportName', '')}{s.get('marketingTransportNo', '')}"
                    items.append(s)
            return items
    return [] if isinstance(data, dict) else (data if isinstance(data, list) else [])


# ══════════════════════════════════════════════════════════════
# 3. 输入解析层
# ══════════════════════════════════════════════════════════════

def parse(q: str) -> dict:
    """解析用户自然语言查询
    
    参数:
        q: 用户输入字符串，如 "一家三口大理5天4夜 预算2万 从广州出发 飞机"
    
    返回:
        dict: 结构化旅游参数
    """
    info = {
        "dest": "大理", "days": 5, "budget": 10000,
        "from": "广州", "prefer": "高铁", "guests": "2人",
        "style": "", "needs": [], "date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        # 🚗 自驾语义区分（见 自驾语义约束.md）
        # drive_mode: "全程自驾"=自己开车从家到目的地 | "当地租车"=公交到后再租 | "both"=两者都要对比
        "drive_mode": "none"
    }
    C = ["昆明", "丽江", "大理", "西双版纳", "香格里拉", "腾冲", "普洱",
         "北京", "上海", "广州", "深圳", "杭州", "成都", "重庆", "西安",
         "三亚", "海口", "厦门", "青岛", "大连", "桂林", "张家界", "黄山",
         "南京", "武汉", "长沙", "苏州", "贵阳", "拉萨"]
    
    for c in C:
        if c in q:
            info["dest"] = c
            break

    m = re.search(r'(\d+)\s*天', q)
    if m:
        info["days"] = int(m.group(1))

    m = re.search(r'预算\s*(\d+)\s*万', q)
    if m:
        info["budget"] = int(m.group(1)) * 10000

    for c in C:
        if f"从{c}" in q or f"{c}出发" in q:
            info["from"] = c
            break

    if "飞机" in q or "机票" in q:
        info["prefer"] = "飞机"

    # ── 🚗 自驾语义区分（关键：不能混淆两种自驾）──
    # 全程自驾：自己开车从出发地到目的地（长途跨城，如广州开车1600km到大理）
    # 当地租车：公交（飞机/高铁）到目的地后，在当地租车自驾（如飞到大理后租车 ¥200~400/天）
    drive_full = bool(re.search(r'全程自驾|自己开车去|开车过去|自驾过去|全程开车', q))
    drive_local = bool(re.search(r'当地租车|租车自驾|到了.*租车|落地.*租车|当地.*自驾|下飞机.*租|高铁.*租|到了.*自驾', q))
    drive_generic = bool(re.search(r'自驾|开车', q)) and not drive_local  # 歧义关键词

    if drive_full and drive_local:
        info["drive_mode"] = "both"
        info["prefer"] = "自驾"
        info["needs"].append("对比全程自驾vs当地租车")
    elif drive_full:
        info["drive_mode"] = "全程自驾"
        info["prefer"] = "自驾"
    elif drive_local:
        info["drive_mode"] = "当地租车"
        info["needs"].append("当地租车自驾")
    elif drive_generic:
        # 歧义：用户只说"自驾"，默认按当地租车处理（更常见的亲子游选择）
        info["drive_mode"] = "当地租车"
        info["prefer"] = "自驾"
        info["needs"].append("当地租车自驾")
        state.add_warning("语义", "用户说「自驾」未明确是全程还是当地，默认按「当地租车」处理。如需对比全程自驾，请说「全程自驾」")

    if "一家三口" in q:
        info["guests"] = "一家三口(2大1小)"
    if "亲子" in q:
        info["style"] = "亲子"
        info["needs"].append("亲子友好")
    if "慢节奏" in q or "不赶" in q:
        info["needs"].append("慢节奏")
    if "自然" in q:
        info["needs"].append("自然风光")

    # 安全约束校验
    info = validate_input(info)
    return info


def validate_input(info: dict) -> dict:
    """输入安全校验（见 安全约束.md）
    
    参数:
        info: 解析后的结构化参数
    
    返回:
        dict: 校验并修正后的参数
    """
    # 天数校验
    if info["days"] < 1:
        state.add_warning("校验", f"天数 {info['days']} 无效，重置为5")
        info["days"] = 5
    if info["days"] > 30:
        state.add_warning("校验", f"天数 {info['days']} 超上限，截断为30")
        info["days"] = 30

    # 预算校验
    if info["budget"] < 1000:
        state.add_warning("校验", f"预算 ¥{info['budget']} 过低，重置为10000")
        info["budget"] = 10000
    if info["budget"] > 500000:
        state.add_warning("校验", f"预算 ¥{info['budget']} 异常高，截断为500000")
        info["budget"] = 500000

    # 日期校验：确保不早于今天
    try:
        d = datetime.strptime(info["date"], "%Y-%m-%d")
        if d < datetime.now():
            info["date"] = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            state.add_warning("校验", f"日期已过期，调整为 {info['date']}")
    except:
        info["date"] = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

    return info


# ══════════════════════════════════════════════════════════════
# 4. 数据采集层（Loop 引擎）
# ══════════════════════════════════════════════════════════════

def collect_data(info: dict) -> tuple:
    """全自动 Loop 数据采集
    
    参数:
        info: 结构化旅游参数
    
    返回:
        tuple: (采集结果 dict, 剩余缺口 list, 最终循环数 int)
    """
    results = {}
    gaps = ["hotel", "train", "poi", "flight"]
    
    print(f"\n🎯 {info['dest']} {info['days']}天 ¥{info['budget']:,} {info['guests']} | {info['prefer']}优先 | 从{info['from']}出发\n")
    state.log(f"启动采集 | 目标:{info['dest']} | 循环上限:{MAX_LOOP}")
    
    for loop in range(1, MAX_LOOP + 1):
        state.loop = loop
        fixed = 0
        
        # ── 查酒店（关键：至少获取6个以上供三方案筛选）──
        if "hotel" in gaps:
            r = flyai(f'search-hotel --dest-name "{info["dest"]}" --check-in-date {info["date"]}')
            if get_items(r):
                results["hotel"] = r
                gaps.remove("hotel")
                fixed += 1
                state.gaps_filled.append(f"hotel(L{loop})")
            else:
                state.add_warning("酒店", "主策略失败，尝试关键词搜索")
                r2 = flyai(f'keyword-search --query "{info["dest"]}亲子酒店双床房推荐"')
                if get_items(r2):
                    results["hotel"] = r2
                    gaps.remove("hotel")
                    fixed += 1
                    state.gaps_filled.append("hotel(降级)")
                else:
                    state.add_error("酒店", "所有策略均失败")
        
        # ── 查火车 ──
        if "train" in gaps:
            r = flyai(f'search-train --origin "{info["from"]}" --dest "{info["dest"]}" --date {info["date"]}')
            if get_items(r):
                results["train"] = r
                gaps.remove("train")
                fixed += 1
                state.gaps_filled.append(f"train(L{loop})")
            else:
                r2 = flyai(f'keyword-search --query "{info["from"]}到{info["dest"]}高铁火车票 {info["date"]}"')
                if get_items(r2):
                    results["train"] = r2
                    gaps.remove("train")
                    fixed += 1
                    state.gaps_filled.append("train(降级)")
        
        # ── 查景点 ──
        if "poi" in gaps:
            r = flyai(f'search-poi --city-name "{info["dest"]}"')
            if get_items(r):
                results["poi"] = r
                gaps.remove("poi")
                fixed += 1
                state.gaps_filled.append(f"poi(L{loop})")
            else:
                r2 = flyai(f'keyword-search --query "{info["dest"]}必去景点攻略门票"')
                if get_items(r2):
                    results["poi"] = r2
                    gaps.remove("poi")
                    fixed += 1
                    state.gaps_filled.append("poi(降级)")
        
        # ── 查机票 ──
        if "flight" in gaps:
            r = flyai(f'search-flight --origin "{info["from"]}" --destination "{info["dest"]}" --dep-date {info["date"]}')
            if get_items(r):
                results["flight"] = r
                gaps.remove("flight")
                fixed += 1
                state.gaps_filled.append(f"flight(L{loop})")
            else:
                r2 = flyai(f'keyword-search --query "{info["from"]}到{info["dest"]}机票 {info["date"]}"')
                if get_items(r2):
                    results["flight"] = r2
                    gaps.remove("flight")
                    fixed += 1
                    state.gaps_filled.append("flight(降级)")
        
        # ── 🚗 全程自驾距离估算（仅当 drive_mode 为"全程自驾"或"both"时计算）──
        if "drive" not in results and info.get("drive_mode") in ("全程自驾", "both"):
            dist_map = {
                "广州-大理": 1600, "广州-丽江": 1750, "广州-昆明": 1400,
                "昆明-大理": 320, "成都-大理": 800, "广州-桂林": 500
            }
            dist = dist_map.get(f'{info["from"]}-{info["dest"]}', 800)
            results["drive"] = {
                "km": dist, "h": round(dist / 100, 1),
                "gas": f"¥{int(dist * 0.7)}", "toll": f"¥{int(dist * 0.5)}",
                "total": int(dist * 1.2)
            }

        # ── 🚗 当地租车费用估算（当 drive_mode 为"当地租车"或"both"时计算）──
        if "rental" not in results and info.get("drive_mode") in ("当地租车", "both"):
            # 租车费用 = 日租金 × 天数 + 保险 + 油费
            rental_per_day = 300  # 经济型 SUV ¥200~400/天，取中间值
            insurance = 50 * info["days"]  # 保险约 ¥50/天
            gas_local = 80 * info["days"]  # 当地每天油费约 ¥80
            rental_total = rental_per_day * info["days"] + insurance + gas_local
            results["rental"] = {
                "per_day": rental_per_day,
                "days": info["days"],
                "insurance": insurance,
                "gas_local": gas_local,
                "total": rental_total,
                "note": "经济型SUV估算，携程/神州租车实际价格以预订为准"
            }
        
        # ── 打印进展 ──
        icons = {"hotel": "🏨", "train": "🚄", "poi": "🎯", "flight": "✈️"}
        status = " ".join([f"{'✅' if k not in gaps else '⏳'}{icons.get(k, '')}" for k in ["hotel", "train", "poi", "flight"]])
        print(f"  Loop {loop}: {status} | 修复{fixed} | 剩余缺口{len(gaps)}")
        state.gaps_remaining = list(gaps)
        
        if not gaps:
            break
    
    return results, gaps, loop


# ══════════════════════════════════════════════════════════════
# 5. 酒店方案生成层（核心优化）
# ══════════════════════════════════════════════════════════════

def price_parse(raw: str) -> int:
    """解析酒店价格字符串为整数
    
    参数:
        raw: 价格原始字符串，如 "¥9x"、"¥1xx"、"450"
    
    返回:
        int: 整数价格，失败返回99999
    """
    try:
        s = str(raw)
        # 模糊价格替换
        for old, new in [("xx", "00"), ("9x", "90"), ("1xx", "100"),
                        ("2xx", "200"), ("3xx", "300"), ("4xx", "400"),
                        ("5xx", "500"), ("6xx", "600")]:
            s = s.replace(old, new)
        n = int(re.sub(r'[^0-9]', '', s))
        return n if n > 0 else 99999
    except:
        return 99999


def hotel_tier_name(price: int) -> str:
    """根据价格确定酒店档次名称
    
    参数:
        price: 解析后的整数价格
    
    返回:
        str: 档次名称
    """
    if price <= 150:
        return "经济实惠型"
    elif price <= 350:
        return "舒适品质型"
    else:
        return "亲子精选型"


def analyze_hotel(h: dict, budget_per_night: int, guests: str) -> dict:
    """分析单个酒店的优缺点
    
    参数:
        h: 酒店数据 dict
        budget_per_night: 每晚预算上限
        guests: 出行人员描述
    
    返回:
        dict: 包含 pros, cons, score 的分析结果
    """
    price = price_parse(h.get('price', '0'))
    name = h.get('name', '未知酒店')
    location = h.get('interestsPoi', h.get('address', '位置未标注'))
    star = h.get('star', '未知')
    
    pros = []
    cons = []
    
    # 价格分析
    if price < budget_per_night * 0.5:
        pros.append(f"💰 价格友好：¥{price}/晚，远低于预算 ¥{budget_per_night}/晚，可大幅节省住宿开支")
    elif price <= budget_per_night:
        pros.append(f"💰 预算匹配：¥{price}/晚，在预算 ¥{budget_per_night}/晚以内")
    else:
        cons.append(f"💸 超预算：¥{price}/晚 超出预算 ¥{budget_per_night}/晚，需压缩其他开支")
    
    # 位置分析
    if location and location != "位置未标注":
        if "古城" in location:
            pros.append(f"📍 近古城：{location}，步行可达核心景点，带孩子不折腾")
        elif "洱海" in location:
            pros.append(f"🌊 近洱海：{location}，出门即景，适合散步")
        else:
            pros.append(f"📍 位置：{location}")
    else:
        cons.append("📍 位置信息不足：无法判断出行便利度")
    
    # 类型分析
    if "经济型" in star or "经济" in star:
        cons.append("🏷️ 经济型定位：设施相对基础，带亲子家庭需评估舒适度")
    elif "舒适" in star:
        pros.append("🏷️ 舒适型：设施中上，性价比高")
    
    # 亲子适配
    if "亲子" in name:
        pros.append("👶 亲子标签：酒店主打亲子定位，可能有儿童设施")
    else:
        cons.append("👶 亲子不确定：未标注亲子设施，需电话确认有无双床房+儿童用品")
    
    # 评分
    score = min(100, max(10, 100 - price * 0.2))  # 价格越低分越高（简化版）
    if pros:
        score += len(pros) * 5
    if cons:
        score -= len(cons) * 3
    
    return {"pros": pros, "cons": cons, "score": min(100, max(10, int(score))),
            "price": price, "name": name, "location": location, "star": star}


def gen_hotel_section(hotels: list, budget: int, days: int, guests: str) -> str:
    """生成酒店三方案对比 Markdown 内容
    
    参数:
        hotels: 酒店数据列表
        budget: 总预算
        days: 天数
        guests: 出行人员
    
    返回:
        str: 完整的酒店方案 Markdown
    """
    if not hotels:
        return "\n### 🏨 住宿方案\n\n> ⚠️ FlyAI 接口未返回酒店数据，建议使用飞猪APP手动查询。\n"

    budget_per_night = budget // (days - 1) if days > 1 else budget  # 总预算/(天数-1) 约为每晚预算

    # 排序
    hotels_sorted = sorted(hotels, key=lambda h: price_parse(h.get('price', '0')))

    # 按价格分为三档
    analyzed = []
    for h in hotels_sorted:
        analysis = analyze_hotel(h, budget_per_night, guests)
        analysis["raw"] = h
        analyzed.append(analysis)

    # 从各档中选取代表（至少取3个，不足则全取）
    tiers = {"经济实惠型": [], "舒适品质型": [], "亲子精选型": []}
    for a in analyzed:
        tier = hotel_tier_name(a["price"])
        tiers[tier].append(a)

    # 每档取最佳评分的一个
    selected = []
    for tier_name in ["经济实惠型", "舒适品质型", "亲子精选型"]:
        if tiers[tier_name]:
            best = max(tiers[tier_name], key=lambda x: x["score"])
            best["tier_name"] = tier_name
            selected.append(best)

    # 如果不够3个，从剩余中补
    if len(selected) < 3 and len(analyzed) > len(selected):
        for a in analyzed:
            if a not in selected:
                a["tier_name"] = hotel_tier_name(a["price"])
                selected.append(a)
            if len(selected) >= 3:
                break

    tiers_emoji = {"经济实惠型": "💚", "舒适品质型": "💙", "亲子精选型": "🧡"}

    p = f"""
## 住宿方案对比（每晚详解）

> 💰 每晚住宿预算参考：**¥{budget_per_night:,}/晚**（总预算 ¥{budget:,} ÷ {days - 1}晚）
> 👥 {guests} | 🔑 **必须双床房** | 📞 预订前电话确认

---

"""
    for i, a in enumerate(selected, 1):
        emoji = tiers_emoji.get(a["tier_name"], "📌")
        p += f"""### 方案{i}：{emoji} {a['tier_name']} — {a['name']}

| 维度 | 详情 |
|------|------|
| **价格** | ¥{a['price']}/晚（{days - 1}晚合计 ¥{a['price'] * (days - 1):,}） |
| **档次** | {a['star']} |
| **位置** | {a['location']} |
| **综合评分** | {'⭐' * (a['score'] // 20)}{'☆' * (5 - a['score'] // 20)} ({a['score']}分) |

#### ✅ 优点

"""
        for pro in a["pros"]:
            p += f"- {pro}\n"

        p += f"""
#### ⚠️ 缺点

"""
        for con in a["cons"]:
            p += f"- {con}\n"

        p += "\n---\n"

    # 总结推荐
    best_overall = max(selected, key=lambda x: x["score"])
    p += f"""
### 🏆 综合推荐：{best_overall['name']}

{best_overall['tier_name']} **评分 {best_overall['score']} 分**，综合性价比最高。

| 如看重... | 推荐 |
|-----------|------|
"""
    if selected:
        cheapest = min(selected, key=lambda x: x["price"])
        p += f"| 💰 **节省开支** | {cheapest['name']}（¥{cheapest['price']}/晚）|\n"
        mid = sorted(selected, key=lambda x: x["score"])[len(selected)//2]
        p += f"| ⚖️ **均衡体验** | {best_overall['name']}（¥{best_overall['price']}/晚）|\n"
        most = max(selected, key=lambda x: x["price"])
        p += f"| 👶 **亲子品质** | {most['name']}（¥{most['price']}/晚）|\n"

    p += f"""
> ⚠️ **预订提醒**：以上为 FlyAI 实时查询结果（{datetime.now().strftime('%Y-%m-%d')}），暑假旺季价格波动大，建议提前2周在飞猪/携程下单，并**致电确认双床房**。
"""
    return p


# ══════════════════════════════════════════════════════════════
# 6. 方案生成层
# ══════════════════════════════════════════════════════════════

def gen_plan_md(info: dict, res: dict, gaps: list, loop_count: int) -> str:
    """生成完整的 Markdown 旅行方案
    
    参数:
        info: 结构化旅游参数
        res: 采集结果 dict
        gaps: 剩余缺口列表
        loop_count: 实际执行的循环数
    
    返回:
        str: 完整的 Markdown 文档
    """
    d, days, budget = info["dest"], info["days"], info["budget"]
    hotels = get_items(res.get("hotel", {}))
    pois = get_items(res.get("poi", {}))
    trains = get_items(res.get("train", {}))
    flights = get_items(res.get("flight", {}))
    drive = res.get("drive", {})
    rental = res.get("rental", {})  # 🚗 当地租车费用
    drive_mode = info.get("drive_mode", "none")  # 🚗 自驾语义
    from_city = info["from"]
    date_str = info["date"]

    # 计算预算
    best_hotel_price = 100
    if hotels:
        try:
            best_hotel_price = min(price_parse(h.get('price', '100')) for h in hotels)
        except:
            pass

    flight_est = 3600 if info["prefer"] == "飞机" else 0  # 3人机票估算
    hotel_total = best_hotel_price * (days - 1)
    rental_cost = rental.get("total", 0) if drive_mode in ("当地租车", "both") else 0  # 🚗 租车费用
    drive_cost = drive.get("total", 0) if drive_mode in ("全程自驾", "both") else 0  # 🚗 全程自驾费用
    other_cost = 2500
    est_total = flight_est + hotel_total + rental_cost + drive_cost + other_cost

    p = f"""# 🧭 {d} {days}天{days - 1}夜 旅行方案

> 📅 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')} | 🤖 Agent v5
> 🎯 {info['guests']} | 💰 ¥{budget:,} | 🚗 {info['prefer']}优先 | 从{from_city}出发
> 📊 数据采集：{loop_count}轮循环 | 成功：{len([g for g in ['hotel','train','poi','flight'] if g not in gaps])}/4

---

## 一、行程概览

| 项目 | 详情 |
|------|------|
| 目的地 | {d} |
| 天数 | {days}天{days - 1}夜 |
| 出发地 | {from_city} |
| 预算 | ¥{budget:,} |
| 出行偏好 | {info['prefer']}优先 |
| 风格要求 | {', '.join(info.get('needs', [])) or '默认'} |
| 查询日期 | {date_str} |

---

## 二、交通方案

"""
    # 机票
    if flights:
        p += "### ✈️ 机票\n\n"
        for i, f in enumerate(flights[:3], 1):
            p += f"| {i} | {f.get('flightNo', f.get('_name', f.get('name', '?')))} | {f.get('price', f.get('_price', '?'))} |\n"
        p += "\n"
    else:
        p += "### ✈️ 机票\n\n> ⚠️ FlyAI 未返回机票数据，建议飞猪APP查询。\n\n"

    # 火车
    if trains:
        p += "### 🚄 高铁/火车\n\n"
        for i, t in enumerate(trains[:3], 1):
            p += f"| {i} | {t.get('_name', t.get('trainNo', t.get('name', '?')))} | {t.get('_price', t.get('price', '?'))} |\n"
        p += "\n"
    else:
        p += "### 🚄 高铁/火车\n\n> ⚠️ FlyAI 未返回火车数据。\n\n"

    # 🚗 自驾对比（语义区分：全程自驾 vs 当地租车）
    if drive_mode != "none":
        p += "### 🚗 自驾方案对比\n\n"
        p += "> ⚠️ 人类说「自驾」有两个意思，Agent 必须区分：\n"
        p += "> ① **全程自驾**：自己开车从家到目的地（长途跨城）\n"
        p += "> ② **当地租车**：公交到目的地后，在当地租车自驾（更常见的亲子游选择）\n\n"

        p += "| 维度 | 全程自驾 🚗 | 当地租车 🏎️ |\n"
        p += "|------|-----------|----------|\n"

        # 全程自驾行
        if drive:
            p += f"| **交通方式** | 自己开车 {drive.get('km','?')}km | 飞机/高铁 + 当地租车 |\n"
            p += f"| **单程耗时** | {drive.get('h','?')}小时 | 飞机2.5h+租车 |\n"
            p += f"| **费用明细** | 油费{drive.get('gas','?')} + 过路费{drive.get('toll','?')} | 机票/高铁 + 租车(见下方) |\n"
            p += f"| **全程交通费** | ¥{drive.get('total','?')} | 机票¥3,600 + 租车¥{rental.get('total',0):,} |\n"
        else:
            p += "| **交通方式** | 自己开车（距离未估算） | 飞机/高铁 + 当地租车 |\n"
            p += "| **单程耗时** | 未知 | 飞机2.5h+租车 |\n"
            p += "| **费用明细** | 油费+过路费 | 机票/高铁 + 租车(见下方) |\n"

        # 当地租车行
        if rental:
            p += f"| **租车日租金** | — | ¥{rental.get('per_day',300)}/天 |\n"
            p += f"| **租车天数** | — | {rental.get('days',5)}天 |\n"
            p += f"| **保险** | — | ¥{rental.get('insurance',250)} |\n"
            p += f"| **当地油费** | — | ¥{rental.get('gas_local',400)} |\n"
            p += f"| **租车合计** | — | **¥{rental.get('total',2150):,}** |\n"
            p += f"| **亲子友好度** | ⭐⭐ 长途孩子累 | ⭐⭐⭐⭐ 短途+随时停 |\n"
            p += f"| **适合场景** | 行李多、时间充裕 | **时间有限、5天以内行程** |\n"
        else:
            p += f"| **租车估算** | — | ¥300/天 × {days}天 ≈ ¥{300*days:,} |\n"

        p += "\n"

    elif drive:
        # 旧版兼容：仅有全程自驾数据
        p += f"""### 🚗 自驾参考

| 距离 | 耗时 | 油费 | 过路费 | 合计 |
|------|------|------|--------|------|
| {drive.get('km', '?')}km | {drive.get('h', '?')}h | {drive.get('gas', '?')} | {drive.get('toll', '?')} | ¥{drive.get('total', '?')} |

"""

    # ── 酒店三方案（核心）──
    p += gen_hotel_section(hotels, budget, days, info['guests'])

    # ── 每日行程 ──
    p += f"""
---

## 每日行程参考

"""
    for day in range(1, days + 1):
        if day - 1 < len(pois):
            poi = pois[day - 1]
            p += f"""### 📅 D{day}：{poi.get('name', '自由探索')}

- **景点**：{poi.get('name', '自由探索')}
- **类型**：{poi.get('type', poi.get('category', '未标注'))}
- **建议**：根据当日天气和个人体力灵活调整，亲子出游不赶行程

"""
        else:
            p += f"""### 📅 D{day}：自由探索日

- 根据体力情况，可逛逛当地市集、品尝美食，或酒店休息
- 亲子游的核心是「孩子开心、大人不累」

"""

    # ── 预算概算 ──
    p += f"""---

## 预算概算

| 项目 | 估算 |
|------|------|
| ✈️ 机票（{info['guests']} 往返）| ¥{flight_est:,} |
| 🏨 住宿（{days - 1}晚） | ¥{hotel_total:,} |
"""
    # 🚗 自驾费用行（按语义区分）
    if drive_mode == "全程自驾":
        p += f"| 🚗 全程自驾（{from_city}→{d} 单程） | ¥{drive_cost:,} |\n"
    elif drive_mode == "当地租车":
        p += f"| 🏎️ 当地租车（{rental.get('days', days)}天） | ¥{rental_cost:,} |\n"
    elif drive_mode == "both":
        p += f"| 🚗 全程自驾（{from_city}→{d}） | ¥{drive_cost:,} |\n"
        p += f"| 🏎️ 当地租车（{rental.get('days', days)}天） | ¥{rental_cost:,} |\n"
    p += f"""| 🍜 餐饮 + 门票 + 当地交通 | ¥{other_cost:,} |
| **预估总计** | **¥{est_total:,}** |
| **预算状态** | {'✅ 预算内' if est_total <= budget else f'⚠️ 超 ¥{est_total - budget:,}'} |

---

## 数据采集状态

| 数据项 | 状态 | 说明 |
|--------|------|------|
| 🏨 酒店 | {'✅ 成功' if 'hotel' not in gaps else '❌ 失败'} | 获取 {len(hotels)} 条 |
| 🎯 景点 | {'✅ 成功' if 'poi' not in gaps else '❌ 失败'} | 获取 {len(pois)} 条 |
| 🚄 火车 | {'✅ 成功' if 'train' not in gaps else '❌ 失败'} | 获取 {len(trains)} 条 |
| ✈️ 机票 | {'✅ 成功' if 'flight' not in gaps else '❌ 失败'} | 获取 {len(flights)} 条 |

"""

    if gaps:
        p += f"\n> ⚠️ 以下数据未成功获取：{', '.join(gaps)}。建议使用对应APP手动查询。\n"

    # ── 执行日志 ──
    p += f"""---

## Agent 执行日志

```
🧭 Agent v5 启动 | {d} {days}天 ¥{budget:,}
📊 循环: {loop_count}/{MAX_LOOP} | 数据项: {4 - len(gaps)}/4 成功
📝 采集路径: {', '.join(state.gaps_filled) if state.gaps_filled else '无'}
⚠️ 警告: {len(state.warnings)} | ❌ 错误: {len(state.errors)}
⏱️ 耗时: {time.time() - state.start_time:.1f}s
```

"""
    if state.errors:
        p += "### 错误详情\n\n"
        for e in state.errors:
            p += f"- ❌ **{e['ctx']}**: {e['detail']}\n"

    if state.warnings:
        p += "\n### 警告详情\n\n"
        for w in state.warnings:
            p += f"- ⚠️ **{w['ctx']}**: {w['detail']}\n"

    p += f"""

> 🤖 生成方式：Agent v5（FlyAI 飞猪API + 三方案对比 + 优缺点分析）
> 📄 输出标准：见 `输出标准.md`
"""
    return p


# ══════════════════════════════════════════════════════════════
# 7. 主流程
# ══════════════════════════════════════════════════════════════

def run(q: str) -> str:
    """完整执行：解析 → 采集 → 生成 → 保存
    
    参数:
        q: 用户自然语言查询
    
    返回:
        str: 保存的文件路径
    """
    print(f"\n{'='*50}")
    print(f"🧭 旅行 Agent v5 启动")
    print(f"{'='*50}\n")
    print(f"📝 查询: {q}\n")

    # 1. 解析
    info = parse(q)
    state.log(f"解析完成: {info['dest']} {info['days']}天 ¥{info['budget']:,} | {info['guests']} | {info['prefer']} | {info['date']}")

    # 2. 采集
    results, gaps, loops = collect_data(info)

    # 3. 生成
    print(f"\n📄 生成方案中...")
    plan = gen_plan_md(info, results, gaps, loops)
    
    # 打印摘要
    print(plan[:500] + "...\n")

    # 4. 保存
    safe_dest = re.sub(r'[^\w]', '', info["dest"])
    filename = f"{safe_dest}{info['days']}天{info['days']-1}夜_旅行方案.md"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(plan)

    print(f"✅ 方案已保存: {filepath}")
    print(f"📊 采集 {4 - len(gaps)}/4 项 | {loops} 轮循环 | {time.time() - state.start_time:.1f}s")
    
    if state.errors:
        print(f"⚠️ {len(state.errors)} 个错误（详情见方案文件底部日志）")
    
    return filepath


if __name__ == '__main__':
    q = sys.argv[1] if len(sys.argv) > 1 else "一家三口大理5天4夜 预算2万 高铁"
    run(q)
    print("\n✅ 全自动执行完毕")
