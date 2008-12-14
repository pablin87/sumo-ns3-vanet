#! /usr/bin/env python
import sys
from optparse import OptionParser
import os

import constants
from util import run_command, fatal


def main(argv):
    parser = OptionParser()
    (options, args) = parser.parse_args()

    # first of all, change to the directory of ns-3
    d = os.path.join(os.path.dirname(__file__), os.path.split(constants.BRANCH)[-1])
    print "Entering directory `%s'" % d
    os.chdir(d)

    run_command(["./waf", "configure",
                 "--with-regression-traces", os.path.join("..", constants.BRANCH + constants.REGRESSION_SUFFIX),
                 "--with-pybindgen", os.path.join("..", constants.LOCAL_PYBINDGEN_PATH),
                 "--with-nsc", os.path.join("..", constants.LOCAL_NSC_PATH),
                 ])
    run_command(["./waf"])

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
