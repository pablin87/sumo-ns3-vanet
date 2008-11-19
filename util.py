import sys
import subprocess

def fatal(msg):
    print >> sys.stderr, msg
    sys.exit(2)


def run_command(*args, **kwargs):
    if len(args):
        argv = args[0]
    elif 'args' in kwargs:
        argv = kwargs['args']
    else:
        argv = None
    if argv is not None:
        print " => ", ' '.join(argv)
    # FIXME: check_call is python >= 2.5 only, but we need to support python 2.3 as well
    return subprocess.check_call(*args, **kwargs)
