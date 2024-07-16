#! /usr/bin/env python3
# (C) 2024: Hans Georg Schaathun <georg@schaathun.net>

"""
Symbolically differentiate the lens potential of the SIE lens.

- `n` is the maximum number of terms
- `nproc` is the number of threads
"""

import multiprocessing as mp
import sys
import time
import argparse

import sympy
from libamplitudes import *
from sympy import symbols, sqrt, diff, sin, cos, asin, atan2, asinh

def zeroth(lens="SIS"):
    raise "Unknown lens model"

class AmplitudesCalculator:
    def __init__(self,lens="SIE",maxn=7,verbose=False):
        self.verbose = verbose
        if lens == "SIS":
            (a,b,x,y) = psiSIS()
        if lens == "SIE":
            (a,b,x,y) = psiSIE()
        self.dict = { (1,0) : a, (0,1) : b }
        if self.verbose:
            self.diagnostic(1,0)
            self.diagnostic(0,1)
        self.x = x
        self.y = y
        self.maxn = maxn
        manager = mp.Manager()
        self.queue = manager.Queue()
        self.jobs = []
    def diagnostic(self,i,j):
        print( i, j, self.dict[(i,j)] )
    def run(self,np=None):
        if np == None:
            nproc == self.maxn+1
        else:
            npproc = np
        with mp.Pool(processes=nproc) as pool:
            pass
    def __call__(self,i,j):
        if i == 0:
           res = sympy.simplify( diff( self.dict[(i,j-1)], self.y ) )
        else:
           res = sympy.simplify( diff( self.dict[(i-1,j)], self.x ) )
        res = self.dict[(i,j)]
        if self.verbose:  self.diagnostic(i,j)
        return res

def makeAmplitude(q):
        i,j,f,x,y = q.get()
        if i == 0:
           res = sympy.simplify( diff( f, y ) )
        else:
           res = sympy.simplify( diff( f, x ) )
        res = self.dict[(i,j)]
        if self.verbose:  self.diagnostic(i,j)
        return res

def main(lens="SIS",n=50,nproc=None,fn=None):

    global num_processes

    if nproc is None: nproc = n
    print( f"Using {nproc} CPUs" )

    
    # The filename is generated from the number of amplitudes
    if fn is None: fn = str(n) + '.txt'

    start = time.time()

    c = AmplitudesCalculator(verbose=True)

    for i in range(2,n+1):
        for j in range(i):
            c( i-j, j )
        c( 0, i )

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
