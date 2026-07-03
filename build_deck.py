#!/usr/bin/env python3
"""Build the complete AI真垃圾 deck following html-ppt skill rules"""
import os, re

TEMPLATE = os.path.expanduser('D:/Work/.agents/skills/html-ppt-full/templates/full-decks/tech-sharing/index.html')
STYLE_CSS = os.path.expanduser('D:/Work/.agents/skills/html-ppt-full/templates/full-decks/tech-sharing/style.css')
OUTPUT = os.path.expanduser('D:/Work/分享会/deck_v3.html')

with open(STYLE_CSS,'r',encoding='utf-8') as f:
    tech_css = f.read()

with open(TEMPLATE,'r',encoding='utf-8') as f:
    html = f.read()

# Fix asset paths
html = html.replace('../../../assets/', 'assets/')
# Inline tech-sharing CSS
html = html.replace('<link rel="stylesheet" href="style.css">', f'<style>{tech_css}</style>')
# Remove animation CSS (not deployed on server)
html = html.replace('<link rel="stylesheet" href="assets/animations/animations.css">', '')
# Update title
html = html.replace('<title>Rust 异步运行时内部机制 · Tech Sharing</title>',
                    '<title>AI 真垃圾 · 分享会</title>')

# Add touch swipe CSS
swipe_css = '''
/* Touch swipe + card interactions */
.deck{touch-action:pan-y}
.card-dim{opacity:.3!important;transition:all .4s}
.card-active{opacity:1!important;border-color:var(--accent)!important;border-top-width:3px!important}
.hide{display:none!important}
'''
html = html.replace('</style>', swipe_css + '\n</style>')

# Build all 20 slides
slides = []

# Helper: card with border
def card(b, title, body, accent=''):
    a = f' card-accent' if accent else ''
    return f'<div class="card{a}"{b}>{title}{body}</div>'

# 1. Cover
slides.append('''<section class="slide" data-title="Cover">
  <p class="kicker anim-fade-up" data-anim="fade-up">share·ing / 2026-07-07</p>
  <h1 class="h1 anim-fade-up" data-anim="fade-up">AI 真垃圾<br><span style="background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent">从用它到懂它</span></h1>
  <p class="lede mt-m" style="max-width:42ch">四大工程体系 × AI Agent 落地方法论</p>
  <p style="color:var(--text-3);font-size:13px;margin-top:4px">从迷信到理解，从"AI瞎猜"到"让它猜准"</p>
  <div class="speaker" style="margin-top:20px"><div class="av"></div><div><b>CM</b><span>@ 开想传媒 · 2026-07-07</span></div></div>
  <div class="deck-footer"><span class="mono">#提示词工程 #上下文工程 #规训工程 #循环工程</span><span class="slide-number" data-current="1" data-total="20"></span></div>
  <div class="notes">大家好，今天分享AI真垃圾。两个意思。</div>
</section>''')

# 2. Interaction - with expandable answer card
slides.append('''<section class="slide center tc" data-title="互动">
  <div>
    <p class="kicker" style="margin-bottom:16px">INTERACTION</p>
    <div style="font-size:clamp(36px,5vw,60px);letter-spacing:16px;margin-bottom:20px;color:#fff">← ↑ → ↓ ←</div>
    <p class="lede" style="font-size:clamp(20px,2.5vw,34px)">猜下一个：<strong>↑ → ？</strong></p>
    <div id="s2Card" class="hide" style="margin-top:24px">
      <div style="font-size:clamp(48px,6vw,80px);color:var(--accent);margin-bottom:8px">↓</div>
      <p style="color:var(--text-2)">左上右下，顺时针转圈</p>
      <p class="lede mt-m" style="font-size:clamp(16px,1.8vw,22px)"><strong>AI 的核心——就是个猜字系统</strong></p>
    </div>
  </div>
  <div class="notes">玩个小游戏。答案左下右顺时针转圈。</div>
</section>''')

# 3. Counter-intuitive
slides.append('''<section class="slide center tc" data-title="反认知">
  <div><p class="kicker">COUNTER-INTUITIVE</p>
  <h1 class="h1" style="font-size:clamp(44px,7vw,100px);line-height:1.1">AI 的核心<br>就是<span style="background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent">个猜字系统</span></h1>
  <p class="lede" style="margin:16px auto;max-width:34ch">给它一段上文，它算概率，猜下一个最合理的字/词</p></div>
  <div class="notes">AI的核心就是个猜字系统。</div>
</section>''')

