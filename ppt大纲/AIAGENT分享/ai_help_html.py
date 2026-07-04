# AI 科普页面 — 瑞士国际主义风格 (guizang-ppt-skill)
# 主题色: 柠檬黄 (#FFD500)
AI_HELP_HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>AI Engineering · 把AI当员工</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400;500;600;700;800;900&family=JetBrains+Mono:wght@300;400;500;600&family=Noto+Sans+SC:wght@200;300;400;500;700;900&display=swap" rel="stylesheet">
<style>
:root{
  --paper:#fafaf8;
  --paper-rgb:250,250,248;
  --ink:#0a0a0a;
  --ink-rgb:10,10,10;
  --grey-1:#f0f0ee;
  --grey-2:#d4d4d2;
  --grey-3:#737373;
  --accent:#FFD500;
  --accent-rgb:255,213,0;
  --accent-on:#0a0a0a;
  --accent-bright:#FFE44D;
  --sans:"Inter","Helvetica Neue","Helvetica","Arial","Segoe UI Variable","Segoe UI",system-ui,-apple-system,sans-serif;
  --sans-zh:"PingFang SC","Hiragino Sans GB","Source Han Sans SC","Noto Sans SC","Microsoft YaHei UI","Microsoft YaHei","微软雅黑",sans-serif;
  --mono:"JetBrains Mono","IBM Plex Mono","SF Mono","Cascadia Code","Consolas","Courier New",ui-monospace,monospace;
  --nav-safe-bottom:8vh;
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:100%;height:100%;overflow:hidden;background:var(--paper);color:var(--ink);font-family:var(--sans),var(--sans-zh);-webkit-font-smoothing:antialiased}

/* WebGL 网格背景 */
canvas.bg{position:fixed;inset:0;width:100vw;height:100vh;z-index:0;display:block;opacity:.55;mix-blend-mode:multiply;pointer-events:none}

#deck{position:fixed;inset:0;width:10000vw;height:100vh;display:flex;flex-wrap:nowrap;transition:transform .9s cubic-bezier(.77,0,.175,1);z-index:10;will-change:transform}
.slide{
  width:100vw;height:100vh;flex:0 0 100vw;
  position:relative;
  padding:8vh 6vw;
  display:flex;flex-direction:column;
  overflow:hidden;
  background:var(--paper);color:var(--ink);
}
.slide.grey{background:var(--grey-1)}
.slide.dark{background:var(--ink);color:var(--paper)}
.slide.accent{background:var(--accent);color:var(--accent-on)}
.slide.hero{background:transparent}

/* 极细线 */
.rule{width:100%;height:1px;background:currentColor;opacity:.15}
.rule.accent{background:var(--accent);opacity:1;height:2px}

/* 点阵 */
.dots{background-image:radial-gradient(currentColor 1px, transparent 1px);background-size:12px 12px;opacity:.18}

/* ── 版面布局 ── */
.row{display:flex;gap:4vw;flex:1;align-items:center}
.row.reverse{flex-direction:row-reverse}
.col{display:flex;flex-direction:column}
.col-left{width:38%;flex-shrink:0}
.col-right{width:58%;flex-shrink:0}
.fill{flex:1}
.center{align-items:center;justify-content:center;text-align:center}
.mr{margin-top:auto}

/* ── 主标题（英文）── */
.h-en{
  font-family:var(--sans);font-weight:200;
  font-size:min(5.4vw,9vh);
  line-height:.92;letter-spacing:-.03em;
  margin-bottom:.6vh;
}
.h-en.sm{font-size:min(4.4vw,7.5vh)}

/* ── 副标题（中文）── */
.h-cn{
  font-family:var(--sans),var(--sans-zh);font-weight:300;
  font-size:min(1.5vw,2.6vh);
  line-height:1.3;letter-spacing:.12em;
  opacity:.55;margin-bottom:2.4vh;
}

/* ── 编号标签 ── */
.tag-nb{
  font-family:var(--mono);font-size:max(13px,min(.8vw,1.4vh));
  letter-spacing:.2em;color:var(--accent);font-weight:500;
  display:flex;align-items:center;gap:.8em;margin-bottom:2vh;
}
.tag-nb::before{content:"";width:20px;height:1px;background:currentColor}

/* ── 正文 ── */
.body{
  font-family:var(--sans),var(--sans-zh);font-weight:400;
  font-size:max(18px,min(1.1vw,2vh));line-height:1.65;opacity:.8;
}
.body-sm{
  font-family:var(--sans),var(--sans-zh);font-weight:400;
  font-size:max(16px,min(.95vw,1.7vh));line-height:1.55;opacity:.72;
}
.meta{
  font-family:var(--mono);font-size:max(13px,min(.78vw,1.4vh));
  letter-spacing:.16em;text-transform:uppercase;opacity:.55;
}

/* ── 亮点块 ── */
.accent-block{
  background:var(--accent);color:var(--accent-on);
  padding:1.8vh 2vw;border-radius:2px;
  font-size:max(15px,min(.95vw,1.7vh));line-height:1.55;
}
.accent-block.dark{background:var(--ink);color:var(--paper)} 

/* ── 引用/比喻 ── */
.callout{
  border-left:3px solid var(--accent);
  padding:1.4vh 1.6vw;margin-bottom:1.6vh;
  font-size:max(15px,min(.95vw,1.7vh));line-height:1.55;opacity:.85;
}
.callout .emoji{font-size:1.2em;margin-right:.3em}

