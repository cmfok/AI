import re

with open('slide4_review.html', 'r', encoding='utf-8') as f:
    content = f.read()

# The left column starts at the g2 div and ends at the training cards section
# I need to replace the content between g2 opening and the training cards
# Reorder: domestic box first, foreign box second

start_marker = '<div class="g2" style="flex:1;align-items:start">'
# Find the end of the left column (before training cards)
end_marker = '<div style="padding-top:0">'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("ERROR: markers not found")
    exit(1)

new_left = '''  <div class="g2" style="flex:1;align-items:start">
    <div style="display:flex;flex-direction:column;gap:10px">
      <!-- 国内框 -->
      <div style="border:1px solid var(--border);border-radius:var(--radius);padding:10px;display:flex;gap:4px;background:var(--bg-soft)">
        <div style="flex:1;display:flex;flex-direction:column;gap:6px">
          <div class="tag" style="display:flex;align-items:center;gap:10px;padding:6px 10px">
            <img src="ai/icon/brand/bytedance-color.svg" style="width:22px;height:22px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/bytedance-text.svg" style="height:16px;width:auto" onerror="this.style.display='none'">
          </div>
          <div class="tag" style="display:flex;align-items:center;gap:10px;padding:6px 10px">
            <img src="ai/icon/brand/alibaba-color.svg" style="width:22px;height:22px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/alibaba-text.svg" style="height:16px;width:auto" onerror="this.style.display='none'">
          </div>
          <div class="tag" style="display:flex;align-items:center;gap:10px;padding:6px 10px">
            <img src="ai/icon/brand/kimi.svg" style="width:22px;height:22px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/kimi-text.svg" style="height:16px;width:auto" onerror="this.style.display='none'">
          </div>
          <div class="tag" style="display:flex;align-items:center;gap:10px;padding:6px 10px">
            <img src="ai/icon/brand/deepseek-color.svg" style="width:22px;height:22px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/deepseek-text.svg" style="height:16px;width:auto" onerror="this.style.display='none'">
          </div>
          <div class="tag" style="display:flex;align-items:center;gap:10px;padding:6px 10px">
            <img src="ai/icon/brand/zhipu-color.svg" style="width:22px;height:22px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/zhipu-text.svg" style="height:16px;width:auto" onerror="this.style.display='none'">
          </div>
        </div>
        <div style="flex:1;display:flex;flex-direction:column;gap:6px">
          <div class="tag" style="display:flex;align-items:center;gap:10px;padding:6px 10px;background:rgba(59,108,255,.06)">
            <img src="ai/icon/brand/doubao-color.svg" style="width:22px;height:22px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/doubao-text.svg" style="height:16px;width:auto" onerror="this.style.display='none'">
          </div>
          <div class="tag" style="display:flex;align-items:center;gap:10px;padding:6px 10px;background:rgba(59,108,255,.06)">
            <img src="ai/icon/brand/qwen-color.svg" style="width:22px;height:22px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/qwen-text.svg" style="height:16px;width:auto" onerror="this.style.display='none'">
          </div>
          <div class="tag" style="display:flex;align-items:center;gap:10px;padding:6px 10px;background:rgba(59,108,255,.06)">
            <img src="ai/icon/brand/kimi.svg" style="width:22px;height:22px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/kimi-text.svg" style="height:16px;width:auto" onerror="this.style.display='none'">
          </div>
          <div class="tag" style="display:flex;align-items:center;gap:10px;padding:6px 10px;background:rgba(59,108,255,.06)">
            <img src="ai/icon/brand/deepseek-color.svg" style="width:22px;height:22px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/deepseek-text.svg" style="height:16px;width:auto" onerror="this.style.display='none'">
          </div>
          <div class="tag" style="display:flex;align-items:center;gap:10px;padding:6px 10px;background:rgba(59,108,255,.06)">
            <img src="ai/icon/brand/chatglm-color.svg" style="width:22px;height:22px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/chatglm-text.svg" style="height:16px;width:auto" onerror="this.style.display='none'">
          </div>
        </div>
      </div>
      <!-- 国外框 -->
      <div style="border:1px solid var(--border);border-radius:var(--radius);padding:10px;display:flex;gap:4px;background:var(--bg-soft)">
        <div style="flex:1;display:flex;flex-direction:column;gap:6px">
          <div class="tag" style="display:flex;align-items:center;gap:10px;padding:6px 10px">
            <img src="ai/icon/brand/openai.svg" style="width:22px;height:22px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/openai-text.svg" style="height:16px;width:auto" onerror="this.style.display='none'">
          </div>
          <div class="tag" style="display:flex;align-items:center;gap:10px;padding:6px 10px">
            <img src="ai/icon/brand/google-brand-color.svg" style="height:22px;width:auto" onerror="this.style.display='none'">
          </div>
          <div class="tag" style="display:flex;align-items:center;gap:10px;padding:6px 10px">
            <img src="ai/icon/brand/anthropic.svg" style="width:22px;height:22px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/anthropic-text.svg" style="height:16px;width:auto" onerror="this.style.display='none'">
          </div>
          <div class="tag" style="display:flex;align-items:center;gap:10px;padding:6px 10px">
            <img src="ai/icon/brand/xai.svg" style="width:22px;height:22px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/xai-text.svg" style="height:16px;width:auto" onerror="this.style.display='none'">
          </div>
          <div class="tag" style="display:flex;align-items:center;gap:10px;padding:6px 10px">
            <img src="ai/icon/brand/bfl.svg" style="width:22px;height:22px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/bfl-text.svg" style="height:16px;width:auto" onerror="this.style.display='none'">
          </div>
        </div>
        <div style="flex:1;display:flex;flex-direction:column;gap:6px">
          <div class="tag" style="display:flex;align-items:center;gap:10px;padding:6px 10px;background:rgba(229,62,62,.06)">
            <img src="ai/icon/brand/openai.svg" style="width:22px;height:22px" onerror="this.style.display='none'">
            <span style="font-weight:600;font-size:15px">ChatGPT</span>
          </div>
          <div class="tag" style="display:flex;align-items:center;gap:10px;padding:6px 10px;background:rgba(229,62,62,.06)">
            <img src="ai/icon/brand/gemini-color.svg" style="width:22px;height:22px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/gemini-text.svg" style="height:16px;width:auto" onerror="this.style.display='none'">
          </div>
          <div class="tag" style="display:flex;align-items:center;gap:10px;padding:6px 10px;background:rgba(229,62,62,.06)">
            <img src="ai/icon/brand/claude-color.svg" style="width:22px;height:22px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/claude-text.svg" style="height:16px;width:auto" onerror="this.style.display='none'">
          </div>
          <div class="tag" style="display:flex;align-items:center;gap:10px;padding:6px 10px;background:rgba(229,62,62,.06)">
            <img src="ai/icon/brand/grok.svg" style="width:22px;height:22px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/grok-text.svg" style="height:16px;width:auto" onerror="this.style.display='none'">
          </div>
          <div class="tag" style="display:flex;align-items:center;gap:10px;padding:6px 10px;background:rgba(229,62,62,.06)">
            <img src="ai/icon/brand/flux.svg" style="width:22px;height:22px" onerror="this.style.display='none'">
            <img src="ai/icon/brand/flux-text.svg" style="height:16px;width:auto" onerror="this.style.display='none'">
          </div>
        </div>
      </div>
    </div>
    '''

new_content = content[:start_idx] + new_left + content[end_idx:]

with open('slide4_review.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Done!")
