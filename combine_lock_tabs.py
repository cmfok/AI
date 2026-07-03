# -*- coding: utf-8 -*-
"""Combine lock button and tab bar into a single row"""

path = '/home/ubuntu/share-ppt/control.html'

with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# Old pattern: lockRow inside sticky, then scroll > tab-bar
old_lock = '''  <div id="lockRow" style="display:flex;gap:6px;margin-bottom:8px;align-items:center">
    <button class="btn" id="lockBtn">\U0001F513 翻页已解锁</button>
    <span style="font-size:11px;color:#8b949e">锁定后展示页不响应翻页</span>
  </div>
</div>
<div class="scroll">
  <div class="tab-bar">
    <button class="tab-btn active" data-tab="script">\U0001F4DD 演讲稿</button>
    <button class="tab-btn" data-tab="questions">\U0001F4AC 观众问题</button>
  </div>'''

new_lock = '''  <div id="lockRow" style="display:flex;gap:4px;margin-bottom:6px;align-items:stretch">
    <button class="btn" id="lockBtn" style="flex-shrink:0;white-space:nowrap;font-size:12px;padding:6px 10px">\U0001F513 翻页已解锁</button>
    <button class="tab-btn active" data-tab="script" style="font-size:12px">\U0001F4DD 演讲稿</button>
    <button class="tab-btn" data-tab="questions" style="font-size:12px">\U0001F4AC 观众问题</button>
  </div>
</div>
<div class="scroll">
  <div class="tab-bar" style="display:none"></div>'''

if old_lock in html:
    html = html.replace(old_lock, new_lock)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print('Combined lock + tab bar')
else:
    print('Old pattern not found')
    idx = html.find('lockRow')
    if idx > 0:
        print(repr(html[idx:idx+350]))
    else:
        print('lockRow not found')
