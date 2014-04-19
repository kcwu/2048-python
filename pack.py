import subprocess

template = '''import os
exec os.popen('echo %s|base64 -d|gzip -d').read()'''

def main():
    data = subprocess.check_output('python ~/Downloads/code/minipy/minipy.py --rename -p AI,getNextMove ai_modules/kcwu_short.py | sed -e s/100000000\.0/1e8/ | gzip -9| base64', shell=True)
    data = data.replace('\n','')
    print template % data

main()
