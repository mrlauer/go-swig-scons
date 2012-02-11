import os
import subprocess
from SCons.Script import *

GOCPPPATH = os.path.join(os.environ['GOROOT'], 'pkg', 'darwin_amd64')
GOPKGPATH = GOCPPPATH

def _make_gocflags(env):
    return '-I' + env['GOPKGPATH']

def generate(env):
    # a builder for go
    # TODO: check env for proper architecture
    gobld = Builder(action = {},
                    suffix = '$GOOBJSUFFIX',
                    single_source = 1)
    gobld.add_action('.go', '$GOCOMPILER $_GOINFLAGS -o $TARGET $SOURCE')
    gobld.add_action('.c', '$GOCC $GOCFLAGS -o $TARGET $SOURCE')

    # a builder for gopack
    gopackbld = Builder(action = 'gopack grc $TARGET $SOURCES',
            suffix = '.a',
            src_suffix = '$GOOBJSUFFIX',
            src_builder = ['GoObject'])

    # builders for executables and libraries.
    # Should we at least check?
    goexebuild = Builder(action = '$GOLINKER $_GOLINKFLAGS -o $TARGET $SOURCES',
            suffix = '',
            src_suffix = '$GOOBJSUFFIX',
            src_builder = ['GoObject'])
    golibbuild = Builder(action = '$GOLINKER $_GOLINKFLAGS -o $TARGET $SOURCES',
            suffix = '.a',
            src_suffix = '$GOOBJSUFFIX',
            src_builder = ['GoObject'])

    env.PrependENVPath('PATH', os.path.join(os.environ['GOROOT'], 'bin'))
    env.PrependENVPath('PATH', '/usr/local/bin')
    env.SetDefault(GONUMBER = '6')
    env.SetDefault(GOCOMPILER = '${GONUMBER}g')
    env.SetDefault(GOCC = '${GONUMBER}c')
    env.SetDefault(GOLINKER = '${GONUMBER}l')
    env.SetDefault(GOOBJSUFFIX = '.${GONUMBER}')
    env.Append(BUILDERS = { 'GoObject' : gobld })
    env.Append(BUILDERS = { 'GoPack' : gopackbld })
    env.Append(BUILDERS = { 'GoExe' : goexebuild })
    env.Append(BUILDERS = { 'GoLibrary' : golibbuild })
    env.SetDefault(GOPKGPATH = GOCPPPATH)
    env['_make_gocflags'] = _make_gocflags
    env.SetDefault(GOCFLAGS = '${ _make_gocflags(__env__) }')
    env.SetDefault(_GOINFLAGS = '$( ${_concat( "-I", GOINCPATH, "", __env__, RDirs, TARGET, SOURCE ) } $)')
    env.SetDefault(_GOLINKFLAGS = '$( ${_concat( "-L", GOINCPATH, "", __env__, RDirs, TARGET, SOURCE ) } $)')
    #env.Append(SCANNERS = goscan)

def exists(env):
    return env.detect('GoObject')

#scanner for go dependencies
def _goimport_scan(node, env, path, arg = None):
    if not node.exists():
        # generated nodes don't necessarily exist yet, so can't be scanned
        return []
    proc = subprocess.Popen('godeps', stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    output, _ = proc.communicate(node.get_text_contents())

    results = []
    for s in output.split():
        arname = s + '.a'
        for p in path:
            pname = os.path.join(p, arname)
            if os.path.exists(pname):
                results.append(pname)
                break
        else:
            results.append(arname)
    return results

def _goimport_pathfn(env, *args):
    return (env['GOPKGPATH'],)
goscan = Scanner(function = _goimport_scan, skeys = ['.go'], path_function = _goimport_pathfn)