/* ── 要点列表 ── */
.points{display:flex;flex-direction:column;gap:1.2vh}
.point{display:flex;gap:.8vw;align-items:flex-start}
.point .dot{width:5px;height:5px;border-radius:50%;background:var(--accent);margin-top:.6em;flex-shrink:0}
.point .pt{font-size:max(16px,min(.95vw,1.7vh));line-height:1.55;opacity:.78}

/* ── Pipeline 步骤条 ── */
.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:1.2vw;margin-top:1.6vh}
.step{
  padding-top:1.2vh;border-top:2px solid var(--accent);
  display:flex;flex-direction:column;gap:.4vh;
}
.step .nb{font-family:var(--mono);font-size:max(12px,min(.7vw,1.2vh));letter-spacing:.14em;opacity:.5}
.step .t{font-weight:600;font-size:max(15px,min(1vw,1.8vh));line-height:1.2}
.step .d{font-size:max(14px,min(.82vw,1.5vh));line-height:1.5;opacity:.7}

/* ── 封面样式 ── */
.cover{flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center}
.cover .h-en{font-size:min(7vw,12vh);margin-bottom:1vh}
.cover .h-cn{font-size:min(1.8vw,3vh);opacity:.6;margin-bottom:0}
.cover .rule.accent{width:8vw;margin:2.4vh auto}
.cover .meta{opacity:.45}

/* ── 导航 ── */
#nav{position:fixed;left:50%;bottom:2vh;transform:translateX(-50%);z-index:30;display:flex;gap:10px}
#nav .dot{width:6px;height:6px;background:rgba(0,0,0,.28);cursor:pointer;transition:all .25s;border:0;border-radius:0}
#nav .dot.active{background:var(--accent);width:18px}
body.dark-bg #nav .dot{background:rgba(255,255,255,.32)}
body.dark-bg #nav .dot.active{background:var(--accent)}
#hint{position:fixed;bottom:2.4vh;right:2.5vw;z-index:30;font-family:var(--mono);font-size:13px;letter-spacing:.12em;opacity:.35}
body.dark-bg #hint{color:var(--paper);opacity:.4}

/* ── 返回按钮 ── */
.back-link{position:fixed;top:2.4vh;left:2.5vw;z-index:40;font-family:var(--mono);font-size:13px;letter-spacing:.1em;color:var(--ink);opacity:.45;text-decoration:none;transition:opacity .2s}
.back-link:hover{opacity:.85}

::-webkit-scrollbar{display:none}

/* ── 响应式 ── */
@media(max-width:768px){
  .slide{padding:5vh 4vw}
  .row{flex-direction:column;gap:2.4vh}
  .row.reverse{flex-direction:column-reverse}
  .col-left,.col-right{width:100%}
  .h-en{font-size:min(8vw,6vh)}
  .h-en.sm{font-size:min(6.5vw,5vh)}
  .h-cn{font-size:min(2.6vw,2.2vh)}
  .cover .h-en{font-size:min(10vw,7vh)}
  .cover .h-cn{font-size:min(3.2vw,2.6vh)}
  .body{font-size:max(16px,min(3vw,2.2vh))}
  .body-sm{font-size:max(15px,min(2.6vw,2vh))}
  .steps{grid-template-columns:1fr;gap:1.2vh}
  .accent-block{padding:1.4vh 2.4vw}
  .callout{padding:1.2vh 2.4vw}
}
</style>
</head>
<body>
<a href="/" class="back-link">← 返回分享会</a>
<canvas id="bg-grid" class="bg"></canvas>
<div id="hint">← → 翻页 · ESC</div>

<div id="deck">

<!-- ==================== P1: 封面 ==================== -->
<section class="slide hero">
  <div class="cover">
    <div style="margin-bottom:2.4vh;display:flex;gap:1vw">
      <span style="width:14px;height:14px;border-radius:50%;background:var(--accent);display:inline-block"></span>
      <span style="width:14px;height:14px;border-radius:50%;background:var(--ink);display:inline-block"></span>
    </div>
    <div class="h-en">AI Engineering</div>
    <div class="h-cn" style="margin-bottom:0">把AI当员工，一文讲懂四大管理工程</div>
    <div class="rule accent"></div>
    <div class="meta">AI as an Employee · 四大工程 = 四大管理动作</div>
  </div>
</section>

