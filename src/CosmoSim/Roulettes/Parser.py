# (C) 2026: Hans Georg Schaathun <georg@schaathun.net> 

"""
Evaluate roulette amplitudes using `sympy` in python.

This module has been created for debugging, to validate calculations made in
C++.  It seems to be easier to compute with arbitrary precision in python/sympy
than in C++/symengine.
"""

import sympy

def eval1(expr,x,y,g,precision=64):
    """
    Evaluate the expression `expr` substituting for `x`, `y`, and `g` in 
    high precision.

    This is a sketch.
    """
    x0,y0,g0 = sympy.symbols("x,y,g")
    return expr.evalf( precision, subs={ x0: x, y0: y, g0: g } )


class RouletteParser:
    """ Parse, manage, and evaluate algebraic expressions for roulette amplitudes.
    """
    def __init__(self,fn,verbosity=1):
        with open(fn, 'r') as f:
            if verbosity: print( "Opened file", fn ) 
            c = f.read()
        cs = [ x.split(":") for x in c.split() ]
        self.alpha = {}
        self.beta = {}
        for x in cs:
            m,s,a,b = x
            self.alpha[(m,s)] = a
            self.beta[(m,s)] = b
     def alphaXi(self,m,s,x,y,g):
         """get `alpha[m][s]` for Einstein radius `g` at the point (`x`,`y`). """
         return eval1(self.alpha[(m,s)],x,y,g)
     def betaXi(self,m,s,x,y,g):
         """get `beta[m][s]` for Einstein radius `g` at the point (`x`,`y`). """
         return eval1(self.beta[(m,s)],x,y,g)
