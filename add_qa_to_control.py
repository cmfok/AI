# -*- coding: utf-8 -*-
import re

path = '/home/ubuntu/share-ppt/control.html'

with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

if 'qa-section' in c or 'qlist' in c:
    print('QA section already exists, skipping')
else:
    qa_html = '''
<!-- === 观众问答 === -->
<div style="margin-top:12px;border-top:1px solid rgba(139,148,158,.12);padding-top:10px">
  <div style="display:flex;gap:6px;align-items:center;margin-bottom:8px">
    <span style="font-size:11px;color:#8b949e;font-weight:600">💬 观众问题</span>
    <span style="font-size:10px;color:#484f58" id="qCount">0</span>
  </div>
  <div id="qlist" style="max-height:40vh;overflow-y:auto"></div>
</div>
<script>
// -- QA 问答系统 --
function goToSlide(n){
  fetch('/api/control/go',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({slide:n})}).catch(function(){});
}
function loadQuestions(){
  fetch('/api/questions').then(function(r){return r.json();}).then(function(d){
    var bp = d.by_page || {};
    var total = 0;
    for(var k in bp) total += bp[k].length;
    document.getElementById('qCount').textContent = total + '个';
    var keys = Object.keys(bp).sort(function(a,b){return parseInt(a)-parseInt(b);});
    var html = '';
    if(total === 0){
      html = '<div style="font-size:12px;color:#484f58;text-align:center;padding:16px">暂无问题</div>';
    } else {
      for(var ki=0;ki<keys.length;ki++){
        var page = keys[ki];
        var qs = bp[page];
        for(var qi=0;qi<qs.length;qi++){
          var q = qs[qi];
          html += '<div style="background:rgba(255,255,255,.03);border:1px solid rgba(139,148,158,.1);border-radius:8px;padding:10px;margin-bottom:6px;font-size:13px">';
          html += '<div style="display:flex;gap:4px;margin-bottom:4px">';
          html += '<span style="color:#484f58">' + (q.name||'匿名') + '</span>';
          html += '<span style="color:#0071e3;font-size:11px;background:rgba(0,113,227,.1);padding:1px 6px;border-radius:4px">P' + (q.page||'?') + '</span>';
          html += '</div>';
          html += '<div style="color:#e6edf3;line-height:1.5;margin-bottom:4px">' + q.question + '</div>';
          if(q.deeper){
            html += '<div style="font-size:12px;color:#8b949e;padding:6px 8px;background:rgba(0,0,0,.15);border-radius:6px;margin-bottom:4px">💡 ' + q.deeper + '</div>';
          }
          html += '<div style="display:flex;gap:4px">';
          html += '<button class="btn" onclick="goToSlide(' + (q.page||1) + ')" style="font-size:11px;padding:3px 10px">跳转</button>';
          html += '</div>';
          html += '</div>';
        }
      }
    }
    document.getElementById('qlist').innerHTML = html;
  }).catch(function(){});
}
loadQuestions();
setInterval(loadQuestions, 5000);
</script>
'''
    c = c.replace('<div class="bottom-nav">', qa_html + '<div class="bottom-nav">')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    print('Injected QA section into control.html')