<!-- ==================== P2: LLM 大语言模型 ==================== -->
<section class="slide dark">
  <div class="row">
    <div class="col-left col">
      <span class="tag-nb" style="color:var(--accent)">LLM BASICS</span>
      <div class="h-en sm" style="color:var(--paper);font-weight:700">LLM: 大语言模型</div>
      <div class="h-cn" style="color:rgba(255,255,255,.85);font-weight:700">从海量文本中"猜"出来的超级大脑</div>
      <div class="callout" style="border-left-color:var(--accent);color:rgba(255,255,255,.92)">
        <span class="emoji">🧠</span> <strong>LLM 的核心原理其实很简单：</strong><br><br>
        给它一段话，它预测<strong>下一个字最可能是什么</strong>。<br>
        就像你看到"今天天气真"，很自然会想到"好"字。<br><br>
        LLM 就是把这个能力放大到极致——<br>
        它读了互联网上<strong>数万亿字的文本</strong>（书籍、网页、论文、代码……），<br>
        学会了"什么词后面通常跟什么词"的统计规律。<br><br>
        <strong>这就是全部。它不思考、不推理、不理解——它只是猜，但猜得极其精准。</strong>
      </div>
		      <div class="accent-block" style="margin-top:auto;background:var(--accent);color:var(--accent-on)">
		        <strong>💡 关键认知：</strong> LLM 非常擅长<strong>语言</strong>，但它天生不擅长<strong>事实</strong>。<br>
		        它知道"销售额"这三个字怎么写，但它<strong>不知道你的销售额是多少</strong>。<br>
		        这个"猜"字，决定了它所有优点，也决定了它所有缺点。
		      </div>
    </div>
    <div class="col-right">
      <div class="steps">
        <div class="step" style="border-top-color:var(--accent)">
          <span class="nb" style="color:rgba(255,255,255,.7)">STAGE 01</span>
          <span class="t" style="color:var(--paper);font-weight:600">📚 预训练（Pre-training）</span>
          <span class="d" style="color:rgba(255,255,255,.88)">喂给 AI 数万亿字的互联网文本——书籍、网页、论文、代码。<br>核心任务：不断预测下一个词，错了就调整参数。<br>相当于"基础教育"：让 AI 学会语言规律和世界知识。</span>
        </div>
        <div class="step" style="border-top-color:var(--accent)">
          <span class="nb" style="color:rgba(255,255,255,.7)">STAGE 02</span>
          <span class="t" style="color:var(--paper);font-weight:600">🎯 指令微调（Fine-tuning）</span>
          <span class="d" style="color:rgba(255,255,255,.88)">用大量高质量"问题-答案"对训练，让 AI 学会理解指令。<br>"用户问什么 → 给出有用回答"——而不是只会续写文字。<br>相当于"岗前培训"：教 AI 怎么和人打交道。</span>
        </div>
        <div class="step" style="border-top-color:var(--accent)">
          <span class="nb" style="color:rgba(255,255,255,.7)">STAGE 03</span>
          <span class="t" style="color:var(--paper);font-weight:600">👍 人类对齐（RLHF）</span>
          <span class="d" style="color:rgba(255,255,255,.88)">人类对 AI 的回答打分、排序、反馈——好的加分、差的扣分。<br>让 AI 学会：说人话、更准确、更安全、更符合预期。<br>相当于"试用期辅导"：用人反馈把 AI 调教成好员工。</span>
        </div>
      </div>
      <!-- LLM 先天缺陷 -->
      <div style="margin-top:1.6vh;padding-top:1.4vh;border-top:1px solid rgba(255,255,255,.15)">
        <div style="font-size:max(17px,min(1.05vw,1.8vh));font-weight:700;font-family:var(--sans),var(--sans-zh);letter-spacing:.08em;color:var(--accent);margin-bottom:.6vh">⚠️ LLM 的先天缺陷</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:.6vw 1.4vw">
          <div style="font-size:max(15px,min(.95vw,1.65vh));line-height:1.5;color:rgba(255,255,255,.92)">
            <strong style="color:var(--accent)">❶ 幻觉</strong> — 不知道答案时会编造，不会说"不知道"
          </div>
          <div style="font-size:max(15px,min(.95vw,1.65vh));line-height:1.5;color:rgba(255,255,255,.92)">
            <strong style="color:var(--accent)">❷ 数学不精</strong> — 擅长文字不擅长精确计算
          </div>
          <div style="font-size:max(15px,min(.95vw,1.65vh));line-height:1.5;color:rgba(255,255,255,.92)">
            <strong style="color:var(--accent)">❸ 知识截止</strong> — 只记得训练时学的，不知道最新信息
          </div>
          <div style="font-size:max(15px,min(.95vw,1.65vh));line-height:1.5;color:rgba(255,255,255,.92)">
            <strong style="color:var(--accent)">❹ 无真正理解</strong> — 靠统计规律，不是真的推理
          </div>
        </div>
        <div style="font-size:max(14px,min(.85vw,1.5vh));line-height:1.4;color:rgba(255,255,255,.6);margin-top:.4vh">理解这些缺陷，才能知道哪些事该交给 AI、哪些不该</div>
      </div>
      <div style="margin-top:auto;padding-top:1.2vh">
        <div class="meta" style="color:rgba(255,255,255,.65)">三个阶段缺一不可：先读万卷书（预训练）→ 再学干活（微调）→ 最后学做人（RLHF）</div>
      </div>
    </div>
  </div>

		  	  <div style="margin-top:2.4vh;padding-top:1.6vh;border-top:1px solid rgba(255,255,255,.12)">
		    <div style="font-size:max(14px,min(.85vw,1.5vh));font-weight:600;color:var(--paper);line-height:1.2;margin-bottom:.6vh">常见大语言模型</div>
		    <div style="display:flex;gap:.6vw;flex-wrap:wrap;align-items:center">
		      <div style="background:var(--accent);color:var(--accent-on);padding:.4vh .8vw;border-radius:4px;font-size:max(13px,min(.78vw,1.4vh));font-weight:600;white-space:nowrap">🧠 GPT</div>
		      <div style="background:rgba(255,255,255,.12);color:rgba(255,255,255,.9);padding:.4vh .8vw;border-radius:4px;font-size:max(13px,min(.78vw,1.4vh));font-weight:500;white-space:nowrap">🌐 DeepSeek</div>
		      <div style="background:rgba(255,255,255,.12);color:rgba(255,255,255,.9);padding:.4vh .8vw;border-radius:4px;font-size:max(13px,min(.78vw,1.4vh));font-weight:500;white-space:nowrap">🍫 豆包</div>
		      <div style="background:rgba(255,255,255,.12);color:rgba(255,255,255,.9);padding:.4vh .8vw;border-radius:4px;font-size:max(13px,min(.78vw,1.4vh));font-weight:500;white-space:nowrap">📖 Kimi</div>
		      <div style="background:rgba(255,255,255,.12);color:rgba(255,255,255,.9);padding:.4vh .8vw;border-radius:4px;font-size:max(13px,min(.78vw,1.4vh));font-weight:500;white-space:nowrap">🔮 通义千问</div>
		      <div style="background:rgba(255,255,255,.12);color:rgba(255,255,255,.9);padding:.4vh .8vw;border-radius:4px;font-size:max(13px,min(.78vw,1.4vh));font-weight:500;white-space:nowrap">📝 文心一言</div>
		    </div>
		  </div></section>

