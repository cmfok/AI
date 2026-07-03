# -*- coding: utf-8 -*-
"""Fix answer polling: clear stale answer + improve detection"""

pages = [
    '/home/ubuntu/share-ppt/ai/1/index.html',
    '/home/ubuntu/share-ppt/ai/2/index.html',
    '/home/ubuntu/share-ppt/ai/3/index.html',
    '/home/ubuntu/share-ppt/index.html',
    '/home/ubuntu/share-ppt/ai-4/index.html',
]

# Find and replace the answer polling block
old_poll = '''  // Check for AI answers from control
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
  }, 2000);'''

new_poll = '''  // Check for AI answers from control API
  var _lastAnsId = Date.now();
  setInterval(function(){
    fetch('/api/control/current').then(function(r){return r.json();}).then(function(d){
      if(d.answer && d.answer_slide && d.answer_slide > 0 && d.answer_slide !== _lastAnsId){
        _lastAnsId = d.answer_slide;
        var box = document.getElementById('aiAnswerOverlay');
        var txt = document.getElementById('aiAnswerText');
        var qel = document.getElementById('aiAnswerQ');
        if(box && txt){
          if(qel && d.answer_question && d.answer_question.length > 0){
            qel.textContent = d.answer_question;
            qel.style.display = '';
          } else if(qel) qel.style.display = 'none';
          txt.textContent = d.answer;
          box.classList.add('show');
          setTimeout(function(){ box.classList.remove('show'); }, 15000);
        }
        // Navigate to the slide
        if(d.answer_slide > 0){
          var s = d.answer_slide;
          window.location.hash = '#/' + s;
          if(typeof go === 'function') setTimeout(function(){ go(s - 1); }, 300);
          if(window.__goSlide) setTimeout(function(){ window.__goSlide(s - 1); }, 300);
        }
        // Clear answer from server
        fetch('/api/control/go',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({slide:d.slide||1,answer:'',answer_question:'',answer_slide:0})}).catch(function(){});
      }
    }).catch(function(){});
  }, 2000);'''

for page in pages:
    with open(page, 'r', encoding='utf-8') as f:
        html = f.read()
    
    if old_poll in html:
        html = html.replace(old_poll, new_poll)
        with open(page, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'Updated: {page}')
    else:
        # Check if there's any answer polling
        if '_lastAnsId' in html:
            print(f'SKIP (different format): {page}')
        else:
            print(f'MISSING polling: {page}')
