#! /usr/bin/env python
import sys
from optparse import OptionParser
import os
from xml.dom import minidom as dom

import constants
from util import run_command, fatal


def build_nsc():
    # XXX: Detect gcc major version(s) available to build supported stacks
    for kernel in ['linux-2.6.18', 'linux-2.6.26']:
        run_command(['python', 'scons.py', kernel])
    

def build_ns3(config):
    cmd = [
        "./waf", "configure",
        ]

    try:
        ns3_traces, = config.getElementsByTagName("ns-3-traces")
    except ValueError:
        print "Note: configuring ns-3 without regression traces"
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
        arch = os.uname()[4]
        if arch == 'x86_64' or arch == 'i686' or arch == 'i586' or arch == 'i486' or arch == 'i386':
            cmd.extend(["--with-nsc", os.path.join("..", nsc.getAttribute("dir"))])
        else:
            print "Note: configuring ns-3 without NSC (architecture not supported)"

    run_command(cmd)
    run_command(["./waf"])


def main(argv):
    parser = OptionParser()
    (options, args) = parser.parse_args()

    try:
        dot_config = open(".config", "rt")
    except IOError:
        print >> sys.stderr, "** ERROR: missing .config file; you probably need to run the download.py script first."
    config = dom.parse(dot_config)
    dot_config.close()

    nsc_config_elems = config.getElementsByTagName("nsc")
    if nsc_config_elems:
        nsc_config, = nsc_config_elems
        nsc_dir = nsc_config.getAttribute("dir")
        print "# Build NSC"
        cwd = os.getcwd()
        os.chdir(nsc_dir)
        print "Entering directory `%s'" % nsc_dir
        try:
            build_nsc()
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
