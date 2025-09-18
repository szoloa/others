#!/bin/python

import sys
import Question

def main(argv):
    p = Question.Questions()
    p.addquestion(*argv)
    p.close()

if __name__ == '__main__':
    main(sys.argv[1:])