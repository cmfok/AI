import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = '<div class="g2" style="flex:1;align-items:start">'
end_marker = '<div class="eco-bar"'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("ERROR: markers not found")
    print(f"start found: {start_idx != -1}, end found: {end_idx != -1}")
    exit(1)

new_section = '''  <div style="width:100%;flex:1;display:flex;flex-direction:column;gap:6px">
    <div style="display:flex;gap:6px;flex:1">
      <!-- 国外框 -->
      <div style="flex:1;border:1px solid var(--border);border-radius:var(--radius);padding:8px;display:flex;gap:4px;background:var(--bg-soft)">
        <div style="flex:1;display:flex;flex-direction:column;gap:3px">
          <div class="tag" style="display:flex;align-items:center;gap:4px;padding:4px 6px">
            <img src="ai/icon/brand/openai.svg" style="width:18px;height:18px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/openai-text.svg" style="height:13px;width:auto" onerror="this.style.display='none'">
          </div>
          <div class="tag" style="display:flex;align-items:center;gap:4px;padding:4px 6px">
            <img src="ai/icon/brand/google-brand-color.svg" style="height:18px;width:auto" onerror="this.style.display='none'">
          </div>
          <div class="tag" style="display:flex;align-items:center;gap:4px;padding:4px 6px">
            <img src="ai/icon/brand/anthropic.svg" style="width:18px;height:18px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/anthropic-text.svg" style="height:13px;width:auto" onerror="this.style.display='none'">
          </div>
          <div class="tag" style="display:flex;align-items:center;gap:4px;padding:4px 6px">
            <img src="ai/icon/brand/xai.svg" style="width:18px;height:18px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/xai-text.svg" style="height:13px;width:auto" onerror="this.style.display='none'">
          </div>
          <div class="tag" style="display:flex;align-items:center;gap:4px;padding:4px 6px">
            <img src="ai/icon/brand/bfl.svg" style="width:18px;height:18px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/bfl-text.svg" style="height:13px;width:auto" onerror="this.style.display='none'">
          </div>
        </div>
        <div style="flex:1;display:flex;flex-direction:column;gap:3px">
          <div class="tag" style="display:flex;align-items:center;gap:4px;padding:4px 6px">
            <img src="ai/icon/brand/openai.svg" style="width:18px;height:18px" onerror="this.style.display='none'">
            <span style="font-weight:600;font-size:12px">ChatGPT</span>
          </div>
          <div class="tag" style="display:flex;align-items:center;gap:4px;padding:4px 6px">
            <img src="ai/icon/brand/gemini-color.svg" style="width:18px;height:18px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/gemini-text.svg" style="height:13px;width:auto" onerror="this.style.display='none'">
          </div>
          <div class="tag" style="display:flex;align-items:center;gap:4px;padding:4px 6px">
            <img src="ai/icon/brand/claude-color.svg" style="width:18px;height:18px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/claude-text.svg" style="height:13px;width:auto" onerror="this.style.display='none'">
          </div>
          <div class="tag" style="display:flex;align-items:center;gap:4px;padding:4px 6px">
            <img src="ai/icon/brand/grok.svg" style="width:18px;height:18px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/grok-text.svg" style="height:13px;width:auto" onerror="this.style.display='none'">
          </div>
          <div class="tag" style="display:flex;align-items:center;gap:4px;padding:4px 6px">
            <img src="ai/icon/brand/flux.svg" style="width:18px;height:18px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/flux-text.svg" style="height:13px;width:auto" onerror="this.style.display='none'">
          </div>
        </div>
      </div>
      <!-- 国内框 -->
      <div style="flex:1;border:1px solid var(--border);border-radius:var(--radius);padding:8px;display:flex;gap:4px;background:var(--bg-soft)">
        <div style="flex:1;display:flex;flex-direction:column;gap:3px">
          <div class="tag" style="display:flex;align-items:center;gap:4px;padding:4px 6px">
            <img src="ai/icon/brand/bytedance-color.svg" style="width:18px;height:18px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/bytedance-text.svg" style="height:13px;width:auto" onerror="this.style.display='none'">
          </div>
          <div class="tag" style="display:flex;align-items:center;gap:4px;padding:4px 6px">
            <img src="ai/icon/brand/alibaba-color.svg" style="width:18px;height:18px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/alibaba-text.svg" style="height:13px;width:auto" onerror="this.style.display='none'">
          </div>
          <div class="tag" style="display:flex;align-items:center;gap:4px;padding:4px 6px">
            <img src="ai/icon/brand/kimi.svg" style="width:18px;height:18px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/kimi-text.svg" style="height:13px;width:auto" onerror="this.style.display='none'">
          </div>
          <div class="tag" style="display:flex;align-items:center;gap:4px;padding:4px 6px">
            <img src="ai/icon/brand/deepseek-color.svg" style="width:18px;height:18px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/deepseek-text.svg" style="height:13px;width:auto" onerror="this.style.display='none'">
          </div>
          <div class="tag" style="display:flex;align-items:center;gap:4px;padding:4px 6px">
            <img src="ai/icon/brand/zhipu-color.svg" style="width:18px;height:18px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/zhipu-text.svg" style="height:13px;width:auto" onerror="this.style.display='none'">
          </div>
        </div>
        <div style="flex:1;display:flex;flex-direction:column;gap:3px">
          <div class="tag" style="display:flex;align-items:center;gap:4px;padding:4px 6px">
            <img src="ai/icon/brand/doubao-color.svg" style="width:18px;height:18px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/doubao-text.svg" style="height:13px;width:auto" onerror="this.style.display='none'">
          </div>
          <div class="tag" style="display:flex;align-items:center;gap:4px;padding:4px 6px">
            <img src="ai/icon/brand/qwen-color.svg" style="width:18px;height:18px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/qwen-text.svg" style="height:13px;width:auto" onerror="this.style.display='none'">
          </div>
          <div class="tag" style="display:flex;align-items:center;gap:4px;padding:4px 6px">
            <img src="ai/icon/brand/kimi.svg" style="width:18px;height:18px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/kimi-text.svg" style="height:13px;width:auto" onerror="this.style.display='none'">
          </div>
          <div class="tag" style="display:flex;align-items:center;gap:4px;padding:4px 6px">
            <img src="ai/icon/brand/deepseek-color.svg" style="width:18px;height:18px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/deepseek-text.svg" style="height:13px;width:auto" onerror="this.style.display='none'">
          </div>
          <div class="tag" style="display:flex;align-items:center;gap:4px;padding:4px 6px">
            <img src="ai/icon/brand/chatglm-color.svg" style="width:18px;height:18px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/chatglm-text.svg" style="height:13px;width:auto" onerror="this.style.display='none'">
          </div>
        </div>
      </div>
    </div>
    <div style="display:flex;gap:6px">
      <div class="ca-card" id="p4c1" onclick="toggleP4Card(1)" style="flex:1;border-left:3px solid var(--good);margin-bottom:0"><div class="ch" style="font-size:12px">① 预训练 <span class="ic" style="font-size:10px">▼</span></div><div class="cb"><div class="cb-inner" style="font-size:12px">把真实世界的所有文字资料都<b>喂</b>给它，让它学会人类语言逻辑，并据此<b>"猜词"</b></div></div></div>
      <div class="ca-card" id="p4c2" onclick="toggleP4Card(2)" style="flex:1;border-left:3px solid var(--accent);margin-bottom:0"><div class="ch" style="font-size:12px">② 指令微调 <span class="ic" style="font-size:10px">▼</span></div><div class="cb"><div class="cb-inner" style="font-size:12px">给AI大量<b>"问题→正确答案"</b>配对数据，让它学会回答问题</div></div></div>
      <div class="ca-card" id="p4c3" onclick="toggleP4Card(3)" style="flex:1;border-left:3px solid var(--bad);margin-bottom:0"><div class="ch" style="font-size:12px">③ RLHF <span class="ic" style="font-size:10px">▼</span></div><div class="cb"><div class="cb-inner" style="font-size:12px">人类给AI的回答<b>打分</b>，AI为拿高分过度优化，变成<b>"舔狗"</b></div></div></div>
      <div class="ca-card" id="p4c4" onclick="toggleP4Card(4)" style="flex:1;border-left:3px solid var(--warn);margin-bottom:0"><div class="ch" style="font-size:12px">⚠️ 局限 <span class="ic" style="font-size:10px">▼</span></div><div class="cb"><div class="cb-inner" style="font-size:12px">幻觉 / 知识截止 / 无真实理解</div></div></div>
    </div>
  </div>'''

new_content = content[:start_idx] + new_section + content[end_idx:]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Done! Replaced successfully.")
print(f"Replaced {end_idx - start_idx} chars")