# 4. Models - with expandable 3-stage cards
slides.append('''<section class="slide" data-title="模型">
  <p class="kicker">MODELS</p>
  <h2 class="h2">模型</h2>
  <p style="color:var(--text-2);margin-bottom:12px;font-size:14px">豆包·ChatGPT·Gemini·千问·DeepSeek·Kimi·GLM-4·Claude</p>
  <div class="grid g3 mt-l anim-stagger-list">
    <div class="card card-accent" id="c1" style="opacity:1"><h4>① 预训练</h4><p class="dim" id="d1">喂海量文字资料</p></div>
    <div class="card card-dim" id="c2"><h4 style="color:var(--text-3)">② 指令微调</h4><p class="dim" id="d2" style="color:var(--text-3)">点击展开</p></div>
    <div class="card card-dim" id="c3"><h4 style="color:var(--text-3)">③ RLHF</h4><p class="dim" id="d3" style="color:var(--text-3)">点击展开</p></div>
  </div>
  <div id="limitBox" class="hide" style="margin-top:12px">
    <div class="card" style="border-left:4px solid var(--bad);background:rgba(247,118,142,.04)"><p style="font-size:13px;line-height:1.7">⚠ <b>三个局限</b>：①幻觉（天气案例）②知识截止（父亲节案例）③无真实理解（10:10钟表）</p></div>
  </div>
  <div class="notes">三个训练阶段。AI变舔狗。三个局限。</div>
</section>''')

# 5. 转折
slides.append('''<section class="slide center tc" data-title="转折">
  <div><p class="kicker">TURNING POINT</p>
  <h1 class="h1" style="font-size:clamp(32px,4.5vw,64px);line-height:1.15">让 AI 瞎猜，<span style="color:var(--accent)">绝不靠谱</span><br>四大工程，<span style="color:var(--accent-2)">让 AI 猜准</span></h1>
  <p style="color:var(--text-2);margin-top:16px;font-size:13px;max-width:36ch;margin:16px auto">吐槽：AI真垃圾——猜字·幻觉·知识截止·无真实理解。但学会正确打开方法，就能变生产力。</p>
  <div class="row wrap mt-l" style="justify-content:center"><span class="pill pill-accent">提示词工程</span><span class="pill" style="background:rgba(121,192,255,.12);color:#79c0ff">上下文工程</span><span class="pill" style="background:rgba(247,118,142,.12);color:var(--bad)">规训工程</span><span class="pill" style="background:rgba(210,168,255,.12);color:#d2a8ff">循环工程</span></div></div>
  <div class="notes">吐槽完讲方法。四大工程就是答案。</div>
</section>''')