<!-- ==================== P3: Prompt Engineering ==================== -->
<section class="slide grey">
  <div class="row">
    <div class="col-left col">
      <span class="tag-nb">CHAPTER 01</span>
      <div class="h-en sm"><strong style="font-weight:700;font-size:min(6.4vw,10vh)">Prompt</strong><br><span style="font-weight:200">Engineering</span></div>
      <div class="h-cn">提示词工程</div>
      <div class="point" style="margin-bottom:1vh">
        <span class="dot" style="margin-top:.7em"></span>
        <span class="body-sm"><strong>派活说不清楚，员工一定干偏。</strong> AI 也一样——输入质量决定输出质量。</span>
      </div>
      <div class="callout">
        <span class="emoji">📖</span> 助理第一天上班，经理派活：<br><br>
        ❌ "做一份上月经营分析"<br>
        → 助理不知道从哪下手，给了一堆零散数据<br><br>
        ✅ "你是运营分析助理，帮我做一份<span style="background:var(--accent);color:var(--accent-on);padding:0 .15em">上月经营分析</span>，<span style="background:var(--accent);color:var(--accent-on);padding:0 .15em">用表格列出各品类销售额、环比变化，标出异常项</span>"<br>
        → 一次做对<br><br>
        <strong>提示词工程 = 派活要讲清楚角色、要求和标准</strong>
      </div>
      <div class="accent-block dark" style="margin-top:auto">
        <strong>💡</strong> 同一个助理、同一个任务——派活方式不同，结果天差地别。AI 也是你的员工，好好派活是第一步。
      </div>
    </div>
    <div class="col-right">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:1.6vw 2vw;margin-bottom:2vh">
        <div style="border-top:2px solid var(--accent);padding-top:1.2vh">
          <div style="font-size:max(14px,min(.78vw,1.4vh));opacity:.5;font-family:var(--mono);letter-spacing:.14em;margin-bottom:.4vh">RULE 01</div>
          <div style="font-weight:600;font-size:max(15px,min(1vw,1.8vh));margin-bottom:.3vh">🎯 定角色</div>
          <div class="body-sm">先说清楚身份："你是运营分析助理"——AI 立刻切换到分析视角</div>
        </div>
        <div style="border-top:2px solid var(--accent);padding-top:1.2vh">
          <div style="font-size:max(14px,min(.78vw,1.4vh));opacity:.5;font-family:var(--mono);letter-spacing:.14em;margin-bottom:.4vh">RULE 02</div>
          <div style="font-weight:600;font-size:max(15px,min(1vw,1.8vh));margin-bottom:.3vh">📋 讲要求</div>
          <div class="body-sm">明确交付物："用表格列出品类、销售额、环比变化"</div>
        </div>
        <div style="border-top:2px solid var(--accent);padding-top:1.2vh">
          <div style="font-size:max(14px,min(.78vw,1.4vh));opacity:.5;font-family:var(--mono);letter-spacing:.14em;margin-bottom:.4vh">RULE 03</div>
          <div style="font-weight:600;font-size:max(15px,min(1vw,1.8vh));margin-bottom:.3vh">📝 给参考</div>
          <div class="body-sm">给一个模板："照上月的报告格式来写，重点看变化最大的品类"</div>
        </div>
        <div style="border-top:2px solid var(--accent);padding-top:1.2vh">
          <div style="font-size:max(14px,min(.78vw,1.4vh));opacity:.5;font-family:var(--mono);letter-spacing:.14em;margin-bottom:.4vh">RULE 04</div>
          <div style="font-weight:600;font-size:max(15px,min(1vw,1.8vh));margin-bottom:.3vh">🚧 设标准</div>
          <div class="body-sm">划定范围："只看线上渠道，金额精确到元，异常项标红"</div>
        </div>
      </div>
      <div class="accent-block">
        <strong>🔑 四个派活技巧：</strong>定角色 · 讲要求 · 给参考 · 设标准。对这个 AI 助理有效，对你的每个 AI 任务都有效。
      </div>
    </div>
  </div>

	  	  <div style="margin-top:2.4vh;padding-top:1.6vh;border-top:1px solid rgba(0,0,0,.08)">
	    <div style="font-size:max(13px,min(.78vw,1.4vh));opacity:.5;font-family:var(--mono);letter-spacing:.16em;margin-bottom:.8vh">POPULAR AI CHAT PLATFORMS</div>
	    <div style="display:flex;gap:.6vw;flex-wrap:wrap">
	      <div style="background:var(--accent);color:var(--accent-on);padding:.4vh .8vw;border-radius:4px;font-size:max(13px,min(.78vw,1.4vh));font-weight:600;white-space:nowrap">🌐 网页版DeepSeek</div>
	      <div style="background:var(--grey-1);padding:.4vh .8vw;border-radius:4px;font-size:max(13px,min(.78vw,1.4vh));font-weight:500;white-space:nowrap">💬 ChatGPT</div>
	      <div style="background:var(--grey-1);padding:.4vh .8vw;border-radius:4px;font-size:max(13px,min(.78vw,1.4vh));font-weight:500;white-space:nowrap">🍫 豆包</div>
	      <div style="background:var(--grey-1);padding:.4vh .8vw;border-radius:4px;font-size:max(13px,min(.78vw,1.4vh));font-weight:500;white-space:nowrap">📖 Kimi</div>
	      <div style="background:var(--grey-1);padding:.4vh .8vw;border-radius:4px;font-size:max(13px,min(.78vw,1.4vh));font-weight:500;white-space:nowrap">🔮 通义千问</div>
	      <div style="background:var(--grey-1);padding:.4vh .8vw;border-radius:4px;font-size:max(13px,min(.78vw,1.4vh));font-weight:500;white-space:nowrap">📝 文心一言</div>
	      <div style="background:var(--grey-1);padding:.4vh .8vw;border-radius:4px;font-size:max(13px,min(.78vw,1.4vh));font-weight:500;white-space:nowrap">💜 智谱清言</div>
	    </div>
	    <div style="font-size:max(12px,min(.72vw,1.3vh));opacity:.5;margin-top:.6vh;line-height:1.4">日常使用这些平台就是在做提示词工程——说得越清楚，AI 回答越精准。</div>
	  </div></section>

