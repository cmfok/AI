#!/usr/bin/env python3
"""AI 真垃圾 · 分享会 PPT 质量检查脚本
用法: python3 check_deck.py
循环检查直到全部通过，再通知用户。
"""
import subprocess, sys, os, re, json, time

HOST = 'https://8008.cmfok.online'
DECK_PATH = '/home/ubuntu/share-ppt/ai_scroll.html'
LOCAL_PATH = os.path.join(os.path.dirname(__file__), 'deck_final_v2.html')

errors = []
warnings = []

def check(label, condition, detail=''):
    if condition:
        print(f'  ✅ {label}')
    else:
        errors.append(label)
        print(f'  ❌ {label} — {detail}')

def warn(label, detail=''):
    warnings.append(label)
    print(f'  ⚠️  {label} — {detail}')

print('=' * 60)
print('🔍 分享会 PPT 质量检查')
print('=' * 60)

# 1. 检查本地文件存在
print('\n📁 1. 文件检查')
check('本地文件存在', os.path.exists(LOCAL_PATH), f'找不到 {LOCAL_PATH}')

if not os.path.exists(LOCAL_PATH):
    sys.exit(1)

with open(LOCAL_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

# 2. HTML 结构检查
print('\n📐 2. HTML 结构检查')
check('包含 <!DOCTYPE html>', '<!DOCTYPE html>' in html)
check('包含 </html>', '</html>' in html)

# Count sections
slide_count = html.count('<section class="slide')
check(f'至少10个slide', slide_count >= 10, f'只有 {slide_count} 个 slide')

# Count notes
notes_count = html.count('class="notes"')
check(f'slide数≈notes数', abs(slide_count - notes_count) <= 3, f'{slide_count} slides vs {notes_count} notes')

# 3. 资源引用检查
print('\n🔗 3. 资源引用检查')
assets = ['assets/base.css', 'assets/fonts.css', 'assets/runtime.js']
for a in assets:
    check(f'引用 {a}', a in html)

# Check for tech-sharing CSS
check('内联 tech-sharing 样式', 'tpl-tech-sharing' in html)
check('包含 runtime.js', 'runtime.js' in html)

# 4. 关键内容检查
print('\n📝 4. 关键内容检查')
keywords = ['AI 真垃圾', '四大工程', '提示词工程', '上下文工程', '规训工程', '循环工程', '猜字系统', '推理强', '400万']
for k in keywords:
    check(f'包含 "{k}"', k in html)

# 5. 控制台通信检查
print('\n📡 5. 控制台通信检查')
check('包含 fetch(/api/control/current)', '/api/control/current' in html)
check('包含 slide 展开逻辑', 'expand' in html or 'card' in html)

# 6. 样式变量检查
print('\n🎨 6. 样式变量检查')
for var in ['--bg', '--accent', '--text-1', '--text-2', '--border', '--grad']:
    check(f'CSS变量 {var}', var in html)

# 7. 服务器部署检查
print('\n🌐 7. 服务器部署检查')
try:
    import urllib.request
    resp = urllib.request.urlopen(f'{HOST}/ai', timeout=10)
    check(f'页面HTTP状态码 200', resp.status == 200, f'实际 {resp.status}')
    body = resp.read().decode('utf-8')
    check('服务器页面包含标题', 'AI 真垃圾' in body)
    
    # Check assets on server
    for a in assets:
        try:
            r = urllib.request.urlopen(f'{HOST}/{a}', timeout=5)
            check(f'服务器 {a} 可访问', r.status == 200, f'实际 {r.status}')
        except Exception as e:
            check(f'服务器 {a} 可访问', False, str(e))
except Exception as e:
    warn(f'服务器连接失败: {e}')
    check('服务器页面可访问', False, str(e))

# 8. Slide 4 卡片交互检查
print('\n🃏 8. 卡片交互检查')
check('Slide 2 答案容器 s2a', 'id="s2a"' in html)
check('Slide 4 卡片 m1', 'id="m1"' in html)
check('Slide 4 卡片 m2', 'id="m2"' in html)
check('Slide 4 卡片 m3', 'id="m3"' in html)
check('Slide 4 局限容器 lb', 'id="lb"' in html)

# 9. 逐字稿检查
print('\n📖 9. 逐字稿检查')
notes_content = re.findall(r'<div class="notes">(.*?)</div>', html, re.DOTALL)
empty_notes = [i for i, n in enumerate(notes_content) if len(n.strip()) < 10]
check(f'逐字稿不空', len(empty_notes) == 0, f'Slide {[i+1 for i in empty_notes]} 逐字稿为空')

# Summary
print('\n' + '=' * 60)
if errors:
    print(f'❌ 共 {len(errors)} 个错误:')
    for e in errors:
        print(f'   • {e}')
    if warnings:
        print(f'\n⚠️  共 {len(warnings)} 个警告:')
        for w in warnings:
            print(f'   • {w}')
    print(f'\n🔁 需要修复后重新检查')
    sys.exit(1)
else:
    print(f'✅ 全部检查通过! ({len(warnings)} 个警告)')
    if warnings:
        for w in warnings:
            print(f'   ⚠️  {w}')
    print('\n🎉 可以通知用户了!')
