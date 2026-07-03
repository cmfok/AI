# -*- coding: utf-8 -*-
import re

path = '/home/ubuntu/share-ppt/control.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

m = re.search(r'function loadQuestions.*?setInterval\(loadQuestions, 5000\)', html, re.DOTALL)
if m:
    text = m.group()
    # Check single and double quote balance
    sq = text.count("'")
    dq = text.count('"')
    print(f'Single quotes: {sq} (should be even)')
    print(f'Double quotes: {dq} (should be even)')
    
    # Check the onkeydown line specifically
    for line in text.split('\n'):
        if 'onkeydown' in line:
            print(f'\nFound onkeydown line:')
            print(f'  {line.strip()[:150]}')
            # Check quote balance in this line
            sq_line = line.count("'")
            dq_line = line.count('"')
            print(f'  Single quotes in line: {sq_line}')
            print(f'  Double quotes in line: {dq_line}')
            # Check escaped quotes
            esq = line.count("\\'")
            edq = line.count('\\"')
            print(f'  Escaped single: {esq}, Escaped double: {edq}')
else:
    print('Could not find loadQuestions function')
