import subprocess

res = subprocess.Popen(['git','status'], stdout=subprocess.PIPE).communicate()[0]
print(res.decode('utf-8'))

if 't.py' in res.decode('utf-8'):
    print(f'Found file: t.py')