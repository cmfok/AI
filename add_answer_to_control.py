# -*- coding: utf-8 -*-
path = '/home/ubuntu/share-ppt/control.html'

with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the button line in question rendering
old_btn_line = "html += '<button class=\"btn\" onclick=\"goToSlide(' + (q.page||1) + ')\" style=\"font-size:11px;padding:3px 10px\">跳转</button>';"

new_btn_block = """html += '<button class="btn" onclick="goToSlide(' + (q.page||1) + ')" style="font-size:11px;padding:3px 10px">跳转</button>';
          html += '<button class="btn" onclick="toggleAnswer(' + q.id + ')" style="font-size:11px;padding:3px 10px">回答</button>';
          html += '</div>';
          html += '<div id="ans' + q.id + '" style="display:none;margin-top:6px">';
          html += '<div style="display:flex;gap:4px">';
          html += '<input id="ansInput' + q.id + '" type="text" placeholder="输入回答..." style="flex:1;padding:6px 8px;border-radius:6px;border:1px solid rgba(139,148,158,.2);background:rgba(0,0,0,.2);color:#e6edf3;font-size:12px;outline:none">';
          html += '<button class="btn" onclick="submitAnswer(' + q.id + ')" style="font-size:11px;padding:3px 10px">发送</button>';
          html += '</div></div>';
"""

if old_btn_line in html:
    html = html.replace(old_btn_line, new_btn_block)
    print('Replaced button line')
else:
    print('Old button line not found, searching...')
    idx = html.find('跳转')
    if idx > 0:
        print(repr(html[idx-50:idx+100]))
    else:
        # Try to find the pattern without escaped quotes
        idx = html.find('goToSlide')
        if idx > 0:
            print('Found goToSlide at', idx)
            print(repr(html[idx-100:idx+150]))

# Add toggleAnswer and submitAnswer functions
old_fn = "function loadQuestions(){"
new_fn = """function toggleAnswer(id){
  var el = document.getElementById('ans' + id);
  if(el) el.style.display = el.style.display === 'none' ? 'block' : 'none';
}
function submitAnswer(id){
  var input = document.getElementById('ansInput' + id);
  var text = input ? input.value.trim() : '';
  if(!text) return;
  // Show answer in the card
  var answerDiv = document.createElement('div');
  answerDiv.style.cssText = 'font-size:12px;color:#7ee787;padding:6px 8px;background:rgba(0,0,0,.15);border-radius:6px;margin-top:4px';
  answerDiv.innerHTML = '💬 ' + text;
  var ansBox = document.getElementById('ans' + id);
  if(ansBox) ansBox.parentNode.insertBefore(answerDiv, ansBox.nextSibling);
  if(ansBox) ansBox.style.display = 'none';
  input.value = '';
  // Broadcast to all display page channels
  try{ new BroadcastChannel('ppt-ctrl').postMessage({type:'voice-answer',question:'',answer:text,slide:0}); }catch(e){}
  try{ new BroadcastChannel('ai3-control').postMessage({type:'voice-answer',question:'',answer:text,slide:0}); }catch(e){}
}
function loadQuestions(){"""

if old_fn in html:
    html = html.replace(old_fn, new_fn)
    print('Added answer functions')
else:
    print('loadQuestions not found')

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

print('Done')
