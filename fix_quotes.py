# -*- coding: utf-8 -*-
"""Fix unescaped single quotes in onkeydown handler"""

path = '/home/ubuntu/share-ppt/control.html'

with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# The problematic pattern: 'Enter' inside a single-quoted JS string
# Current: onkeydown="if(event.key==='Enter')submitAnswer(' + q.id + ')"
# Fixed:   onkeydown="if(event.key===\'Enter\')submitAnswer(' + q.id + ')"

old = "onkeydown=\"if(event.key==='Enter')submitAnswer(' + q.id + ')\""
new = "onkeydown=\"if(event.key===\\'Enter\\')submitAnswer(' + q.id + ')\""

if old in c:
    c = c.replace(old, new)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    print('Fixed unescaped quotes in onkeydown')
else:
    print('Pattern not found')
    # Try to find what's there
    idx = c.find('onkeydown')
    if idx > 0:
        print('Found onkeydown at', idx)
        print(repr(c[idx:idx+120]))
