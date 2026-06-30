# (C) 2022-26: Hans Georg Schaathun <georg@schaathun.net> 

"""
The CosmoSim package comprises several components, including scripts,
GUI, and API.

The root module provides wrappers around most of the C++ classes,
to make the python API more streamlined.
"""

from . import CosmoSimPy as cs
import numpy as np
import pandas as pd
import threading as th
import os, sys

from .CLI import Arguments

from .Dictionary import *

Parameters = Arguments.Parameters
setDebug = cs.setDebug

__version__ = "3.2.0b1"

def getSourceFileName():
    """
    Get the filename for an image source.
    """
    dir = os.path.dirname(os.path.abspath(__file__))
    return( os.path.join( dir, f"einstein.png" ) )

def getPathFN(fn):
    dir = os.path.dirname(os.path.abspath(__file__))
    return  os.path.join( dir, fn )

maxmlist = [ 50, 100, 200 ]
def getFileName(maxm):
    """
    Get the filename for the amplitudes files.
    The argument `maxm` is the maximum number of terms (nterms) to be
    used in the simulator.
    """
    dir = os.path.dirname(os.path.abspath(__file__))
    for m in maxmlist:
        m0 = m
        if maxm <= m:
            return( os.path.join( dir, f"sis{m}.txt" ) )
    raise Exception( f"Cannot support m > {m0}." )

