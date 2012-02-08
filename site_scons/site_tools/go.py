import os
from SCons.Script import *

GOCPPPATH = os.path.join(os.environ['GOROOT'], 'pkg', 'darwin_amd64')
GOPKGPATH = GOCPPPATH

def _make_gocflags(env):
    return '-I' + env['GOPKGPATH']

def generate(env):
    # a builder for go
    # TODO: check env for proper architecture
    gobld = Builder(action = {},
                    suffix = '.6',
                    single_source = 1)
    gobld.add_action('.go', '6g -o $TARGET $SOURCE')
    gobld.add_action('.c', '6c $GOCFLAGS -o $TARGET $SOURCE')

    # a builder for gopack
    gopackbld = Builder(action = 'gopack grc $TARGET $SOURCES',
            suffix = '.a',
            src_suffix = '.6',
            src_builder = ['GoObject'])

    # builders for executables and libraries.
    # Should we at least check?
    goexebuild = Builder(action = '6l -o $TARGET $SOURCES',
            suffix = '',
            src_suffix = '.6',
            src_builder = ['GoObject'])
    golibbuild = Builder(action = '6l -o $TARGET $SOURCES',
            suffix = '.a',
            src_suffix = '.6',
            src_builder = ['GoObject'])

    env.PrependENVPath('PATH', os.path.join(os.environ['GOROOT'], 'bin'))
    env.PrependENVPath('PATH', '/usr/local/bin')
    env.Append(BUILDERS = { 'GoObject' : gobld })
    env.Append(BUILDERS = { 'GoPack' : gopackbld })
    env.SetDefault(GOPKGPATH = GOCPPPATH)
    env['_make_gocflags'] = _make_gocflags
    env.SetDefault(GOCFLAGS = '${ _make_gocflags(__env__) }')

def exists(env):
    return env.detect('GoObject')

#scanner for go dependencies
def _goimport_scan(node, env, path, arg = None):
    if not os.path.exists(str(node)) :
        # generated nodes don't necessarily exist yet, so can't be scanned
        return []
    stdin, stdout = os.popen2('godeps')
    stdin.write(node.get_text_contents())
    stdin.close()
    output = stdout.read()

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
#env.Append(SCANNERS = goscan)

