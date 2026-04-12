#! /usr/bin/env python3
# (C) 2026: Hans Georg Schaathun <georg@schaathun.net>

"""
Simulator class to managa bulk image generation.
"""

import tomllib as tl

import cv2 as cv
import sys
import os
import numpy as np
import matplotlib.pyplot as plt

from . import CosmoSim

from .Arguments import CosmoParser
from .Parameters import Parameters
import pandas as pd

defaultoutcols = [ "index", "filename", "source", "lens", "chi", "R", "phi", "einsteinR", "sigma", "sigma2", "theta", "x", "y" ]


class GenericSim:
    """
    This is a generic superclass for shared methods.
    """
    def __init__(self,param=None,verbose=1):
        if verbose > 0: print( "[GenericSim] init ..." )
        if param is None: param = Parameters()
        self.verbose = verbose
    def setParameters(self):
        raise Exception("Not implemented")
    def initSim(self,sim):
        sim.makeSource( self.param )
        if verbose > 0: print ( "[initSim] ready for runSim()\n" ) ;
        sim.runSim()
        if verbose > 0: print ( "[initSim] runSim() completed\n" ) ;
        self.sim = sim
    def getActual(self):
        param = self.param
        name = self.name
        fn = os.path.join(param.get("directory"),"actual-" + str(name) + ".png" ) 
        im = self.sim.getActualImage( reflines=param.get( "reflines" ) )
        cv.imwrite(fn,im)
    def getApparent(self):
        param = self.param
        name = self.name
        fn = os.path.join(param.get("directory"),"apparent-" + str(name) + ".png" ) 
        im = self.sim.getApparentImage( reflines=param.get( "reflines" ) )
        cv.imwrite(fn,im)
    def getAnnotated(self,centred=None,cropsize=None):
        """
        Stub for a future function to get an image with annotations.
        """
        im = self.sim.getDistortedImage( critical=True )
        im = annotatePoint( im, self.centrepoint, colour=( 64, 255, 64 ) )
        pt = self.sim.getXiOffset( (0,0) )
        im = annotatePoint( im, pt, colour=( 64, 64, 255 ) )
        x, y = pt
        convradius = np.sqrt( x*x + y*y )
        im = annotateCircle( im, pt, radius=convradius, colour=( 64, 64, 255 ) )
        return im
    def getImage(self,centred=None,cropsize=None):
        param = self.param
        if centred is None: centred = param.get( "centred" )
        if centred:
            im = self.centreimage
        else:
            im = self.image
        if cropsize is None: cropsize = param.get( "cropsize" )
        if cropsize:
            im = crop(im,int( param.get( "cropsize" ) ))
        if param.get( "reflines" ):
            drawAxes(im)
        return im
    def saveImage(self,name=None):
        im = self.getImage()
        if name is None:
            name = self.name
        if self.directory is None:
            fn = str(name) + ".png"
        else:
            fn = os.path.join(self.directory, str(name) + ".png" )
        cv.imwrite(fn,im)
