# -*- coding: utf-8 -*-
"""Rewrite the questions section of control.html with simpler, more robust code"""
import re

path = '/home/ubuntu/share-ppt/control.html'

with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the entire loadQuestions function and surrounding script
old_script_start = '''<!-- === 观众问答 === -->
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
  fetch('/api/control/go',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({slide:n})}).catch(function(e){console.error("loadQuestions error:",e)});
}
function toggleAnswer(id){
  var el = document.getElementById('ans' + id);
  if(el) el.style.display = el.style.display === 'none' ? 'block' : 'none';
}
function submitAnswer(id){
  var input = document.getElementById('ansInput' + id);
  var text = input ? input.value.trim() : '';
  if(!text) return;
  var answerDiv = document.createElement('div');
  answerDiv.style.cssText = 'font-size:12px;color:#7ee787;padding:6px 8px;background:rgba(0,0,0,.15);border-radius:6px;margin-top:4px';
  answerDiv.innerHTML = '💬 ' + text;
  var ansBox = document.getElementById('ans' + id);
  if(ansBox) ansBox.parentNode.insertBefore(answerDiv, ansBox.nextSibling);
  if(ansBox) ansBox.style.display = 'none';
  input.value = '';
  try{ new BroadcastChannel('ppt-ctrl').postMessage({type:'voice-answer',question:'',answer:text,slide:0}); }catch(e){}
  try{ new BroadcastChannel('ai3-control').postMessage({type:'voice-answer',question:'',answer:text,slide:0}); }catch(e){}
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
          html += '<div style="display:flex;gap:4px;flex-wrap:wrap">';
          html += '<button class="btn" onclick="goToSlide(' + (q.page||1) + ')" style="font-size:11px;padding:3px 10px">跳转</button>';
          html += '<button class="btn" onclick="toggleAnswer(' + q.id + ')" style="font-size:11px;padding:3px 10px">回答</button>';
          html += '</div>';
          html += '<div id="ans' + q.id + '" style="display:none;margin-top:6px">';
          html += '<div style="display:flex;gap:4px">';
          html += '<input id="ansInput' + q.id + '" type="text" placeholder="输入回答...回车发送" onkeydown="if(event.key===' + "'" + 'Enter' + "'" + ')submitAnswer(' + q.id + ')" style="flex:1;padding:6px 8px;border-radius:6px;border:1px solid rgba(139,148,158,.2);background:rgba(0,0,0,.2);color:#e6edf3;font-size:12px;outline:none">';
          html += '<button class="btn" onclick="submitAnswer(' + q.id + ')" style="font-size:11px;padding:3px 10px">发送</button>';
          html += '</div></div>';
          html += '</div>';
        }
      }
    }
    document.getElementById('qlist').innerHTML = html;
  }).catch(function(e){
    console.error('Q&A error:', e);
    document.getElementById('qCount').textContent = '❌ '+e.message;
  });
}
loadQuestions();
setInterval(loadQuestions, 5000);
</script>'''

