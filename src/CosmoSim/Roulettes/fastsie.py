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
from .libamplitudes import *

from .sie import thirdworker, RouletteManager
# def thirdworker(q,ampdict,indict, var=[] ):
from .sie2026 import find_exp_cof

def symdiff( dd ):
    x, y = sympy.symbols( "x y", real=True )
    f = sympy.symbols("f", positive=True, real=True)
    g = sympy.symbols( "g", positive=True, real=True )

    theta = sympy.symbols( "p", real=True )
    x1 = sympy.cos(theta)*x+sympy.sin(theta)*y
    y1 = -sympy.sin(theta)*x+sympy.cos(theta)*y 
    r = sympy.sqrt( x**2 + y**2 )
    f1 = sympy.sqrt( 1 - f**2 )
    r1 = sympy.sqrt( r**2 - f1**2*y1**2 )

    ss = [ x, y, x1, y1, f, f1, r, r1 ]
    prf = g*sympy.sqrt( f )

    # Compute higher order derivatives using Theorem 3.
    res = { k : prf*sum( [ c*sympy.prod( [ a**b for a,b in zip(ss,e) ] ) 
                      for (c,e) in dd[k] ] )
                   / (r*r*r1)**(2*sum(k)-3)
           for k in dd }

    # Add the first order derivatives using Theorem 1.
    prf1 = prf/f1
    a = sympy.asinh( ( f1 / f ) * x1/r )
    b = sympy.asin( f1* y1/r )
    res[(1,0)] = prf1*(sympy.cos(theta)*a - sympy.sin(theta)*b)
    res[(0,1)] = prf1*(sympy.sin(theta)*a + sympy.cos(theta)*b)

    return res


class FastRoulette(RouletteManager):
    def __init__(self,thirdworker=thirdworker):
       self.mgr = mp.Manager()      
       self.psivec = psiSIE()
       self.thirdworker = thirdworker
       self.vars = sympy.symbols( "x y", real=True )

    def getDict(self,n=50,nproc=None):
        pass
    def getDiff(self,n,nproc):
        dd = find_exp_cof( order=n+1 )
        self.psidiff = symdiff( dd )

        print( "[fastsie] getDiff returns")
        return self.psidiff


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate roulette amplitude formulæ for CosmoSim.')
    parser.add_argument('n', metavar='N', type=int, nargs="?", default=50,
                    help='Max m (number of terms)')
    parser.add_argument('nproc', type=int, nargs="?",
                    help='Number of processes.')
    parser.add_argument('--output', help='Output filename')
    parser.add_argument('--tex', 
                    help='TeX output file')
    args = parser.parse_args()

    n = args.n
    if args.nproc is None: 
        nproc = n
    else:
        nproc = args.nproc
    print( f"Using {nproc} CPUs" )

    mgr = FastRoulette( )
    alphabeta = mgr.getAmplitudes(n,nproc )

    if args.output:
       ampPrint(alphabeta,args.output)
    if args.tex:
       texPrint(alphabeta,args.tex,latex=sympy.latex,opt="10pt,paper=a0,landscape")
    print( "sieamplitudes.py: completing" )

