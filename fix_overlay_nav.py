# -*- coding: utf-8 -*-
"""Fix overlay navigation and show question+answer"""

pages = [
    '/home/ubuntu/share-ppt/ai/1/index.html',
    '/home/ubuntu/share-ppt/ai/2/index.html',
    '/home/ubuntu/share-ppt/ai/3/index.html',
    '/home/ubuntu/share-ppt/index.html',
    '/home/ubuntu/share-ppt/ai-4/index.html',
]

new_overlay = '''<style>
/* AI回答浮层 */
#aiAnswerOverlay{position:fixed;bottom:30px;right:30px;max-width:440px;background:rgba(0,0,0,.92);border:1px solid rgba(126,231,135,.3);border-radius:14px;padding:14px 16px;z-index:9999;backdrop-filter:blur(12px);box-shadow:0 8px 40px rgba(0,0,0,.5);transform:translateY(20px);opacity:0;transition:all .4s cubic-bezier(.2,0,.3,1);pointer-events:none}
#aiAnswerOverlay.show{transform:translateY(0);opacity:1;pointer-events:auto}
#aiAnswerOverlay .aao-label{font-size:10px;color:#7ee787;font-weight:600;letter-spacing:.5px;margin-bottom:4px}
#aiAnswerOverlay .aao-q{font-size:13px;color:#e6edf3;line-height:1.5;margin-bottom:6px;padding-bottom:6px;border-bottom:1px solid rgba(255,255,255,.08)}
#aiAnswerOverlay .aao-a{font-size:14px;line-height:1.7;color:#d4d4d4}
#aiAnswerOverlay .aao-close{position:absolute;top:8px;right:10px;font-size:16px;color:#484f58;cursor:pointer;border:none;background:none;padding:2px 6px;border-radius:4px;line-height:1}
#aiAnswerOverlay .aao-close:hover{color:#e6edf3;background:rgba(255,255,255,.06)}
</style>
<div id="aiAnswerOverlay">
  <button class="aao-close" onclick="document.getElementById('aiAnswerOverlay').classList.remove('show')">\u2716</button>
  <div class="aao-label">\U0001F916 AI \u56DE\u7B54</div>
  <div class="aao-q" id="aiAnswerQ"></div>
  <div class="aao-a" id="aiAnswerText"></div>
</div>
<script>
// Receive voice-answer and show overlay + navigate
document.addEventListener('DOMContentLoaded', function(){
  function setupBC(name, delay){
    setTimeout(function(){
      try{
        var bc = new BroadcastChannel(name);
        bc.onmessage = function(e){
          var d = e.data;
          if(d && d.type === 'voice-answer' && d.answer){
            // Show overlay
            var box = document.getElementById('aiAnswerOverlay');
            var txt = document.getElementById('aiAnswerText');
            var qel = document.getElementById('aiAnswerQ');
            if(box && txt){
              if(qel && d.question) qel.textContent = d.question;
              else if(qel) qel.style.display = 'none';
              txt.textContent = d.answer;
              box.classList.add('show');
              setTimeout(function(){ box.classList.remove('show'); }, 15000);
            }
            // Navigate to slide
            if(d.slide && d.slide > 0){
              var s = d.slide;
              // Try all navigation methods (one will work per page)
              window.location.hash = '#/' + s;
              if(typeof go === 'function') setTimeout(function(){ go(s - 1); }, 100);
              if(window.__goSlide) setTimeout(function(){ window.__goSlide(s - 1); }, 100);
            }
          }
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
        
        # Remove old overlay if exists
        if 'aiAnswerOverlay' in html:
            # Find everything from the old <style> to the closing </script> of overlay
            old_start = html.find('<style>\n/* AI回答浮层 */')
            if old_start == -1:
                old_start = html.find('<style>\n/* AI回答浮层')
            if old_start == -1:
                old_start = html.find('/* AI回答浮层 */')
                if old_start > 0:
                    # Find the parent style tag
                    while old_start > 0 and html[old_start] != '<':
                        old_start -= 1
            
            if old_start > 0:
                old_end = html.find('</script>\n</body>', old_start)
                if old_end > old_start:
                    old_end += len('</script>')
                    html = html[:old_start] + html[old_end:]
                    print(f'Removed old overlay in {page}')
                else:
                    print(f'Could not find end of old overlay in {page}')
            else:
                print(f'Could not find start of old overlay in {page}')
        
        # Inject new overlay before </body>
        if '</body>' in html:
            html = html.replace('</body>', new_overlay + '\n</body>')
            with open(page, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f'Injected new overlay into {page}')
        else:
            print(f'Missing </body> in {page}')
    except Exception as e:
        print(f'Error with {page}: {e}')
