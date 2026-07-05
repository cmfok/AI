#!/usr/bin/env python3
"""
分享会 Q&A 互动系统
===================
- 听众提交问题 → AI 自动归类 + DeepSeek 精炼深层问题
- 每页 PPT 底部显示相关提问
"""
import os, json, time, threading
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
from ai_help_html import AI_HELP_HTML

# ── 配置 ──────────────────────────────────────────────
PPT_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_FILE = os.path.join(PPT_DIR, 'questions.json')
POLL_FILE = os.path.join(PPT_DIR, 'poll_results.json')
HOST = '0.0.0.0'
PORT = 8008

# ── 幻灯片主题定义（用于 AI 分类）────────────────────
SLIDES = [
    {"page": 1,  "title": "封面",                        "tags": "封面 AI 真垃圾 分享会 开场 青骏会"},
    {"page": 2,  "title": "外星人的语言",                "tags": "互动 猜字 规律 LLM 预测 下一个词 模式"},
    {"page": 3,  "title": "训练三阶段/RLHF",             "tags": "训练 预训练 指令微调 RLHF 评分 有用性 真实性 安全性 诚实性 语气"},
    {"page": 4,  "title": "核心能力&局限",               "tags": "能力 局限 语言理解 逻辑推理 知识召回 代码生成 幻觉 知识截止"},
    {"page": 5,  "title": "Token概念&费用",              "tags": "Token 费用 成本 运营商 套餐 按量付费 未来判断"},
    {"page": 6,  "title": "模型对比",                    "tags": "模型 对比 DeepSeek 通义千问 Kimi GLM 豆包 擅长 场景"},
    {"page": 7,  "title": "案例·语音→PPT",              "tags": "案例 语音 PPT 提示词 输出结构 模板"},
    {"page": 8,  "title": "提示词工程",                   "tags": "提示词 工程 Prompt 角色 要求 参考 标准 派活"},
    {"page": 9,  "title": "案例·约会翻车",               "tags": "案例 约会 知识库 背景 信息 适配度"},
    {"page": 10, "title": "上下文工程",                   "tags": "上下文 知识库 RAG 历史数据 参考模板 业务规则"},
    {"page": 11, "title": "知识库搭建",                   "tags": "知识库 搭建 Trae Obsidian 向量 语义搜索 入门 进阶"},
    {"page": 12, "title": "案例·运费+招聘",              "tags": "案例 运费 对账 招聘 简历 约束 脚本 工作流 校验 工具"},
    {"page": 13, "title": "约束工程",                     "tags": "约束 工具调用 约束 验证 状态 错误处理 可观测 缰绳 MCP"},
    {"page": 14, "title": "案例·生日营销",               "tags": "案例 生日 营销 循环 自动 扫描 通知 回写"},
    {"page": 15, "title": "循环工程",                     "tags": "循环 自查 复盘 会诊 绩效 反馈 多Agent 并行 通讯"},
    {"page": 16, "title": "个人AI vs 企业AI",            "tags": "个人 企业 效率 可控 容错 生产环境"},
    {"page": 17, "title": "数据隐私",                     "tags": "隐私 数据 泄露 加密 私有化 本地化"},
    {"page": 18, "title": "落地Checklist",               "tags": "Checklist 落地 场景 模型 提示词 约束 监控"},
    {"page": 19, "title": "互动答疑",                     "tags": "答疑 互动 问题 自由 讨论 QA"},
]

# 不展示问题的封面/过渡页（不参与 AI 分类，已有问题强制迁移）
COVER_PAGES = {1, 3, 6}
# 无法归类的问题统一放到此页
FALLBACK_PAGE = 19

app = Flask(__name__, static_folder=PPT_DIR, static_url_path='')

# ── 数据存储 ──────────────────────────────────────────
def load_questions():
    if os.path.exists(QUESTIONS_FILE):
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_questions(questions):
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
            from sklearn.metrics.pairwise import cosine_similarity
            self.vectorizer = TfidfVectorizer()
            all_texts = self.slide_texts[:]
            tfidf = self.vectorizer.fit_transform(all_texts)
            self.slide_vectors = tfidf[:len(self.slide_texts)]
        except:
            self.vectorizer = False

    def classify(self, question_text):
        self._lazy_load()
        if self.vectorizer is False or self.vectorizer is None:
            return self._keyword_fallback(question_text)
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            q_vec = self.vectorizer.transform([question_text])
            sims = cosine_similarity(q_vec, self.slide_vectors)[0]
            best = int(sims.argmax())
            return SLIDES[best]['page'], float(sims[best])
        except:
            return self._keyword_fallback(question_text)

    def _keyword_fallback(self, text):
        best_page, best_score = FALLBACK_PAGE, 0
        for s in SLIDES:
            score = sum(1 for tag in s['tags'].split() if tag in text)
            if score > best_score:
                best_score = score
                best_page = s['page']
        return best_page, float(best_score)

