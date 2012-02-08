import os
import re
from SCons.Script import *

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

# returns a cfile to be linked with the original library and a cgo module
def GoSwigComplete(env, basename, module):
    swigNodes = env.GoSwig(basename, MODULE=module)
    lib = env.GoPack(module + '.a', swigNodes[1:])
    return [swigNodes[0], lib]
    
def generate(env):
    goswigbld = Builder(
            generator = _swig_generator,
            src_suffix = '.i',
            suffix = '$SWIGCXXFILESUFFIX',
            emitter = _goswig_emitter,
        )

    env.Append(BUILDERS = { 'GoSwig' : goswigbld })
    AddMethod(env, GoSwigComplete)

def exists(env):
    return env.detect('GoSwig')
