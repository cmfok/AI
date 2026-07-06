#!/usr/bin/env python3
"""
分享会 Q&A 互动系统
===================
- 听众提交问题 → AI 自动归类 + DeepSeek 精炼深层问题
- 每页 PPT 底部显示相关提问
"""
import os, json, time, threading, re
from flask import Flask, request, jsonify, render_template_string, send_from_directory
from datetime import datetime
import httpx
import requests as requests_mod
from ai_help_html import AI_HELP_HTML

# ── 配置 ──────────────────────────────────────────────
PPT_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_FILE = os.path.join(PPT_DIR, 'questions.json')
POLL_FILE = os.path.join(PPT_DIR, 'poll_results.json')
HOST = '0.0.0.0'
PORT = 8008

# ── 数据库配置 ──────────────────────────────────────────
DB_USER = 'lobster'
DB_PASSWORD = os.environ.get('DB_PASSWORD')
if not DB_PASSWORD:
    raise RuntimeError("DB_PASSWORD 环境变量未设置，请设置后重试")
DB_NAME = 'ecommerce_db'

# ── 幻灯片主题定义（用于 AI 分类）────────────────────
SLIDES = [
    {"page": 1,  "title": "【新插入页标题待填写】",           "tags": "新插入页"},
    {"page": 2,  "title": "封面",                        "tags": "封面 AI 真垃圾 分享会 开场 青骏会"},
    {"page": 3,  "title": "外星人的语言",                "tags": "互动 猜字 规律 LLM 预测 下一个词 模式"},
    {"page": 4,  "title": "训练三阶段/RLHF",             "tags": "训练 预训练 指令微调 RLHF 评分 有用性 真实性 安全性 诚实性 语气"},
    {"page": 5,  "title": "核心能力&局限",               "tags": "能力 局限 语言理解 逻辑推理 知识召回 代码生成 幻觉 知识截止"},
    {"page": 6,  "title": "Token概念&费用",              "tags": "Token 费用 成本 运营商 套餐 按量付费 未来判断"},
    {"page": 7,  "title": "模型对比",                    "tags": "模型 对比 DeepSeek 通义千问 Kimi GLM 豆包 擅长 场景"},
    {"page": 8,  "title": "案例·语音→PPT",              "tags": "案例 语音 PPT 提示词 输出结构 模板"},
    {"page": 9,  "title": "提示词工程",                   "tags": "提示词 工程 Prompt 角色 要求 参考 标准 派活"},
    {"page": 10, "title": "案例·约会翻车",               "tags": "案例 约会 知识库 背景 信息 适配度"},
    {"page": 11, "title": "上下文工程",                   "tags": "上下文 知识库 RAG 历史数据 参考模板 业务规则"},
    {"page": 12, "title": "知识库搭建",                   "tags": "知识库 搭建 Trae Obsidian 向量 语义搜索 入门 进阶"},
    {"page": 13, "title": "案例·运费+招聘",              "tags": "案例 运费 对账 招聘 简历 约束 脚本 工作流 校验 工具"},
    {"page": 14, "title": "约束工程",                     "tags": "约束 工具调用 约束 验证 状态 错误处理 可观测 缰绳 MCP"},
    {"page": 15, "title": "案例·生日营销",               "tags": "案例 生日 营销 循环 自动 扫描 通知 回写"},
    {"page": 16, "title": "循环工程",                     "tags": "循环 自查 复盘 会诊 绩效 反馈 多Agent 并行 通讯"},
    {"page": 17, "title": "个人AI vs 企业AI",            "tags": "个人 企业 效率 可控 容错 生产环境"},
    {"page": 18, "title": "数据隐私",                     "tags": "隐私 数据 泄露 加密 私有化 本地化"},
    {"page": 19, "title": "落地Checklist",               "tags": "Checklist 落地 场景 模型 提示词 约束 监控"},
]

# ── 幻灯片详细描述（用于 LLM 语义理解）──────────────────
SLIDE_DESCRIPTIONS = [
    {"page": 1,  "title": "【新插入页】",          "desc": "新的幻灯片页面，标题待填写"},
    {"page": 2,  "title": "封面",                 "desc": "AI 真垃圾分享会开场页，介绍演讲主题和两个阶段感受"},
    {"page": 3,  "title": "外星人的语言",         "desc": "互动猜字游戏，展示LLM预测下一个词的原理，让观众理解AI底层模式识别机制"},
    {"page": 4,  "title": "训练三阶段/RLHF",      "desc": "大模型训练流程：预训练→指令微调→RLHF评分，涵盖有用性/真实性/安全性/诚实性"},
    {"page": 5,  "title": "核心能力&局限",        "desc": "大模型的核心能力（语言理解/逻辑推理/知识召回/代码生成）和局限（幻觉/知识截止）"},
    {"page": 6,  "title": "Token概念&费用",       "desc": "Token的概念、成本计算、按量付费模式、未来趋势判断"},
    {"page": 7,  "title": "模型对比",              "desc": "DeepSeek/通义千问/Kimi/GLM/豆包等模型的擅长场景对比"},
    {"page": 8,  "title": "案例·语音→PPT",        "desc": "提示词工程实际案例：通过语音输入自动生成PPT，展示提示词输出结构设计"},
    {"page": 9,  "title": "提示词工程",             "desc": "如何写好Prompt让AI听话：角色设定、要求约束、参考示例、质量标准、任务派发"},
    {"page": 10, "title": "案例·约会翻车",         "desc": "上下文工程案例：因知识库缺失导致AI回答翻车，说明背景信息的重要性"},
    {"page": 11, "title": "上下文工程",             "desc": "RAG/知识库/历史数据/参考模板/业务规则：让AI理解业务上下文的工程方法"},
    {"page": 12, "title": "知识库搭建",             "desc": "如何使用Trae/Obsidian搭建知识库、向量存储与语义搜索、入门到进阶路径"},
    {"page": 13, "title": "案例·运费+招聘",        "desc": "约束工程案例：运费对账规则校验、招聘简历筛选的脚本工作流和校验机制"},
    {"page": 14, "title": "约束工程",               "desc": "工具调用/MCP/约束验证/状态管理/错误处理/可观测性：如何给AI套上缰绳"},
    {"page": 15, "title": "案例·生日营销",         "desc": "循环工程案例：生日营销自动化——自动扫描客户→通知→回写的闭环流程"},
    {"page": 16, "title": "循环工程",               "desc": "自查/复盘/会诊/绩效反馈/多Agent并行协作/Agent间通讯机制"},
    {"page": 17, "title": "个人AI vs 企业AI",      "desc": "个人使用与落地到企业生产环境的差异：效率优先vs可控性/容错性"},
    {"page": 18, "title": "数据隐私",               "desc": "AI时代的数据隐私保护：加密/私有化部署/本地化方案/防泄露措施"},
    {"page": 19, "title": "落地Checklist",         "desc": "AI落地的完整检查清单：场景识别→模型选择→提示词设计→约束构建→监控运维"},
]

# 不展示问题的封面/过渡页（不参与 AI 分类，已有问题强制迁移）
COVER_PAGES = {2, 4, 7}
# 无法归类的问题统一放到此页
FALLBACK_PAGE = 20

app = Flask(__name__, static_folder=PPT_DIR, static_url_path='')

# ── 数据存储 ──────────────────────────────────────────
_questions_lock = threading.RLock()

def load_questions():
    with _questions_lock:
        if os.path.exists(QUESTIONS_FILE):
            with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

def save_questions(questions):
    with _questions_lock:
        with open(QUESTIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)

# ── AI 分类引擎（TF-IDF + 余弦相似度，纯 CPU 零依赖）──
class Classifier:
    def __init__(self):
        self.vectorizer = None
        self.slide_vectors = None
        self.slide_texts = [f"{s['title']} {s['tags']}" for s in SLIDES]
        self._lock = threading.Lock()

    def _lazy_load(self):
        if self.vectorizer is not None:
            return
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            import numpy as np
            self.vectorizer = TfidfVectorizer(
                analyzer='char', ngram_range=(1, 3),
                max_features=5000, sublinear_tf=True
            )
            self.slide_vectors = self.vectorizer.fit_transform(self.slide_texts)
            print(f'[分类器] TF-IDF 已加载，{self.slide_vectors.shape[1]} 个特征')
        except Exception as e:
            print(f'[分类器] TF-IDF 加载失败: {e}')
            self.vectorizer = False

    def classify(self, question_text):
        """将问题归类到最相关的幻灯片页面，排除封面/过渡页"""
        with self._lock:
            self._lazy_load()

        if self.vectorizer:
            from sklearn.metrics.pairwise import cosine_similarity
            import numpy as np
            q_vec = self.vectorizer.transform([question_text])
            scores = cosine_similarity(q_vec, self.slide_vectors)[0]
            # 按分数从高到低排序，跳过封面页
            ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
            for idx, score in ranked:
                page = SLIDES[idx]['page']
                if page not in COVER_PAGES:
                    return page, float(score)
            # 全部是封面页（不可能），保底返回 FALLBACK_PAGE
            return FALLBACK_PAGE, 0.0
        else:
            return self._keyword_fallback(question_text)

    def _keyword_fallback(self, text):
        """降级方案：关键词匹配（跳过封面页）"""
        text_lower = text.lower()
        best_score = -1
        best_page = FALLBACK_PAGE
        for s in SLIDES:
            if s['page'] in COVER_PAGES:
                continue
            score = sum(1 for kw in s['tags'].split() if kw.lower() in text_lower)
            if score > best_score:
                best_score = score
                best_page = s['page']
        return best_page, best_score / 10.0

classifier = Classifier()

# ── DeepSeek 输入分析（类型判断 + 精炼）─────────────────
# 优先从环境变量读取，未设置时从 deepseek_key.json 读取
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
if not DEEPSEEK_API_KEY:
    try:
        with open(os.path.join(os.path.dirname(__file__), 'deepseek_key.json')) as f:
            DEEPSEEK_API_KEY = json.load(f).get('deepseek_api_key', '')
    except:
        pass
DEEPSEEK_BASE_URL = 'https://api.deepseek.com/v1'

# 关键词降级：判断输入是分享还是提问
SHARE_KEYWORDS = ['分享', '场景', '我们公司', '我们工厂', '我在用', '我们目前', '目前公司', '目前我们', '我的经验',
                  '分享一下', '推荐', '介绍', '我们用了', '我用了', '我们尝试', '我们的做法']
QUESTION_KEYWORDS = ['怎么', '如何', '为什么', '能不能', '是否', '什么', '哪', '吗', '?', '？',
                     '会不会', '可以不', '怎样', '该怎么办', '怎么解决', '怎么处理', '怎么避免']

def _keyword_type_detect(text):
    """关键词降级：判断输入是分享还是提问"""
    text_l = text.lower()
    share_score = sum(1 for kw in SHARE_KEYWORDS if kw in text_l)
    question_score = sum(1 for kw in QUESTION_KEYWORDS if kw in text_l)
    if question_score > share_score:
        return 'question'
    elif share_score > question_score:
        return 'share'
    return 'question'  # 默认当作提问

def analyze_input(text):
    """用 DeepSeek 一次调用：判断类型(分享/提问) + 精炼内容"""
    if not DEEPSEEK_API_KEY:
        return _keyword_type_detect(text), '', ''
    try:
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一个AI分享会的助手，帮助整理听众的输入。请用中文回答，只返回JSON。"},
                {"role": "user", "content": f"""听众提交了一段内容，请做三件事：
1. 判断这是「分享场景」还是「提问问题」
   - 分享场景：听众在分享自己使用AI的经验、场景或做法
   - 提问问题：听众在询问某个具体问题、寻求解决方案或建议
2. 如果是提问：把他的问题转化成更清晰的表述，挖掘他背后可能真正关心的问题
3. 如果是分享：提取他分享的核心场景或经验

原始内容：{text}

请严格按以下 JSON 格式返回，不要多余内容：
{{"type": "share/question", "refined": "转化后的清晰表述/核心场景", "deeper": "（提问）他可能真正关心的是... / （分享）这个场景的关键点..."}}"""}
            ],
            "temperature": 0.3,
            "max_tokens": 1024
        }
        with httpx.Client(timeout=60) as client:
            resp = client.post(
                f'{DEEPSEEK_BASE_URL}/chat/completions',
                headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {DEEPSEEK_API_KEY}'},
                json=payload
            )
            if resp.status_code == 200:
                data = resp.json()
                content = data['choices'][0]['message']['content']
                match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
                if match:
                    result = json.loads(match.group())
                    rtype = result.get('type', '').strip().lower()
                    if rtype not in ('share', 'question'):
                        rtype = _keyword_type_detect(text)
                    return rtype, result.get('refined', ''), result.get('deeper', '')
    except Exception as e:
        print(f'[分析] LLM 调用失败: {e}')
    # 降级
    return _keyword_type_detect(text), '', ''

# ── 语义理解管道（新增）──────────────────────────────────
import hashlib

_semantic_cache = {}  # text_hash → {ts, result}
_SEMANTIC_CACHE_TTL = 300  # 5 分钟

def _build_semantic_system_prompt():
    """构建语义理解管道的 System Prompt（含四大工程体系 + 19 页详情）"""
    slide_text = '\n'.join([
        f"P{s['page']}: {s['title']}（{s['desc']}）"
        for s in SLIDE_DESCRIPTIONS
    ])
    return f"""你是一个AI分享会的语义理解引擎。本次分享会的主题是"AI真垃圾"——
探讨AI在企业场景下的真实落地实践，核心内容围绕四大工程体系：

【四大工程体系】
① 提示词工程（Prompt Engineering）
  - 写好指令让AI听话：角色设定、要求约束、参考示例、任务派发
  - 案例：语音→PPT 智能转换（第8页）

② 上下文工程（Context Engineering）
  - RAG/知识库/背景信息：让AI理解业务上下文
  - 案例：约会翻车之知识库缺失（第10页）、知识库搭建（第12页）

③ 规训工程（Constraint Engineering）
  - MCP/约束/校验/工具调用：限制AI的行为边界
  - 案例：运费对账规则、招聘简历筛选（第13页）

④ 循环工程（Loop Engineering）
  - 自循环Agent/多Agent编排：AI自主闭环运行
  - 案例：生日营销自动化（第15页）

【页面列表（共19页）】
{slide_text}

请分析以下听众输入，严格按JSON格式返回。
注意：
- 页面匹配基于语义理解，禁止关键词硬匹配
- 候选页列表长度 0~3，最多3个候选
- 改写后的表述要简洁清晰，适合投屏展示
- 无法匹配任何页面时返回空列表"""