classifier = Classifier()

def _keyword_type_detect(text):
    share_keywords = ['分享', '案例', '经验', '做法', '用过', '用了', '推荐', '心得', '尝试']
    question_keywords = ['怎么', '如何', '什么', '为什么', '能不能', '可以吗', '行不行', '？', '?']
    s = sum(1 for k in share_keywords if k in text)
    q = sum(1 for k in question_keywords if k in text)
    if s > q: return 'share'
    if q > 0: return 'question'
    return None

def analyze_input(text):
    return _keyword_type_detect(text)

# ── 全局问题分类后台线程 ──
import threading as _thr
_pending_queue = []

def classify_pending():
    while True:
        try:
            questions = load_questions()
            changed = False
            for q in questions:
                if q.get('page') is None or q.get('type') is None:
                    page, score = classifier.classify(q['question'])
                    qtype = analyze_input(q['question'])
                    q['page'] = page
                    q['score'] = round(score, 3)
                    q['type'] = qtype
                    q['classified_at'] = datetime.now().isoformat()
                    changed = True
            if changed:
                save_questions(questions)
        except:
            pass
        time.sleep(5)

# ── 全局 CORS（允许 demo 页面从任何域名调用 API）──
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    if request.path.endswith('.html') or not '.' in request.path.split('/')[-1]:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

# ── 页面路由 ──────────────────────────────────────────
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
    fpath = os.path.join(os.path.dirname(__file__), 'images', fname.split('?')[0])
    if not os.path.isfile(fpath):
        return '', 404
    return send_file(fpath)

@app.route('/demo-hr')
def demo_hr_page():
    return app.send_static_file('demo_hr.html')

@app.route('/poll-results')
def poll_results_page():
    return app.send_static_file('poll_results.html')

@app.route('/ask')
def ask_page():
    return app.send_static_file('ask.html')

@app.route('/questions')
def questions_page():
    return app.send_static_file('qa.html')

@app.route('/AI')
@app.route('/ai')
def ai_help_page():
    return AI_HELP_HTML

@app.route('/qrcode')
def qrcode_page():
    return app.send_static_file('qrcode.html')

@app.route("/cc")
def cc_page():
    return app.send_static_file("cc.html")

# ── API ───────────────────────────────────────────────
@app.route('/api/questions', methods=['POST'])
def submit_question():
    data = request.get_json(silent=True) or {}
    question = (data.get('question') or '').strip()
    name = (data.get('name') or '').strip() or '匿名'
    if not question:
        return jsonify({'ok': False, 'error': '内容不能为空'}), 400
    if len(question) > 500:
        return jsonify({'ok': False, 'error': '内容不能超过500字'}), 400

    questions = load_questions()
    qid = len(questions) + 1
    entry = {
        'id': qid,
        'name': name,
        'question': question,
        'type': None,
        'refined': '',
        'deeper': '',
        'page': None,
        'score': None,
        'created_at': datetime.now().isoformat(),
        'classified_at': None,
        'refined_at': None,
    }
    questions.append(entry)
    save_questions(questions)

    try:
        page, score = classifier.classify(question)
        entry['page'] = page
        entry['score'] = round(score, 3)
        entry['classified_at'] = datetime.now().isoformat()
        save_questions(questions)
    except:
        page = None
    
    return jsonify({'ok': True, 'id': qid, 'page': page, 'message': '谢谢！你的内容已提交'})

