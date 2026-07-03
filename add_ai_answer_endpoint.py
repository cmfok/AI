# -*- coding: utf-8 -*-
"""Add AI answer endpoint to app.py and update control page"""

path = '/home/ubuntu/share-ppt/app.py'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add the AI answer endpoint after the delete endpoint
old = """    return jsonify({'ok': True, 'message': '已删除'})

@app.route('/status')"""

new = """    return jsonify({'ok': True, 'message': '已删除'})

@app.route('/api/questions/ai-answer', methods=['POST'])
def ai_answer_question():
    \"\"\"用 DeepSeek 自动回答观众问题\"\"\"
    data = request.json
    qid = data.get('id')
    question_text = data.get('question', '')
    
    if not question_text:
        return jsonify({'ok': False, 'error': '缺少问题内容'}), 400
    
    try:
        import httpx
        prompt = f\"\"\"你是一个AI分享会的演讲助手。现场有听众问了一个问题，请用口语化的方式给出一个简短、实用的回答（控制在200字以内）。

听众问题：{question_text}

背景：这是一场关于「AI真垃圾」的分享会，主题是四大工程体系（提示词工程、上下文工程、规训工程、循环工程）和AI Agent落地方法论。
分享者希望回答能结合这四大工程体系的实际应用场景。

请直接输出回答内容，不要加任何前缀或说明。\"\"\"
        
        with httpx.Client(timeout=30) as client:
            resp = client.post(
                f'{DEEPSEEK_BASE_URL}/chat/completions',
                headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {DEEPSEEK_API_KEY}'},
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "你是一个AI落地实战专家，擅长用通俗的语言解释AI技术概念和应用方法。回答要简短、口语化、有实操价值。"},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.5,
                    "max_tokens": 512
                }
            )
            if resp.status_code == 200:
                answer = resp.json()['choices'][0]['message']['content'].strip()
                return jsonify({'ok': True, 'answer': answer})
            else:
                return jsonify({'ok': False, 'error': f'AI服务返回{resp.status_code}'}), 502
    except Exception as e:
        print(f'[AI回答] 异常: {e}')
        return jsonify({'ok': False, 'error': 'AI服务暂时不可用'}), 502

@app.route('/status')"""

if old in content:
    content = content.replace(old, new)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Added /api/questions/ai-answer endpoint')
else:
    print('Pattern not found')
    idx = content.find('已删除')
    if idx > 0:
        print('Found 已删除 at', idx)
        print(repr(content[idx:idx+100]))