def _keyword_fallback(text):
    """语义理解降级：关键词方案"""
    rtype = _keyword_type_detect(text)
    # TF-IDF 分类
    page, score = classifier.classify(text)
    return {
        'type': rtype,
        'refined': text[:200],
        'page': page if page else None,
        'candidate_pages': [page] if page else [],
        'reason': '关键词降级匹配'
    }

def semantic_understand(text, source='manual'):
    """语义理解管道：类型识别 + 问题改写 + 语义页码匹配 + 多页面判断
    返回: {type, refined, page, candidate_pages, reason}
    """
    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    # 检查缓存
    if text_hash in _semantic_cache:
        cached = _semantic_cache[text_hash]
        if time.time() - cached['ts'] < _SEMANTIC_CACHE_TTL:
            print(f'[语义理解] 缓存命中: {text[:50]}...')
            return cached['result']

    if not DEEPSEEK_API_KEY:
        result = _keyword_fallback(text)
        _semantic_cache[text_hash] = {'ts': time.time(), 'result': result}
        return result

    system_prompt = _build_semantic_system_prompt()
    try:
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f'听众输入：{text}\n\n返回格式：{{"type":"question|share","refined":"改写后表述","page":页码,"candidate_pages":[页码列表],"reason":"匹配理由"}}'}
            ],
            "temperature": 0.3,
            "max_tokens": 2048
        }
        with httpx.Client(timeout=15) as client:
            resp = client.post(
                f'{DEEPSEEK_BASE_URL}/chat/completions',
                headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {DEEPSEEK_API_KEY}'},
                json=payload
            )
            if resp.status_code == 200:
                content = resp.json()['choices'][0]['message']['content']
                match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
                if match:
                    result = json.loads(match.group())
                    rtype = result.get('type', '').strip().lower()
                    if rtype not in ('share', 'question'):
                        rtype = 'question'
                    refined = result.get('refined', text)[:500]
                    page = result.get('page')
                    candidate_pages = result.get('candidate_pages', [])
                    if not isinstance(candidate_pages, list):
                        candidate_pages = []
                    candidate_pages = [p for p in candidate_pages if isinstance(p, int) and 1 <= p <= len(SLIDES)][:3]
                    if page is not None and (not isinstance(page, int) or page < 1 or page > len(SLIDES)):
                        page = None

                    result_data = {
                        'type': rtype,
                        'refined': refined,
                        'page': page,
                        'candidate_pages': candidate_pages,
                        'reason': result.get('reason', '')
                    }
                    _semantic_cache[text_hash] = {'ts': time.time(), 'result': result_data}
                    print(f'[语义理解] 成功: type={rtype}, page={page}, candidates={candidate_pages}')
                    return result_data
    except httpx.TimeoutException:
        print(f'[语义理解] LLM 超时(15s)，降级到关键词: {text[:50]}...')
    except Exception as e:
        print(f'[语义理解] LLM 调用失败: {e}')

    # 降级
    result = _keyword_fallback(text)
    _semantic_cache[text_hash] = {'ts': time.time(), 'result': result}
    return result

def _semantic_cache_cleanup():
    """后台线程：定期清理过期的语义理解缓存"""
    while True:
        time.sleep(60)
        now = time.time()
        global _semantic_cache
        keys_to_del = [k for k, v in _semantic_cache.items() if now - v['ts'] >= _SEMANTIC_CACHE_TTL]
        for k in keys_to_del:
            del _semantic_cache[k]
        if keys_to_del:
            print(f'[缓存清理] 移除了 {len(keys_to_del)} 条语义理解缓存')

# ── 后台异步归类 ──────────────────────────────────────
def classify_pending():
    """后台线程：处理未归类/未定类型的问题 + 精炼 + 迁移封面页问题"""
    while True:
        try:
            time.sleep(5)
            questions = load_questions()
            changed = False
            for q in questions:
                # 阶段1：还未判断类型 → 用 LLM 分析（类型 + 精炼）
                if q.get('type') is None:
                    qtype, refined, deeper = analyze_input(q['question'])
                    q['type'] = qtype
                    if refined:
                        q['refined'] = refined
                        q['deeper'] = deeper
                        q['refined_at'] = datetime.now().isoformat()
                    changed = True
                    print(f'[类型] 问题#{q["id"]} → {qtype} (精炼:{bool(refined)})')

                page = q.get('page')
                # 阶段2：未归类 → 分类到幻灯片页
                if page is None:
                    page, score = classifier.classify(q['question'])
                    q['page'] = page
                    q['score'] = round(score, 3)
                    q['classified_at'] = datetime.now().isoformat()
                    changed = True
                    print(f'[分类] 问题#{q["id"]} → 第{page}页 (置信度:{score:.2f})')
                # 阶段3：落在封面页 → 重新分配到非封面页
                elif page in COVER_PAGES:
                    new_page, score = classifier.classify(q['question'])
                    q['page'] = new_page
                    q['score'] = round(score, 3)
                    q['classified_at'] = datetime.now().isoformat()
                    changed = True
                    print(f'[迁移] 问题#{q["id"]} 原第{page}页(封面) → 第{new_page}页 (置信度:{score:.2f})')
            if changed:
                save_questions(questions)
        except Exception as e:
            print(f'[后台] classify_pending 异常: {e}', flush=True)
            import traceback
            traceback.print_exc()

# ── 全局 CORS（允许 demo 页面从任何域名调用 API）──
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    # 禁止 Cloudflare 缓存 HTML 页面
    if request.path.endswith('.html') or not '.' in request.path.split('/')[-1]:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.route('/hr-sessions')
def hr_sessions_page():
    return app.send_static_file('hr_sessions.html')

# ── HR Agent 实时会话 API ──────────────────────────────
import glob as _glob

@app.route('/api/hr-session/latest')
def hr_session_latest():
    """返回最新的 HR Agent 会话 ID"""
    session_dir = '/root/.openclaw/agents/hr/sessions'
    # ubuntu 无 /root 读权限，用 sudo ls
    try:
        import subprocess as _sp
        out = _sp.check_output(['sudo', 'sh', '-c', 'ls -t ' + session_dir + '/*.jsonl'], timeout=5, text=True, stderr=_sp.DEVNULL)
        files = [f.strip() for f in out.split('\n') if f.strip() and '.jsonl' in f]
    except:
        files = sorted(_glob.glob('/tmp/hr_sessions/*.jsonl'), key=os.path.getmtime, reverse=True)
    # 过滤掉 .bak / .reset / trajectory / checkpoint
    clean = [f for f in files if '.bak' not in f and '.reset' not in f 
             and 'trajectory' not in f and 'checkpoint' not in f]
    if not clean:
        return jsonify({'ok': False, 'error': '暂无会话'}), 404
    # 按 CM 的 open_id 筛选飞书对话
    cm_open_id = 'ou_3eb13a90e8147a4597ef609bbab5e99e'
    for f in clean:
        try:
            with open(f, 'r') as fh:
                first = json.loads(fh.readline())
            if first.get('type') == 'message':
                msg = first.get('message', {})
                content = msg.get('content', [])
                for c in content:
                    if c.get('type') == 'text':
                        txt = c.get('text', '')
                        if 'chat_id' in txt and cm_open_id[:10] in txt:
                            sid = os.path.basename(f).replace('.jsonl', '')
                            return jsonify({'ok': True, 'session_id': sid, 'path': f})
                        break
        except:
            continue
    # 没找到 CM 的对话，退回第一个
    sid = os.path.basename(clean[0]).replace('.jsonl', '')
    return jsonify({'ok': True, 'session_id': sid, 'path': clean[0]})

@app.route('/api/hr-session/<sid>')
def hr_session_get(sid):
    """获取会话消息，支持增量轮询（?from=N 只返回第 N 行及之后）"""
    session_dir = '/root/.openclaw/agents/hr/sessions'
    if not os.path.isdir(session_dir):
        session_dir = '/tmp/hr_sessions'
    fpath = os.path.join(session_dir, sid + '.jsonl')
    if not os.path.isfile(fpath):
        # 可能权限问题，尝试 /tmp 路径
        fpath = os.path.join('/tmp/hr_sessions', sid + '.jsonl')
    if not os.path.isfile(fpath):
        return jsonify({'ok': False, 'error': '会话不存在'}), 404
    
    from_line = request.args.get('from', 0, type=int)
    messages = []
    line_num = 0
    try:
        # 文件在 /root/ 下需要用 sudo 读
        if fpath.startswith('/root/'):
            import subprocess as _sp
            content = _sp.check_output(['sudo', 'cat', fpath], timeout=10, text=True)
            lines = content.split('\n')
        else:
            with open(fpath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        
        for line in lines:
                if line_num < from_line:
                    line_num += 1
                    continue
                try:
                    d = json.loads(line)
                    if d.get('type') == 'message':
                        msg = d.get('message', {})
                        role = msg.get('role', '')
                        content = msg.get('content', [])
                        text_parts = []
                        card_data = None
                        for c in content:
                            t = c.get('type', '')
                            if t == 'text':
                                raw = c.get('text', '')
                                # 检测卡片文件路径
                                card_match = re.search(r'/tmp/resume_card_\d+\.json', raw)
                                if card_match:
                                    try:
                                        with open(card_match.group(0), 'r') as cf:
                                            card_data = json.load(cf)
                                        text_parts.append(raw.split('\n')[0])  # 保留第一行摘要
                                    except:
                                        text_parts.append(raw)
                                elif role == 'user' and 'Conversation info (untrusted metadata)' in raw:
                                    # 清理 Feishu 元数据包装，提取实际消息
                                    lines = raw.split('\n')
                                    for line in reversed(lines):
                                        line = line.strip()
                                        if line and not line.startswith('{') and not line.startswith('}') and not line.startswith('[') and not line.startswith('```') and 'message_id' not in line and 'sender_id' not in line and 'chat_id' not in line and 'timestamp' not in line and 'Conversation' not in line and 'Sender' not in line and 'untrusted' not in line:
                                            text_parts.append(line)
                                            break
                                else:
                                    text_parts.append(raw)
                            elif t == 'thinking':
                                text_parts.append('💭 ' + str(c.get('thinking', ''))[:200])
                            elif t == 'toolCall':
                                text_parts.append('🔧 ' + c.get('name', 'tool'))
                            elif t == 'toolResult':
                                text_parts.append('📋 ' + str(c.get('result', ''))[:300])
                        messages.append({
                            'role': role,
                            'text': '\n'.join(text_parts) if text_parts else '',
                            'ts': d.get('timestamp', ''),
                            'line': line_num,
                            'card': card_data
                        })
                except:
                    pass
                line_num += 1
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
    
    total_lines = line_num
    return jsonify({
        'ok': True,
        'session_id': sid,
        'messages': messages,
        'total_lines': total_lines,
        'has_more': total_lines > 0
    })

# ── 发送消息到飞书 HR Agent ───────────────────────────
@app.route('/api/send-to-hr', methods=['POST'])
def send_to_hr_agent():
    """接收网页消息，通过飞书 API 发送给 HR Agent"""
    data = request.get_json(silent=True) or {}
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'ok': False, 'error': '消息为空'}), 400
    
    try:
        # 加载飞书凭证
        cred_path = '/opt/scripts/.feishu_hr_cred.json'
        if not os.path.exists(cred_path):
            return jsonify({'ok': False, 'error': '飞书凭证不存在'}), 500
        cred = json.load(open(cred_path))
        
        # 获取 tenant_access_token
        r = requests_mod.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
                         json={'app_id': cred['app_id'], 'app_secret': cred['app_secret']}, timeout=10)
        token = r.json().get('tenant_access_token', '')
        if not token:
            return jsonify({'ok': False, 'error': '飞书认证失败'}), 500
        
        # 发送消息（CM 的 open_id）
        open_id = 'ou_3eb13a90e8147a4597ef609bbab5e99e'
        resp = requests_mod.post(
            'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id',
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
            json={'receive_id': open_id, 'msg_type': 'text',
                  'content': json.dumps({'text': text})},
            timeout=10
        )
        if resp.status_code == 200:
            return jsonify({'ok': True, 'message': '已发送到飞书 HR Agent'})
        return jsonify({'ok': False, 'error': f'飞书API错误: {resp.status_code} {resp.text[:200]}'}), 500
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

# ── 读取服务器文件为 base64（仅限 /tmp/hr_media/ 目录）──
ALLOWED_MEDIA_DIR = '/tmp/hr_media'

@app.route('/api/read-file')
def read_file_base64():
    """读取服务器文件，返回 base64（仅限 /tmp/hr_media/ 目录）"""
    fpath = request.args.get('path', '')
    if not fpath:
        return jsonify({'ok': False, 'error': '路径为空'}), 400
    fname = os.path.basename(fpath)
    safe_path = os.path.normpath(os.path.join(ALLOWED_MEDIA_DIR, fname))
    if not safe_path.startswith(ALLOWED_MEDIA_DIR):
        return jsonify({'ok': False, 'error': '禁止访问'}), 403
    if not os.path.isfile(safe_path):
        return jsonify({'ok': False, 'error': '文件不存在'}), 404
    try:
        import base64
        with open(safe_path, 'rb') as f:
            raw = f.read()
        b64 = base64.b64encode(raw).decode()
        return jsonify({'ok': True, 'base64': b64, 'filename': fname, 'size': len(b64)})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

