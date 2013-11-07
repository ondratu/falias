#!/usr/bin/env python

from sys import exit, argv
from falias.security import smartsha1

if __name__ == "__main__":
    if len(argv) < 2:
        print "Usage:"
        print " %s passwordstring" % argv[0]
        exit(1)

    print smartsha1(argv[1])
#endif
