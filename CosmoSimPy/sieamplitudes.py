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

def firstworker(q,resDict,maxm=6):
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
        print( "I.", os.getpid(), i, j )
        resDict[(i,j)] = res
        q.task_done()     # Tell the queue that the job is complete

        # Note that new jobs are submitted to the queue before 
        # `q.task_done()` is called.  Hence the queue will not be
        # empty if the current job should spawn new ones. 
    print ( "I.", os.getpid(),"returning" )


def getDict(n=50,nproc=None):

    q = mp.JoinableQueue()  # Input queue.  It is joinable to control completion.
    mgr = mp.Manager()      
    resDict = mgr.dict()     # Output data structure

    # Get and store the initial case m+s=1
    (psi,a,b,x,y) = psiSIE()
    resDict[(0,0)] = psi
    resDict[(1,0)] = a
    resDict[(0,1)] = b

    # Submit first round of jobs
    q.put( (2,0,a,x,y) )
    q.put( (1,1,a,x,y) )
    q.put( (0,2,b,x,y) )

    # Create a pool of workers to process the input queue.
    with mp.Pool(nproc, firstworker,(q,resDict,n,)) as pool: 

        q.join()   # Block until the input jobs are completed
        print( "I getDict() joined queue" )

    print( "I pool closed" )
    sys.stdout.flush()

    print( "I getDict returns" )
    sys.stdout.flush()
    return resDict, x, y

def secondworker(q,psidiff,diff1,theta ):
    print ( os.getpid(),"working" )
    cont = True
    while cont:
      try:
        m,n = q.get(False)   # does not block
        res = (sum( [
                  binomial( m, i )*
                  binomial( n, j )*
                  cos(theta)**(m-i+j)*
                  sin(theta)**(n-j+i)*
                  (-1)**i
                  * diff1[(m+n-i-j,j+i)]
                  for i in range(m+1) for j in range(n+1) ] ) )
        print( "II.", os.getpid(), m, n )
        psidiff[(m,n)] = res
      except queue.Empty:
        print ( "II.", os.getpid(), "completes" )
        cont = False

    print ( "II.", os.getpid(),"returning" )

def getDiff(n,nproc,diff1):
    mgr = mp.Manager()      
    q = mp.Queue()          # Input queue
    psidiff = mgr.dict()     # Output data structure

    theta = symbols("p",positive=True,real=True)
    for k in diff1.keys():
           q.put( k )
    pool = mp.Pool(nproc, secondworker,(q,psidiff,diff1,theta))

    q.close()
    pool.close()
    pool.join()
    print( "II. pool closed" )
    sys.stdout.flush()

    print( "II. getDiff returns")
    sys.stdout.flush()
    return psidiff

def gamma(m,s):
    if (m+s)%2 == 0:
        return 0
    else:
        if s == 0:
            r = -1/2
        else:
            r = -1
        r /= 2**m
        r *= binomial( m+1, (m+1-s)/2 )
        return r
def thirdworker(q,ampdict,indict, var=[] ):
    print ( os.getpid(),"working" )
    cont = True
    sq = indict[2,0]+indict[0,2]
    while cont:
      try:
        m,s = q.get(False)   # does not block
        c = gamma(m,s)
        if c == 0:
            a = 0
            b = 0
        else:
            c *= sq**((m+1-s)/2)
            a = c*sympy.collect( sum( [
                  (-1)**k
                  * binomial( s, 2*k )
                  * indict[(s-2*k,2*k)]
                  for k in range(int(s/2+1)) ] ),
                  var )
            b = c*sympy.collect( sum( [
                  (-1)**k
                  * binomial( s, 2*k+1 )
                  * indict[(s-2*k-1,2*k+1)]
                  for k in range(int((s-1)/2+1)) ] ),
                  var )
        print( "III.", os.getpid(), m, n )
        ampdict[(m,s)] = (a,b)
      except queue.Empty:
        print ( "III.", os.getpid(), "completes" )
        cont = False

    print ( "III.", os.getpid(),"returning" )

def getAmplitudes(n,nproc,diff2,var=[]):
    q = mp.Queue()         # Input queue
    mgr = mp.Manager()      
    rdict = mgr.dict()     # Output data structure

    for m in range(n):
       for s in range((m+1)%2,m+2,2):
           q.put((m,s))
    pool = mp.Pool(nproc, thirdworker,(q,rdict,diff2,var))

    q.close()
    pool.close()
    pool.join()
    print( "III pool closed" )
    sys.stdout.flush()

    print( "III getAmplitudes returns" )
    sys.stdout.flush()
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
        fn = "sie" + str(n) + '.txt'
    else:
        fn = args.output

    start = time.time()
    diff1,x,y = getDict(n,nproc)
    print( "Time spent:", time.time() - start)
    diff2 = getDiff(n,nproc,diff1)
    print( "Time spent:", time.time() - start)
    alphabeta = getAmplitudes(n,nproc,diff2,var=[x,y] )
    print( "Time spent:", time.time() - start)

    with open(fn, 'w') as f:
        print( "Opened file", fn ) 
        for (m,s) in alphabeta.keys():

            alpha,beta = alphabeta[(m,s)]
            res = f'{m}:{s}:{alpha}:{beta}'
            f.write(str(res) + '\n')
        f.close()

    print( "Time spent:", time.time() - start)
