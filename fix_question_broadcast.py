# -*- coding: utf-8 -*-
path = '/home/ubuntu/share-ppt/control.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace("question:'',answer:d.answer,slide:qpage", 'question:qtext,answer:d.answer,slide:qpage')
with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('Fixed question broadcast')
