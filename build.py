#! /usr/bin/env python
import sys
from optparse import OptionParser
import os
from xml.dom import minidom as dom

import constants
from util import run_command, fatal, CommandError


def build_nsc():
    # XXX: Detect gcc major version(s) available to build supported stacks
    #  - we could just issue "python scons.py" and have NSC decide what it can
    #    build. This might be more sane?
    kernels = ['liblinux2.6.18.so', 'liblinux2.6.26.so']
    run_command(['python', 'scons.py'] + kernels)
    

def build_ns3(config):
    cmd = [
        "python", "waf", "configure",
        ]

    try:
        ns3_traces, = config.getElementsByTagName("ns-3-traces")
    except ValueError:
        # Don't print a warning message here since regression traces
        # are no longer used.
        pass
    else:
        cmd.extend([
                "--with-regression-traces", os.path.join("..", ns3_traces.getAttribute("dir")),
                ])

    try:
        pybindgen, = config.getElementsByTagName("pybindgen")
    except ValueError:
        print "Note: configuring ns-3 without pybindgen"
    else:
        cmd.extend([
                "--with-pybindgen", os.path.join("..", pybindgen.getAttribute("dir")),
        ])

    try:
        nsc, = config.getElementsByTagName("nsc")
    except ValueError:
        print "Note: configuring ns-3 without NSC"
    else:
        # Build NSC if the architecture supports it
        if sys.platform not in ['linux2']:
            arch = None
        else:
            arch = os.uname()[4]
        if arch == 'x86_64' or arch == 'i686' or arch == 'i586' or arch == 'i486' or arch == 'i386':
            cmd.extend(["--with-nsc", os.path.join("..", nsc.getAttribute("dir"))])
        else:
            print "Note: configuring ns-3 without NSC (architecture not supported)"

    run_command(cmd)
    run_command(["python", "waf"])


def main(argv):
    parser = OptionParser()
    parser.add_option('--disable-nsc',
                      help=("Don't try to build NSC"), action="store_true", default=False,
                      dest='disable_nsc')
    (options, args) = parser.parse_args()

    cwd = os.getcwd()

    try:
        dot_config = open(".config", "rt")
    except IOError:
        print >> sys.stderr, "** ERROR: missing .config file; you probably need to run the download.py script first."
        sys.exit(2)

    config = dom.parse(dot_config)
    dot_config.close()

    if options.disable_nsc:
        print "# Skip NSC (by user request)"
        for node in config.getElementsByTagName("nsc"):
            config.documentElement.removeChild(node)
    elif sys.platform in ['darwin', 'win32']:
        print "# Skip NSC (platform not supported)"
    else:
        nsc_config_elems = config.getElementsByTagName("nsc")
        if nsc_config_elems:
            nsc_config, = nsc_config_elems
            nsc_dir = nsc_config.getAttribute("dir")
            print "# Build NSC"
            os.chdir(nsc_dir)
            print "Entering directory `%s'" % nsc_dir
            try:
                try:
                    build_nsc()
                except CommandError:
                    print "# Build NSC: failure (ignoring NSC)"
                    config.documentElement.removeChild(nsc_config)
            finally:
                os.chdir(cwd)
            print "Leaving directory `%s'" % nsc_dir


    print "# Build NS-3"
    ns3_config, = config.getElementsByTagName("ns-3")
    d = os.path.join(os.path.dirname(__file__), ns3_config.getAttribute("dir"))
    print "Entering directory `%s'" % d
    os.chdir(d)
    try:
        build_ns3(config)
    finally:
        os.chdir(cwd)
    print "Leaving directory `%s'" % d


    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
