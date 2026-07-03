# -*- coding: utf-8 -*-
"""Replace the questions script block in control.html"""

path = '/home/ubuntu/share-ppt/control.html'

with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the second script block
start = None
end = None
for i, line in enumerate(lines):
    if line.strip() == 'function goToSlide(n){':
        start = i
    if start and line.strip() == 'setInterval(loadQuestions, 5000);':
        end = i
        break

if start and end:
    print('Found script block from line', start+1, 'to', end+1)
    
    new_script = '''function goToSlide(n){
  fetch('/api/control/go',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({slide:n})}).catch(function(){});
}
var _qdata = {};
function aiAnswer(id){
  var ansBox = document.getElementById('ans' + id);
  if(!ansBox) return;
  var qtext = _qdata[id] || '';
  ansBox.style.display = 'block';
  ansBox.innerHTML = '<div style="text-align:center;padding:8px;color:#8b949e;font-size:12px">\U0001F914 AI思考中...</div>';
  fetch('/api/questions/ai-answer', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({id:id, question:qtext})
  }).then(function(r){return r.json();}).then(function(d){
    if(d.ok){
      var txt = d.answer.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
      ansBox.innerHTML = '<div style="font-size:12px;color:#7ee787;padding:8px;background:rgba(0,0,0,.15);border-radius:6px">\U0001F916 ' + txt + '</div>';
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
        h += '<span style="color:#484f58;font-size:13px">' + (q.name||'\u533F\u540D') + '</span>';
        h += '<span style="color:#58a6ff;font-size:10px;background:rgba(0,113,227,.1);padding:1px 6px;border-radius:4px">P' + (q.page||'?') + '</span>';
        h += '</div>';
        h += '<div style="color:#e6edf3;line-height:1.5;margin-bottom:4px;font-size:13px">' + q.question + '</div>';
        if(q.deeper){
          h += '<div style="font-size:11px;color:#8b949e;padding:6px 8px;background:rgba(0,0,0,.15);border-radius:6px;margin-bottom:4px">\U0001F4A1 ' + q.deeper + '</div>';
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
}
loadQuestions();
setInterval(loadQuestions, 5000);
'''
    # Convert new_script to list of lines
    new_lines = new_script.split('\n')
    # Keep the trailing newline for each line except last
    new_lines = [l + '\n' for l in new_lines[:-1]] + [new_lines[-1]]
    
    lines = lines[:start] + new_lines + lines[end+1:]
    
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print('Replaced script block successfully')
else:
    print('Script block not found:', start, end)