# Slides 6-20: remaining content
more_slides = [
    (6, '提示词工程', 'PROMPT ENGINEERING', '''
<div class="grid g2 mt-l">
  <div class="card card-accent" style="border-top-color:var(--bad);padding:20px"><h3 style="color:var(--bad)">❌ 没有提示词</h3><p class="dim">"帮我做个PPT"→AI瞎猜</p></div>
  <div class="card card-accent" style="border-top-color:var(--accent);padding:20px"><h3 style="color:var(--accent)">✅ 有提示词</h3><p class="dim">Trae语音→MD→生成PPT</p></div>
</div>
<p style="color:var(--text-2);margin-top:12px;font-size:13px"><strong>四个规则</strong>：定角色·讲要求·给参考·设标准</p>
<p style="color:var(--text-3);margin-top:8px;font-size:12px;line-height:1.6">故事：朋友问AI约会→"喜欢一个女孩该去哪"→AI答看电影吃饭。教他用结构问→方案完整。又失败了！AI推荐<strong style="color:var(--bad)">烤肉</strong>，女孩是<strong style="color:var(--bad)">素食主义者</strong>！</p>'''),

    (7, '上下文工程', 'CONTEXT ENGINEERING', '''
<p style="color:var(--text-2);margin-bottom:16px;font-size:14px">结构对了，但AI不了解女孩。不是改指令，是<strong style="color:#fff">把背景资料喂给AI</strong>。</p>
<div class="grid g3 mt-l anim-stagger-list">
  <div class="card"><div style="font-size:28px">📁</div><h4 class="mt-s">可迁移</h4><p class="dim">换模型不用重新喂</p></div>
  <div class="card"><div style="font-size:28px">📋</div><h4 class="mt-s">可生长</h4><p class="dim">不断加内容，AI越来越懂你</p></div>
  <div class="card"><div style="font-size:28px">📚</div><h4 class="mt-s">有记忆</h4><p class="dim">不用每次重新说一遍</p></div>
</div>'''),

    (8, '知识库搭建', 'KNOWLEDGE BASE', '''
<div class="grid g3 mt-l anim-stagger-list">
  <div class="card" style="border-top:3px solid var(--text-3)"><h4 style="font-size:22px">🥉 青铜</h4><p class="dim"><strong style="color:#fff">MD + Trae</strong><br>先跑起来</p></div>
  <div class="card" style="border-top:3px solid var(--accent-2)"><h4 style="font-size:22px;color:var(--accent-2)">🥈 白银</h4><p class="dim"><strong style="color:#fff">+ Obsidian</strong><br>能搜能管</p></div>
  <div class="card" style="border-top:3px solid #d2a8ff"><h4 style="font-size:22px;color:#d2a8ff">🥇 黄金</h4><p class="dim"><strong style="color:#fff">+ 向量模型/插件</strong><br>语义搜索</p></div>
</div>'''),

    (9, '招聘简历', 'CASE · RECRUIT', '''
<div class="grid g2 mt-l">
  <div class="card card-accent" style="border-top-color:var(--bad);padding:20px"><h3 style="color:var(--bad)">❌ 无规训</h3><p class="dim">通用分析不精准</p></div>
  <div class="card card-accent" style="border-top-color:var(--accent);padding:20px"><h3 style="color:var(--accent)">✅ 规训六件套</h3><p class="dim">多维度评分+JD匹配+预警推荐</p></div>
</div>
<p style="color:var(--text-2);margin-top:12px;font-size:13px">六大组件：工具调用·约束安全·验证校验·状态管理·错误处理·可观测性</p>'''),

    (10, '运费对账', 'CASE · FREIGHT', '''
<div class="grid g2 mt-l">
  <div class="card card-accent" style="border-top-color:var(--bad);padding:20px"><h3 style="color:var(--bad)">❌ 人工对账</h3><p class="dim">Excel半天还怕错</p></div>
  <div class="card card-accent" style="border-top-color:var(--accent);padding:20px"><h3 style="color:var(--accent)">✅ 脚本自动化</h3><p class="dim">ERP→重量→地址→报价→1秒零误差</p></div>
</div>'''),

    (11, '规训工程', 'HARNESS ENGINEERING', '''
<p style="color:var(--text-2);margin-bottom:12px;font-size:14px">AI真垃圾——不是AI的问题，是<strong style="color:#fff">没给它手脚、没套缰绳</strong>。规训工程就是手脚和缰绳。</p>
<div class="grid g3 mt-l anim-stagger-list">
  <div class="card"><h4 style="font-size:14px">🔧 工具调用</h4><p class="dim" style="font-size:12px">给AI装上手和脚</p></div>
  <div class="card"><h4 style="font-size:14px">🛡 约束安全</h4><p class="dim" style="font-size:12px">设边界不乱来</p></div>
  <div class="card"><h4 style="font-size:14px">✅ 验证校验</h4><p class="dim" style="font-size:12px">自己检查自己</p></div>
  <div class="card"><h4 style="font-size:14px">📦 状态管理</h4><p class="dim" style="font-size:12px">存外部文件</p></div>
  <div class="card"><h4 style="font-size:14px">🔄 错误处理</h4><p class="dim" style="font-size:12px">出错不崩</p></div>
  <div class="card"><h4 style="font-size:14px">📊 可观测性</h4><p class="dim" style="font-size:12px">每一步可回溯</p></div>
</div>'''),

    (12, '脚本vs工作流', 'SCRIPT vs WORKFLOW', '''
<div class="grid g3 mt-l anim-stagger-list">
  <div class="card" style="border-top:3px solid var(--text-3)"><h4>🐍 脚本</h4><p class="dim">确定性·Python</p></div>
  <div class="card" style="border-top:3px solid var(--accent-2)"><h4 style="color:var(--accent-2)">🔗 固定工作流</h4><p class="dim">扣子Coze·Dify</p></div>
  <div class="card" style="border-top:3px solid #d2a8ff"><h4 style="color:#d2a8ff">🤖 AI工作流</h4><p class="dim">Trae·Qoder·Claude Code</p></div>
</div>'''),

    (13, '生日营销', 'CASE · BIRTHDAY', '''
<p class="lede" style="color:var(--accent);font-size:20px">真实案例 · 变现 <strong style="font-size:clamp(24px,3vw,40px)">400万+</strong></p>
<p style="color:var(--text-2);line-height:1.7;margin-top:12px;font-size:14px">用户扫码→小程序填生日地址→数据库→AI每天扫描→客服联系→送礼品→复购→<strong style="color:#fff">闭环</strong></p>'''),
]