# ── API 路由 ───────────────────────────────────────────
@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/test')
def test_page():
    return app.send_static_file('test.html')

@app.route('/Y')
@app.route('/y')
def script_card():
    return app.send_static_file('Y.html')

@app.route('/case-study')
def case_study_page():
    return app.send_static_file('case_study.html')

@app.route('/demo')
def demo_page():
    return app.send_static_file('demo.html')

@app.route('/images/<path:fname>')
def serve_image(fname):
    from flask import send_file
    img_dir = os.path.join(os.path.dirname(__file__), 'images')
    safe = os.path.realpath(os.path.join(img_dir, fname.split('?')[0]))
    if not safe.startswith(os.path.realpath(img_dir) + os.sep):
        return '', 403
    if not os.path.isfile(safe):
        return '', 404
    return send_file(safe)

@app.route('/ai/<path:subpath>')
def serve_ai_static(subpath):
    """显式服务 ai/ 静态资源目录（图标、动画子页面等）"""
    ai_dir = os.path.join(os.path.dirname(__file__), 'ai')
    return send_from_directory(ai_dir, subpath)


@app.route('/demo-hr')
def demo_hr_page():
    return app.send_static_file('demo_hr.html')

@app.route('/poll-results')
def poll_results_page():
    return render_template_string(POLL_RESULTS_HTML)

@app.route('/ask')
def ask_page():
    return render_template_string(ASK_HTML)

@app.route('/questions')
def questions_page():
    return render_template_string(QUESTIONS_HTML)

@app.route('/AI')
@app.route('/ai')
def ai_help_page():
    return app.send_static_file('tech_display.html')

@app.route('/qrcode')
def qrcode_page():
    return render_template_string(QRCODE_HTML)
@app.route("/cc")
def cc_page():
    return app.send_static_file("cc/index.html")


@app.route('/api/questions', methods=['POST'])
def submit_question():
    data = request.get_json(force=True)
    name = data.get('name', '').strip() or '匿名'
    question = data.get('question', '').strip()
    source = data.get('source', 'manual')  # qrcode | voice | manual
    if not question:
        return jsonify({'ok': False, 'error': '内容不能为空'}), 400
    if len(question) > 500:
        return jsonify({'ok': False, 'error': '内容不能超过500字'}), 400

    # 语义理解管道：类型识别 + 问题改写 + 页码匹配 + 多页面判断
    sem_result = semantic_understand(question, source)
    rtype = sem_result['type']
    refined = sem_result['refined']
    page = sem_result['page']
    candidate_pages = sem_result['candidate_pages']
    reason = sem_result['reason']

    # 'share' 类型：不入队列，直接返回
    if rtype == 'share':
        print(f'[提交] 分享场景(不入队列): {question[:60]}...')
        return jsonify({
            'ok': True, 'type': 'share',
            'question': question, 'refined': refined,
            'message': '感谢你的分享！你的经验已记录。'
        })

    # 'question' 类型：进入问题队列
    with _questions_lock:
        questions = load_questions()
        qid = len(questions) + 1
        multi_page = len(candidate_pages) > 1
        entry = {
            'id': qid,
            'name': name,
            'question': question,
            'original': question,
            'type': rtype,          # 'question'
            'refined': refined,
            'deeper': '',
            'page': page,
            'candidate_pages': candidate_pages,
            'multi_page': multi_page,
            'score': None,
            'source': source,
            'created_at': datetime.now().isoformat(),
            'classified_at': datetime.now().isoformat(),
            'refined_at': datetime.now().isoformat(),
        }
        questions.append(entry)
        save_questions(questions)

    print(f'[提交] 问题#{qid}: type={rtype}, page={page}, candidates={candidate_pages}, source={source}')
    return jsonify({
        'ok': True, 'id': qid, 'page': page,
        'type': rtype, 'refined': refined,
        'candidate_pages': candidate_pages,
        'multi_page': multi_page,
        'message': '谢谢！你的问题已提交'
    })

@app.route('/api/questions', methods=['GET'])
def get_questions():
    questions = load_questions()
    # 按页面分组返回
    by_page = {}
    for q in questions:
        p = q.get('page') or 0
        by_page.setdefault(p, []).append({
            'id': q['id'],
            'name': q['name'],
            'question': q['question'],
            'original': q.get('original', q['question']),
            'type': q.get('type'),        # 'share' | 'question' | null
            'refined': q.get('refined', ''),
            'deeper': q.get('deeper', ''),
            'page': q.get('page'),
            'candidate_pages': q.get('candidate_pages', []),
            'multi_page': q.get('multi_page', False),
            'source': q.get('source', 'manual'),
        })
    return jsonify({
        'total': len(questions),
        'classified': sum(1 for q in questions if q.get('page')),
        'by_page': by_page,
        'slides': SLIDES,
    })

@app.route('/api/questions/update', methods=['POST'])
def update_question_page():
    data = request.json
    qid = data.get('id')
    new_page = data.get('page')
    if qid is None or new_page is None:
        return jsonify({'ok': False, 'message': '缺少参数'}), 400
    questions = load_questions()
    for q in questions:
        if q['id'] == qid:
            q['page'] = int(new_page)
            save_questions(questions)
            return jsonify({'ok': True, 'message': f'已调整到第{new_page}页'})
    return jsonify({'ok': False, 'message': '未找到该问题'}), 404

@app.route('/api/questions/move', methods=['POST'])
def move_question():
    """移动问题到其他页码（control.html 使用的别名）"""
    return update_question_page()

@app.route('/api/questions/delete', methods=['POST'])
def delete_question():
    data = request.get_json(silent=True) or {}
    qid = data.get('id')
    if qid is None:
        return jsonify({'ok': False, 'message': '缺少参数'}), 400
    with _questions_lock:
        questions = load_questions()
        questions = [q for q in questions if q['id'] != qid]
        save_questions(questions)
    return jsonify({'ok': True, 'message': '已删除'})

# ── 语义理解 API（新增）─────────────────────────────────

@app.route('/api/questions/semantic-understand', methods=['POST'])
def api_semantic_understand():
    """语义理解管道：类型识别 + 问题改写 + 页码匹配 + 多页面判断"""
    data = request.get_json(silent=True) or {}
    text = data.get('text', '').strip()
    source = data.get('source', 'manual')
    if not text:
        return jsonify({'ok': False, 'error': '缺少文本'}), 400
    result = semantic_understand(text, source)
    return jsonify({'ok': True, **result})


@app.route('/api/questions/multi-page-ask', methods=['POST'])
def api_multi_page_ask():
    """多页面候选反问：返回候选页列表供听众选择"""
    data = request.get_json(silent=True) or {}
    qid = data.get('qid')
    candidate_pages = data.get('candidate_pages', [])
    if not candidate_pages:
        return jsonify({'ok': False, 'error': '无候选页'}), 400

    # 构建选项列表
    page_map = {s['page']: s['title'] for s in SLIDES}
    options = []
    for p in candidate_pages:
        title = page_map.get(p, f'第{p}页')
        options.append(f'第{p}页 - {title}')
    options.append('以上都不是，请直接回答')

    return jsonify({
        'ok': True,
        'questions': [{
            'q': '您的问题似乎涉及以下多个主题，请问最接近哪一个？',
            'options': options
        }]
    })


@app.route('/api/questions/voice-process', methods=['POST'])
def api_voice_process():
    """语音语义处理：语音文字→语义理解→入队列"""
    data = request.get_json(silent=True) or {}
    text = data.get('text', '').strip()
    session_id = data.get('session_id', '')
    if not text:
        return jsonify({'ok': False, 'error': '缺少语音文本'}), 400

    # 调用语义理解管道
    result = semantic_understand(text, 'voice')
    if result['type'] == 'share':
        return jsonify({
            'ok': True, 'type': 'share',
            'refined': result['refined'],
            'entered_queue': False,
            'message': '分享场景，不入队列'
        })

    # 'question' 类型：创建问题加入队列
    with _questions_lock:
        questions = load_questions()
        qid = len(questions) + 1
        multi_page = len(result['candidate_pages']) > 1
        entry = {
            'id': qid,
            'name': '语音',
            'question': text,
            'original': text,
            'type': 'question',
            'refined': result['refined'],
            'deeper': '',
            'page': result['page'],
            'candidate_pages': result['candidate_pages'],
            'multi_page': multi_page,
            'score': None,
            'source': 'voice',
            'created_at': datetime.now().isoformat(),
            'classified_at': datetime.now().isoformat(),
            'refined_at': datetime.now().isoformat(),
        }
        questions.append(entry)
        save_questions(questions)

    return jsonify({
        'ok': True, 'type': 'question',
        'refined': result['refined'],
        'qid': qid,
        'page': result['page'],
        'entered_queue': True
    })


@app.route('/status')
def status_page():
    return render_template_string(STATUS_HTML)

