# -*- coding: utf-8 -*-
"""Fix: add API answer posting to control page + display page polling"""

import re

# --- Step 1: Update control page ---
path = '/home/ubuntu/share-ppt/control.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Add API post before the BroadcastChannel post
old_bc = "      try{ new BroadcastChannel('ppt-ctrl').postMessage({type:'voice-answer',question:qi.q,answer:d.answer,slide:qi.p}); }catch(e){}"
new_bc = "      fetch('/api/control/go',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({slide:qi.p,answer:d.answer,answer_question:qi.q,answer_slide:qi.p})}).catch(function(){});\n      try{ new BroadcastChannel('ppt-ctrl').postMessage({type:'voice-answer',question:qi.q,answer:d.answer,slide:qi.p}); }catch(e){}"

if old_bc in c:
    c = c.replace(old_bc, new_bc)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    print('Updated control page answer broadcast')
else:
    print('Control: pattern not found')
    idx = c.find('ppt-ctrl')
    if idx > 0:
        print(repr(c[idx-50:idx+100]))

# --- Step 2: Update display pages to poll for answers ---
pages = [
    '/home/ubuntu/share-ppt/ai/1/index.html',
    '/home/ubuntu/share-ppt/ai/2/index.html',
    '/home/ubuntu/share-ppt/ai/3/index.html',
    '/home/ubuntu/share-ppt/index.html',
    '/home/ubuntu/share-ppt/ai-4/index.html',
]

# Polling code to add (injects into the existing setInterval polling)
answer_poll = '''
  // Check for AI answers from control
  var _lastAnsId = 0;
  setInterval(function(){
    fetch('/api/control/current').then(function(r){return r.json();}).then(function(d){
      if(d.answer && d.answer_slide && d.answer_slide !== _lastAnsId){
        _lastAnsId = d.answer_slide;
        var box = document.getElementById('aiAnswerOverlay');
        var txt = document.getElementById('aiAnswerText');
        var qel = document.getElementById('aiAnswerQ');
        if(box && txt){
          if(qel && d.answer_question) qel.textContent = d.answer_question;
          else if(qel) qel.style.display = 'none';
          txt.textContent = d.answer;
          box.classList.add('show');
          setTimeout(function(){ box.classList.remove('show'); }, 15000);
        }
        // Navigate
        if(d.answer_slide){
          var s = d.answer_slide;
          window.location.hash = '#/' + s;
          if(typeof go === 'function') setTimeout(function(){ go(s - 1); }, 200);
          if(window.__goSlide) setTimeout(function(){ window.__goSlide(s - 1); }, 200);
        }
        // Clear the answer so it doesn't show again
        fetch('/api/control/go',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({slide:d.slide||1,answer:'',answer_question:'',answer_slide:0})}).catch(function(){});
      }
    }).catch(function(){});
  }, 2000);
'''

for page in pages:
    with open(page, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Check if answer polling already exists
    if '_lastAnsId' in html:
        print(f'SKIP: {page} already has answer polling')
        continue
    
    # Inject the polling code before </body>
    if '</body>' in html:
        html = html.replace('</body>', '<script>' + answer_poll + '</script>\n</body>')
        with open(page, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'OK: Injected answer polling into {page}')
    else:
        print(f'ERR: {page} missing </body>')
