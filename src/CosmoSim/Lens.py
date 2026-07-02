# (C) 26: Hans Georg Schaathun <georg@schaathun.net> 

"""
Python wrappers for Lens classes from C++.  The main purpose of the
wrappers is to reference constituent objects and prevent garbage collection.
"""

from . import CosmoSimPy as cs

class SampledPsiFunctionLens(cs.SampledPsiFunctionLens):
    def __init__(self,lens,size,verbose=1):
        self.lens = lens
        return super().__init__( lens, size )
