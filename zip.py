#!/usr/bin/env python3

import os, shutil, zipfile

# build = 'plugin.video.rightnow_media'
build = 'plugin.video.rightnow-media'
zfile = build+'.zip'

files = [
    'addon.xml',
    # 'auth.py',
    'changelog.txt',
    'default.py',
    'LICENSE.txt',
    'readme.txt',
    'icon.png',
    'fanart.jpg',

]

shutil.rmtree(build,ignore_errors=True)

os.mkdir(build)

for file in files:
    dest_file = os.path.join(build,file)
    shutil.copy(file,dest_file)

with zipfile.ZipFile(zfile,'w') as Z:
    for file in files:
        dest_file = os.path.join(build,file)
        Z.write(dest_file)