for idx, title, kicker, body in more_slides:
    slides.append(f'''<section class="slide" data-title="{title}">
  <p class="kicker">{kicker}</p>
  <h2 class="h2">{title}</h2>
  {body}
  <div class="notes">内容待补充。</div>
</section>''')

# Add remaining slides (14-20)
remaining = [
    (14, '递进对比', 'PROGRESSION', '<div class="grid g2 mt-l" style="max-width:500px;margin:0 auto"><div class="card card-accent" style="border-top-color:var(--bad);padding:20px"><h3 style="color:var(--bad)">只有规训</h3><p class="dim">单次执行</p></div><div class="card card-accent" style="border-top-color:var(--accent);padding:20px"><h3 style="color:var(--accent)">加循环</h3><p class="dim">做→查→修→再输出</p></div></div>'),
    (15, '循环工程', 'LOOP ENGINEERING', '<p style="color:var(--text-2);margin-bottom:12px;font-size:14px">AI做一遍就完了。<strong style="color:#fff">循环工程就是逼它再做一遍</strong>。</p><div class="grid g3 mt-l"><div class="card"><h4>↺ 循环流程</h4><p class="dim">设定→引导→执行→检查→修复</p></div><div class="card" style="border-left:3px solid var(--bad)"><h4 style="color:var(--bad)">⚠ 痛点</h4><p class="dim">AI没有眼睛</p></div><div class="card" style="border-left:3px solid var(--accent-2)"><h4 style="color:var(--accent-2)">🔮 未来</h4><p class="dim">多Agent并行</p></div></div>'),
    (16, '个人vs企业', 'PERSONAL vs ENTERPRISE', '<div class="grid g2 mt-l" style="max-width:500px;margin:0 auto"><div class="card" style="border-top:3px solid var(--accent-2);padding:20px"><h3 style="color:var(--accent-2)">👤 个人</h3><p class="dim">提示词+上下文·错了Ctrl+Z</p></div><div class="card" style="border-top:3px solid var(--bad);padding:20px"><h3 style="color:var(--bad)">🏢 企业</h3><p class="dim">四大工程全得上·错了就是钱</p></div></div>'),
    (17, '数据隐私', 'DATA PRIVACY', '<ul style="font-size:14px;line-height:2.2;list-style:none;padding-left:0;margin-top:12px"><li><span class="pill pill-accent" style="font-size:10px;padding:2px 8px">①</span> 问问题→<strong style="color:#fff">用API</strong> ② 上传→<strong style="color:#fff">用Trae</strong> ③ 聊机密→<strong style="color:#fff">隐私模式</strong> ④ 复制→<strong style="color:#fff">企业版</strong> ⑤ 多人→<strong style="color:#fff">一人一账号</strong></li></ul><div class="card mt-m" style="border-left:3px solid #d2a8ff;max-width:350px"><p style="font-size:13px"><strong style="color:#d2a8ff">🅿️ Pro升级：私有化部署</strong></p></div>'),
    (18, 'Checklist', 'CHECKLIST', '<div class="grid g2 mt-l"><div class="card"><p style="font-size:14px;line-height:2">① 明确场景 ② 选模型 ③ 搭知识库<br>④ 设计提示词 ⑤ 配置规训 ⑥ 评估隐私<br>⑦ 搭建工作流 ⑧ 循环优化</p></div><div class="card"><p style="font-size:13px"><strong>三层工具</strong>：API Key→本地工具→知识库</p></div></div>'),
    (19, '答疑', 'Q&A', '<div class="card mt-l" style="max-width:450px;margin:16px auto"><p style="font-size:15px;line-height:1.6"><strong>AI——当你不会用它的时候，他真的是垃圾。当你学会用它的时候，就能变废为宝。厉害的不是AI，是人类的脑子。</strong></p></div>'),
    (20, '附录', 'APPENDIX', '<div class="grid g2 mt-l" style="max-width:450px;margin:0 auto"><div class="card" style="border-left:3px solid var(--accent-2)"><h4 style="color:var(--accent-2)">🇨🇳 国内稳定</h4><p class="dim">DeepSeek·Qwen·GLM-4·豆包</p></div><div class="card" style="border-left:3px solid var(--accent)"><h4 style="color:var(--accent)">🌍 个人灵活</h4><p class="dim">ChatGPT·Claude·Gemini</p></div></div><p style="color:var(--text-3);text-align:center;margin-top:12px;font-size:13px">不是哪个更好，是哪个更适合你的场景</p>'),
]

