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
import sieamplitudes as s1
import sieorig as s2
from sympy import symbols, diff, sin, cos, asin, atan2, asinh, binomial


def main():
    parser = argparse.ArgumentParser(description='Generate roulette amplitude formulæ for CosmoSim.')
    parser.add_argument('n', metavar='N', type=int, nargs="?", default=50,
                    help='Max m (number of terms)')
    parser.add_argument('nproc', type=int, nargs="?",
                    help='Number of processes.')
    parser.add_argument('--output', help='Output filename')
    parser.add_argument('--diff', default=False,action="store_true",
                    help='Simply differentiate psi')
    parser.add_argument('--lens', default="SIE",
                    help='Lens model')
    parser.add_argument('--tex', 
                    help='TeX output file')
    args = parser.parse_args()

    n = args.n
    if args.nproc is None: 
        nproc = n
    else:
        nproc = args.nproc
    print( f"Using {nproc} CPUs" )

    psivec = zeroth( args.lens )
    
    mgr1 = s1.RouletteManager( psivec=psivec,thirdworker=s1.thirdworker )
    ab1 = mgr1.getAmplitudes(n,nproc )
    mgr2 = s1.RouletteManager( psivec=psivec,thirdworker=s2.thirdworker )
    ab2 = mgr1.getAmplitudes(n,nproc )

    for (m,s) in ab1.keys():
        a1,b1 = ab1[(m,s)] 
        a2,b2 = ab2[(m,s)] 
        print( f"a{(m,s)}={sympy.simplify(a1-a2)}" )
        print( f"b{(m,s)}={sympy.simplify(b1-b2)}" )

if __name__ == "__main__":
    main()
