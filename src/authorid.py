#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# Distance metrics
# ----------------------------------------------------------------------
# Ivan Vladimir Meza-Ruiz/ ivanvladimir at turing.iimas.unam.mx
# 2012/IIMAS/UNAM
# ----------------------------------------------------------------------
# authorid.py is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# -------------------------------------------------------------------------

import optparse
import sys
import os
import os.path

# Local imports
import docread
import distance
import Weights as W

def verbose(*args):
    if opts.verbose:
        print >> out, "".join(args)

def info(*args):
    print >> out, "".join(args)

# MAIN
if __name__ == "__main__":
    usage="""%prog [options] dir [anwers]

        Runs user identification 

        dir   : Directory with author examples
        answer: File with answers for trainning
"""

    version="%prog 0.1"

    # Command line options
    p = optparse.OptionParser(usage=usage,version=version)
    p.add_option("-o", "--output",default=None,
            action="store", dest="output",
            help="Output [STDOUT]")
    p.add_option("-m", "--mode",default='test',
            action="store", dest="mode",
            help="test|train [test]")
    p.add_option("-w", "--weights",default=None,
            action="store", dest="weights",
            help="test|train [test]")
    p.add_option("-i", "--iters",default=10,type="int",
            action="store", dest="iters",
            help="Training iterations [10]")
    p.add_option("", "--known_pattern",default=r'known.*\.txt',
            action="store", dest="known",
            help="pattern for known files [known*]")
    p.add_option("", "--unknown_pattern",default=r'unknown*.txt',
            action="store", dest="unknown",
            help="pattern for unknown file [unknown*]")
    p.add_option("-v", "--verbose",
            action="store_true", dest="verbose",
            help="Verbose mode [Off]")
    opts, args = p.parse_args()

    # Arguments 
    if not len(args) > 0:
        p.error('Wrong number of arguments')

    if not opts.mode in ["train","test"]:
        p.error('Mode argument not valid: train or test')


    dirname = args[0]

    # Parameters
    out = sys.stdout
    if opts.output:
        try:
            out = open(opts.output)
        except:
            p.error('Output parameter could not been open: {0}'\
                    .format(opts.output))

    # Loading ingnore if exists
    _ignore=[]
    if os.path.exists('.ignore'):
        verbose('Loading files to ignore frm: .ignore')
        with open('.ignore') as file:
            _ignore=file.read().readlines()

        
    # load problems or problem
    problems=docread.dirproblems(dirname,opts.known,opts.unknown,_ignore)

    # TRAINNING MODE
    if opts.mode.startswith("train"):
      
        # Loading answers file
        if not len(args)==2:
            p.error("Answers needed for train mode")
        verbose('Loading answer file: {0}'.format(args[1]))
        answers = docread.loadanswers(args[1])

        # Checking for consistency
        if not len(problems) == len(answers):
            p.error("Not match for number of problems({0}) and \
            answers({1})".format(len(problems),len(answers)))

        # Loading weights or initializing
        if opts.weights:
            verbose('Loading weights file: {0}'.format(args[1]))
            # TODO load weights when given file
        else:
            WS=W.Weights()

        # Iterating over problems
        for it in range(opts.iters):
            info("="*60)
            info("Iteration {0}".format(it))
            info("="*60)

            Acc_=0
            Total_=0.0
            for id,(ks,uks) in problems:
                info('Analysing problem: {0}'.format(id))
                info('Answer to unknown: {0}'.format(answers[id]))
                if answers[id].startswith('Y'):
                    ANS=True
                else:
                    ANS=False

                # Load unknown
                if len(uks) > 1:
                    p.error("More than one unknown file for {0}".format(id))
                
                doc_=docread.txt(uks[0])

                # Load knowns
                docs = []
                for k in ks:
                    docs.append((k,docread.txt(k)))
                    
                    
                verbose('Starting comparison')
                for k,doc in docs:
                    verbose('Comparing with: {0}'.format(k))
                    feats=[]
                    for n,f in distance.distances:
                        d=f(doc_,doc)
                        verbose("{0} distance".format(n).ljust(30),
                                "{0:0.4f}".format(d))
                        feats.append((n,d))
                    D=WS.val(feats)
                    info("Total distance".ljust(30),"{0:0.4f}".format(D))
                    if D > 0.0:
                        RES=True
                    else:
                        RES=False

                    if RES==ANS:
                        Acc_+=1
                    else:
                        if ANS:
                            WS.plus([(e,1) for e,f in feats ])
                            WS.minus(feats)
                        else:
                            WS.plus([(e,-1) for e,f in feats ])
                            WS.minus(feats)
                    Total_+=1
            info("Total Accuracy".ljust(30),"{0:0.4f}".format(Acc_/Total_))

            verbose("Final weights")
            verbose("".join(["{0:30s} {1:0.4f}\n".format(e,c) 
                for e,c in WS.weights()]))

                            