for idx, title, kicker, body in remaining:
    slides.append(f'''<section class="slide" data-title="{title}">
  <p class="kicker">{kicker}</p>
  <h2 class="h2">{title}</h2>
  {body}
  <div class="notes">内容待补充。</div>
</section>''')

# Insert all slides between <!-- 1. Cover --> and <!-- 8. Q&A -->
start_marker = '<!-- 1. Cover -->'
end_marker = '<!-- 8. Q&A -->'
start_idx = html.index(start_marker)
end_idx = html.index(end_marker)

new_slides = '\n\n'.join(slides)
result = html[:start_idx] + new_slides + '\n' + html[end_idx:]

# Add control integration + touch swipe + card logic before </body>
extra = '''
<script>
/* Touch swipe navigation */
(function(){
  var startX=0,startY=0,threshold=60;
  document.addEventListener('touchstart',function(e){startX=e.touches[0].clientX;startY=e.touches[0].clientY;},{passive:true});
  document.addEventListener('touchend',function(e){
    var dx=e.changedTouches[0].clientX-startX,dy=e.changedTouches[0].clientY-startY;
    if(Math.abs(dx)>Math.abs(dy)&&Math.abs(dx)>threshold){
      if(dx<0)window.location.hash='#/'+(parseInt((window.location.hash||'#/1').slice(2))+1);
      else window.location.hash='#/'+Math.max(1,parseInt((window.location.hash||'#/1').slice(2))-1);
    }
  },{passive:true});
})();
/* Control API polling + card interactions */
var cState=0;
setInterval(function(){
  fetch('/api/control/current').then(function(r){return r.json();}).then(function(d){
    if(d.lock)return;
    if(d.slide){var h='#/'+d.slide;if(window.location.hash!==h)window.location.hash=h;}
    if(d.slide===2&&d.expand!==undefined){var e=document.getElementById('s2Card');if(e)e.className=d.expand?'':'hide';}
    if(d.slide===4){
      if(d.card!==undefined){cState=d.card;
        [1,2,3].forEach(function(i){
          var el=document.getElementById('c'+i);if(!el)return;
          if(d.card===i){el.className='card card-accent';el.style.opacity='1';document.getElementById('d'+i).innerHTML=['喂海量文字资料','给问答对·学对话格式','人类打分→AI变"舔狗"'][i-1];document.getElementById('d'+i).style.color='var(--text-2)';}
          else if(d.card===0){el.className='card';el.style.opacity='1';document.getElementById('d1').innerHTML='喂海量文字资料';document.getElementById('d2').innerHTML='点击展开';document.getElementById('d3').innerHTML='点击展开';document.getElementById('d2').style.color='var(--text-3)';document.getElementById('d3').style.color='var(--text-3)';}
          else{el.className='card card-dim';}
        });
      }
      if(d.mode==='limitations'){var b=document.getElementById('limitBox');if(b)b.className='';}
      if(d.mode==='normal'){var b2=document.getElementById('limitBox');if(b2)b2.className='hide';}
    }
  }).catch(function(){});
},1500);
</script>'''

result = result.replace('</body>', extra + '\n</body>')

with open(OUTPUT,'w',encoding='utf-8') as f:
    f.write(result)
print(f'✅ Deck built: {OUTPUT}')
print(f'   Slides: {result.count("class=\"slide\"")}')
print(f'   Size: {len(result)} bytes')
