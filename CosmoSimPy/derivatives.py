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
import queue

import sympy
from libamplitudes import *
from sympy import symbols, sqrt, diff, sin, cos, asin, atan2, asinh, binomial

def firstworker(q,outq,maxm=6):
    print ( os.getpid(),"working" )
    while True:
        i,j,f,x,y = q.get(True)   # Blocks until there is a job on the queue
        if i == 0:
           res = sympy.simplify( diff( f, y ) )
        else:
           res = sympy.simplify( diff( f, x ) )
        if i+j < maxm:     # Submit jobs for next round
            q.put( (i+1, j, res, x, y) ) 
            if i==0:
               q.put( (0, j+1, res, x, y) ) 
        print( "I", os.getpid(), i, j )
        outq.put( (i,j,res) )
        q.task_done()     # Tell the queue that the job is complete

        # Note that new jobs are submitted to the queue before 
        # `q.task_done()` is called.  Hence the queue will not be
        # empty if the current job should spawn new ones. 
    print ( "I.", os.getpid(),"returning" )


def getDict(n=50,nproc=None):
    q = mp.JoinableQueue()  # Input queue.  It is joinable to control completion.
    outq = mp.Queue()       # Output queue

    # Get and store the initial case m+s=1
    (a,b,x,y) = psiSIE0()
    resDict = { (1,0) : a, (0,1) : b }

    # Submit first round of jobs
    q.put( (2,0,a,x,y) )
    q.put( (1,1,a,x,y) )
    q.put( (0,2,b,x,y) )

    # Create a pool of workers to process the input queue.
    with mp.Pool(nproc, firstworker,(q,outq,n,)) as pool: 

       q.join()   # Block until the input jobs are completed
       print( "I getDict() joined queue" )

    print( "I pool closed" )

    while not outq.empty():
        print( "I. attempt to get from queue, size", outq.qsize() )
        i,j,res = outq.get(False)
        print( "I storing",  i, j )
        resDict[(i,j)] = res
        print( "I stored",  i, j )
    print( "I getDict returns" )
    return resDict

def secondworker(q,outq,diff1,theta ):
    print ( os.getpid(),"working" )
    cont = True
    while cont:
      try:
        m,n = q.get(False)   # does not block
        res = sympy.simplify(sum( [
                  binomial( m+n, i+j )*
                  cos(theta)**(m-i+j)*
                  sin(theta)**(n-j+i)*
                  (-1)**i
                  * diff1[(m-i+j,n-j+i)]
                  for i in range(m+1) for j in range(n+1) ] ) )
        print( "II.", os.getpid(), m, n )
        outq.put( (m,n,res) )
      except queue.Empty:
        print ( "II.", os.getpid(), "completes" )
        cont = False

    print ( "II.", os.getpid(),"returning" )

def getDiff(n,nproc,diff1):
    q = mp.Queue()          # Input queue
    outq = mp.Queue()       # Output queue

    psidiff = {}
    theta = symbols("p",positive=True,real=True)
    for i in range(n+1):
       for j in range(n-i+1):
           if i+j > 0: q.put((i,j))
    pool = mp.Pool(nproc, secondworker,(q,outq,diff1,theta))
    q.close()
    pool.close()
    pool.join()
    print( "II. pool closed" )

    while not outq.empty():
        i,j,res = outq.get()
        psidiff[(i,j)] = res

    print( "II. getDiff returns" )
    return psidiff

def gamma(m,s,chi):
    if (m+s)%2 == 0:
        return 0
    else:
        if s == 0:
            r = -1/2
        else:
            r = -1
        r *= chi**(m+1)
        r /= 2**m
        r *= binomial( m+1, (m+1-s)/2 )
        return r
def thirdworker(q,outq,diff2,chi ):
    print ( os.getpid(),"working" )
    cont = True
    while cont:
      try:
        m,n = q.get(False)   # does not block
        a = sympy.simplify( sum( [
                  (-1)**k
                  * binomial( s, 2*k )
                  * diff1[(s-2*k,2*k)]
                  for k in range(s/2+1) ] ) )
        b = sympy.simplify( sum( [
                  (-1)**k
                  * binomial( s, 2*k+1 )
                  * diff1[(s-2*k-1,2*k+1)]
                  for k in range((s-1)/2+1) ] ) )
        c = gamma(m,s,chi)
        a *= c
        b *= c
        print( "III.", os.getpid(), m, n )
        outq.put((m,n,a,b))
      except queue.Empty:
        print ( "III.", os.getpid(), "completes" )
        cont = False

    print ( "III.", os.getpid(),"returning" )

def getAmplitudes(n,nproc,diff2):
    q = mp.Queue()          # Input queue
    outq = mp.Queue()       # Output queue

    rdict = {}

    for m in range(n+1):
       for s in range((m+1)%2,m+2,2):
           q.put((m,s))
    chi = symbols("c",positive=True,real=True)
    pool = mp.Pool(nproc, thirdworker,(q,outq,diff2,chi))
    q.close()
    pool.close()
    pool.join()
    print( "III pool closed" )

    while not outq.empty():
        i,j,a,b = outq.get()
        rdict[(i,j)] = (a,b)

    print( "III getAmplitudes returns" )
    return rdict


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate roulette amplitude formulæ for CosmoSim.')
    parser.add_argument('n', metavar='N', type=int, nargs="?", default=50,
                    help='Max m (number of terms)')
    parser.add_argument('nproc', type=int, nargs="?",
                    help='Number of processes.')
    parser.add_argument('--output', help='Output filename')
    parser.add_argument('--diff', default=False,action="store_true",
                    help='Simply differentiate psi')
    args = parser.parse_args()

    n = args.n
    if args.nproc is None: 
        nproc = n
    else:
        nproc = args.nproc
    print( f"Using {nproc} CPUs" )
    
    # The filename is generated from the number of amplitudes
    if args.output is None:
        fn = str(n) + '.txt'
    else:
        fn = args.fn

    start = time.time()
    diff1 = getDict(n,nproc)
    diff2 = getDiff(n,nproc,diff1)
    alphabeta = getAmplitudes(n,nproc,diff2)

    print( "Time spent:", time.time() - start)
