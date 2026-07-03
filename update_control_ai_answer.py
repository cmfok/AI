# -*- coding: utf-8 -*-
"""Update control page to use AI-generated answers instead of manual input"""

path = '/home/ubuntu/share-ppt/control.html'

with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the submitAnswer + toggleAnswer functions + the q rendering
old_script = '''function goToSlide(n){
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
        h += '<input id="ansInput' + q.id + '" type="text" placeholder="输入回答..." onkeydown="if(event.key===\\'Enter\\')submitAnswer(' + q.id + ')" style="flex:1;padding:6px 8px;border-radius:6px;border:1px solid rgba(139,148,158,.2);background:rgba(0,0,0,.2);color:#e6edf3;font-size:12px;outline:none">';
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
}'''

new_script = '''var _qdata = {};
function goToSlide(n){
  fetch('/api/control/go',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({slide:n})}).catch(function(){});
}
function aiAnswer(id){
  var ansBox = document.getElementById('ans' + id);
  if(!ansBox) return;
  var question = _qdata[id] || '';
  ansBox.style.display = 'block';
  ansBox.innerHTML = '<div style="text-align:center;padding:8px;color:#8b949e;font-size:12px">\U0001F914 AI思考中...</div>';
  fetch('/api/questions/ai-answer', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({id:id, question:question})
  }).then(function(r){return r.json();}).then(function(d){
    if(d.ok){
      ansBox.innerHTML = '<div style="font-size:12px;color:#7ee787;padding:8px;background:rgba(0,0,0,.15);border-radius:6px">\U0001F916 ' + esc(d.answer) + '</div>';
      try{ new BroadcastChannel('ppt-ctrl').postMessage({type:'voice-answer',question:'',answer:d.answer,slide:0}); }catch(e){}
      try{ new BroadcastChannel('ai3-control').postMessage({type:'voice-answer',question:'',answer:d.answer,slide:0}); }catch(e){}
    } else {
      ansBox.innerHTML = '<div style="font-size:12px;color:#e53e3e;padding:8px">\u274C ' + (d.error||'\u56DE\u7B54\u5931\u8D25') + '</div>';
    }
  }).catch(function(){
    ansBox.innerHTML = '<div style="font-size:12px;color:#e53e3e;padding:8px">\u274C \u7F51\u7EDC\u9519\u8BEF</div>';
  });
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
    document.getElementById('qCount').textContent = total + '\u4E2A';
    if(total === 0){
      list.innerHTML = '<div style="text-align:center;padding:20px;color:#484f58">\u6682\u65E0\u95EE\u9898</div>';
      return;
    }
    var keys = Object.keys(bp).sort(function(a,b){return a-b;});
    var h = '';
    for(var ki=0;ki<keys.length;ki++){
      var page = keys[ki];
      var qs = bp[page];
      for(var qi=0;qi<qs.length;qi++){
        var q = qs[qi];
        _qdata[q.id] = q.question;
        h += '<div style="background:rgba(255,255,255,.03);border:1px solid rgba(139,148,158,.1);border-radius:8px;padding:10px;margin-bottom:6px">';
        h += '<div style="display:flex;gap:4px;margin-bottom:4px;align-items:center">';
        h += '<span style="color:#484f58;font-size:13px">' + esc(q.name||'\u533F\u540D') + '</span>';
        h += '<span style="color:#58a6ff;font-size:10px;background:rgba(0,113,227,.1);padding:1px 6px;border-radius:4px">P' + (q.page||'?') + '</span>';
        h += '</div>';
        h += '<div style="color:#e6edf3;line-height:1.5;margin-bottom:4px;font-size:13px">' + esc(q.question) + '</div>';
        if(q.deeper){
          h += '<div style="font-size:11px;color:#8b949e;padding:6px 8px;background:rgba(0,0,0,.15);border-radius:6px;margin-bottom:4px">\U0001F4A1 ' + esc(q.deeper) + '</div>';
        }
        h += '<div style="display:flex;gap:4px;flex-wrap:wrap">';
        h += '<button class="btn" onclick="goToSlide(' + (q.page||1) + ')" style="font-size:11px;padding:3px 10px">\u8DF3\u8F6C</button>';
        h += '<button class="btn" onclick="aiAnswer(' + q.id + ')" style="font-size:11px;padding:3px 10px">\U0001F916 AI\u56DE\u7B54</button>';
        h += '</div>';
        h += '<div id="ans' + q.id + '" style="display:none;margin-top:6px"></div>';
        h += '</div>';
      }
    }
    list.innerHTML = h;
  }).catch(function(e){
    console.error('Q&A error:', e);
    var c = document.getElementById('qCount');
    if(c) c.textContent = 'err';
    var l = document.getElementById('qlist');
    if(l) l.innerHTML = '<div style="text-align:center;padding:20px;color:#e53e3e">\u52A0\u8F7D\u5931\u8D25\uFF0C\u8BF7\u5237\u65B0</div>';
  });
}'''

if old_script in html:
    html = html.replace(old_script, new_script)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print('Updated control page with AI answer')
else:
    print('Old script not found')
    # Debug
    idx = html.find('function goToSlide')
    if idx > 0:
        print('Found goToSlide at', idx)
        # Print the next 500 chars
        print(repr(html[idx:idx+300]))
