import os
import re

GOCPPPATH = os.path.join(os.environ['GOROOT'], 'pkg', 'darwin_amd64')
GOPKGPATH = GOCPPPATH

env = Environment(tools = ['default', 'go', 'goswig'])
Export('env')
SConscript('src/SConscript', variant_dir='build', duplicate=0)
