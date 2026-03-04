# (C) 2024: Hans Georg Schaathun <georg@schaathun.net> 

from CosmoSim import sourceDict
import numpy as np

class Args:
    def __init__(self):
        self.__dict__ = {}

class Arg:
    pass

class Parameters:
    """
    The Parameters class wraps the commandline arguments as well as a CSV 
    row as a dict-like object.
    """
    def __init__(self,args=None,cfg=None):
        if args:
            self._args = args
        else:
            self._args = Arg()
        self._row = {}
        if cfg:
            cfg1 = cfg["simulator"]
            if "cropsize" not in self._args.__dict__:
                self._args.cropsize = cfg1.get( "cropsize", 256 )
            if "imagesize" not in self._args.__dict__:
                self._args.imagesize = cfg1.get( "imagesize", 512 )
            if "source" not in self._args.__dict__:
                try:
                    self._args.source = cfg["source"]["mode"]
                except:
                    self._args.source = None
    def setRow(self,row):
        self._row = row
    def get(self,key,default=None):
        if self._args is None:
            r = default
        else:
            try:
                r = self._args.__dict__[key]
            except KeyError:
                print( self._args )
                r = default
        r = self._row.get(key,r)
        return r
    def __getitem__(self,key):
        return get(key)
    def __setitem__(self,key,v):
        self._row[key] = v

