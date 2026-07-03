# -*- coding: utf-8 -*-
"""Add voice-answer overlay and BC handler to all display pages"""

import os

# The CSS + JS to inject
overlay_code = '''
<style>
/* AI回答浮层 */
#aiAnswerOverlay{position:fixed;bottom:30px;right:30px;max-width:420px;background:rgba(0,0,0,.92);border:1px solid rgba(126,231,135,.3);border-radius:14px;padding:16px 18px;z-index:9999;backdrop-filter:blur(12px);box-shadow:0 8px 40px rgba(0,0,0,.5);transform:translateY(20px);opacity:0;transition:all .4s cubic-bezier(.2,0,.3,1);pointer-events:none}
#aiAnswerOverlay.show{transform:translateY(0);opacity:1;pointer-events:auto}
#aiAnswerOverlay .aao-label{font-size:10px;color:#7ee787;font-weight:600;letter-spacing:.5px;margin-bottom:6px}
#aiAnswerOverlay .aao-text{font-size:14px;line-height:1.7;color:#e6edf3}
#aiAnswerOverlay .aao-close{position:absolute;top:8px;right:10px;font-size:16px;color:#484f58;cursor:pointer;border:none;background:none;padding:2px 6px;border-radius:4px}
#aiAnswerOverlay .aao-close:hover{color:#e6edf3;background:rgba(255,255,255,.06)}
</style>
<div id="aiAnswerOverlay">
  <button class="aao-close" onclick="document.getElementById('aiAnswerOverlay').classList.remove('show')">\u2716</button>
  <div class="aao-label">\U0001F916 AI \u56DE\u7B54</div>
  <div class="aao-text" id="aiAnswerText"></div>
</div>
<script>
// \u63a5\u53d7 voice-answer \u6d88\u606f\u5e76\u663e\u793a\u6d6e\u5c42
document.addEventListener('DOMContentLoaded', function(){
  setTimeout(function(){
    try{
      var bc = new BroadcastChannel('ppt-ctrl');
      var origHandler = bc.onmessage;
      bc.onmessage = function(e){
        if(origHandler) origHandler(e);
        var d = e.data;
        if(d && d.type === 'voice-answer' && d.answer){
          var el = document.getElementById('aiAnswerText');
          var box = document.getElementById('aiAnswerOverlay');
          if(el && box){
            el.textContent = d.answer;
            box.classList.add('show');
            setTimeout(function(){ box.classList.remove('show'); }, 12000);
          }
        }
      };
    }catch(e){}
  }, 500);
  setTimeout(function(){
    try{
      var bc3 = new BroadcastChannel('ai3-control');
      bc3.onmessage = function(e){
        var d = e.data;
        if(d && d.type === 'voice-answer' && d.answer){
          var el = document.getElementById('aiAnswerText');
          var box = document.getElementById('aiAnswerOverlay');
          if(el && box){
            el.textContent = d.answer;
            box.classList.add('show');
            setTimeout(function(){ box.classList.remove('show'); }, 12000);
          }
        }
      };
    }catch(e){}
  }, 600);
});
</script>
'''

pages = [
    '/home/ubuntu/share-ppt/ai/1/index.html',
    '/home/ubuntu/share-ppt/ai/2/index.html',
    '/home/ubuntu/share-ppt/ai/3/index.html',
    '/home/ubuntu/share-ppt/index.html',
]

for page in pages:
    if not os.path.exists(page):
        print(f'SKIP: {page} not found')
        continue
    
    with open(page, 'r', encoding='utf-8') as f:
        html = f.read()
    
    if 'aiAnswerOverlay' in html:
        print(f'OK: {page} already has overlay')
        continue
    
    # Inject before </body>
    if '</body>' in html:
        html = html.replace('</body>', overlay_code + '\n</body>')
        with open(page, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'OK: Injected overlay into {page}')
    else:
        print(f'ERR: {page} missing </body>')

# Also check ai-4 path
page4 = '/home/ubuntu/share-ppt/ai-4/index.html'
if os.path.exists(page4):
    with open(page4, 'r', encoding='utf-8') as f:
        html = f.read()
    if 'aiAnswerOverlay' not in html:
        if '</body>' in html:
            html = html.replace('</body>', overlay_code + '\n</body>')
            with open(page4, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f'OK: Injected overlay into {page4}')
        else:
            print(f'ERR: {page4} missing </body>')
    else:
        print(f'OK: {page4} already has overlay')

print('Done')
