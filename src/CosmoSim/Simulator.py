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
    def __init__(self,param=None,row=None,outcols=None,verbose=1):
        if verbose > 0: print( "[GenericSim] init ..." )
        self.verbose = verbose

        self.outcols = outcols

        if param is None: param = Parameters()
        self.param = param
        self.directory = param.get( "directory" )
        if self.directory:
            os.makedirs( self.directory, exist_ok=True )

    def initSim(self,row):
        if not row is None:
            self.setParameters( row )
            if self.verbose: print( "index", row.get( "index", None ) )
            self.param.setRow( row )
            try:
                name = row.name.split(".")[0]
            except:
                name = row["filename"].split(".")[0]
            self.row = row
        elif name == None:
            name = self.param.get( "name" )
        self.name = name

        self.image = self.sim.getDistortedImage( 
                         critical=self.param.get( "criticalcurves" ),
                         showmask=self.param.get( "showmask" ) ) 
        (self.centreimage,self.centrepoint) = centreImage(self.image)
        print( "[datagen.py] Centre Point", self.centrepoint,
              "(Centre of Luminence in Planar Co-ordinates)" )
    def setParameters(self):
        raise Exception("Not implemented")
    def runSim(self):
        self.sim.makeSource( self.param )
        if verbose > 0: print ( "[initSim] ready for runSim()\n" ) ;
        self.sim.runSim()
        if self.verbose > 0: print ( "[initSim] runSim() completed\n" ) ;
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
