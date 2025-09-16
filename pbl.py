#!/bin/python

import sys
import Problem

def main(argv):
    p = Problem.Problems()
    p.addProblem(*argv)
    p.close()

if __name__ == '__main__':
    main(sys.argv[1:])