@app.route('/api/status')
def status():
    import subprocess, json
    questions = load_questions()
    
    # Server info
    disk = subprocess.run(['df', '-h', '/'], capture_output=True, text=True).stdout.split('\n')[1].split()
    uptime = subprocess.run(['uptime', '-p'], capture_output=True, text=True).stdout.strip()
    mem = subprocess.run(['free', '-h'], capture_output=True, text=True).stdout.split('\n')[1].split()
    
    # DB info
    db_info = {'dbs': 0, 'tables': 0, 'latest_orders': '', 'db_size': ''}
    try:
        r = subprocess.run(['mysql', '-u', DB_USER, f'-p{DB_PASSWORD}', '-e', 
            "SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA='ecommerce_db';"],
            capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            db_info['tables'] = r.stdout.strip().split('\n')[-1]
        r2 = subprocess.run(['mysql', '-u', DB_USER, f'-p{DB_PASSWORD}', 'ecommerce_db', '-e',
            "SELECT MAX(created_at) FROM fact_order_api_v2;"],
            capture_output=True, text=True, timeout=5)
        if r2.returncode == 0:
            db_info['latest_orders'] = r2.stdout.strip().split('\n')[-1]
        r3 = subprocess.run(['du', '-sh', '/var/lib/mysql/ecommerce_db'], capture_output=True, text=True, timeout=5)
        if r3.returncode == 0:
            db_info['db_size'] = r3.stdout.split()[0]
        r4 = subprocess.run(['mysql', '-u', DB_USER, f'-p{DB_PASSWORD}', '-e',
            "SELECT COUNT(*) FROM information_schema.SCHEMATA;"],
            capture_output=True, text=True, timeout=5)
        if r4.returncode == 0:
            db_info['dbs'] = r4.stdout.strip().split('\n')[-1]
    except: pass
    
    # Cron jobs status
    cron_status = {'total': 0, 'success': 0, 'failed': 0, 'recent': []}
    try:
        with open('/opt/scripts/logs/cron_executions.jsonl') as f:
            lines = f.readlines()[-500:]
        jobs_seen = {}
        for line in lines:
            try:
                r = json.loads(line)
                name = r['job']
                if name not in jobs_seen:
                    jobs_seen[name] = {'total': 0, 'success': 0, 'failed': 0, 'last': '', 'last_status': ''}
                jobs_seen[name]['total'] += 1
                if r['status'] == 'success':
                    jobs_seen[name]['success'] += 1
                else:
                    jobs_seen[name]['failed'] += 1
                jobs_seen[name]['last'] = r['ts']
                jobs_seen[name]['last_status'] = r['status']
            except: pass
        cron_status['jobs'] = jobs_seen
        cron_status['total'] = len(jobs_seen)
    except: pass
    
    return jsonify({
        'server': {'disk_used': disk[2], 'disk_total': disk[1], 'disk_pct': disk[4], 'uptime': uptime,
                   'mem_used': mem[2], 'mem_total': mem[1]},
        'database': db_info,
        'cron': cron_status,
    })

# ── 投票 API ──────────────────────────────────────────
POLL_QUESTION = '你是否想了解AI运行的底层逻辑？'

# ── 扩展调查问题 ──
EXTRA_POLLS = {
    'ai_tool': {'question': '你平时使用最多的AI是哪一个？', 'options': ['ChatGPT', '豆包', 'Kimi', 'DeepSeek', '其他', '没用过']},
    'usage': {'question': '主要是通过什么方式使用？', 'options': ['网页版', '手机App', 'AI Agent(API接入)', 'Vibe coding(API接入)', '集成到业务系统', '基本没用过']},
}
EXTRA_POLL_FILE = os.path.join(PPT_DIR, 'extra_poll_results.json')

POLL_RESULTS_HTML = '''<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>投票结果 · 演讲者看板</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Noto Sans SC",sans-serif;background:#f5f5f4;padding:20px;color:#0a0a0a}
.card{background:#fff;border-radius:12px;padding:24px;margin-bottom:16px;box-shadow:0 1px 8px rgba(0,0,0,.06)}
h1{font-size:18px;font-weight:700;margin-bottom:16px}
h2{font-size:15px;font-weight:600;margin-bottom:10px}
.bar-wrap{display:flex;align-items:center;gap:8px;margin-bottom:6px}
.bar-label{width:140px;font-size:13px;text-align:right;flex-shrink:0}
.bar-track{flex:1;height:20px;background:#eee;border-radius:4px;overflow:hidden}
.bar-fill{height:100%;background:#002FA7;border-radius:4px;transition:width .3s}
.bar-num{width:40px;font-size:13px;font-weight:600;flex-shrink:0}
.refresh{text-align:right;font-size:12px;color:#737373;margin-bottom:12px}
.btn{display:inline-block;padding:6px 16px;background:#002FA7;color:#fff;border-radius:6px;text-decoration:none;font-size:13px;margin-top:8px}
</style></head>
<body>
<div class="card" style="text-align:center"><h1>📊 现场投票结果</h1><p style="font-size:14px;color:#737373">演讲者专用 · 实时刷新查看</p></div>
<div id="results"></div>
<div class="card" style="text-align:center"><a href="/Y" class="btn">← 返回演讲稿</a></div>
<script>
async function loadResults(){
  try{
    const r=await fetch('/api/extra-poll');
    const d=await r.json();
    let html='';
    const labels={'ai_tool':'🤖 你平时使用最多的AI是哪一个？','usage':'💻 主要是通过什么方式使用？'};
    for(const [id,data] of Object.entries(d)){
      html+='<div class="card"><h2>'+labels[id]+'</h2>';
      const total=Object.values(data).reduce((a,b)=>a+b,0);
      html+='<div class="refresh">共 '+total+' 票</div>';
      for(const [opt,count] of Object.entries(data)){
        const pct=total?Math.round(count/total*100):0;
        html+='<div class="bar-wrap"><div class="bar-label">'+opt+'</div><div class="bar-track"><div class="bar-fill" style="width:'+pct+'%"></div></div><div class="bar-num">'+count+'</div></div>';
      }
      html+='</div>';
    }
    document.getElementById('results').innerHTML=html;
  }catch(e){}
}
loadResults();
setInterval(loadResults,5000);
</script>
</body></html>'''

def load_extra_polls():
    if os.path.exists(EXTRA_POLL_FILE):
        with open(EXTRA_POLL_FILE, 'r') as f:
            return json.load(f)
    return {k: {opt: 0 for opt in v['options']} for k, v in EXTRA_POLLS.items()}

def save_extra_polls(data):
    with open(EXTRA_POLL_FILE, 'w') as f:
        json.dump(data, f)

def load_poll():
    if os.path.exists(POLL_FILE):
        with open(POLL_FILE, 'r') as f:
            return json.load(f)
    return {'yes': 0, 'no': 0, 'voters': []}

def save_poll(data):
    with open(POLL_FILE, 'w') as f:
        json.dump(data, f)

@app.route('/api/poll', methods=['GET'])
def get_poll():
    data = load_poll()
    total = data['yes'] + data['no']
    return jsonify({
        'question': POLL_QUESTION,
        'yes': data['yes'],
        'no': data['no'],
        'total': total,
        'yes_pct': round(data['yes']/total*100, 1) if total else 0,
        'no_pct': round(data['no']/total*100, 1) if total else 0,
    })

@app.route('/api/poll/vote', methods=['POST'])
def vote_poll():
    data = request.get_json(force=True)
    answer = data.get('answer')
    voter = data.get('voter', '')
    if answer not in ('yes', 'no'):
        return jsonify({'ok': False, 'error': '无效投票'}), 400
    poll = load_poll()
    if voter and voter in poll['voters']:
        return jsonify({'ok': False, 'error': '你已经投过票了'}), 400
    poll[answer] += 1
    if voter:
        poll['voters'].append(voter)
    save_poll(poll)
    total = poll['yes'] + poll['no']
    return jsonify({'ok': True, 'yes': poll['yes'], 'no': poll['no'], 'total': total})

@app.route('/api/extra-poll', methods=['GET'])
def get_extra_poll():
    return jsonify(load_extra_polls())

@app.route('/api/extra-poll/vote', methods=['POST'])
def vote_extra_poll():
    data = request.get_json(force=True)
    poll_id = data.get('poll_id')
    option = data.get('option')
    cancel = data.get('cancel', False)
    if poll_id not in EXTRA_POLLS or option not in EXTRA_POLLS[poll_id]['options']:
        return jsonify({'ok': False, 'error': '无效投票'}), 400
    polls = load_extra_polls()
    if cancel:
        polls[poll_id][option] = max(0, polls[poll_id][option] - 1)
    else:
        polls[poll_id][option] += 1
    save_extra_polls(polls)
    return jsonify({'ok': True, 'results': polls[poll_id]})

# ── 反问环节 API ──────────────────────────────────────
@app.route('/api/followup/debug', methods=['GET'])
def debug_followup():
    """调试端点：直接测试反问生成，返回完整DeepSeek响应"""
    question_text = request.args.get('q', 'How to debug this issue?')
    try:
        prompt = f"""你是一个AI分享会的助手。听众提了一个问题，现需通过反问更准确理解他的真实需求。

听众问题：{question_text}

请生成2个选择题，每个3-4个选项，选项要贴合AI在企业应用的实际场景。

请严格按以下JSON格式返回（不要任何多余文字）：
{{"questions":[{{"q":"反问问题","options":["选项1","选项2","选项3"]}},{{"q":"反问问题2","options":["选项1","选项2","选项3"]}}]}}"""
        print(f'[debug_followup] API_KEY长度={len(DEEPSEEK_API_KEY)}, URL={DEEPSEEK_BASE_URL}', flush=True)
        with httpx.Client(timeout=30) as client:
            resp = client.post(
                f'{DEEPSEEK_BASE_URL}/chat/completions',
                headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {DEEPSEEK_API_KEY}'},
                json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3, "max_tokens": 2048}
            )
            result = {
                'http_status': resp.status_code,
                'key_prefix': DEEPSEEK_API_KEY[:8] if DEEPSEEK_API_KEY else 'EMPTY',
                'key_len': len(DEEPSEEK_API_KEY),
            }
            if resp.status_code == 200:
                raw = resp.json()
                content = raw['choices'][0]['message']['content']
                result['deepseek_content'] = content[:1000]
                # Try parse
                outer_match = re.search(r'\{.*\}', content, re.DOTALL)
                if outer_match:
                    result['matched_text'] = outer_match.group()[:500]
                    try:
                        parsed = json.loads(outer_match.group())
                        result['parsed_ok'] = True
                        result['questions'] = parsed.get('questions', [])
                    except json.JSONDecodeError as jde:
                        result['parsed_ok'] = False
                        result['parse_error'] = str(jde)
                else:
                    result['matched_text'] = '(no match)'
            else:
                result['response_body'] = resp.text[:500]
            return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500


@app.route('/api/followup', methods=['POST'])
def generate_followup():
    """根据已提交的问题，生成反问选项"""
    data = request.get_json(force=True)
    qid = data.get('id')
    question_text = data.get('question', '')
    debug_mode = data.get('_debug', False)  # 调试标志
    if not question_text:
        return jsonify({'ok': False, 'error': '缺少问题'}), 400

    try:
        prompt = f"""你是一个AI分享会的助手。听众提了一个问题，现需通过反问更准确理解他的真实需求。

听众问题：{question_text}

请生成2个选择题，每个3-4个选项，选项要贴合AI在企业应用的实际场景。

请严格按以下JSON格式返回（不要任何多余文字）：
{{"questions":[{{"q":"反问问题","options":["选项1","选项2","选项3"]}},{{"q":"反问问题2","options":["选项1","选项2","选项3"]}}]}}"""
        with httpx.Client(timeout=30) as client:
            resp = client.post(
                f'{DEEPSEEK_BASE_URL}/chat/completions',
                headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {DEEPSEEK_API_KEY}'},
                json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3, "max_tokens": 2048}
            )
            if resp.status_code == 200:
                raw = resp.json()
                content = raw['choices'][0]['message']['content']
                print(f'[反问] DeepSeek返回: {content[:200]}')
                # 提取最外层 JSON 并解析
                outer_match = re.search(r'\{.*\}', content, re.DOTALL)
                if outer_match:
                    try:
                        result = json.loads(outer_match.group())
                        questions = result.get('questions', [])
                        if questions:
                            for q in questions:
                                q['options'] = q.get('options', []) + ['其他（请填写）']
                            return jsonify({'ok': True, 'questions': questions})
                    except json.JSONDecodeError as jde:
                        print(f'[反问] JSON解析异常: {jde}')
                        if debug_mode:
                            return jsonify({'ok': False, 'debug': f'JSONDecodeError: {jde}', 'matched_text': outer_match.group()[:500], 'full_content': content[:1000]}), 200
                print(f'[反问] JSON解析失败, 原始内容: {content[:300]}')
                if debug_mode:
                    return jsonify({'ok': False, 'debug': 'no valid questions found', 'content': content[:1500]}), 200
            else:
                print(f'[反问] HTTP {resp.status_code}: {resp.text[:200]}')
                if debug_mode:
                    return jsonify({'ok': False, 'debug': f'HTTP {resp.status_code}', 'body': resp.text[:500]}), 200
    except Exception as e:
        print(f'[反问] 异常: {e}')
        if debug_mode:
            return jsonify({'ok': False, 'debug': f'Exception: {e}'}), 200
    return jsonify({'ok': True, 'questions': [
        {'q': '你提到的场景，目前是手工操作还是已经有系统支持？', 'options': ['纯手工', '有系统但不完善', '有系统但不好用', '其他（请填写）'], 'type': 'choice'},
        {'q': '你希望AI在这件事上做到什么程度？', 'options': ['完全自动，不用人管', '辅助决策，人来确认', '先跑通一个试点看看', '其他（请填写）'], 'type': 'choice'},
    ]})

@app.route('/api/followup/answer', methods=['POST'])
def submit_followup():
    """提交反问答案，AI重新归类"""
    data = request.get_json(force=True)
    qid = data.get('id')
    answers = data.get('answers', [])  # [{q, answer, custom}]
    
    questions = load_questions()
    for q in questions:
        if q['id'] == qid:
            q['followup'] = answers
            q['followup_at'] = datetime.now().isoformat()
            # 用原始问题+反问答案重新归类
            enhanced = q['question'] + ' ' + ' '.join([a.get('answer','') + a.get('custom','') for a in answers])
            page, score = classifier.classify(enhanced)
            q['page'] = page
            q['score'] = round(score, 3)
            save_questions(questions)
            return jsonify({'ok': True, 'page': page, 'message': f'已归类到第{page}页'})
    
    return jsonify({'ok': False, 'error': '问题未找到'}), 404

# ── 企业AI 简历分析（异步任务模式，避免 Cloudflare 超时）──
import os, sys, threading, uuid, time as time_mod

_G5_PROD = '/opt/scripts/G5/prod'
if os.path.isdir(_G5_PROD) and _G5_PROD not in sys.path:
    sys.path.insert(0, _G5_PROD)
if '/opt/scripts/G5' not in sys.path:
    sys.path.insert(0, '/opt/scripts/G5')

# 异步任务存储 {task_id: {status, result, error, created_at}}
_resume_tasks = {}

def _run_enterprise_analysis(task_id, resume, file_b64, filename):
    """后台线程：执行 G5 pipeline 并存储结果"""
    tmp_pdf = None
    try:
        import fitz
        
        if file_b64:
            import base64
            raw = base64.b64decode(file_b64)
            tmp_pdf = '/tmp/_demo_resume_' + str(int(time_mod.time())) + '.pdf'
            with open(tmp_pdf, 'wb') as f:
                f.write(raw)
            print(f'[企业AI] PDF直存: {tmp_pdf}, {len(raw)} bytes', flush=True)
        else:
            tmp_pdf = '/tmp/_demo_resume_' + str(int(time_mod.time())) + '.pdf'
            doc = fitz.open()
            page = doc.new_page()
            rect = fitz.Rect(50, 50, 545, 800)
            fonts_to_try = ["china-ss", "china-s", "china-t", "helv"]
            inserted = -1
            used_font = None
            for fn in fonts_to_try:
                try:
                    inserted = page.insert_textbox(rect, resume, fontsize=11, fontname=fn)
                    used_font = fn
                    break
                except Exception:
                    continue
            if inserted < 0:
                inserted = page.insert_textbox(rect, resume, fontsize=11)
                used_font = "default"
            overflow = inserted
            while overflow > 0 and overflow < len(resume):
                page = doc.new_page()
                overflow = page.insert_textbox(rect, resume[-overflow:], fontsize=11,
                                               fontname=used_font if used_font != "default" else None)
            doc.save(tmp_pdf)
            doc.close()
            print(f'[企业AI] PDF生成: {tmp_pdf}, 字体={used_font}', flush=True)

        from demo_analyzer import demo_analyze as g5_analyze
        from pathlib import Path

        hr_cfg = json.load(open('/opt/scripts/G5/hr_config.json'))
        app_t = hr_cfg['feishu']['app_token']
        tbl_id = hr_cfg['feishu']['tables']['position_info']

        cred_path = '/opt/scripts/.feishu_it_cred.json'
        a = json.load(open(cred_path))
        r = requests_mod.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
                          json={'app_id': a['app_id'], 'app_secret': a['app_secret']}, timeout=30)
        token = r.json().get('tenant_access_token', '')

        positions, jds = [], {}
        if token:
            url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{app_t}/tables/{tbl_id}/records?page_size=500'
            d = requests_mod.get(url, headers={'Authorization': f'Bearer {token}'}, timeout=30).json()
            for rec in d.get('data', {}).get('items', []):
                fld = rec.get('fields', {})
                name = fld.get('招聘岗位', '')
                if name and fld.get('岗位状态', '') == '招聘中':
                    positions.append(name)
                    jds[name] = fld.get('📃 岗位JD', '') or fld.get('岗位职责和要求', '') or ''

        if not positions:
            score_dir = Path('/opt/scripts/G5/prod/岗位评分标准')
            for f in sorted(score_dir.glob('*.md')):
                stem = f.stem
                pname = stem.split('_', 1)[1].replace('简历初筛评分标准', '').strip() if '_' in stem else stem
                if pname:
                    positions.append(pname)
                    jds[pname] = f.read_text('utf-8')[:500]

        print(f'[企业AI] 岗位数={len(positions)}, PDF={tmp_pdf}', flush=True)
        # 步骤1：通知前端已获取岗位列表
        _resume_tasks[task_id] = {
            'status': 'positions_loaded',
            'positions': positions[:10],
            'count': len(positions),
            'created_at': time_mod.time()
        }
        
        pos, result_data = g5_analyze(tmp_pdf, positions, jds)
        result_data['_matched_position'] = pos
        result_data['_positions_count'] = len(positions)
        
        # 步骤2：通知前端匹配结果
        _resume_tasks[task_id] = {
            'status': 'matched',
            'position': pos,
            'reason': result_data.get('_position_reason', ''),
            'count': len(positions),
            'created_at': time_mod.time()
        }
        time_mod.sleep(0.8)  # 短暂停顿让前端有时间渲染
        
        # 评分标准
        scoring_info = {}
        global_rules_path = Path('/opt/scripts/G5/prod/全局评分标准.md')
        if global_rules_path.exists():
            scoring_info['global_rules'] = global_rules_path.read_text('utf-8')[:3000]
        if pos and pos in jds:
            scoring_info['position_jd'] = jds[pos][:3000]
            scoring_info['position_name'] = pos

        _resume_tasks[task_id] = {
            'status': 'done',
            'result': {'ok': True, 'result': result_data, 'scoring': scoring_info, 'engine': 'G5-pipeline(MiMo-v2.5+scoring)'}
        }
        print(f'[企业AI] 任务 {task_id[:8]} 完成', flush=True)

    except Exception as e:
        import traceback
        traceback.print_exc()
        _resume_tasks[task_id] = {'status': 'error', 'error': str(e)}
    finally:
        if tmp_pdf and os.path.exists(tmp_pdf):
            try: os.unlink(tmp_pdf)
            except: pass

