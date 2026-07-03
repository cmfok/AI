# -*- coding: utf-8 -*-
"""Update overlay to navigate to slide when receiving voice-answer"""

pages = [
    '/home/ubuntu/share-ppt/ai/1/index.html',
    '/home/ubuntu/share-ppt/ai/2/index.html',
    '/home/ubuntu/share-ppt/ai/3/index.html',
    '/home/ubuntu/share-ppt/index.html',
    '/home/ubuntu/share-ppt/ai-4/index.html',
]

# The new handler code - adds navigation to the slide
new_handler = '''<script>
// Receive voice-answer messages and show overlay + navigate
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
          // Navigate to the relevant slide
          if(d.slide && d.slide > 0){
            if(window.location.hash) window.location.hash = '#/' + d.slide;
            if(typeof go === 'function') go(d.slide - 1);
            if(window.__goSlide) window.__goSlide(d.slide - 1);
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
          if(d.slide && d.slide > 0){
            if(window.location.hash) window.location.hash = '#/' + d.slide;
            if(typeof go === 'function') go(d.slide - 1);
            if(window.__goSlide) window.__goSlide(d.slide - 1);
          }
        }
      };
    }catch(e){}
  }, 600);
});
</script>'''

# Find and replace the old overlay script
old_script_start = '''<script>
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
</script>'''

for page in pages:
    try:
        with open(page, 'r', encoding='utf-8') as f:
            html = f.read()
        
        if old_script_start in html:
            html = html.replace(old_script_start, new_handler)
            with open(page, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f'Updated: {page}')
        else:
            print(f'Old script not found in: {page}')
            # Check if it has the overlay at all
            if 'aiAnswerOverlay' in html:
                print(f'  Has overlay but script format differs')
            else:
                print(f'  No overlay found')
    except Exception as e:
        print(f'Error: {page} - {e}')
