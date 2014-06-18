# Copyright 2014 Google Inc. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
import subprocess
import sys

template = '''import os
exec os.popen('echo %s|base64 -d|gzip -d').read()'''

def main():
    fn = sys.argv[1]
    data = subprocess.check_output('python ~/Downloads/code/minipy/minipy.py --rename -p AI,getNextMove %s | sed -e s/100000000\.0/1e8/ | gzip -9| base64' % fn, shell=True)
    data = data.replace('\n','')
    print template % data

main()
