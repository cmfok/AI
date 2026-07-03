# -*- coding: utf-8 -*-
"""Restructure control.html with tab bar: 演讲稿 / 观众问题 / 锁定翻页"""

path = '/home/ubuntu/share-ppt/control.html'

with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

if 'tab-bar' in html:
    print('Tabs already exist, skipping')
else:
    # 1. Add tab bar CSS before the closing </style>
    tab_css = '''
/* ── Tab 切换 ── */
.tab-bar{display:flex;gap:4px;margin-bottom:8px}
.tab-btn{flex:1;padding:7px 0;border-radius:8px;border:1px solid rgba(139,148,158,.12);background:rgba(255,255,255,.02);color:#8b949e;font-size:12px;font-weight:500;cursor:pointer;text-align:center;transition:all .2s;font-family:inherit}
.tab-btn.active{background:rgba(0,113,227,.12);border-color:rgba(0,113,227,.3);color:#58a6ff}
.tab-btn:active{transform:scale(.97)}
.tab-content{display:none}
.tab-content.active{display:block}
'''
    html = html.replace('</style>', tab_css + '</style>')

    # 2. Add tab bar after lockRow (in the sticky section)
    tab_bar = '''
  <div class="tab-bar">
    <button class="tab-btn active" data-tab="script">📝 演讲稿</button>
    <button class="tab-btn" data-tab="questions">💬 观众问题</button>
  </div>
'''
    html = html.replace('<div class="scroll">', '<div class="scroll">' + tab_bar)

    # 3. Wrap speaker panel + next-prev in tab-content script (active)
    speaker_wrap_open = '<div class="tab-content active" id="tabScript">\n'
    speaker_wrap_close = '\n</div>'
    
    # Find the speaker panel section
    old_scroll_content = '<div class="speaker-panel">\n    <div class="sl" id="sl">P1 · 封面</div>\n    <div class="sc" id="sc">加载中...</div>\n  </div>\n  <div class="next-prev">'
    new_scroll_content = speaker_wrap_open + '<div class="speaker-panel">\n    <div class="sl" id="sl">P1 · 封面</div>\n    <div class="sc" id="sc">加载中...</div>\n  </div>\n  <div class="next-prev">' + speaker_wrap_close
    
    html = html.replace(old_scroll_content, new_scroll_content)

    # 4. Wrap the questions section in tab-content
    questions_wrap_open = '<div class="tab-content" id="tabQuestions">\n'
    
    # Find the questions section start
    qa_marker = '<!-- === 观众问答 === -->'
    if qa_marker in html:
        qa_wrapped = questions_wrap_open + '\n' + qa_marker
        html = html.replace(qa_marker, qa_wrapped)
        # Add closing tag at appropriate place - before <div class="bottom-nav">
        html = html.replace('<div class="bottom-nav">', '</div>\n<div class="bottom-nav">')
    else:
        print('WARNING: QA marker not found')

    # 5. Add tab switching JS before the lock toggle code or at end
    tab_js = '''
// ── Tab 切换 ──
document.querySelectorAll('.tab-btn').forEach(function(btn){
  btn.addEventListener('click', function(){
    document.querySelectorAll('.tab-btn').forEach(function(b){b.className='tab-btn';});
    this.className='tab-btn active';
    document.querySelectorAll('.tab-content').forEach(function(tc){tc.className='tab-content';});
    var tab = this.dataset.tab;
    var target = document.getElementById('tab' + tab.charAt(0).toUpperCase() + tab.slice(1));
    if(target) target.className='tab-content active';
  });
});
'''
    # Insert before the existing lock toggle
    lock_marker = "var locked=false;"
    if lock_marker in html:
        html = html.replace(lock_marker, tab_js + '\n' + lock_marker)
    else:
        print('WARNING: lock marker not found, appending to end')
        html = html.replace('</script>', '\n' + tab_js + '\n</script>', 1)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print('Tabs added successfully')
