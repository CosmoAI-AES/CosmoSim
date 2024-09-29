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
from sympy import symbols, diff, sin, cos, asin, atan2, asinh, binomial

from sieamplitudes import firstworker, secondworker, RouletteManager, main

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
def innersum(diffdict,m,s):
    c =  m+1-s
    if c%2 == 1:
        raise RuntimeError( "m-s is even" )
    H = int(c/2)
    a = lambda k : sum( [
          binomial(H,i) *
          diffdict[m+1-2*k-2*i,2*k+2*i]
          for i in range(H+1)
        ] )
    b = lambda k : sum( [
          binomial(H,i) *
          diffdict[m-2*k-2*i,2*k+2*i+1]
          for i in range(H+1)
        ] )
    return (a,b)
def thirdworker(q,ampdict,indict, var=[] ):
    print ( os.getpid(),"sieorig thirdworker working" )
    cont = True
    while cont:
      try:
        m,s = q.get(False)   # does not block
        c = gamma(m,s)
        if c == 0:
            a = 0
            b = 0
        else:
            (h1,h2) = innersum(indict,m,s)
            a = c*sympy.collect( sum( [
                  (-1)**k
                  * binomial( s, 2*k )
                  * h1(k)
                  for k in range(int(s/2+1)) ] ),
                  var )
            b = c*sympy.collect( sum( [
                  (-1)**k
                  * binomial( s, 2*k+1 )
                  * h2(k)
                  for k in range(int((s-1)/2+1)) ] ),
                  var )
        print( "III.", os.getpid(), m, s )
        ampdict[(m,s)] = (a,b)
      except queue.Empty:
        print ( "III.", os.getpid(), "completes" )
        cont = False

    print ( "III.", os.getpid(),"returning" )

if __name__ == "__main__":
    main(thirdworker)
