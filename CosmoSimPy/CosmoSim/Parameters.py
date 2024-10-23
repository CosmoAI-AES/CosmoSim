# (C) 2024: Hans Georg Schaathun <georg@schaathun.net> 

from CosmoSim import sourceDict
import numpy as np

class Parameters:
    """
    The Parameters class wraps the commandline arguments as well as a CSV 
    row as a dict-like object.
    """
    def __init__(self,args):
        self._args = args
        self._row = {}
    def setRow(self,row):
        self._row = row
    def get(self,key,default=None):
        print( "Parameters.get(", key, ")" )
        try:
            r = self._args.__dict__[key]
        except AttributeError:
            print( self._args )
            r = default
        print( "Parameters.get() args ->", r )
        r = self._row.get(key,r)
        print( "Parameters.get() row ->", r )
        return r
    def __getitem__(self,key):
        return get(key)
    def __setitem__(self,key,v):
        self._row[key] = v