@app.route('/api/resume/enterprise-analyze', methods=['POST'])
def enterprise_analyze_resume():
    """异步企业AI简历分析：接收请求，返回 task_id，后台执行"""
    data = request.get_json(silent=True)
    if not data:
        data = {}
    resume = data.get('resume', '').strip()
    file_b64 = data.get('file_base64', '')
    filename = data.get('filename', 'resume.pdf')

    if (not resume or len(resume) < 10) and not file_b64:
        return jsonify({'ok': False, 'error': '简历内容不足'}), 400

    task_id = str(uuid.uuid4())
    _resume_tasks[task_id] = {'status': 'processing', 'created_at': time_mod.time()}
    
    thread = threading.Thread(target=_run_enterprise_analysis, args=(task_id, resume, file_b64, filename), daemon=True)
    thread.start()
    
    return jsonify({'ok': True, 'task_id': task_id, 'status': 'processing'})

@app.route('/api/resume/task/<task_id>', methods=['GET'])
def get_resume_task(task_id):
    """查询异步任务结果"""
    task = _resume_tasks.get(task_id)
    if not task:
        return jsonify({'status': 'not_found'}), 404
    if task['status'] == 'done':
        return jsonify(task['result'])
    if task['status'] == 'error':
        return jsonify({'ok': False, 'error': task['error']}), 500
    # 透传中间状态（positions_loaded, matched, processing）
    return jsonify(task)

# 清理旧任务（保留最近 50 个）
def _cleanup_old_tasks():
    now = time_mod.time()
    old = [k for k, v in _resume_tasks.items() if v.get('created_at', 0) < now - 600]
    for k in old:
        del _resume_tasks[k]


# ── 通用AI 简历分析（MiMo 多模态，文本+PDF图片）───────
@app.route('/api/resume/analyze', methods=['POST'])
def analyze_resume_general():
    """调用 MiMo 多模态 API，像HR专家一样分析简历"""
    data = request.get_json(silent=True)
    if not data:
        data = {}
    resume = data.get('resume', '').strip()
    file_b64 = data.get('file_base64', '')
    filename = data.get('filename', 'resume.pdf')
    
    if not resume and not file_b64:
        return jsonify({'ok': False, 'error': '简历内容不足'}), 400

    prompt = f"""你是一个拥有10年资深人力资源的招聘专家，请为这份简历进行专业分析并给出是否面试的建议。

（简历已附在消息后面的 PDF 图片中，请基于图片中的简历内容进行分析）"""
    try:
        import fitz, base64
        tmp_pdf = '/tmp/_general_resume_' + str(int(time.time())) + '.pdf'
        
        if file_b64:
            # PDF 直存
            raw = base64.b64decode(file_b64)
            with open(tmp_pdf, 'wb') as f:
                f.write(raw)
            print(f'[通用AI] PDF直存: {tmp_pdf}, {len(raw)} bytes', flush=True)
        else:
            # 文本 → 临时 PDF
            doc = fitz.open()
            page = doc.new_page()
            rect = fitz.Rect(50, 50, 545, 800)
            fonts_to_try = ["china-ss", "china-s", "china-t", "helv"]
            used_font = None
            for fn in fonts_to_try:
                try:
                    page.insert_textbox(rect, resume, fontsize=11, fontname=fn)
                    used_font = fn
                    break
                except Exception:
                    continue
            if not used_font:
                page.insert_textbox(rect, resume, fontsize=11)
            doc.save(tmp_pdf)
            doc.close()

        # 调用 MiMo 多模态
        from engines.mimo_engine import _pdf_to_images, _call_mimo
        images = _pdf_to_images(tmp_pdf)
        content = [{"type": "text", "text": prompt}]
        for b64 in images:
            content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}})
        messages = [{"role": "user", "content": content}]
        text = _call_mimo(messages, model="mimo-v2.5")
        os.unlink(tmp_pdf)

        return jsonify({
            'ok': True,
            'result': text,
            'model': 'mimo-v2.5',
            'provider': 'MiMo 多模态'
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'ok': False, 'error': str(e)}), 500


# ── PDF 文字提取 ──────────────────────────────────────
@app.route('/api/resume/extract-text', methods=['POST'])
def extract_resume_text():
    data = request.get_json(silent=True)
    if not data:
        data = {}
    b64 = data.get('file_base64', '')
    filename = data.get('filename', 'resume.pdf')
    if not b64:
        return jsonify({'ok': False, 'error': '缺少文件内容'}), 400
    try:
        import base64, tempfile, subprocess
        raw = base64.b64decode(b64)
        print(f'[提取] {filename}, base64解码后 {len(raw)} bytes', flush=True)
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(raw)
            tmp_path = f.name
        result = subprocess.run(['pdftotext', tmp_path, '-'], capture_output=True, text=True, timeout=30)
        os.unlink(tmp_path)
        if result.returncode == 0 and result.stdout.strip():
            return jsonify({'ok': True, 'text': result.stdout.strip()})
        print(f'[提取] 失败: returncode={result.returncode}, stderr={result.stderr[:200]}, stdout_len={len(result.stdout)}', flush=True)
        return jsonify({'ok': False, 'error': 'PDF文字提取失败'}), 400
    except Exception as e:
        return jsonify({'ok': False, 'error': f'提取出错: {str(e)}'}), 500

