#! /usr/bin/env python3
# (C) 2026: Hans Georg Schaathun <georg@schaathun.net>

"""
Simulator class to manage bulk image generation.

Different subclasses are required for different backend simulators, like
`RouletteRegenerator` and `CosmoSim`.
The `GenericSim` superclass contains shared methods.

The constructor may takes a data row, typically a pandas Series object,
reconfigures the backend simulator, and generates the distorted image.
Since the object retains much of the simulation data, extensive information
and annotated images may be retrieved as well.

The constructor may take a backend simulator instance as parameter.  This saves
the cost of reinstantiation in bulk simulation, and it also leaves the possibility
to set defaults in advance.
"""

import tomllib as tl

import cv2 as cv
import sys
import os
import numpy as np
import matplotlib.pyplot as plt

from . import CosmoSim

from .Image import centreImage, drawAxes, crop, annotatePoint, annotateCircle, translateImage

from .Arguments import CosmoParser
from . import Parameters
import pandas as pd

defaultoutcols = [ "index", "filename", "source", "lens", "chi", "R", "phi", "einsteinR", "sigma", "sigma2", "theta", "x", "y" ]

class GenericSim:
    """
    This is a generic superclass for shared methods.
    """
    def __init__(self,param=None,row=None,name=None,outcols=None,verbose=1):
        if verbose > 1: print( "[GenericSim] init ..." )
        self.verbose = verbose

        self.outcols = outcols

        self.name = name
        if param is None: 
            if verbose: print( "[GenericSim] No parameters give. Using defaults" )
            param = Parameters()
        self.param = param
        self.directory = param.get( "directory" )
        if self.directory:
            os.makedirs( self.directory, exist_ok=True )

    def setParameters(self,row):
        """
        Reset parameters in the backend simulator, using the given data row.
        This is an auxiliary for `initSim()` and will normally have to be 
        overridden depending on the class of the backend simulator.
        """
        raise NotImplementedError()
    def initSim(self,row):
        """
        Run the simulator with the given data row.
        """
        if not row is None:
            if self.verbose > 1: print( "[initSim] using row" )
            self.setParameters( row )
            if self.verbose > 1: print( "index", row.get( "index", None ) )
            self.param.setRow( row )
            try:
                name = row.name.split(".")[0]
            except:
                name = row["filename"].split(".")[0]
            self.row = row
            self.name = name
        elif self.verbose > 1: print( "[initSim] row is None" )
        if self.name is None:
            self.name = self.param.get( "name" )
        if self.verbose>1: print( "[initSim] item name:", self.name )

        self.runSim()

        self.image = self.getDistortedImage( )
        (self.centreimage,self.centrepoint) = centreImage(self.image)
        if self.verbose: print(
                "[datagen.py] Centre Point", self.centrepoint,
                "(Centre of Luminence in Planar Co-ordinates)" )
    def getDistortedImage(self):
        return  self.sim.getDistortedImage( 
                         critical=self.param.get( "criticalcurves" ),
                         showmask=self.param.get( "showmask" ) ) 
    def setParameters(self):
        raise Exception("Not implemented")
    def runSim(self):
        if self.verbose>2: print( "[runSim]" )
        self.sim.makeSource( self.param )
        if self.verbose > 1: print ( "[GenericSim] ready for runSim()\n" ) ;
        self.sim.runSim()
        if self.verbose > 1: print ( "[GenericSim] runSim() completed\n" ) ;
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
        if cropsize is None: cropsize = self.param.get( "cropsize" )
        if cropsize:
            im = crop(im,int( cropsize ) )
        return im
    def getImage(self,centred=None,cropsize=None):
        if centred is None: centred = self.param.get( "centred" )
        if centred:
            im = self.centreimage
        else:
            im = self.image
        if cropsize is None: cropsize = self.param.get( "cropsize" )
        if cropsize:
            im = crop(im,int( cropsize ) )
        if self.param.get( "reflines" ):
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
        if self.verbose: print( "[saveImage]", fn )
        cv.imwrite(fn,im)
