import os
import re

GOCPPPATH = os.path.join(os.environ['GOROOT'], 'pkg', 'darwin_amd64')
GOPKGPATH = GOCPPPATH

# a builder for go
# TODO: check env for proper architecture
gobld = Builder(action = {},
                suffix = '.6',
                single_source = 1)
gobld.add_action('.go', '6g -o $TARGET $SOURCE')
gobld.add_action('.c', '6c $GOCFLAGS -o $TARGET $SOURCE')

def _find_swig_module(swig_file):
    try:
        swig_src = swig_file.srcnode()
        with open(unicode(swig_src)) as f:
            for l in f:
                m = re.match(r'\s*%module\s+(\w+)', l)
                if m:
                    return m.group(1)
    except:
        pass
    return None

# a builder for goswig
def _goswig_emitter(target, source, env):
    module = env.get('MODULE') or _find_swig_module(source[0])
    if module:
        target.append(module + '.go')
        target.append(module + '_gc' + env['CFILESUFFIX'])
    return target, source

def _swig_generator(source, target, env, for_signature):
    t = str(target[0])
    dirname = os.path.dirname(t)
    return 'swig -go -c++ -o %s -outdir %s $SOURCE' % (t, dirname)

goswigbld = Builder(
        generator = _swig_generator,
        src_suffix = '.i',
        suffix = '$SWIGCXXFILESUFFIX',
        emitter = _goswig_emitter,
        )

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

# returns a cfile to be linked with the original library and a cgo module
def GoSwigComplete(env, basename, module):
    swigNodes = env.GoSwig(basename, MODULE=module)
    lib = env.GoPack(module + '.a', swigNodes[1:])
    return [swigNodes[0], lib]
    
def _make_gocflags(env):
    return '-I' + env['GOPKGPATH']

env = Environment()
env.PrependENVPath('PATH', os.path.join(os.environ['GOROOT'], 'bin'))
env.PrependENVPath('PATH', '/usr/local/bin')
env.Append(BUILDERS = { 'GoObject' : gobld })
env.Append(BUILDERS = { 'GoSwig' : goswigbld })
env.Append(BUILDERS = { 'GoPack' : gopackbld })
env.SetDefault(GOPKGPATH = GOCPPPATH)
env['_make_gocflags'] = _make_gocflags
env.SetDefault(GOCFLAGS = '${ _make_gocflags(__env__) }')
AddMethod(env, GoSwigComplete)

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

Export('env')
SConscript('src/SConscript', variant_dir='build', duplicate=0)
