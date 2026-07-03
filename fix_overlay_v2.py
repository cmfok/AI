# -*- coding: utf-8 -*-
"""Fix overlay: dedup messages + better positioning"""

import re

pages = [
    '/home/ubuntu/share-ppt/ai/1/index.html',
    '/home/ubuntu/share-ppt/ai/2/index.html',
    '/home/ubuntu/share-ppt/ai/3/index.html',
    '/home/ubuntu/share-ppt/index.html',
    '/home/ubuntu/share-ppt/ai-4/index.html',
]

new_overlay = '''<style>
#aiAnswerOverlay{position:fixed;bottom:20px;left:50%;transform:translateX(-50%) translateY(30px);max-width:90vw;width:560px;background:rgba(0,0,0,.92);border:1px solid rgba(126,231,135,.3);border-radius:14px;padding:14px 16px;z-index:9999;backdrop-filter:blur(12px);box-shadow:0 8px 40px rgba(0,0,0,.5);opacity:0;transition:all .4s cubic-bezier(.2,0,.3,1);pointer-events:none;display:block}
#aiAnswerOverlay.show{opacity:1;transform:translateX(-50%) translateY(0);pointer-events:auto}
#aiAnswerOverlay .aao-label{font-size:10px;color:#7ee787;font-weight:600;letter-spacing:.5px;margin-bottom:4px}
#aiAnswerOverlay .aao-q{font-size:13px;color:#e6edf3;line-height:1.5;margin-bottom:6px;padding-bottom:6px;border-bottom:1px solid rgba(255,255,255,.08)}
#aiAnswerOverlay .aao-a{font-size:14px;line-height:1.7;color:#d4d4d4}
#aiAnswerOverlay .aao-close{position:absolute;top:8px;right:10px;font-size:14px;color:#484f58;cursor:pointer;border:none;background:none;padding:2px 5px;border-radius:4px;line-height:1}
#aiAnswerOverlay .aao-close:hover{color:#e6edf3;background:rgba(255,255,255,.06)}
</style>
<div id="aiAnswerOverlay">
  <button class="aao-close" onclick="document.getElementById('aiAnswerOverlay').classList.remove('show')">&times;</button>
  <div class="aao-label">\U0001F916 AI \u56DE\u7B54</div>
  <div class="aao-q" id="aiAnswerQ"></div>
  <div class="aao-a" id="aiAnswerText"></div>
</div>
<script>
// AI\u56DE\u7B54\u6d6e\u5c42 + \u5bfc\u822a
document.addEventListener('DOMContentLoaded', function(){
  var _lastMsg = 0;
  function showAnswer(d){
    var now = Date.now();
    if(now - _lastMsg < 2000) return; // \u9632\u6b62\u91cd\u590d\u89e6\u53d1
    _lastMsg = now;
    var box = document.getElementById('aiAnswerOverlay');
    var txt = document.getElementById('aiAnswerText');
    var qel = document.getElementById('aiAnswerQ');
    if(!box || !txt) return;
    if(qel && d.question) qel.textContent = d.question;
    else if(qel) qel.style.display = 'none';
    txt.textContent = d.answer || '';
    box.classList.add('show');
    setTimeout(function(){ box.classList.remove('show'); }, 15000);
    // \u5bfc\u822a
    if(d.slide && d.slide > 0){
      var s = d.slide;
      window.location.hash = '#/' + s;
      if(typeof go === 'function') setTimeout(function(){ go(s - 1); }, 200);
      if(window.__goSlide) setTimeout(function(){ window.__goSlide(s - 1); }, 200);
    }
  }
  function setupBC(name, delay){
    setTimeout(function(){
      try{
        var bc = new BroadcastChannel(name);
        bc.onmessage = function(e){
          var d = e.data;
          if(d && d.type === 'voice-answer' && d.answer) showAnswer(d);
        };
      }catch(e){}
    }, delay);
  }
  setupBC('ppt-ctrl', 500);
  setupBC('ai3-control', 600);
});
</script>'''

for page in pages:
    try:
        with open(page, 'r', encoding='utf-8') as f:
            html = f.read()
        
        # Remove ALL previous overlay CSS blocks
        html = re.sub(r'<style>[\s\S]*?aiAnswerOverlay[\s\S]*?</style>', '', html)
        # Remove ALL overlay HTML divs
        html = re.sub(r'<div id="aiAnswerOverlay"[\s\S]*?</div>\s*', '', html)
        # Remove ALL overlay script blocks (both old and new)
        html = re.sub(r'<script>[\s\S]*?voice-answer[\s\S]*?messages[\s\S]*?</script>\s*', '', html, flags=re.IGNORECASE)
        html = re.sub(r'<script>[\s\S]*?AI\u56DE\u7B54\u6d6e\u5c42[\s\S]*?</script>\s*', '', html)
        html = re.sub(r'<script>\s*// Receive voice-answer[\s\S]*?</script>\s*', '', html)
        html = re.sub(r'<script>[\s\S]*?function setupBC[\s\S]*?</script>\s*', '', html)
        
        # Inject new overlay
        html = html.replace('</body>', new_overlay + '\n</body>')
        
        with open(page, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'Fixed: {page}')
    except Exception as e:
        print(f'Error {page}: {e}')
