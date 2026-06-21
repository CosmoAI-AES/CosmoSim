# (C) 2022-26: Hans Georg Schaathun <georg@schaathun.net> 

"""
The CosmoSim package comprises several components, including scripts,
GUI, and API.

The root module provides wrappers around most of the C++ classes,
to make the python API more streamlined.
"""

from .CLI import Arguments
from . import CosmoSimPy

import os

Parameters = Arguments.Parameters
setDebug = CosmoSimPy.setDebug

__version__ = "3.0.3"

def getSourceFileName():
    """
    Get the filename for an image source.
    """
    dir = os.path.dirname(os.path.abspath(__file__))
    return( os.path.join( dir, f"einstein.png" ) )

def getPathFN(fn):
    dir = os.path.dirname(os.path.abspath(__file__))
    return  os.path.join( dir, fn )
