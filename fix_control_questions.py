# -*- coding: utf-8 -*-
"""Debug and fix the control page questions display"""
import re

path = '/home/ubuntu/share-ppt/control.html'

with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Check if loadQuestions function exists and has the right structure
if 'function loadQuestions' not in html:
    print('ERROR: loadQuestions function not found')
else:
    print('OK: loadQuestions function exists')

# 2. Check if the API URL is correct
if "/api/questions" in html:
    print('OK: /api/questions endpoint referenced')
else:
    print('ERROR: /api/questions not referenced')

# 3. Check the catch handler
if 'catch(function(e)' in html:
    print('Has error-catching catch handler')
else:
    print('Has EMPTY catch handler (errors silenced)')

# 4. The REAL fix: The loadQuestions script is inside tabQuestions div which starts hidden.
#    The script extracts content from the API and sets innerHTML.
#    But there might be an issue with how the HTML is generated - let me check for 
#    unescaped content that could break innerHTML

# Find the loadQuestions function
m = re.search(r'function loadQuestions\(\)\s*\{.*?setInterval\(loadQuestions,\s*\d+\)', html, re.DOTALL)
if m:
    func_text = m.group()
    print(f'\nloadQuestions function: {len(func_text)} chars')
    
    # Check for potential issues in the template strings
    # Count proper HTML generation
    div_opens = func_text.count("'<div")
    div_closes = func_text.count("</div>'")
    print(f'Template div opens: {div_opens}')
    print(f'Template div closes: {div_closes}')
    
    if div_opens != div_closes:
        print(f'WARNING: Div imbalance in template!')
    
    # Check if there's a qlist fallback display
    if '暂无问题' in func_text:
        print('Has empty state text')
    
    # Check if the deeper field might cause issues
    for line in func_text.split('\n'):
        if 'deeper' in line:
            print(f'Deeper field line: {line.strip()[:100]}')

# 5. Let me also check the full API response structure
# The loadQuestions function uses d.by_page and iterates over it with for-in
# That should be fine for a plain object

# 6. One potential issue: the script is inside tabQuestions div which has display:none
# When the page loads, the script still runs but the DOM elements it references exist.
# Let me verify qlist exists before the script:
qlist_before = html.find('<div id="qlist"')
script_before = html.find('<script>', qlist_before)
if qlist_before > 0 and script_before > qlist_before:
    print('\nOK: qlist div exists before script')
else:
    print('\nWARNING: qlist may not exist before script')

print('\n--- Analysis complete ---')
