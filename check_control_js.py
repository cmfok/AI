# -*- coding: utf-8 -*-
import re

path = '/home/ubuntu/share-ppt/control.html'

with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# Find the loadQuestions script
scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
print(f'Found {len(scripts)} inline script blocks')

for i, s in enumerate(scripts):
    if 'loadQuestions' in s:
        print(f'\nScript #{i} (loadQuestions): {len(s)} chars')
        # Find the exact loadQuestions function
        match = re.search(r'function loadQuestions.*?setInterval\(loadQuestions, 5000\)', s, re.DOTALL)
        if match:
            func_text = match.group()
            print(f'Function text ({len(func_text)} chars)')
            # Check for the key parts
            checks = ['fetch(/api/questions)', 'by_page', 'qlist', 'innerHTML', 'qCount']
            for c in checks:
                if c in func_text:
                    print(f'  OK: {c}')
                else:
                    print(f'  MISSING: {c}')
            
            # Check the HTML generation for answers
            if 'ansInput' in func_text:
                print('  Has answer input')
            if 'toggleAnswer' in func_text:
                print('  Has toggleAnswer')
            if 'submitAnswer' in func_text:
                print('  Has submitAnswer')
        else:
            print('Could not find loadQuestions function')
        
        # Check for potential issues
        if '\\n' in func_text:
            print('  WARNING: contains literal \\n')
        if '\\t' in func_text:
            print('  WARNING: contains literal \\t')

print('\n--- Checking for common issues ---')
# Check if the script tags are properly closed
open_scripts = len(re.findall(r'<script>', html))
close_scripts = len(re.findall(r'</script>', html))
print(f'<script> tags: {open_scripts}')
print(f'</script> tags: {close_scripts}')

# Check for unclosed tags in the questions section
qlist_idx = html.find('qlist')
if qlist_idx > 0:
    print(f'\nqlist found at position {qlist_idx}')
    # Check the HTML around it
    section = html[qlist_idx:qlist_idx+2000]
    # Count div openings/closings in the loadQuestions rendered HTML
    div_opens = section.count('<div')
    div_closes = section.count('</div>')
    print(f'div opens in qlist section: {div_opens}')
    print(f'div closes in qlist section: {div_closes}')

print('\nDone')