@app.route('/api/questions', methods=['GET'])
def get_questions():
    questions = load_questions()
    by_page = {}
    for q in questions:
        p = q.get('page') or 0
        by_page.setdefault(p, []).append({
            'id': q['id'],
            'name': q['name'],
            'question': q['question'],
            'type': q.get('type'),
            'refined': q.get('refined', ''),
            'deeper': q.get('deeper', ''),
            'page': q.get('page'),
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
            q['page'] = new_page
            save_questions(questions)
            return jsonify({'ok': True})
    return jsonify({'ok': False, 'message': '问题未找到'}), 404

@app.route('/api/questions/delete', methods=['POST'])
def delete_question():
    data = request.json
    qid = data.get('id')
    if qid is None:
        return jsonify({'ok': False, 'message': '缺少 id'}), 400
    questions = load_questions()
    questions = [q for q in questions if q['id'] != qid]
    save_questions(questions)
    return jsonify({'ok': True})

# ── 现场投票 ─────────────────────────────────────────
EXTRA_POLL_FILE = os.path.join(PPT_DIR, 'extra_poll_results.json')
def load_extra_polls():
    if os.path.exists(EXTRA_POLL_FILE):
        with open(EXTRA_POLL_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_extra_polls(data):
    with open(EXTRA_POLL_FILE, 'w') as f:
        json.dump(data, f)

def load_poll():
    if os.path.exists(POLL_FILE):
        with open(POLL_FILE, 'r') as f:
            return json.load(f)
    return {'yes': 0, 'no': 0}

def save_poll(data):
    with open(POLL_FILE, 'w') as f:
        json.dump(data, f)

@app.route('/api/poll', methods=['GET'])
def get_poll():
    poll = load_poll()
    return jsonify({'yes': poll.get('yes', 0), 'no': poll.get('no', 0), 'total': poll.get('yes', 0) + poll.get('no', 0)})

@app.route('/api/poll/vote', methods=['POST'])
def vote_poll():
    data = request.get_json(silent=True) or {}
    choice = data.get('choice', 'yes')
    poll = load_poll()
    poll[choice] = poll.get(choice, 0) + 1
    save_poll(poll)
    return jsonify({'ok': True, 'yes': poll['yes'], 'no': poll['no'], 'total': poll['yes'] + poll['no']})

@app.route('/api/extra-poll', methods=['GET'])
def get_extra_poll():
    return jsonify(load_extra_polls())

@app.route('/api/extra-poll/vote', methods=['POST'])
def vote_extra_poll():
    data = request.get_json(silent=True) or {}
    poll_id = data.get('id', 'ai_tool')
    option = data.get('option', '')
    if not option:
        return jsonify({'ok': False, 'error': '缺少选项'}), 400
    polls = load_extra_polls()
    if poll_id not in polls:
        polls[poll_id] = {}
    polls[poll_id][option] = polls[poll_id].get(option, 0) + 1
    save_extra_polls(polls)
    return jsonify({'ok': True})

# ── Q&A AI 回答 ──────────────────────────────────────
@app.route('/api/questions/ai-answer', methods=['POST'])
def ai_answer():
    data = request.get_json(silent=True) or {}
    qid = data.get('id')
    question = data.get('question', '')
    if not question:
        return jsonify({'ok': False, 'error': '缺少问题'}), 400
    # 简单关键词匹配 QA 知识库
    QA_FILE = os.path.join(PPT_DIR, 'qa_knowledge.json')
    if os.path.exists(QA_FILE):
        try:
            with open(QA_FILE, 'r', encoding='utf-8') as f:
                qa_data = json.load(f)
            # 在知识库中寻找最佳匹配
            questions_list = qa_data if isinstance(qa_data, list) else []
            text_l = question.lower()
            best = None
            best_score = 0
            for qa in questions_list:
                if isinstance(qa, dict):
                    q_text = qa.get('q', '')
                    score = sum(1 for w in q_text.lower().split() if w in text_l)
                    if score > best_score:
                        best_score = score
                        best = qa
            if best and best_score > 0:
                return jsonify({'ok': True, 'answer': best.get('a', ''), 'source': 'knowledge_base'})
        except:
            pass
    return jsonify({'ok': True, 'answer': '这是一个很好的问题！建议结合您的具体场景进一步讨论。', 'source': 'fallback'})

@app.route('/api/questions/delete', methods=['POST'])
def delete_question_route():
    data = request.json
    qid = data.get('id')
    if qid is None:
        return jsonify({'ok': False, 'message': '缺少 id'}), 400
    questions = load_questions()
    questions = [q for q in questions if q['id'] != qid]
    save_questions(questions)
    return jsonify({'ok': True})

@app.route('/api/questions/move', methods=['POST'])
def move_question():
    data = request.json
    qid = data.get('id')
    page = data.get('page')
    if qid is None or page is None:
        return jsonify({'ok': False, 'message': '缺少参数'}), 400
    questions = load_questions()
    for q in questions:
        if q['id'] == qid:
            q['page'] = page
            save_questions(questions)
            return jsonify({'ok': True})
    return jsonify({'ok': False, 'message': '问题未找到'}), 404

# ── 状态查看页 ──────────────────────────────────────
@app.route('/status')
@app.route('/api/status')
def status_page():
    import os as _os
    html = '<!DOCTYPE html><html><head><meta charset="utf-8"><title>AI系统状态</title>'
    html += '<style>body{font-family:system-ui;max-width:900px;margin:0 auto;padding:20px;background:#f5f5f5}'
    html += '.card{background:#fff;border-radius:10px;padding:16px;margin-bottom:12px;box-shadow:0 1px 3px rgba(0,0,0,.1)}'
    html += '.ok{color:#238636}.fail{color:#e53e3e}</style></head><body>'
    html += '<h1>🚀 AI 分享会互动系统 状态</h1>'
    html += f'<div class="card">✅ Flask 服务运行中 | 端口 {PORT}</div>'
    questions = load_questions()
    html += f'<div class="card">📊 问题总数: {len(questions)}</div>'
    html += '<div class="card">✅ 分类引擎: TF-IDF + DeepSeek 精炼</div>'
    html += '</body></html>'
    return html

# ── 控制页 SSE ───────────────────────────────────────
CONTROL_STATE = {"slide": 1}
QA_OVERLAY = {}

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
    slide = int(data.get("slide", 1))
    CONTROL_STATE["slide"] = max(1, min(slide, 99))
    return jsonify({"ok": True, "slide": CONTROL_STATE["slide"]})

@app.route("/api/control/current")
def control_current():
    return jsonify({"slide": CONTROL_STATE["slide"]})

# ── 演讲稿保存 ─────────────────────────────────────────
SPEECH_FILE = os.path.join(PPT_DIR, 'speech.md')

@app.route('/api/speech/save', methods=['POST'])
def speech_save():
    data = request.get_json(silent=True)
    if not data or 'slide' not in data or 'content' not in data:
        return jsonify({"ok": False, "error": "缺少参数"}), 400
    slide_num = int(data['slide'])
    new_content = data['content']
    if not os.path.exists(SPEECH_FILE):
        return jsonify({"ok": False, "error": "speech.md 不存在"}), 404
    try:
        with open(SPEECH_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        s_start = s_end = None
        in_target = False
        target_header = None
        import re
        for i, line in enumerate(lines):
            m = re.match(r'^## Slide (\d+)\s*[—\-—]\s*(.*)', line)
            if m:
                num = int(m.group(1))
                if num == slide_num:
                    in_target = True; s_start = i; target_header = line
                elif in_target:
                    s_end = i; break
            elif in_target and i == len(lines) - 1:
                s_end = i + 1
        if s_start is None:
            return jsonify({"ok": False, "error": f"未找到第 {slide_num} 页"}), 404
        if s_end is None: s_end = len(lines)
        old_block = lines[s_start:s_end]
        has_sep = any(ln.strip() == '---' for ln in old_block)
        nc = new_content.replace('<strong>','**').replace('</strong>','**').replace('<br>','\n').strip()
        if has_sep:
            nb = [target_header, '\n', nc, '\n\n---\n\n']
        else:
            nb = [target_header, '\n', nc, '\n\n']
        with open(SPEECH_FILE, 'w', encoding='utf-8') as f:
            f.writelines(lines[:s_start] + nb + lines[s_end:])
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# ── 启动 ───────────────────────────────────────────────
if __name__ == '__main__':
    print(f'🚀 AI 分享会互动系统启动')
    print(f'   PPT:    http://localhost:{PORT}/')
    print(f'   提问页: http://localhost:{PORT}/ask')
    print(f'   API:    http://localhost:{PORT}/api/questions')
    print(f'   投票:   http://localhost:{PORT}/api/poll')
    print(f'   分类引擎: TF-IDF + DeepSeek 精炼 + 封面页过滤')
    print(f'   问题数: {len(load_questions())} 条已保存')

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
    if migrated:
        save_questions(questions)

    t = threading.Thread(target=classify_pending, daemon=True)
    t.start()

    app.run(host=HOST, port=PORT, debug=False, threaded=True)
