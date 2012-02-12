import os
import sys
import subprocess
import platform

from SCons.Script import *

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
            suffix = '$GOLIBSUFFIX',
            src_suffix = '$GOOBJSUFFIX',
            src_builder = ['GoObject'])

    # figure out the environment
    # Should this be in a Configure block?
    # we'll get GOROOT from the environment for now.
    env.SetDefault(GOROOT = os.environ.get('GOROOT'))
    # get GOOS and GOARCH from the platform. This may not be quite right!
    system = platform.system()
    env.SetDefault(GOOS = system.lower())
    machine = platform.machine()
    goarch = "amd64"
    goarchchar = "6"
    is64 = (sys.maxsize > 2**32)
    if not is64:
        if machine == "i386":
            goarch = "386"
            goarchchar = "8"
        else:
            goarch = "arm"
            goarchchar = "5"
    env.SetDefault(GOARCH = goarch, GOARCHCHAR = goarchchar) 
    env.SetDefault(GOPKGPATH = '$GOROOT/pkg/${GOOS}_${GOARCH}')
    env.SetDefault(COCPPPATH = '$GOPKGPATH')

    env.PrependENVPath('PATH', os.path.join(os.environ['GOROOT'], 'bin'))
    env.PrependENVPath('PATH', '/usr/local/bin')
    env.SetDefault(GOCOMPILER = '${GOARCHCHAR}g')
    env.SetDefault(GOCC = '${GOARCHCHAR}c')
    env.SetDefault(GOLINKER = '${GOARCHCHAR}l')
    env.SetDefault(GOOBJSUFFIX = '.${GOARCHCHAR}')
    env.SetDefault(GOLIBSUFFIX = '${LIBSUFFIX}')
    env.Append(BUILDERS = { 'GoObject' : gobld })
    env.Append(BUILDERS = { 'GoPack' : gopackbld })
    env.Append(BUILDERS = { 'GoExe' : goexebuild })
    env.Append(BUILDERS = { 'GoLibrary' : golibbuild })
    env.SetDefault(GOALLPKGPATH = '$GOINCPATH:$GOPKGPATH')
    env['_make_gocflags'] = _make_gocflags
    env.SetDefault(GOCFLAGS = '${ _make_gocflags(__env__) }')
    env.SetDefault(GOLINKFLAGS = '')
    env.SetDefault(_GOINFLAGS = '$( ${_concat( "-I", GOINCPATH, "", __env__, RDirs, TARGET, SOURCE ) } $)')
    env.SetDefault(_GOLINKFLAGS = '$( ${_concat( "-L", GOINCPATH, "", __env__, RDirs, TARGET, SOURCE ) } $) $GOLINKFLAGS')
    env.Append(SCANNERS = goscan)

def exists(env):
    return env.detect('GoObject')

#scanner for go dependencies
def _goimport_scan(node, env, path, arg = None):
    if callable(path):
        path = path()
    try:
        proc = subprocess.Popen('godeps', stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        output, _ = proc.communicate(node.get_text_contents())
    except OSError, e:
        SCons.Warnings.warn(SCons.Warnings.Warning, "Error executing godeps: %s" % e)
        return []

    topdir = env.Dir('#').abspath

    results = []
    for s in output.split():
        arname = s + env.subst('$GOLIBSUFFIX')
        for p in path:
            pname = os.path.join(topdir, str(p), arname)
            if os.path.exists(pname):
                results.append(pname)
                break
            if File(pname).has_builder():
                results.append(pname)
                break
        else:
            SCons.Warnings.warn(SCons.Warnings.DependencyWarning, "Could not find go dependency %s imported in %s" 
                    % (arname, str(node)))
    return results

def _goimport_pathfn(env, *args):
    return (env.subst,)
goscan = Scanner(function = _goimport_scan, skeys = ['.go'], path_function = FindPathDirs('GOALLPKGPATH'))

