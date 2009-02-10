#! /usr/bin/env python
import sys
from optparse import OptionParser
import os

import constants
from util import run_command, fatal


def build_nsc():
    # XXX: Detect gcc major version(s) available to build supported stacks
    for kernel in ['linux-2.6.18', 'linux-2.6.26']:
        run_command(['python', 'scons.py', kernel])
    

def build_ns3(regression_dir):
    cmd = [
        "./waf", "configure",
        "--with-regression-traces", os.path.join("..", regression_dir),
        "--with-pybindgen", os.path.join("..", constants.LOCAL_PYBINDGEN_PATH),
        ]

    # Build NSC if the architecture supports it
    arch = os.uname()[4]
    if arch == 'x86_64' or arch == 'i686' or arch == 'i586' or arch == 'i486' or arch == 'i386':
        cmd.extend(["--with-nsc", os.path.join("..", constants.LOCAL_NSC_PATH)])

    run_command(cmd)
    run_command(["./waf"])


def main(argv):
    parser = OptionParser()
    (options, args) = parser.parse_args()


    print "# Build NSC"
    print "Entering directory `%s'" % constants.LOCAL_NSC_PATH
    cwd = os.getcwd()
    os.chdir(constants.LOCAL_NSC_PATH)
    try:
        build_nsc()
    finally:
        os.chdir(cwd)
    print "Leaving directory `%s'" % constants.LOCAL_NSC_PATH


    print "# Build NS-3"
    d = os.path.join(os.path.dirname(__file__), os.path.split(constants.NS3_BRANCH)[-1])
    print "Entering directory `%s'" % d
    os.chdir(d)
    try:
        regression_dir = os.path.join(os.path.dirname(__file__), os.path.split(constants.REPO_BRANCH)[-1])
        build_ns3(regression_dir)
    finally:
        os.chdir(cwd)
    print "Leaving directory `%s'" % d


    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