# ── 提问表单 HTML ─────────────────────────────────────
ASK_HTML = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI赋能企业增效 · 现场互动</title>
<style>
      /* ── Reset ── */
      *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
      
      /* ── 变量 & 全局 ── */
      :root{
        --bg:#f5f5f4;
        --card-bg:#fff;
        --ink:#0a0a0a;
        --ink-2:#525252;
        --ink-3:#737373;
        --ink-4:#a3a3a3;
        --border:#d4d4d2;
        --border-light:#e8e8e6;
        --accent:#002FA7;
        --accent-light:#eef3ff;
        --red:#d32f2f;
        --green:#2e7d32;
        --radius:12px;
        --radius-sm:8px;
        --safe-b:env(safe-area-inset-bottom,0px);
      }
      html{font-size:16px;-webkit-text-size-adjust:100%}
      body{
        font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans SC",sans-serif;
        background:var(--bg);min-height:100vh;
        padding:12px var(--safe-b);
        -webkit-font-smoothing:antialiased;
      }
      
      /* ── 容器 (移动端优先) ── */
      .container{max-width:560px;margin:0 auto;display:flex;flex-direction:column;gap:12px}
      .card{
        background:var(--card-bg);border-radius:var(--radius);
        padding:24px 20px;box-shadow:0 1px 12px rgba(0,0,0,.06);
      }
      @media(min-width:480px){
        body{padding:20px}
        .card{padding:32px 28px}
        .container{gap:16px}
      }
      
      /* ── 文字 ── */
      h1{font-size:20px;font-weight:700;color:var(--ink);margin-bottom:2px}
      @media(min-width:480px){h1{font-size:22px}}
      .sub{font-size:14px;color:var(--ink-3);margin-bottom:16px;line-height:1.5}
      label{display:block;font-size:14px;font-weight:600;color:var(--ink);margin-bottom:6px}
      
      /* ── 输入框 (移动端友好) ── */
      input,textarea{
        width:100%;padding:14px;border:1px solid var(--border);border-radius:var(--radius-sm);
        font-size:16px;font-family:inherit;transition:border-color .2s,box-shadow .2s;
        background:var(--card-bg);-webkit-appearance:none;appearance:none;
      }
      input:focus,textarea:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 3px rgba(0,47,167,.12)}
      textarea{height:80px;resize:vertical;min-height:80px}
      @media(min-width:480px){textarea{height:100px}}
      
          /* ── 通用按钮 ── */
      button{
        width:100%;margin-top:16px;padding:14px;
        background:var(--accent);color:#fff;
        border:none;border-radius:var(--radius-sm);
        font-size:16px;font-weight:600;line-height:1.4;
        cursor:pointer;transition:background .15s,opacity .15s;
        -webkit-tap-highlight-color:transparent;touch-action:manipulation;
      }
      button:active{opacity:.85}
      button:disabled{opacity:.45}
      button.sec{
        background:var(--card-bg);color:var(--accent);
        border:2px solid var(--accent);margin-top:8px;
      }
      
      /* ── 成功/错误 ── */
      .success{display:none;text-align:center;padding:24px 0 8px}
      .success .icon{font-size:48px;margin-bottom:10px;display:block}
      .success h2{font-size:20px;color:var(--ink);margin-bottom:6px}
      .success p{font-size:14px;color:var(--ink-3);line-height:1.5}
      .error{color:var(--red);font-size:14px;margin-top:10px;display:none}
      .count{text-align:center;margin-top:12px;font-size:13px;color:var(--ink-4)}
      
      /* ── 投票 ── */
      .poll-q{font-size:20px;font-weight:700;color:var(--ink);margin-bottom:14px;line-height:1.4}
      @media(min-width:480px){.poll-q{font-size:22px}}
      .poll-btns{display:flex;gap:10px}
      .poll-btn{
        flex:1;padding:12px 6px;border:2px solid var(--border);border-radius:var(--radius-sm);
        background:var(--card-bg);font-size:15px;cursor:pointer;transition:all .2s;
        text-align:center;line-height:1.3;-webkit-tap-highlight-color:transparent;
        touch-action:manipulation;user-select:none;-webkit-user-select:none;
      }
      .poll-btn:active{transform:scale(.97)}
      .poll-btn.voted-yes{border-color:var(--accent);background:var(--accent);color:#fff}
      .poll-btn.voted-no{border-color:var(--ink-3);background:var(--ink-3);color:#fff}
      .poll-result{display:none;margin-top:10px;font-size:14px;color:var(--ink-2)}
      .poll-bar{height:8px;border-radius:4px;background:#eee;margin-top:8px;overflow:hidden;display:flex}
      .poll-bar-yes{background:var(--accent);height:100%;transition:width .5s}
      .poll-bar-no{background:var(--ink-3);height:100%;transition:width .5s}

      /* 扩展调查 */
      .extra-options{display:flex;flex-wrap:wrap;gap:6px}
      .extra-btn{font-size:13px;padding:6px 12px;margin:0;width:auto;flex:0 0 auto}
      .extra-btn.voted{background:var(--accent);color:#fff;border-color:var(--accent)}
      .extra-result{font-size:12px;color:var(--ink-3);margin-left:4px}
      
      /* ── 反问 ── */
      .followup{display:none;margin-top:12px}
      .followup .fq{font-size:15px;font-weight:600;color:var(--ink);margin-bottom:8px;margin-top:16px;line-height:1.5}
      .followup .fq:first-child{margin-top:0}
      .followup .fo{
        display:block;width:100%;padding:12px 14px;border:1.5px solid var(--border);
        border-radius:var(--radius-sm);margin-bottom:8px;cursor:pointer;font-size:15px;
        transition:all .15s;background:var(--card-bg);text-align:left;line-height:1.4;
        -webkit-tap-highlight-color:transparent;touch-action:manipulation;
      }
      .followup .fo:active{transform:scale(.98)}
      .followup .fo.selected{border-color:var(--accent);background:var(--accent-light);font-weight:500}
      .followup .fo-custom{width:100%;padding:12px 14px;border:1px solid var(--border);border-radius:var(--radius-sm);
        font-size:16px;margin-top:2px;display:none;-webkit-appearance:none;appearance:none}
      .spinner{display:inline-block;width:18px;height:18px;border:2.5px solid #ddd;border-top-color:var(--accent);
        border-radius:50%;animation:spin .7s linear infinite;vertical-align:middle;margin-right:6px}
      @keyframes spin{to{transform:rotate(360deg)}}
      
      /* ── 标签助手 ── */
      .label-tip{display:inline-block;font-size:12px;font-weight:400;color:var(--ink-4);margin-left:4px}
    </style>
</head>
<body>
<div class="container">

  <!-- 扩展调查 -->
  <div class="card" id="extraPollCard">
    <div class="poll-q">📊 现场小调查</div>
    <div id="extraPollContent">
      <div style="margin-bottom:16px">
        <div style="font-size:14px;font-weight:600;margin-bottom:8px">你平时使用最多的AI是哪一个？</div>
        <div class="extra-options" id="pollAi">
          <div class="poll-btn extra-btn" data-poll="ai_tool" data-opt="ChatGPT" onclick="voteExtra(this)">ChatGPT</div>
          <div class="poll-btn extra-btn" data-poll="ai_tool" data-opt="豆包" onclick="voteExtra(this)">豆包</div>
          <div class="poll-btn extra-btn" data-poll="ai_tool" data-opt="Kimi" onclick="voteExtra(this)">Kimi</div>
          <div class="poll-btn extra-btn" data-poll="ai_tool" data-opt="DeepSeek" onclick="voteExtra(this)">DeepSeek</div>
          <div class="poll-btn extra-btn" data-poll="ai_tool" data-opt="其他" onclick="voteExtra(this)">其他</div>
          <div class="poll-btn extra-btn" data-poll="ai_tool" data-opt="没用过" onclick="voteExtra(this)">没用过</div>
        </div>
      </div>
      <div>
        <div style="font-size:14px;font-weight:600;margin-bottom:8px">主要是通过什么方式使用？</div>
        <div class="extra-options" id="pollUsage">
          <div class="poll-btn extra-btn" data-poll="usage" data-opt="网页版" onclick="voteExtra(this)">网页版</div>
          <div class="poll-btn extra-btn" data-poll="usage" data-opt="手机App" onclick="voteExtra(this)">手机App</div>
          <div class="poll-btn extra-btn" data-poll="usage" data-opt="AI Agent(API接入)" onclick="voteExtra(this)">AI Agent(API接入)</div>
          <div class="poll-btn extra-btn" data-poll="usage" data-opt="Vibe coding(API接入)" onclick="voteExtra(this)">Vibe coding(API接入)</div>
          <div class="poll-btn extra-btn" data-poll="usage" data-opt="集成到业务系统" onclick="voteExtra(this)">集成到业务系统</div>
          <div class="poll-btn extra-btn" data-poll="usage" data-opt="基本没用过" onclick="voteExtra(this)">基本没用过</div>
	        </div>
	      </div>
	    </div>
		  </div>

  <div style="text-align:center;font-size:13px;color:var(--ink-3);line-height:1.6;padding:4px 0 2px">
    上方投票点击即统计，无需提交 · 下方分享你的场景或提问
  </div>

  <!-- 提问卡片 -->
  <div class="card" id="formCard">
    <h1>💡 分享你的AI场景</h1>
    <p class="sub">你在使用AI的过程中遇到过什么问题？或者有什么场景想分享？</p>
    <form id="questionForm">
      <label for="name">你的名字（可选）</label>
      <input type="text" id="name" placeholder="匿名" maxlength="20">
          <label for="question">你的问题或场景 <span style="color:#d32f2f">*</span></label>
              <textarea id="question" placeholder="例如：目前公司在排产效率和排产规划上还是通过人工+excel表的方式来规划，并打印后给到生产部门生产。经常出现排产不及时没预警、排产日期或数量混乱等问题。希望能通过ai来解决。" maxlength="500" required></textarea>
          <div class="error" id="errorMsg"></div>
      <div style="font-size:13px;color:#737373;text-align:center;margin:12px 0 4px;line-height:1.5">AI会分析你的内容，判断是分享场景还是提问，并归类到对应环节。</div>
      <button type="submit" id="submitBtn">提交</button>
        </form>
    <div class="success" id="successMsg">
      <div class="icon">✅</div>
      <h2>提交成功！</h2>
      <p>正在AI分析中...</p>
      <div class="spinner" id="followupSpinner" style="margin:16px auto"></div>
    </div>
    <div class="followup" id="followupArea">
      <div style="font-size:14px;color:#555;margin-bottom:12px">🤖 AI 正在理解你的内容，请补充以下信息：</div>
      <div id="followupQuestions"></div>
      <button onclick="submitFollowup()" id="followupBtn">提交补充信息</button>
      <button class="sec" onclick="skipFollowup()">跳过，直接提交</button>
    </div>
    <div class="success" id="doneMsg" style="display:none">
      <div class="icon">🎉</div>
      <h2>感谢你的参与！</h2>
      <p id="donePage"></p>
      <button style="margin-top:20px;width:auto;padding:10px 24px" onclick="resetForm()">再提交一个</button>
    </div>
    <div class="count" id="countInfo"></div>
    <div style="text-align:center;margin-top:16px">
      <button class="sec" onclick="location.href='/'" style="width:auto;padding:8px 20px;font-size:13px">← 返回主页面</button>
    </div>
  </div>

</div>

<script>
		// ── 扩展调查投票 ──
	// ── 扩展调查投票（localStorage防重复） ──
	const LS_KEY = 'aiad_extra_votes';
	let savedVotes = JSON.parse(localStorage.getItem(LS_KEY) || '{}');
	// 恢复上次投票状态
	document.querySelectorAll('[data-poll]').forEach(el=>{
	  const k = el.dataset.poll+':'+el.dataset.opt;
	  if(savedVotes[k]) el.classList.add('voted');
	});
	async function voteExtra(el){
	  const pollId=el.dataset.poll;
	  const opt=el.dataset.opt;
	  const key = pollId+':'+opt;
	  const wasVoted = el.classList.contains('voted');
	  if(wasVoted){
	    el.classList.remove('voted');
	    delete savedVotes[key];
	    // 取消：计数-1
	    await fetch('/api/extra-poll/vote',{method:'POST',headers:{'Content-Type':'application/json'},
	      body:JSON.stringify({poll_id:pollId,option:opt,cancel:true})});
	  }else{
	    // 避免重复统计：检查localStorage
	    if(savedVotes[key]) return;
	    el.classList.add('voted');
	    savedVotes[key]=true;
	    // 选中：计数+1
	    await fetch('/api/extra-poll/vote',{method:'POST',headers:{'Content-Type':'application/json'},
	      body:JSON.stringify({poll_id:pollId,option:opt})});
	  }
	  localStorage.setItem(LS_KEY, JSON.stringify(savedVotes));
	}
	
	// ── 提问 ──
let currentQid = null;
let followupQuestions = [];

async function loadCount(){
  try{
    const r=await fetch('/api/status');
    const d=await r.json();
    document.getElementById('countInfo').textContent='已有 '+d.total+' 位听众提交了问题';
  }catch(e){}
}
loadCount();

document.getElementById('questionForm').onsubmit=async function(e){
  e.preventDefault();
  const q=document.getElementById('question').value.trim();
  if(!q) return showError('请输入问题');
  const btn=document.getElementById('submitBtn');
  btn.disabled=true;btn.textContent='提交中...';
  try{
    const name=document.getElementById('name').value.trim();
    const r=await fetch('/api/questions',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({name,question:q})
    });
    const d=await r.json();
	    if(d.ok){
	      currentQid=d.id;
	      document.getElementById('formCard').querySelector('form').style.display='none';
	      document.getElementById('successMsg').style.display='block';
	      loadCount();
	      // 获取反问
	      await loadFollowup(q, d.id, d.page);
	    }else showError(d.error||'提交失败');
  }catch(e){showError('网络错误，请重试')}
  btn.disabled=false;btn.textContent='提交问题';
};

// ── 反问 ──
async function loadFollowup(question, qid, page){
  try{
    const r=await fetch('/api/followup',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({id:qid, question})
    });
    const d=await r.json();
    if(d.ok && d.questions && d.questions.length>0){
      followupQuestions=d.questions;
      document.getElementById('successMsg').style.display='none';
      document.getElementById('followupSpinner').style.display='none';
      const area=document.getElementById('followupArea');
      area.style.display='block';
      renderFollowup();
    }else{
      doneSubmit(page);
    }
  }catch(e){doneSubmit(page)}
}

function renderFollowup(){
  const container=document.getElementById('followupQuestions');
  container.innerHTML='';
  followupQuestions.forEach((fq, fi)=>{
    const div=document.createElement('div');
    div.className='fq';
    div.textContent=(fi+1)+'. '+fq.q;
    container.appendChild(div);
    fq.options.forEach((opt, oi)=>{
      const btn=document.createElement('div');
      btn.className='fo';
      btn.textContent=opt;
      btn.dataset.fi=fi; btn.dataset.oi=oi;
      btn.onclick=()=>selectOption(fi, oi);
      container.appendChild(btn);
      if(opt.includes('请填写')){
        const inp=document.createElement('input');
        inp.type='text'; inp.className='fo-custom';
        inp.id='custom_'+fi; inp.placeholder='请输入...';
        container.appendChild(inp);
      }
    });
  });
}

function selectOption(fi, oi){
  const q=followupQuestions[fi];
  if(!q) return;
  // 清除该问题的其他选中
  document.querySelectorAll('.fo').forEach(el=>{
    if(parseInt(el.dataset.fi)===fi) el.classList.remove('selected');
  });
  const el=document.querySelector(`.fo[data-fi="${fi}"][data-oi="${oi}"]`);
  if(el){
    el.classList.add('selected');
    q.selected=oi;
  }
  // 显示/隐藏自定义输入
  const custom=document.getElementById('custom_'+fi);
  if(custom){
    const opt=q.options[oi];
    custom.style.display=opt && opt.includes('请填写')?'block':'none';
  }
}

async function submitFollowup(){
  if(!currentQid) return doneSubmit();
  const answers=followupQuestions.map((q, fi)=>{
    const selected=q.selected!==undefined?q.options[q.selected]:'';
    const custom=document.getElementById('custom_'+fi);
    return {q:q.q, answer:selected, custom:custom?custom.value:''};
  });
  const btn=document.getElementById('followupBtn');
  btn.disabled=true;btn.textContent='分析中...';
  try{
    const r=await fetch('/api/followup/answer',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({id:currentQid, answers})
    });
    const d=await r.json();
    if(d.ok) doneSubmit(d.page);
    else doneSubmit();
  }catch(e){doneSubmit()}
}

function skipFollowup(){doneSubmit()}

function doneSubmit(page){
  document.getElementById('followupArea').style.display='none';
  document.getElementById('successMsg').style.display='none';
  document.getElementById('doneMsg').style.display='block';
  if(page) document.getElementById('donePage').textContent='你的内容已归类到第 '+page+' 页，分享人会在对应环节回应。';
  else document.getElementById('donePage').textContent='谢谢！你的内容已记录，分享人会在对应环节回应。';
  loadCount();
}

function showError(msg){
  const el=document.getElementById('errorMsg');
  el.textContent=msg;el.style.display='block';
}
    function resetForm(){
          currentQid=null;
          document.getElementById('questionForm').reset();
          document.getElementById('formCard').querySelector('form').style.display='block';
          document.getElementById('successMsg').style.display='none';
          document.getElementById('doneMsg').style.display='none';
          document.getElementById('followupArea').style.display='none';
          document.getElementById('followupSpinner').style.display='block';
          document.getElementById('errorMsg').style.display='none';
          document.getElementById('followupBtn').disabled=false;
          document.getElementById('followupBtn').textContent='提交补充信息';
        }
</script>
</body>
</html>'''

QUESTIONS_HTML = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>听众问题 - 分享会</title>
<style>
  *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
  :root{--accent:#002FA7;--accent-light:#eef3ff;--ink:#0a0a0a;--ink-2:#525252;--ink-3:#737373;--grey-1:#f0f0ee;--radius:10px}
  body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans SC",sans-serif;background:#f5f5f4;color:var(--ink);-webkit-font-smoothing:antialiased;padding:20px}
  .container{max-width:800px;margin:0 auto}
  h1{font-size:22px;margin-bottom:4px}
  .sub{font-size:14px;color:var(--ink-3);margin-bottom:20px}
  .stats{display:flex;gap:16px;margin-bottom:20px}
  .stat-box{background:#fff;border-radius:var(--radius);padding:14px 18px;flex:1;text-align:center;box-shadow:0 1px 6px rgba(0,0,0,.06)}
  .stat-box .num{font-size:28px;font-weight:700;color:var(--accent)}
  .stat-box .lbl{font-size:13px;color:var(--ink-3);margin-top:2px}
  .slide-group{background:#fff;border-radius:var(--radius);box-shadow:0 1px 6px rgba(0,0,0,.06);margin-bottom:14px;overflow:hidden}
  .slide-header{padding:12px 16px;background:var(--accent-light);font-weight:600;font-size:15px;border-bottom:1px solid #e0e0de;cursor:pointer;display:flex;justify-content:space-between;align-items:center;transition:background .15s}
  .slide-header:hover{background:#dde6ff}
  .slide-header .count{font-size:13px;font-weight:400;color:var(--ink-3)}
  .q-list{list-style:none;padding:0}
  .q-item{padding:12px 16px;border-bottom:1px solid #f0f0ee}
  .q-item:last-child{border-bottom:none}
  .q-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;flex-wrap:wrap;gap:6px}
  .q-name{font-size:14px;font-weight:600}
  .q-actions{display:flex;gap:6px;align-items:center}
  .page-select{font-size:13px;padding:4px 8px;border:1px solid #d4d4d2;border-radius:6px;background:#fff;cursor:pointer;max-width:160px}
  .page-select:focus{outline:none;border-color:var(--accent)}
  .save-btn{font-size:12px;padding:4px 10px;background:var(--accent);color:#fff;border:none;border-radius:6px;cursor:pointer}
  .save-btn:hover{background:#001f7a}
  .del-btn{font-size:12px;padding:4px 10px;background:#d32f2f;color:#fff;border:none;border-radius:6px;cursor:pointer;opacity:.7}
  .del-btn:hover{opacity:1}
  .q-text{font-size:14px;color:var(--ink-2);line-height:1.5;margin-bottom:4px}
  .q-refined{font-size:13px;color:var(--accent);background:var(--accent-light);padding:4px 10px;border-radius:6px;display:inline-block;margin-top:4px}
  .q-deeper{font-size:13px;color:#6a1b9a;background:#f3e5f5;padding:4px 10px;border-radius:6px;display:inline-block;margin-top:4px;margin-left:4px}
  .empty{padding:30px;text-align:center;font-size:15px;color:var(--ink-3)}
  .toggle-btn{background:none;border:1px solid #d4d4d2;border-radius:6px;padding:6px 14px;font-size:13px;cursor:pointer;margin-bottom:14px;color:var(--ink-3)}
  .toggle-btn:hover{background:var(--grey-1)}
  @media(max-width:600px){.stats{flex-direction:column;gap:8px}}
</style>
</head>
<body>
<div class="container">
  <h1>📋 听众问题</h1>
  <p class="sub">已提交的问题，按分享会页面归类展示</p>
  <div class="stats" id="stats">
    <div class="stat-box"><div class="num" id="totalCount">0</div><div class="lbl">共提交</div></div>
    <div class="stat-box"><div class="num" id="classifiedCount">0</div><div class="lbl">已归类</div></div>
  </div>
  <button class="toggle-btn" onclick="showAll=!showAll;render()">🔽 切换显示模式</button>
  <div id="questionsArea"></div>
</div>
<script>
let questions = [];
let slides = [];
let showAll = true;
	var hidePages = [1,2,4,6,11];
		var pageTypes = [0,
		  '','',  /* 1-3 */
		  '',        /* 4 · 反认知事实 - 过渡 */
		  'AI幻觉、大模型原理相关问题',    /* 5 */
		  '',        /* 6 · 靠猜≠不能用 - 过渡 */
		  '提示词编写相关问题',             /* 7 */
		  '给AI喂数据、知识库相关问题',      /* 8 */
		  'AI工具接入、API、脚本相关问题',   /* 9 */
		  'AI循环反馈、迭代相关问题',        /* 10 */
		  '',        /* 11 · 三个通用场景 - 概述 */
		  '数据比对、对账相关需求',          /* 12 */
		  '流程监控、审批自动化相关需求',     /* 13 */
		  '内容生成、智能问答相关需求',       /* 14 */
		  '是否适合用AI的判断问题',           /* 15 */
		  'AI落地过程中的避坑问题',           /* 16 */
		  '行动步骤、从哪入手的问题',         /* 17 */
		  '评估AI方案、供应商选型的问题',     /* 18 */
		  '其他未分类的开放问题',             /* 19 · 听众自由提问 */
		];

async function load(){
  try{
    const r = await fetch('/api/questions');
    if(!r.ok){ throw new Error('HTTP '+r.status); }
    const d = await r.json();
    questions = d;
    slides = d.slides || [];
    render();
  }catch(e){
    document.getElementById('questionsArea').innerHTML='<div class="empty">\u2776 加载失败: '+e.message+'\u3002\u8bf7\u5237\u65b0\u91cd\u8bd5</div>';
  }
}

function render(){
  document.getElementById('totalCount').textContent = questions.total || 0;
  document.getElementById('classifiedCount').textContent = questions.classified || 0;
  const byPage = questions.by_page || {};
  const html = [];
  const pageOrder = showAll ? [] : Object.keys(byPage).filter(k => byPage[k].length > 0).map(Number).sort((a,b)=>a-b);
  
  if(showAll){
	    for(let p=1; p<=19; p++){
      if(hidePages.includes(p)) continue;
      const items = byPage[p] || [];
      const slide = (slides.find(s=>s.page===p)||{title:'未知页面'});
      html.push(buildGroup(p, slide.title, items));
    }
  } else {
    for(const p of pageOrder){
      if(hidePages.includes(p)) continue;
      const items = byPage[p] || [];
      const slide = (slides.find(s=>s.page===p)||{title:'未知页面'});
      html.push(buildGroup(p, slide.title, items));
    }
  }
  document.getElementById('questionsArea').innerHTML = html.join('');
}

function buildGroup(page, title, items){
  if(items.length === 0 && showAll === false) return '';
  const typeDesc = pageTypes[page] ? '<div style="font-size:13px;color:var(--ink-3);margin-top:2px">\U0001f4cc '+pageTypes[page]+'</div>' : '';
  return '<div class="slide-group"><div class="slide-header">第'+page+'页 · '+title+' <span class="count">'+items.length+' 个问题</span></div>'+
    typeDesc+
    (items.length ? '<ul class="q-list">'+items.map(q => buildItem(q)).join('')+'</ul>' : '<div class="empty">暂无问题</div>')+
    '</div>';
}

function buildItem(q){
  let extra = '';
  const typeLabel = q.type === 'share' ? '💡 分享' : q.type === 'question' ? '❓ 提问' : '';
  const typeTag = typeLabel ? '<span style="font-size:12px;padding:2px 8px;border-radius:4px;background:#f0f0ee;margin-left:6px">'+typeLabel+'</span>' : '';
  if(q.refined) extra += '<div class="q-refined">AI精炼: '+esc(q.refined)+'</div>';
  if(q.deeper) extra += '<div class="q-deeper">追问: '+esc(q.deeper)+'</div>';
  return '<li class="q-item"><div class="q-header"><div class="q-name">'+esc(q.name)+typeTag+'</div>'+
    '<div class="q-actions"><select class="page-select" data-id="'+q.id+'" onchange="updatePage('+q.id+',this)">'+
    pageOptions(q.page)+
    '</select><button class="save-btn" onclick="updatePage('+q.id+',null)" style="display:none">保存</button>'+
    '<button class="del-btn" onclick="deleteQuestion('+q.id+')">✕ 删除</button></div></div>'+
    '<div class="q-text">'+esc(q.question)+'</div>'+extra+'</li>';
}

function pageOptions(selected){
  let opts = '<option value="">未归类</option>';
	  for(let p=1;p<=19;p++){
    const sel = p==selected?' selected':'';
    const t = (slides.find(s=>s.page==p)||{title:''}).title;
    opts += '<option value="'+p+'"'+sel+'>第'+p+'页 · '+t+'</option>';
  }
  return opts;
}

async function updatePage(qid, sel){
  const page = sel ? parseInt(sel.value) : parseInt(event.target.previousElementSibling.value);
  if(!page) return;
  try{
    const r = await fetch('/api/questions/update', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({id:qid, page:page})
    });
    const d = await r.json();
    if(d.ok){
      // 重新加载
      await load();
    } else {
      alert('保存失败: '+d.message);
    }
  }catch(e){
    alert('保存失败');
  }
}

function esc(s){return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}

async function deleteQuestion(id){
  if(!confirm('确定删除该问题？')) return;
  try{
    const r=await fetch('/api/questions/delete',{method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({id})});
    const d=await r.json();
    if(d.ok){ load(); }
    else alert(d.message||'删除失败');
  }catch(e){alert('网络错误')}
}

load();
</script>
</body>
</html>'''

# ── /r/ 路由别名: 绕过 Cloudflare WAF 对 /api/ 的拦截 ──
@app.route('/r/resume/extract-text', methods=['POST'])
def r_extract_text():
    return extract_resume_text()

@app.route('/r/resume/analyze', methods=['POST'])
def r_analyze():
    return analyze_resume_general()

@app.route('/r/resume/enterprise-analyze', methods=['POST'])
def r_enterprise():
    return enterprise_analyze_resume()

@app.route('/r/resume/task/<task_id>', methods=['GET'])
def r_task(task_id):
    return get_resume_task(task_id)

QRCODE_HTML = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>扫码提问 - AI赋能企业增效</title>
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  :root{
    --ikb:#002FA7;
    --ikb-bright:#5B7BFF;
    --ink:#0a0a0a;
    --paper:#fafaf8;
    --grey-1:#f0f0ee;
    --grey-3:#737373;
  }
  html,body{height:100%}
  body{
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue","Noto Sans SC",sans-serif;
    background:var(--ikb);color:#fff;
    display:flex;align-items:center;justify-content:center;
    -webkit-font-smoothing:antialiased;
    padding:20px;
  }
  .card{
    background:#fff;border-radius:20px;
    padding:48px 40px 40px;
    max-width:420px;width:100%;
    text-align:center;
    box-shadow:0 20px 60px rgba(0,0,0,.25);
  }
  .tag{
    font-size:11px;font-weight:600;letter-spacing:.2em;
    color:var(--ikb);text-transform:uppercase;
    margin-bottom:16px;opacity:.6;
  }
  h1{
    font-size:22px;font-weight:700;color:var(--ink);
    margin-bottom:4px;line-height:1.3;
  }
  .sub{
    font-size:14px;color:var(--grey-3);
    margin-bottom:28px;line-height:1.5;
  }
  .qr-wrap{
    background:var(--paper);border-radius:14px;
    padding:12px;margin-bottom:20px;
    border:2px solid var(--grey-1);
  }
  .qr-wrap img{
    width:100%;height:auto;display:block;
    max-width:320px;margin:0 auto;border-radius:6px;
    aspect-ratio:1;
  }
  .btn{
    display:inline-flex;align-items:center;gap:8px;
    background:var(--ikb);color:#fff;
    padding:14px 28px;border-radius:12px;
    text-decoration:none;font-weight:600;font-size:15px;
    transition:background .2s;
  }
  .btn:hover{background:var(--ikb-bright)}
  .hint{
    font-size:12px;color:var(--grey-3);
    margin-top:16px;line-height:1.5;
  }
  @media(max-width:420px){
    .card{padding:28px 20px 24px}
    h1{font-size:20px}
    .qr-wrap img{width:180px;height:180px}
  }
</style>
</head>
<body>
<div class="card">
  <div class="tag">AI ENTERPRISE · SHARING</div>
  <h1>分享一下你使用AI的场景</h1>
  <p class="sub">或者在使用AI的过程中遇到的问题，<br>分享人会在对应环节回应</p>
  <div class="qr-wrap">
    <img src="https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=https://8008.cmfok.online/ask" alt="扫码提问">
  </div>
	  <a href="https://8008.cmfok.online/" class="btn">← 返回PPT</a>
	  <div class="hint">扫码提问或访问 8008.cmfok.online/ask</div>
</div>
</body>
</html>'''

STATUS_HTML = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>服务器状态 - AI赋能企业增效</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--ikb:#002FA7;--green:#2e7d32;--red:#d32f2f;--orange:#e65100}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Noto Sans SC",sans-serif;background:#f0f0ee;color:#0a0a0a;padding:16px;-webkit-font-smoothing:antialiased}
.container{max-width:900px;margin:0 auto}
h1{font-size:22px;font-weight:700;margin-bottom:4px;display:flex;align-items:center;gap:10px}
.sub{font-size:13px;color:#737373;margin-bottom:16px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px;margin-bottom:16px}
.card{background:#fff;border-radius:12px;padding:16px;box-shadow:0 1px 6px rgba(0,0,0,.04)}
.card .lbl{font-size:11px;font-weight:600;color:#737373;text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px}
.card .val{font-size:24px;font-weight:700}
.card .subval{font-size:12px;color:#737373;margin-top:2px}
.green{color:var(--green)}.red{color:var(--red)}.orange{color:var(--orange)}.ikb{color:var(--ikb)}
h2{font-size:16px;font-weight:600;margin:16px 0 8px;color:var(--ikb)}
table{width:100%;border-collapse:collapse;font-size:13px}
th{text-align:left;padding:8px 6px;background:var(--ikb);color:#fff;font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.04em}
td{padding:6px;border-bottom:1px solid #e8e8e6}
tr:hover{background:#f5f5f4}
.badge{display:inline-block;padding:1px 8px;border-radius:10px;font-size:11px;font-weight:600}
.badge-ok{background:#e8f5e9;color:var(--green)}
.badge-fail{background:#ffebee;color:var(--red)}
.last-upd{font-size:11px;color:#a3a3a3;text-align:right;margin-top:12px}
</style>
</head>
<body>
<div class="container">
  <h1>📊 服务器状态</h1>
  <div class="sub">数据实时获取 · 每30秒自动刷新</div>

  <div class="grid" id="serverInfo"></div>

  <h2>🗄️ 数据库</h2>
  <div class="grid" id="dbInfo"></div>

  <h2>⏱️ 最新数据时间</h2>
  <div class="card" id="latestData"></div>

  <h2>⚙️ 定时脚本</h2>
  <div class="card" id="cronTable"></div>

  <div class="last-upd" id="lastUpdate"></div>
</div>

<script>
async function load(){
  try{
    const r=await fetch('/api/status');
    const d=await r.json();
    
    // Server
    const s=d.server;
    document.getElementById('serverInfo').innerHTML = [
      '<div class="card"><div class="lbl">磁盘使用</div><div class="val '+(parseInt(s.disk_pct)>80?'orange':'green')+'">'+s.disk_pct+'</div><div class="subval">'+s.disk_used+' / '+s.disk_total+'</div></div>',
      '<div class="card"><div class="lbl">内存</div><div class="val ikb">'+s.mem_used+'</div><div class="subval">'+s.mem_total+'</div></div>',
      '<div class="card"><div class="lbl">运行时间</div><div class="val" style="font-size:16px">'+s.uptime+'</div></div>'
    ].join('');
    
    // DB
    const db=d.database;
    document.getElementById('dbInfo').innerHTML = [
      '<div class="card"><div class="lbl">数据库数量</div><div class="val ikb">'+db.dbs+'</div></div>',
      '<div class="card"><div class="lbl">数据表</div><div class="val ikb">'+db.tables+'</div></div>',
      '<div class="card"><div class="lbl">数据库大小</div><div class="val ikb">'+db.db_size+'</div></div>'
    ].join('');
    
    // Latest data
    document.getElementById('latestData').innerHTML = '<div style="display:flex;gap:16px;flex-wrap:wrap"><div><strong>最新订单：</strong>'+db.latest_orders+'</div></div>';
    
    // Cron
    const c=d.cron;
    let html='<table><tr><th>脚本</th><th>状态</th><th>最新执行</th><th>成功/总</th></tr>';
    if(c.jobs){
      const names=Object.keys(c.jobs).sort();
      names.forEach(n=>{
        const j=c.jobs[n];
        const ok=j.last_status=='success';
        html+='<tr><td>'+n+'</td><td><span class="badge '+(ok?'badge-ok':'badge-fail')+'">'+(ok?'正常':'异常')+'</span></td><td style="font-size:12px">'+j.last.slice(0,19)+'</td><td>'+j.success+'/'+j.total+'</td></tr>';
      });
    }
    html+='</table><div style="margin-top:8px;font-size:12px;color:#737373">共 '+c.total+' 个脚本</div>';
    document.getElementById('cronTable').innerHTML = html;
    
    document.getElementById('lastUpdate').textContent='更新于 '+new Date().toLocaleString('zh-CN');
  }catch(e){
    document.getElementById('serverInfo').innerHTML='<div class="card">加载失败，请刷新</div>';
  }
}
load();
setInterval(load,30000);
</script>
</body>
</html>'''
# ── 控制页状态 ─────────────────────────────────────
CONTROL_STATE = {"slide": 1, "lock": False, "coverQ": False, "coverP1": False, "expand": False, "card": 0, "pollOverlay": False, "qaShow": False, "themeKey": 0, "overviewKey": 0, "filePopup": 0, "popupScroll": 0, "autoScroll": 0, "sfRules": 0, "sfScroll": 0, "p4open": 0}
CONTROL_STATE_LOCK = threading.Lock()

QA_OVERLAY = {}

# ── Q&A 知识库 ─────────────────────────────────────
QA_FILE = os.path.join(PPT_DIR, 'qa_knowledge.json')
with open(QA_FILE, 'r', encoding='utf-8') as f:
    QA_DATA = json.load(f)

@app.route('/api/qa/ask', methods=['POST'])
def qa_ask():
    data = request.get_json(silent=True) or {}
    text = (data.get('text', '') or '').strip()
    if not text:
        return jsonify({'ok': False, 'error': '缺少问题文本'}), 400

    text_l = text.lower()
    best_match = None
    best_score = 0

    for qa in QA_DATA.get('qa_pairs', []):
        score = 0
        for kw in qa.get('keywords', []):
            if kw.lower() in text_l:
                score += 1
        q_text = qa.get('question', '').lower()
        q_words = set(q_text.split())
        text_words = set(text_l.split())
        overlap = len(q_words & text_words)
        score += overlap * 0.5
        if score > best_score:
            best_score = score
            best_match = qa

    if not best_match or best_score < 0.5:
        return jsonify({
            'ok': False, 'error': '未找到匹配答案',
            'text': text,
            'hint': '试试换个说法，或翻到对应页面我帮你解答'
        })

    return jsonify({
        'ok': True, 'text': text,
        'match': {
            'id': best_match['id'],
            'question': best_match['question'],
            'answer': best_match['answer'],
            'slide': best_match['slide']
        },
        'score': round(best_score, 1)
    })

@app.route('/api/questions/ai-answer', methods=['POST'])
def ai_answer_question():
    """用 DeepSeek 为指定问题生成针对性回答（控制台「🤖 回答」按钮）
    增强版：结合页面内容针对性回答，避免泛泛而谈"""
    data = request.get_json(silent=True) or {}
    qid = data.get('id')
    question = (data.get('question', '') or '').strip()
    if not question:
        return jsonify({'ok': False, 'error': '缺少问题文本'}), 400

    # 获取页面信息（前端传递，用于针对性回答）
    page = data.get('page')
    page_title = data.get('page_title', '')
    page_content = data.get('page_content', '')

    # 先尝试 DeepSeek API
    if DEEPSEEK_API_KEY:
        try:
            if page and page_title:
                # 针对性回答：带页面内容
                summary = page_content[:300] if page_content else ''
                system_prompt = f"""你是一个AI分享会的答疑助手，负责回答听众在分享会中提出的问题。

听众的问题被归类到第{page}页「{page_title}」。
该页面的核心主题是：{summary}

请遵循以下原则回答：
1. 如果问题和该页面内容相关，结合页面中的实际案例来回答
2. 如果问题和该页面无关，直接根据你自己的知识回答，不要指出页面不匹配
3. 控制在200字以内，直击要点
4. 使用通俗易懂的语言
5. 始终给出有实际价值的回答，不要建议用户参考其他页面"""
            else:
                # 无页面信息时使用通用提示
                system_prompt = "你是一个AI分享会的答疑助手，请用中文简要回答听众的问题，控制在200字以内，直击要点。"

            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                "temperature": 0.3,
                "max_tokens": 512
            }
            with httpx.Client(timeout=60) as client:
                resp = client.post(
                    f'{DEEPSEEK_BASE_URL}/chat/completions',
                    headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {DEEPSEEK_API_KEY}'},
                    json=payload
                )
                if resp.status_code == 200:
                    content = resp.json()['choices'][0]['message']['content']
                    source_tag = 'deepseek_page' if page else 'deepseek'
                    return jsonify({'ok': True, 'answer': content, 'source': source_tag})
        except Exception as e:
            print(f'[AI回答] DeepSeek 调用失败: {e}')

    # 降级：关键词匹配 QA 知识库
    text_l = question.lower()
    best_match = None
    best_score = 0
    for qa in QA_DATA.get('qa_pairs', []):
        score = 0
        for kw in qa.get('keywords', []):
            if kw.lower() in text_l:
                score += 1
        if score > best_score:
            best_score = score
            best_match = qa

    if best_match and best_score >= 0.5:
        return jsonify({'ok': True, 'answer': best_match['answer'], 'source': 'qa_knowledge'})

    return jsonify({'ok': False, 'error': '未能生成回答，请手动回应'})

