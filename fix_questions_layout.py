# -*- coding: utf-8 -*-
"""Rewrite the questions section with clean layout"""

path = '/home/ubuntu/share-ppt/control.html'

with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Find the tabQuestions section
old_start = '<div class="tab-content" id="tabQuestions">'
idx_start = c.find(old_start)
idx_end = c.find('<div class="bottom-nav">', idx_start)

if idx_start > 0 and idx_end > idx_start:
    print(f'Found tabQuestions section: {idx_start} to {idx_end}')
    
    new_section = '''<div class="tab-content" id="tabQuestions" style="padding:14px">
  <div style="display:flex;gap:6px;align-items:center;margin-bottom:10px">
    <span style="font-size:12px;color:#8b949e;font-weight:600">\U0001F4AC 观众问题</span>
    <span style="font-size:10px;color:#484f58;padding:2px 8px;background:rgba(139,148,158,.08);border-radius:8px" id="qCount">0</span>
  </div>
  <div id="qlist" style="min-height:100px"></div>
</div>
<script>
function goToSlide(n){
  fetch('/api/control/go',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({slide:n})}).catch(function(){});
}
var _qdata = {};
function aiAnswer(id){
  var ansBox = document.getElementById('ans' + id);
  if(!ansBox) return;
  var qi = _qdata[id] || {}; var qtext = qi.q || ''; var qpage = qi.p || 1;
  ansBox.style.display = 'block';
  ansBox.innerHTML = '<div style="text-align:center;padding:8px;color:#8b949e;font-size:12px">\U0001F914 AI\u601D\u8003\u4E2D...</div>';
  fetch('/api/questions/ai-answer', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({id:id, question:qtext})
  }).then(function(r){return r.json();}).then(function(d){
    if(d.ok){
      var txt = d.answer.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
      ansBox.innerHTML = '<div style="font-size:12px;color:#7ee787;padding:8px;background:rgba(0,0,0,.15);border-radius:6px">\U0001F916 ' + txt + '</div>';
      try{ new BroadcastChannel('ppt-ctrl').postMessage({type:'voice-answer',question:'',answer:d.answer,slide:qpage}); }catch(e){}
      try{ new BroadcastChannel('ai3-control').postMessage({type:'voice-answer',question:'',answer:d.answer,slide:qpage}); }catch(e){}
    } else {
      ansBox.innerHTML = '<div style="font-size:12px;color:#e53e3e;padding:8px">\u274C ' + (d.error||'回答失败') + '</div>';
    }
  }).catch(function(){
    ansBox.innerHTML = '<div style="font-size:12px;color:#e53e3e;padding:8px">\u274C \u7F51\u7EDC\u9519\u8BEF</div>';
  });
}
function loadQuestions(){
  var list = document.getElementById('qlist');
  if(!list) return;
  list.innerHTML = '<div style="text-align:center;padding:20px;color:#484f58">\U0001F4E1 加载中...</div>';
  fetch('/api/questions').then(function(r){
    if(!r.ok) throw new Error('HTTP '+r.status);
    return r.json();
  }).then(function(d){
    var bp = d.by_page || {};
    var total = 0;
    for(var k in bp) total += bp[k].length;
    var cnt = document.getElementById('qCount');
    if(cnt) cnt.textContent = total;
    if(total === 0){
      list.innerHTML = '<div style="text-align:center;padding:30px;color:#484f58;font-size:13px">\U0001F4AC 暂无问题</div>';
      return;
    }
    var keys = Object.keys(bp).sort(function(a,b){return a-b;});
    var h = '';
    for(var ki=0;ki<keys.length;ki++){
      var page = keys[ki];
      var qs = bp[page];
      for(var qi=0;qi<qs.length;qi++){
        var q = qs[qi];
        _qdata[q.id] = {q:q.question, p:q.page||1};
        h += '<div style="background:rgba(255,255,255,.03);border:1px solid rgba(139,148,158,.1);border-radius:8px;padding:10px 12px;margin-bottom:6px">';
        h += '<div style="display:flex;gap:6px;margin-bottom:4px;align-items:center">';
        h += '<span style="color:#8b949e;font-size:12px">\U0001F464 ' + (q.name||'匿名') + '</span>';
        h += '<span style="color:#58a6ff;font-size:10px;background:rgba(0,113,227,.1);padding:1px 6px;border-radius:4px;font-weight:500">P' + (q.page||'?') + '</span>';
        h += '</div>';
        h += '<div style="color:#e6edf3;line-height:1.6;margin-bottom:6px;font-size:13px">' + q.question + '</div>';
        if(q.deeper){
          h += '<div style="font-size:11px;color:#8b949e;padding:6px 8px;background:rgba(0,0,0,.15);border-radius:6px;margin-bottom:6px">\U0001F4A1 ' + q.deeper + '</div>';
        }
        h += '<div style="display:flex;gap:4px;flex-wrap:wrap">';
        h += '<button class="btn" onclick="goToSlide(' + (q.page||1) + ')" style="font-size:11px;padding:4px 10px">\U0001F519 跳转</button>';
        h += '<button class="btn" onclick="aiAnswer(' + q.id + ')" style="font-size:11px;padding:4px 10px">\U0001F916 AI回答</button>';
        h += '</div>';
        h += '<div id="ans' + q.id + '" style="display:none;margin-top:4px"></div>';
        h += '</div>';
      }
    }
    list.innerHTML = h;
  }).catch(function(e){
    console.error('Q&A error:', e);
    list.innerHTML = '<div style="text-align:center;padding:20px;color:#e53e3e;font-size:13px">\u274C 加载失败，请刷新</div>';
  });
}
loadQuestions();
setInterval(loadQuestions, 5000);
</script>'''
    
    c = c[:idx_start] + new_section + c[idx_end:]
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    print('Replaced questions section with clean layout')
else:
    print('Could not find section boundaries')
    print(f'idx_start={idx_start}, idx_end={idx_end}')
