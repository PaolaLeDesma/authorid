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

# System libraries
import optparse
import sys
import os
import os.path
import itertools

# ML libraries
import numpy as np
from sklearn import svm
from sklearn import preprocessing

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


        samples=[]
        classes=[]
        # Transforms documents into samples 
        for id,(ks,uks) in problems:
            info('Reading from : {0}'.format(id))
            info('Answer to unknown: {0}'.format(answers[id]))
            if answers[id].startswith('Y'):
                ANS=1
            else:
                ANS=0

            # Load unknown 
            if len(uks) > 1:
                p.error("More than one unknown file for {0}".format(id))
            
            doc_=docread.trigram(uks[0])

            # Load knowns 
            docs = []
            for k in ks:
                docs.append((k,docread.trigram(k)))
                
                
            verbose('Starting comparison')
            samples_=[]
            classes_=[]
            for k,doc in docs:
                verbose('Comparing with: {0}'.format(k))
                feats=[]
                for n,f in distance.distances:
                    d=f(doc_,doc)
                    verbose("{0} distance".format(n).ljust(30),
                            "{0:0.4f}".format(d))
                    feats.append(d)
                samples_.append(feats)
                classes_.append(ANS)
            samples.append(samples_)
            classes.append(classes_)
        # ML
        N_Acc_=0
        Total_=0.0
        # 1-leave-out
        for i in range(len(samples)):
            X_train = samples[:i]+samples[i+1:]
            X_train = np.array(list(itertools.chain(*X_train)))
            X_test  = np.array(samples[i])
            Y_train = classes[:i]+classes[i+1:]
            Y_train = np.array(list(itertools.chain(*Y_train)))
            Y_test = np.array(classes[i])

            svc = svm.SVC(kernel='poly',C=1.0,gamma=0.2)
            svc.fit(X_train,Y_train)
            preds = svc.predict(X_test) 
            
            for x,x_ in zip(preds,Y_test):
                if x==x_:
                    N_Acc_+=1
                Total_+=1

        info('Accuracy : {0:04f}'.format(N_Acc_/Total_))

