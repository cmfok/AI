path = '/home/ubuntu/share-ppt/app.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old = "return app.send_static_file('qa.html')"
new = "return app.send_static_file('ai/2/qa.html')"

if old in content:
    content = content.replace(old, new)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Fixed ai/2/qa route')
else:
    print('Pattern not found in content')
    # Find what it actually says
    idx = content.find('ai/2/qa')
    if idx > 0:
        print(repr(content[idx:idx+100]))
