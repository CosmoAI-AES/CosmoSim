#! /usr/bin/env python3
# (C) 2024: Hans Georg Schaathun <georg@schaathun.net>

"""
Symbolically differentiate the lens potential of the SIE lens.

- `n` is the maximum number of terms
- `nproc` is the number of threads
"""

import multiprocessing as mp
import sys
import os
import time
import argparse

import sympy
from libamplitudes import *
from sympy import symbols, sqrt, diff, sin, cos, asin, atan2, asinh

def mainworker(q,outq,maxm=6):
    print ( os.getpid(),"working" )
    while True:
        i,j,f,x,y = q.get(True)   # Blocks until there is a job on the queue
        if i == 0:
           res = sympy.simplify( diff( f, y ) )
        else:
           res = sympy.simplify( diff( f, x ) )
        if i < maxm:     # Submit jobs for next round
            q.put( (i+1, j, res, x, y) ) 
            if i==0:
               q.put( (0, j+1, res, x, y) ) 
        print( os.getpid(), i, j, res )
        outq.put( (i,j,res) )
        q.task_done()     # Tell the queue that the job is complete

        # Note that new jobs are submitted to the queue before 
        # `q.task_done()` is called.  Hence the queue will not be
        # empty if the current job should spawn new ones. 


def main(lens="SIS",n=50,nproc=None,fn=None):

    if nproc is None: nproc = n
    print( f"Using {nproc} CPUs" )
    
    # The filename is generated from the number of amplitudes
    if fn is None: fn = str(n) + '.txt'

    start = time.time()

    q = mp.JoinableQueue()  # Input queue.  It is joinable to control completion.
    outq = mp.Queue()       # Output queue

    # Get and store the initial case m+s=1
    (a,b,x,y) = psiSIE()
    dict = { (1,0) : a, (0,1) : b }

    # Submit first round of jobs
    q.put( (2,0,a,x,y) )
    q.put( (1,1,a,x,y) )
    q.put( (0,2,b,x,y) )

    # Create a pool of workers to process the input queue.
    pool = mp.Pool(nproc, mainworker,(q,outq,n,))

    q.join()   # Block until the input jobs are completed

    print( "Time spent:", time.time() - start)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate roulette amplitude formulæ for CosmoSim.')
    parser.add_argument('n', metavar='N', type=int, nargs="?", default=50,
                    help='Max m (number of terms)')
    parser.add_argument('nproc', type=int, nargs="?",
                    help='Number of processes.')
    parser.add_argument('--lens', default="SIE",
                    help='Lens model')
    parser.add_argument('--output', help='Output filename')
    parser.add_argument('--diff', default=False,action="store_true",
                    help='Simply differentiate psi')
    args = parser.parse_args()

    main(lens=args.lens,n=args.n,nproc=args.nproc,fn=args.output)
