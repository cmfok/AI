# -*- coding: utf-8 -*-
path = '/home/ubuntu/share-ppt/control.html'

with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

old = 'html += \'<input id="ansInput\' + q.id + \'" type="text" placeholder="输入回答..." style="flex:1;padding:6px 8px;border-radius:6px;border:1px solid rgba(139,148,158,.2);background:rgba(0,0,0,.2);color:#e6edf3;font-size:12px;outline:none">\';'

new = 'html += \'<input id="ansInput\' + q.id + \'" type="text" placeholder="输入回答...回车发送" onkeydown="if(event.key===\'Enter\')submitAnswer(' + q.id + ')" style="flex:1;padding:6px 8px;border-radius:6px;border:1px solid rgba(139,148,158,.2);background:rgba(0,0,0,.2);color:#e6edf3;font-size:12px;outline:none">\';'

if old in html:
    html = html.replace(old, new)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print('Added Enter key handler')
else:
    print('Pattern not found')
    idx = html.find('ansInput')
    if idx > 0:
        print(repr(html[idx:idx+200]))
