# -*- coding: utf-8 -*-
"""Update control page to pass slide info in broadcast"""

path = '/home/ubuntu/share-ppt/control.html'

with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Update _qdata to also store page number
old1 = "        _qdata[q.id] = q.question;"
new1 = "        _qdata[q.id] = {q:q.question, p:q.page||1};"
if old1 in c:
    c = c.replace(old1, new1)
    print('Updated _qdata')
else:
    print('_qdata assignment not found')

# Update aiAnswer to use page from _qdata
old2 = "  var qtext = _qdata[id] || '';"
new2 = "  var qi = _qdata[id] || {}; var qtext = qi.q || ''; var qpage = qi.p || 1;"
if old2 in c:
    c = c.replace(old2, new2)
    print('Updated aiAnswer variable extraction')
else:
    print('aiAnswer variable extraction not found')

# Update broadcast to include slide
old3 = "try{ new BroadcastChannel('ppt-ctrl').postMessage({type:'voice-answer',question:'',answer:d.answer,slide:0}); }catch(e){}"
new3 = "try{ new BroadcastChannel('ppt-ctrl').postMessage({type:'voice-answer',question:'',answer:d.answer,slide:qpage}); }catch(e){}"
if old3 in c:
    c = c.replace(old3, new3)
    print('Updated ppt-ctrl broadcast')
else:
    print('ppt-ctrl broadcast not found')
    idx = c.find('ppt-ctrl')
    if idx > 0:
        print('  found at', idx, repr(c[idx:idx+100]))

old4 = "try{ new BroadcastChannel('ai3-control').postMessage({type:'voice-answer',question:'',answer:d.answer,slide:0}); }catch(e){}"
new4 = "try{ new BroadcastChannel('ai3-control').postMessage({type:'voice-answer',question:'',answer:d.answer,slide:qpage}); }catch(e){}"
if old4 in c:
    c = c.replace(old4, new4)
    print('Updated ai3-control broadcast')
else:
    print('ai3-control broadcast not found')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('Done')
