#!/usr/bin/env python3

import os, shutil, zipfile

# build = 'plugin.video.rightnow_media'
build = 'plugin.video.rightnow-media'
zfile = build+'.zip'

files = [
    'addon.xml',
    'changelog.txt',
    'default.py',
    'LICENSE.txt',
    'readme.txt',
    'icon.png',
    'fanart.jpg',
    'resources/',
    'resources/settings.xml'
]

shutil.rmtree(build,ignore_errors=True)

os.mkdir(build)

for file in files:
    dest_file = os.path.join(build,file)
    if dest_file.endswith('/'):
        os.mkdir(dest_file)
    else:
        shutil.copy(file,dest_file)

with zipfile.ZipFile(zfile,'w') as Z:
    for file in files:
        dest_file = os.path.join(build,file)
        Z.write(dest_file)

shutil.copy(zfile,'../..')