<!-- ==================== P4: Context Engineering ==================== -->
<section class="slide">
  <div class="row">
    <div class="col-left col">
      <span class="tag-nb">CHAPTER 02</span>
      <div class="h-en sm"><strong style="font-weight:700;font-size:min(6.4vw,10vh)">Context</strong><br><span style="font-weight:200">Engineering</span></div>
      <div class="h-cn">上下文工程</div>
      <div class="point" style="margin-bottom:1vh">
        <span class="dot" style="margin-top:.7em"></span>
        <span class="body-sm"><strong>派完活，还得给资料。</strong> AI 助理不知道你的业务数据、历史情况——不给资料就做，等于闭着眼睛干活。</span>
      </div>
      <div class="callout">
        <span class="emoji">📖</span> 还是那个 AI 助理做经营分析——光派活不够，你得给 TA 东西：<br><br>
        "这是<strong>上月的原始销售数据</strong>和<strong>前三个月的报告参考</strong>，<br>
        各品类<strong>成本结构说明</strong>在这份文档里。基于这些做分析。"<br><br>
        助理有了资料，做出来的报告才靠谱。<br><br>
        <strong>上下文工程 = 给 AI 资料再让它干活</strong>
      </div>
      <div class="accent-block dark" style="margin-top:auto">
        <strong>💡</strong> AI 助理能做出好分析，不是因为它更聪明——而是你给了它<strong>足够多的背景信息</strong>。资料越全，判断越准。
      </div>
    </div>
    <div class="col-right col" style="gap:1.6vh">
      <div style="border-top:2px solid var(--accent);padding-top:1.4vh">
        <div style="display:flex;align-items:center;gap:.6vw;margin-bottom:.4vh">
          <span style="font-size:1.4vw">📁</span>
          <span style="font-weight:600;font-size:max(15px,min(1vw,1.8vh))">给历史数据</span>
        </div>
        <div class="body-sm">把上月的销售明细、客户订单数据喂给 AI——就像助理登录系统看到真实业绩。</div>
      </div>
      <div style="border-top:2px solid var(--accent);padding-top:1.4vh">
        <div style="display:flex;align-items:center;gap:.6vw;margin-bottom:.4vh">
          <span style="font-size:1.4vw">📋</span>
          <span style="font-weight:600;font-size:max(15px,min(1vw,1.8vh))">给参考模板</span>
        </div>
        <div class="body-sm">把前几个月的报告给 AI 看——"照这个格式和风格写"，就像助理参考前辈的成果。</div>
      </div>
      <div style="border-top:2px solid var(--accent);padding-top:1.4vh">
        <div style="display:flex;align-items:center;gap:.6vw;margin-bottom:.4vh">
          <span style="font-size:1.4vw">📚</span>
          <span style="font-weight:600;font-size:max(15px,min(1vw,1.8vh))">给业务规则</span>
        </div>
        <div class="body-sm">把品类分类逻辑、成本核算方法、异常判定标准写成文档喂给 AI——就像给助理一本业务手册。</div>
      </div>
      <div class="accent-block" style="margin-top:auto">
        <strong>🔑 三步走：</strong>给数据 → 给参考 → 给规则。每一步都让 AI 助理的回答更靠谱。
      </div>
    </div>
  </div>

	  	  <div style="margin-top:2.4vh;padding-top:1.6vh;border-top:1px solid rgba(0,0,0,.08)">
	    <div style="font-size:max(13px,min(.78vw,1.4vh));opacity:.5;font-family:var(--mono);letter-spacing:.16em;margin-bottom:.8vh">RAG & KNOWLEDGE BASE TOOLS</div>
	    <div style="display:flex;gap:.6vw;flex-wrap:wrap">
	      <div style="background:var(--accent);color:var(--accent-on);padding:.4vh .8vw;border-radius:4px;font-size:max(13px,min(.78vw,1.4vh));font-weight:600;white-space:nowrap">🤖 Dify</div>
	      <div style="background:var(--grey-1);padding:.4vh .8vw;border-radius:4px;font-size:max(13px,min(.78vw,1.4vh));font-weight:500;white-space:nowrap">⚡ FastGPT</div>
	      <div style="background:var(--grey-1);padding:.4vh .8vw;border-radius:4px;font-size:max(13px,min(.78vw,1.4vh));font-weight:500;white-space:nowrap">📚 RAGFlow</div>
	      <div style="background:var(--grey-1);padding:.4vh .8vw;border-radius:4px;font-size:max(13px,min(.78vw,1.4vh));font-weight:500;white-space:nowrap">🔗 AnythingLLM</div>
	      <div style="background:var(--grey-1);padding:.4vh .8vw;border-radius:4px;font-size:max(13px,min(.78vw,1.4vh));font-weight:500;white-space:nowrap">☁️ 百度千帆</div>
	      <div style="background:var(--grey-1);padding:.4vh .8vw;border-radius:4px;font-size:max(13px,min(.78vw,1.4vh));font-weight:500;white-space:nowrap">🏗️ 阿里百炼</div>
	    </div>
	    <div style="font-size:max(12px,min(.72vw,1.3vh));opacity:.5;margin-top:.6vh;line-height:1.4">上下文工程落地需要工具支撑——这些平台帮你搭建知识库、管理上下文、实现 RAG 检索增强。</div>
	  </div></section>

