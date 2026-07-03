# -*- coding: utf-8 -*-
"""Final fix: persistent answers + matching padding"""

path = '/home/ubuntu/share-ppt/control.html'

with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Find the tabQuestions section
idx_start = c.find('<div class="tab-content" id="tabQuestions"')
idx_end = c.find('<div class="bottom-nav">', idx_start)

if idx_start > 0 and idx_end > idx_start:
    new_section = '''<div class="tab-content" id="tabQuestions" style="padding:16px">
  <div style="display:flex;gap:6px;align-items:center;margin-bottom:10px">
    <span style="font-size:12px;color:#8b949e;font-weight:600">\U0001F4AC 观众问题</span>
    <span style="font-size:10px;color:#484f58;padding:2px 8px;background:rgba(139,148,158,.08);border-radius:8px" id="qCount">0</span>
  </div>
  <div id="qlist" style="min-height:100px"></div>
</div>
<script>
var _qdata = {};
function goToSlide(n){
  fetch('/api/control/go',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({slide:n})}).catch(function(){});
}
function aiAnswer(id){
  var qi = _qdata[id];
  if(!qi) return;
  qi.loading = true;
  qi.answer = '';
  renderQuestions();
  fetch('/api/questions/ai-answer', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({id:id, question:qi.q})
  }).then(function(r){return r.json();}).then(function(d){
    if(d.ok){
      qi.answer = d.answer;
      qi.loading = false;
      renderQuestions();
      try{ new BroadcastChannel('ppt-ctrl').postMessage({type:'voice-answer',question:qi.q,answer:d.answer,slide:qi.p}); }catch(e){}
      try{ new BroadcastChannel('ai3-control').postMessage({type:'voice-answer',question:qi.q,answer:d.answer,slide:qi.p}); }catch(e){}
    } else {
      qi.error = d.error || '\u56DE\u7B54\u5931\u8D25';
      qi.loading = false;
      renderQuestions();
    }
  }).catch(function(){
    qi.error = '\u7F51\u7EDC\u9519\u8BEF';
    qi.loading = false;
    renderQuestions();
  });
}
function loadQuestions(){
  fetch('/api/questions').then(function(r){
    if(!r.ok) throw new Error('HTTP '+r.status);
    return r.json();
  }).then(function(d){
    var bp = d.by_page || {};
    for(var k in bp){
      var qs = bp[k];
      for(var i=0;i<qs.length;i++){
        var q = qs[i];
        if(!_qdata[q.id]) _qdata[q.id] = {q:q.question, p:q.page||1, answer:'', loading:false, error:'', n:q.name||'匿名'};
        else {
          _qdata[q.id].q = q.question;
          _qdata[q.id].p = q.page||1;
          _qdata[q.id].n = q.name||'匿名';
        }
      }
    }
    renderQuestions();
  }).catch(function(e){
    console.error('Q&A error:', e);
    var l = document.getElementById('qlist');
    if(l) l.innerHTML = '<div style="text-align:center;padding:30px;color:#e53e3e">\u274C \u52A0\u8F7D\u5931\u8D25</div>';
  });
}
function renderQuestions(){
  var list = document.getElementById('qlist');
  if(!list) return;
  var ids = Object.keys(_qdata);
  var total = ids.length;
  var cnt = document.getElementById('qCount');
  if(cnt) cnt.textContent = total;
  if(total === 0){
    list.innerHTML = '<div style="text-align:center;padding:30px;color:#484f58;font-size:13px">\U0001F4AC \u6682\u65E0\u95EE\u9898</div>';
    return;
  }
  var h = '';
  for(var i=0;i<ids.length;i++){
    var id = ids[i];
    var qi = _qdata[id];
    h += '<div style="background:rgba(255,255,255,.03);border:1px solid rgba(139,148,158,.1);border-radius:8px;padding:10px 12px;margin-bottom:6px">';
    h += '<div style="display:flex;gap:6px;margin-bottom:4px;align-items:center">';
    h += '<span style="color:#8b949e;font-size:12px">\U0001F464 ' + (qi.n||'匿名') + '</span>';
    h += '<span style="color:#58a6ff;font-size:10px;background:rgba(0,113,227,.1);padding:1px 6px;border-radius:4px;font-weight:500">P' + (qi.p||'?') + '</span>';
    h += '</div>';
    h += '<div style="color:#e6edf3;line-height:1.6;margin-bottom:6px;font-size:13px">' + qi.q + '</div>';
    if(qi.answer){
      h += '<div style="font-size:12px;color:#7ee787;padding:8px;background:rgba(0,0,0,.15);border-radius:6px;margin-bottom:6px">\U0001F916 ' + qi.answer + '</div>';
    } else if(qi.loading){
      h += '<div style="font-size:12px;color:#8b949e;padding:8px;text-align:center">\U0001F914 AI\u601D\u8003\u4E2D...</div>';
    } else if(qi.error){
      h += '<div style="font-size:12px;color:#e53e3e;padding:8px">\u274C ' + qi.error + '</div>';
    }
    h += '<div style="display:flex;gap:4px">';
    h += '<button class="btn" onclick="goToSlide(' + (qi.p||1) + ')" style="font-size:11px;padding:4px 10px">\U0001F519 \u8DF3\u8F6C</button>';
    if(!qi.answer && !qi.loading){
      h += '<button class="btn" onclick="aiAnswer(' + id + ')" style="font-size:11px;padding:4px 10px">\U0001F916 AI\u56DE\u7B54</button>';
    }
    h += '</div>';
    h += '</div>';
  }
  list.innerHTML = h;
}
loadQuestions();
setInterval(loadQuestions, 10000);
</script>'''
    
    c = c[:idx_start] + new_section + c[idx_end:]
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    print('Replaced with persistent answer + matching padding')
else:
    print('Could not find section')
