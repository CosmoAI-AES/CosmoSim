# (C) 2022-26: Hans Georg Schaathun <georg@schaathun.net> 

"""
The CosmoSim package comprises several components, including scripts,
GUI, and API.

The root module provides wrappers around most of the C++ classes,
to make the python API more streamlined.
"""

from .CLI import Arguments
from . import CosmoSimPy

Parameters = Arguments.Parameters
setDebug = CosmoSimPy.setDebug

__version__ = "3.0.3"