<!-- ==================== P5: Harness Engineering ==================== -->
<section class="slide grey">
  <div class="row">
    <div class="col-left col">
      <span class="tag-nb">CHAPTER 03</span>
      <div class="h-en sm"><strong style="font-weight:700;font-size:min(6.4vw,10vh)">Harness</strong><br><span style="font-weight:200">Engineering</span></div>
      <div class="h-cn">规训工程</div>
      <div class="point" style="margin-bottom:1vh">
        <span class="dot" style="margin-top:.7em"></span>
        <span class="body-sm"><strong>助理知道做什么、有资料了，但还得有流程和工具才能开工。</strong> 没有 SOP、没有权限、没有质量检查，再聪明也干不好。</span>
      </div>
      <div class="callout">
        <span class="emoji">📖</span> 还是那个 AI 助理做经营分析——派了活、给了资料，现在要让它<strong>按流程干活</strong>：<br><br>
        ① 从 ERP 拉取销售数据<br>
        ② 按品类汇总计算<br>
        ③ 对比上月标出异常<br>
        ④ 生成报告提交审核<br><br>
        同时告诉它：<strong>可以查数据库，但不能改数据；金额异常先标红，不要擅自修改；报告生成后自动检查格式</strong>。<br><br>
        <strong>Harness = 给 AI 助理定 SOP、配工具、设边界、做检验</strong>
      </div>
      <div class="accent-block dark" style="margin-top:auto">
        <strong>💡</strong> 没有规矩的 AI 助理=野路子。有了 SOP 和工具的 AI 助理=职业选手。差别就在 Harness。
      </div>
    </div>
    <div class="col-right">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:1.6vw 2vw;margin-bottom:2vh">
        <div style="border-top:2px solid var(--accent);padding-top:1.2vh">
          <div style="font-size:max(14px,min(.78vw,1.4vh));opacity:.5;font-family:var(--mono);letter-spacing:.14em;margin-bottom:.4vh">STEP 01</div>
          <div style="font-weight:600;font-size:max(15px,min(1vw,1.8vh));margin-bottom:.3vh">📋 定工作流程</div>
          <div class="body-sm">拉数据→汇总→对比→出报告→提交审核。每一步清楚，不跳步不遗漏。</div>
        </div>
        <div style="border-top:2px solid var(--accent);padding-top:1.2vh">
          <div style="font-size:max(14px,min(.78vw,1.4vh));opacity:.5;font-family:var(--mono);letter-spacing:.14em;margin-bottom:.4vh">STEP 02</div>
          <div style="font-weight:600;font-size:max(15px,min(1vw,1.8vh));margin-bottom:.3vh">🔧 配系统权限</div>
          <div class="body-sm">让 AI 能查 ERP 数据、读数据库——就像助理开通了公司系统账号，有权限才能干活。</div>
        </div>
        <div style="border-top:2px solid var(--accent);padding-top:1.2vh">
          <div style="font-size:max(14px,min(.78vw,1.4vh));opacity:.5;font-family:var(--mono);letter-spacing:.14em;margin-bottom:.4vh">STEP 03</div>
          <div style="font-weight:600;font-size:max(15px,min(1vw,1.8vh));margin-bottom:.3vh">🚫 划安全红线</div>
          <div class="body-sm">能读不能改、金额异常只标红不篡改、敏感数据不对外——红线划清楚，不出事。</div>
        </div>
        <div style="border-top:2px solid var(--accent);padding-top:1.2vh">
          <div style="font-size:max(14px,min(.78vw,1.4vh));opacity:.5;font-family:var(--mono);letter-spacing:.14em;margin-bottom:.4vh">STEP 04</div>
          <div style="font-weight:600;font-size:max(15px,min(1vw,1.8vh));margin-bottom:.3vh">✅ 做质量检验</div>
          <div class="body-sm">报告自动检查：表格完整吗？数据对得上吗？异常标注了吗？不达标就打回重做。</div>
        </div>
      </div>
      <div class="accent-block">
        <strong>🔑 四个管理动作：</strong>定流程 · 配权限 · 划红线 · 做检验。把 AI 助理从一个聪明人训练成职业选手。
      </div>
    </div>
  </div>

	  	  <div style="margin-top:2.4vh;padding-top:1.6vh;border-top:1px solid rgba(0,0,0,.08)">
	    <div style="font-size:max(13px,min(.78vw,1.4vh));opacity:.5;font-family:var(--mono);letter-spacing:.16em;margin-bottom:.8vh">CHINA AI AGENT ECOSYSTEM</div>
	    <div style="display:flex;gap:.6vw;flex-wrap:wrap">
	      <div style="background:var(--accent);color:var(--accent-on);padding:.4vh .8vw;border-radius:4px;font-size:max(13px,min(.78vw,1.4vh));font-weight:600;white-space:nowrap">🦞 OpenClaw</div>
	      <div style="background:var(--grey-1);padding:.4vh .8vw;border-radius:4px;font-size:max(13px,min(.78vw,1.4vh));font-weight:500;white-space:nowrap">🧠 Hermes</div>
	      <div style="background:var(--grey-1);padding:.4vh .8vw;border-radius:4px;font-size:max(13px,min(.78vw,1.4vh));font-weight:500;white-space:nowrap">🤖 Dify</div>
	      <div style="background:var(--grey-1);padding:.4vh .8vw;border-radius:4px;font-size:max(13px,min(.78vw,1.4vh));font-weight:500;white-space:nowrap">⚡ FastGPT</div>
	      <div style="background:var(--grey-1);padding:.4vh .8vw;border-radius:4px;font-size:max(13px,min(.78vw,1.4vh));font-weight:500;white-space:nowrap">🔗 LangChain</div>
	      <div style="background:var(--grey-1);padding:.4vh .8vw;border-radius:4px;font-size:max(13px,min(.78vw,1.4vh));font-weight:500;white-space:nowrap">☁️ 百度千帆</div>
	      <div style="background:var(--grey-1);padding:.4vh .8vw;border-radius:4px;font-size:max(13px,min(.78vw,1.4vh));font-weight:500;white-space:nowrap">🏗️ 阿里百炼</div>
	      <div style="background:var(--grey-1);padding:.4vh .8vw;border-radius:4px;font-size:max(13px,min(.78vw,1.4vh));font-weight:500;white-space:nowrap">🛠️ 腾讯SkillHub</div>
	    </div>
	    <div style="font-size:max(12px,min(.72vw,1.3vh));opacity:.5;margin-top:.6vh;line-height:1.4">从开源自建到云平台托管，国内 AI 智能体生态越来越丰富。</div>
	  </div></section>