new_script = '''<!-- === 观众问答 === -->
<div style="margin-top:12px;border-top:1px solid rgba(139,148,158,.12);padding-top:10px">
  <div style="display:flex;gap:6px;align-items:center;margin-bottom:8px">
    <span style="font-size:11px;color:#8b949e;font-weight:600">💬 观众问题</span>
    <span style="font-size:10px;color:#484f58" id="qCount">0</span>
  </div>
  <div id="qlist" style="max-height:40vh;overflow-y:auto;font-size:12px;color:#8b949e">加载中...</div>
</div>
<script>
function goToSlide(n){
  fetch('/api/control/go',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({slide:n})}).catch(function(){});
}
function toggleAnswer(id){
  var el = document.getElementById('ans' + id);
  if(el) el.style.display = el.style.display === 'none' ? 'block' : 'none';
}
function submitAnswer(id){
  var input = document.getElementById('ansInput' + id);
  var text = input ? input.value.trim() : '';
  if(!text) return;
  var ansBox = document.getElementById('ans' + id);
  if(ansBox){
    var d = document.createElement('div');
    d.style.cssText = 'font-size:12px;color:#7ee787;padding:6px 8px;background:rgba(0,0,0,.15);border-radius:6px;margin-top:4px';
    d.textContent = '💬 ' + text;
    ansBox.parentNode.insertBefore(d, ansBox.nextSibling);
    ansBox.style.display = 'none';
  }
  input.value = '';
}
function loadQuestions(){
  fetch('/api/questions').then(function(r){
    if(!r.ok) throw new Error('HTTP '+r.status);
    return r.json();
  }).then(function(d){
    var list = document.getElementById('qlist');
    if(!list) return;
    var bp = d.by_page || {};
    var total = 0;
    for(var k in bp) total += bp[k].length;
    document.getElementById('qCount').textContent = total + '个';
    if(total === 0){
      list.innerHTML = '<div style="text-align:center;padding:20px;color:#484f58">暂无问题</div>';
      return;
    }
    var keys = Object.keys(bp).sort(function(a,b){return a-b;});
    var h = '';
    for(var ki=0;ki<keys.length;ki++){
      var page = keys[ki];
      var qs = bp[page];
      for(var qi=0;qi<qs.length;qi++){
        var q = qs[qi];
        h += '<div style="background:rgba(255,255,255,.03);border:1px solid rgba(139,148,158,.1);border-radius:8px;padding:10px;margin-bottom:6px">';
        h += '<div style="display:flex;gap:4px;margin-bottom:4px;align-items:center">';
        h += '<span style="color:#484f58;font-size:13px">' + esc(q.name||'匿名') + '</span>';
        h += '<span style="color:#58a6ff;font-size:10px;background:rgba(0,113,227,.1);padding:1px 6px;border-radius:4px">P' + (q.page||'?') + '</span>';
        h += '</div>';
        h += '<div style="color:#e6edf3;line-height:1.5;margin-bottom:4px;font-size:13px">' + esc(q.question) + '</div>';
        if(q.deeper){
          h += '<div style="font-size:11px;color:#8b949e;padding:6px 8px;background:rgba(0,0,0,.15);border-radius:6px;margin-bottom:4px">💡 ' + esc(q.deeper) + '</div>';
        }
        h += '<div style="display:flex;gap:4px;flex-wrap:wrap">';
        h += '<button class="btn" onclick="goToSlide(' + (q.page||1) + ')" style="font-size:11px;padding:3px 10px">跳转</button>';
        h += '<button class="btn" onclick="toggleAnswer(' + q.id + ')" style="font-size:11px;padding:3px 10px">回答</button>';
        h += '</div>';
        h += '<div id="ans' + q.id + '" style="display:none;margin-top:6px">';
        h += '<div style="display:flex;gap:4px">';
        h += '<input id="ansInput' + q.id + '" type="text" placeholder="输入回答..." onkeydown="if(event.key===\'Enter\')submitAnswer(' + q.id + ')" style="flex:1;padding:6px 8px;border-radius:6px;border:1px solid rgba(139,148,158,.2);background:rgba(0,0,0,.2);color:#e6edf3;font-size:12px;outline:none">';
        h += '<button class="btn" onclick="submitAnswer(' + q.id + ')" style="font-size:11px;padding:3px 10px">发送</button>';
        h += '</div></div>';
        h += '</div>';
      }
    }
    list.innerHTML = h;
  }).catch(function(e){
    console.error('Q&A error:', e);
    var c = document.getElementById('qCount');
    if(c) c.textContent = 'err';
    var l = document.getElementById('qlist');
    if(l) l.innerHTML = '<div style="text-align:center;padding:20px;color:#e53e3e">加载失败，请刷新</div>';
  });
}
function esc(s){
  if(!s) return '';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
document.getElementById('qlist').textContent = '加载中...';
loadQuestions();
setInterval(loadQuestions, 5000);
</script>'''

if old_script_start in html:
    html = html.replace(old_script_start, new_script)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print('Replaced questions section with simpler version')
else:
    print('Old script not found')
    # Find what's different
    idx = html.find('toggleAnswer')
    if idx > 0:
        print('Found toggleAnswer at', idx)
        print(repr(html[idx-50:idx+50]))
    else:
        # Find the start of the questions section
        idx = html.find('观众问答')
        if idx > 0:
            print('Found 观众问答 at', idx)
            # Print a section
            section = html[idx:idx+200]
            lines = section.split('\n')
            for i, line in enumerate(lines[:10]):
                print(f'{i}: {line}')