@app.route('/api/control/qa-show', methods=['POST'])
def qa_show():
    data = request.get_json(silent=True) or {}
    QA_OVERLAY['question'] = data.get('question', '')
    QA_OVERLAY['answer'] = data.get('answer', '')
    QA_OVERLAY['slide'] = data.get('slide', 1)
    return jsonify({'ok': True})

@app.route('/api/control/qa-overlay')
def qa_overlay():
    return jsonify(QA_OVERLAY if QA_OVERLAY else {})

@app.route("/control")
def control_page():
    return app.send_static_file("control.html")

@app.route("/tech")
def tech_display():
    return app.send_static_file("tech_display.html")

@app.route("/tech-control")
def tech_control():
    return app.send_static_file("tech_control.html")

@app.route("/api/control/go", methods=["POST"])
def control_go():
    data = request.get_json(silent=True) or {}
    with CONTROL_STATE_LOCK:
        slide = int(data.get("slide", 1))
        CONTROL_STATE["slide"] = max(1, min(slide, 99))
        for key, value in data.items():
            if key in ("slide", "_speech"):
                continue
            CONTROL_STATE[key] = value

    # ── 演讲稿保存（嵌入此端点，避免在 Cloudflare 代理层被 405）──
    speech_info = data.get("_speech")
    speech_result = None
    if speech_info and isinstance(speech_info, dict):
        sid = int(speech_info.get("slide", slide))
        content = speech_info.get("content", "")
        try:
            if os.path.exists(SPEECH_FILE):
                with open(SPEECH_FILE, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                s_start = s_end = None
                in_target = False
                target_header = None
                for i, line in enumerate(lines):
                    m = re.match(r'^## Slide (\d+)\s*[—\-—]\s*(.*)', line)
                    if m:
                        num = int(m.group(1))
                        if num == sid:
                            in_target = True; s_start = i; target_header = line
                        elif in_target:
                            s_end = i; break
                    elif in_target and i == len(lines) - 1:
                        s_end = i + 1
                if s_start is not None:
                    if s_end is None: s_end = len(lines)
                    old_block = lines[s_start:s_end]
                    has_sep = any(ln.strip() == '---' for ln in old_block)
                    nc = content.replace('<strong>','**').replace('</strong>','**').replace('<br>','\n').strip()
                    if has_sep:
                        nb = [target_header, '\n', nc, '\n\n---\n\n']
                    else:
                        nb = [target_header, '\n', nc, '\n\n']
                    with open(SPEECH_FILE, 'w', encoding='utf-8') as f:
                        f.writelines(lines[:s_start] + nb + lines[s_end:])
                    speech_result = {"ok": True}
                else:
                    speech_result = {"ok": False, "error": f"未找到第 {sid} 页"}
            else:
                speech_result = {"ok": False, "error": "speech.md 不存在"}
        except Exception as e:
            speech_result = {"ok": False, "error": str(e)}

    resp = {"ok": True, **CONTROL_STATE}
    if speech_result is not None:
        resp["speech"] = speech_result
    return jsonify(resp)

@app.route("/api/control/current")
def control_current():
    with CONTROL_STATE_LOCK:
        return jsonify(dict(CONTROL_STATE))


# ── 幻灯片总数 ─────────────────────────────────────────
@app.route("/api/slides/total")
def slides_total():
    """自动从 index.html 统计实际 <section class="slide"> 数量"""
    index_path = os.path.join(PPT_DIR, 'index.html')
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        count = content.count('<section class="slide')
        return jsonify({"total": max(count, 1)})
    except Exception:
        return jsonify({"total": 22})  # 降级默认值

# ── 演讲稿保存 ─────────────────────────────────────────
SPEECH_FILE = os.path.join(PPT_DIR, 'speech.md')

@app.route('/api/speech/save', methods=['POST'])
def speech_save():
    """保存演讲稿中某一页的内容到 speech.md"""
    data = request.get_json(silent=True)
    print(f'[speech_save] 收到请求: {data}')
    if not data or 'slide' not in data or 'content' not in data:
        return jsonify({"ok": False, "error": "缺少参数"}), 400

    slide_num = int(data['slide'])
    new_content = data['content']

    if not os.path.exists(SPEECH_FILE):
        return jsonify({"ok": False, "error": "speech.md 不存在"}), 404

    try:
        with open(SPEECH_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 按 "## Slide N" 定位每个 slide 的起止行
        slide_start = None
        slide_end = None
        in_target = False
        target_header = None

        for i, line in enumerate(lines):
            m = re.match(r'^## Slide (\d+)\s*[—\-—]\s*(.*)', line)
            if m:
                num = int(m.group(1))
                if num == slide_num:
                    in_target = True
                    slide_start = i
                    target_header = line
                elif in_target:
                    # 下一个 slide 开始，当前 slide 结束
                    slide_end = i
                    break
            elif in_target and i == len(lines) - 1:
                slide_end = i + 1  # 文件末尾

        if slide_start is None:
            return jsonify({"ok": False, "error": f"未找到第 {slide_num} 页"}), 404
        if slide_end is None:
            slide_end = len(lines)

        # 原始块 = lines[slide_start:slide_end] = header + 旧内容 + 可选 ---
        old_block = lines[slide_start:slide_end]

        # 检查块内是否有 '---' 分隔符（在内容之后）
        has_separator = any(ln.strip() == '---' for ln in old_block)

        # 转换前端 HTML 标签回 Markdown
        new_content_text = new_content.replace('<strong>', '**').replace('</strong>', '**').replace('<br>', '\n')
        new_content_text = new_content_text.strip()

        # 构建新 slide 块（保持 --- 后有空行，兼容原始格式）
        if has_separator:
            new_block = [target_header, '\n', new_content_text, '\n\n---\n\n']
        else:
            new_block = [target_header, '\n', new_content_text, '\n\n']

        # 替换
        new_lines = lines[:slide_start] + new_block + lines[slide_end:]

        with open(SPEECH_FILE, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

        return jsonify({"ok": True})

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ── 启动 ───────────────────────────────────────────────
# /ye 文档路由
import os as _os
YE_DIR = "/var/www/qingjunhui/web"

@app.route("/ye")
def ye_redirect():
    from flask import redirect
    return redirect("/ye/")

@app.route("/ye/")
def ye_index():
    return _serve_ye_file("index.html")

@app.route("/ye/<path:subpath>")
def ye_serve(subpath):
    return _serve_ye_file(subpath)

def _serve_ye_file(subpath):
    if not subpath or subpath.endswith("/"):
        subpath = subpath + "index.html"
    req_path = _os.path.normpath(_os.path.join(YE_DIR, subpath))
    if not req_path.startswith(_os.path.realpath(YE_DIR)):
        return "Forbidden", 403
    if not _os.path.isfile(req_path):
        return "Not found", 404
    with open(req_path, "r", encoding="utf-8") as _f:
        return _f.read()



if __name__ == '__main__':
    print(f'🚀 AI 分享会互动系统启动')
    print(f'   PPT:    http://localhost:{PORT}/')
    print(f'   提问页: http://localhost:{PORT}/ask')
    print(f'   API:    http://localhost:{PORT}/api/questions')
    print(f'   投票:   http://localhost:{PORT}/api/poll')
    print(f'   分类引擎: TF-IDF + DeepSeek 精炼 + 封面页过滤')
    print(f'   问题数: {len(load_questions())} 条已保存')

    # 启动时迁移：将已存在的封面页问题重新分配到非封面页
    questions = load_questions()
    migrated = 0
    for q in questions:
        if q.get('page') in COVER_PAGES:
            new_page, score = classifier.classify(q['question'])
            old_page = q['page']
            q['page'] = new_page
            q['score'] = round(score, 3)
            q['classified_at'] = datetime.now().isoformat()
            migrated += 1
            print(f'[启动迁移] 问题#{q["id"]} 原第{old_page}页(封面) → 第{new_page}页')
    if migrated:
        save_questions(questions)
        print(f'[启动迁移] 共迁移 {migrated} 个问题')

    # 启动后台分类线程
    t = threading.Thread(target=classify_pending, daemon=True)
    t.start()

    # 启动语义理解缓存清理线程
    t_cache = threading.Thread(target=_semantic_cache_cleanup, daemon=True)
    t_cache.start()

    app.run(host=HOST, port=PORT, debug=False, threaded=True)
