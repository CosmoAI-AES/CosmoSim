#! /usr/bin/env python3
# (C) 2023: Hans Georg Schaathun <georg@schaathun.net>

"""
Generate the 50.txt file containing expressions for alpha and beta
for the SIS model in Roulettes.

Usage: `python3 Amplitudes_gen.py [n [nproc]]`

- `n` is the maximum number of terms
- `nproc` is the number of threads
"""

import multiprocessing as mp
import sys
import time
import argparse

import sympy
from sympy import symbols, sqrt, diff, sin, cos, asin, atan2, asinh

def identity(f): return f

def listener(fn,q):
    '''Listens for messages on the Queue q and writes to file `fn`. '''
    print( "Listener starts with file ", fn ) 
    with open(fn, 'w') as f:
        print( "Opened file", fn ) 
        cont = True
        while cont:
            # print(f'Jobs running: {}')
            m = q.get()
            # print("got write job:", m)
            if m == 'kill':
                print("Done")
                cont = False
            else:
                f.write(str(m) + '\n')
                f.flush()
        print( "File writer terminated", fn ) 
        f.close()
    if hit_except: print( "Failed to open file ", fn )

def psiSIS():
    # g is the Einstein radius and (x,y) coordinates in the lens plane
    x, y = symbols('x, y', real=True)
    g = symbols("g", positive=True, real=True)
    psi = - g * sqrt(x ** 2 + y ** 2)
    alpha = sympy.factor(diff(psi, x))
    beta = sympy.factor(diff(psi, y))
    return (alpha,beta,x,y)
def psiSIE():
    # g is the Einstein radius and (x,y) coordinates in the lens plane
    x, y = symbols('x, y', real=True)
    g = symbols("g", positive=True, real=True)
    f = symbols("f", positive=True, real=True)
    p = symbols("p", positive=True, real=True)
    r = sqrt(x ** 2 + y ** 2)
    sp = sin(p)
    cp = cos(p)
    alpha = - g * sqrt( f/(1-f*f) )  * (
            cp * asinh( ( sqrt( 1-f*f )/f) * (x*cp+y*sp)/(sqrt(x ** 2 + y ** 2)) )
            -
            sp * asin( sqrt( 1-f*f )* (-x*sp+y*cp)/r )
            )
    beta = - g * sqrt( f/(1-f*f) )  * (
            sp * asinh( ( sqrt( 1-f*f )/f) * (x*cp+y*sp)/(sqrt(x ** 2 + y ** 2)) )
            +
            cp * asin( sqrt( 1-f*f )* (-x*sp+y*cp)/r )
            )
    return (alpha,beta,x,y)
def psiSIE0():
    # g is the Einstein radius and (x,y) coordinates in the lens plane
    x, y = symbols('x, y', real=True)
    g = symbols("g", positive=True, real=True)
    f = symbols("f", positive=True, real=True)
    r = sqrt(x ** 2 + y ** 2)
    alpha = - g * sqrt( f/(1-f*f) )  * asinh( ( sqrt( 1-f*f )/f) * x/r )
    beta = - g * sqrt( f/(1-f*f) )  * asin( sqrt( 1-f*f )* y/r )
    psi = - g * sqrt( f/(1-f*f) )  * ( y * asin( sqrt( 1-f*f )* y/r )
                                      + x * asinh( ( sqrt( 1-f*f )/f) * x/r ) )
    return (psi,alpha,beta,x,y)