<!-- ==================== P6: Loop Engineering ==================== -->
<section class="slide">
  <div class="row">
    <div class="col-left col">
      <span class="tag-nb">CHAPTER 04</span>
      <div class="h-en sm"><strong style="font-weight:700;font-size:min(6.4vw,10vh)">Loop</strong><br><span style="font-weight:200">Engineering</span></div>
      <div class="h-cn">循环工程</div>
      <div class="point" style="margin-bottom:1vh">
        <span class="dot" style="background:var(--accent);margin-top:.7em"></span>
        <span class="body-sm"><strong>AI 助理第一次做的报告，不可能完美。</strong> 好管理者会让助理先做→自己审核→给反馈→助理改进。AI 要变成得力干将，也得走这个循环。</span>
      </div>
      <div class="callout" style="border-left-color:var(--accent)">
        <span class="emoji">📖</span> 还是那个 AI 助理，第一次提交经营分析报告：<br><br>
        你一看，发现几个问题——<br>
        品类分类不对、某个金额算错了、异常分析不够深入。<br><br>
        ✅ 你打回去：<br>
        "品类按线上/线下重新分类，XX品类的金额再核对一下，异常项补充原因分析"<br><br>
        AI 助理修改后再提交，这次好多了。<br>
        下个月，它记得你上次的要求，一次就做对了。<br><br>
        <strong>Loop 工程 = PDCA 循环：计划→执行→检查→改进</strong>
      </div>
      <div class="accent-block dark" style="margin-top:auto;background:var(--ink);color:var(--paper)">
        <strong>💡</strong> AI 助理不是天生就会——<strong>是管理者一次次"打回去、给反馈"把它练出来的</strong>。没有这个循环，AI 永远停在第一版。
      </div>
    </div>
    <div class="col-right">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:1.6vw 2vw;margin-bottom:2vh">
        <div style="border-top:2px solid var(--accent);padding-top:1.2vh">
          <div style="font-size:max(14px,min(.78vw,1.4vh));opacity:.5;font-family:var(--mono);letter-spacing:.14em;margin-bottom:.4vh">LEVEL 01</div>
          <div style="font-weight:600;font-size:max(15px,min(1vw,1.8vh));margin-bottom:.3vh">🔍 自查（自己先审）</div>
          <div class="body-sm">AI 做完报告先自己查一遍：分类全了吗？金额对了吗？异常标了吗？——像助理交活前自己过一遍。</div>
        </div>
        <div style="border-top:2px solid var(--accent);padding-top:1.2vh">
          <div style="font-size:max(14px,min(.78vw,1.4vh));opacity:.5;font-family:var(--mono);letter-spacing:.14em;margin-bottom:.4vh">LEVEL 02</div>
          <div style="font-weight:600;font-size:max(15px,min(1vw,1.8vh));margin-bottom:.3vh">💭 复盘（看思路）</div>
          <div class="body-sm">让 AI 把分析过程写出来：为什么标这个异常？用了什么判断标准？你看思路对不对，像看助理的工作底稿。</div>
        </div>
        <div style="border-top:2px solid var(--accent);padding-top:1.2vh">
          <div style="font-size:max(14px,min(.78vw,1.4vh));opacity:.5;font-family:var(--mono);letter-spacing:.14em;margin-bottom:.4vh">LEVEL 03</div>
          <div style="font-weight:600;font-size:max(15px,min(1vw,1.8vh));margin-bottom:.3vh">👥 会诊（多模型）</div>
          <div class="body-sm">重要数据让两三个 AI 各自分析再对比——就像开会让大家各抒己见，取最靠谱的方案。</div>
        </div>
        <div style="border-top:2px solid var(--accent);padding-top:1.2vh">
          <div style="font-size:max(14px,min(.78vw,1.4vh));opacity:.5;font-family:var(--mono);letter-spacing:.14em;margin-bottom:.4vh">LEVEL 04</div>
          <div style="font-weight:600;font-size:max(15px,min(1vw,1.8vh));margin-bottom:.3vh">📊 绩效反馈（人机循环）</div>
          <div class="body-sm">你看完报告→打回给 AI 改进→AI 记住你的偏好→下次更准。就像每月的绩效评估，越来越好。</div>
        </div>
      </div>
      <div class="accent-block" style="margin-top:auto">
        <strong>🔑 四个管理环节：</strong>自查 → 复盘 → 会诊 → 绩效反馈。你带人的方法，带 AI 同样有效。
      </div>
    </div>
	  </div>
	  <div style="margin-top:2.4vh;padding-top:1.6vh;border-top:1px solid rgba(0,0,0,.08)">
	    <div style="font-size:max(14px,min(.85vw,1.5vh));line-height:1.5;color:var(--ink);opacity:.75;text-align:center;max-width:80%;margin:0 auto">
	      <strong style="color:var(--accent)">企业深度定制AI，核心是把人审AI的反馈循环嵌进你的业务流程。</strong><br>
	      前面三个工程有通用工具，循环工程没有——因为它必须长在你的业务里。
	    </div>
	  </div>
	  <div style="position:absolute;bottom:3vh;left:50%;transform:translateX(-50%);z-index:25;text-align:center">
	    <a href="/?slide=6" style="font-family:var(--sans),var(--sans-zh);font-size:13px;font-weight:500;color:var(--ink);opacity:.35;text-decoration:none;transition:opacity .2s">
	      ← 返回分享会第6页
	    </a>
	  </div>
	</section>

