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
    if lens == "SIS":
        return psiSIS()
    if lens == "SIE":
        return psiSIE()
    raise "Unknown lens model"

def main(lens="SIS",n=50,nproc=None,fn=None):

    global num_processes

    if nproc is None: nproc = n
    print( f"Using {nproc} CPUs" )

    
    # The filename is generated from the number of amplitudes
    if fn is None: fn = str(n) + '.txt'

    start = time.time()

    # Must use Manager queue here, or will not work
    manager = mp.Manager()
    q = manager.Queue()


    alpha, beta, x, y = zeroth(lens)

    d = { (1,0) : alpha, (0,1) : beta }

    for i in range(2,n+1):
        for j in range(i):
            d[(i-j,j)] = diff( d[i-j-1,j], x )
        d[(0,i)] = diff( d[0,i-1], y )


    print( "Time spent:", time.time() - start)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate roulette amplitude formulæ for CosmoSim.')
    parser.add_argument('n', metavar='N', type=int, nargs="?", default=50,
                    help='Max m (number of terms)')
    parser.add_argument('nproc', type=int, nargs="?",
                    help='Number of processes.')
    parser.add_argument('--lens', default="SIS",
                    help='Lens model')
    parser.add_argument('--output', help='Output filename')
    parser.add_argument('--diff', default=False,action="store_true",
                    help='Simply differentiate psi')
    args = parser.parse_args()

    main(lens=args.lens,n=args.n,nproc=args.nproc,fn=args.output)