</div><!-- /deck -->

<div id="nav"></div>

<script>
// Windows 标记
if(/Win/i.test(navigator.platform||'')) document.body.classList.add('is-win');

// 翻页导航
(function(){
  var deck = document.getElementById('deck');
  var slides = document.querySelectorAll('.slide');
  var total = slides.length;
  var current = 0;
  var nav = document.getElementById('nav');
  
  for(var i=0;i<total;i++){
    var dot = document.createElement('button');
    dot.className = 'dot' + (i===0?' active':'');
    dot.addEventListener('click',goTo.bind(null,i));
    nav.appendChild(dot);
  }
  
  function goTo(idx){
    if(idx<0||idx>=total||idx===current) return;
    current = idx;
    deck.style.transform = 'translateX(-'+(current*100)+'vw)';
    document.querySelectorAll('#nav .dot').forEach(function(d,i){
      d.classList.toggle('active',i===current);
    });
    document.body.classList.toggle('dark-bg',slides[current].classList.contains('dark'));
  }
  
  document.addEventListener('keydown',function(e){
    if(e.key==='ArrowRight'||e.key==='ArrowDown'||e.key===' '){e.preventDefault();goTo(current+1)}
    if(e.key==='ArrowLeft'||e.key==='ArrowUp'){e.preventDefault();goTo(current-1)}
    if(e.key==='Home'){e.preventDefault();goTo(0)}
    if(e.key==='End'){e.preventDefault();goTo(total-1)}
    if(e.key==='Escape'){document.getElementById('overview').style.display=
      document.getElementById('overview').style.display==='none'?'flex':'none'}
  });
  
  // 触摸
  var sx=0;
  document.addEventListener('touchstart',function(e){sx=e.touches[0].clientX});
  document.addEventListener('touchend',function(e){
    var dx=sx-e.changedTouches[0].clientX;
    if(Math.abs(dx)>50) goTo(current+(dx>0?1:-1));
  });
  
  // 滚轮
  var wt;
  document.addEventListener('wheel',function(e){
    if(e.ctrlKey||e.metaKey) return;
    clearTimeout(wt);
    wt=setTimeout(function(){goTo(current+(e.deltaY>0||e.deltaX>0?1:-1))},100);
  },{passive:true});
  
  if(slides[0].classList.contains('dark')) document.body.classList.add('dark-bg');
})();
</script>

<script>
// WebGL 网格背景
(function(){
  var c=document.getElementById('bg-grid'),ctx=c.getContext('2d');
  function r(){c.width=window.innerWidth;c.height=window.innerHeight}
  r();window.addEventListener('resize',r);
  function d(){
    ctx.clearRect(0,0,c.width,c.height);
    ctx.strokeStyle='rgba(0,0,0,.07)';ctx.lineWidth=0.5;
    var s=40;
    for(var x=0;x<=c.width;x+=s){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,c.height);ctx.stroke()}
    for(var y=0;y<=c.height;y+=s){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(c.width,y);ctx.stroke()}
    ctx.fillStyle='rgba(0,0,0,.1)';
    for(var x=0;x<=c.width;x+=12)
      for(var y=0;y<=c.height;y+=12) ctx.fillRect(x,y,0.8,0.8);
  }
  d();window.addEventListener('resize',d);
})();
</script>
</body>
</html>"""
