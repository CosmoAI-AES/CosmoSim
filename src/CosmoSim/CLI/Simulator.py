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

import cv2 as cv
import sys
import os
import numpy as np
import matplotlib.pyplot as plt

from .. import CosmoSim

from ..Image import centreImage, drawAxes, crop, annotatePoint, annotateCircle, translateImage

from .Arguments import CosmoParser, Parameters
import pandas as pd

defaultoutcols = [ "index", "filename", "source", "lens", "chi", "R", "phi"
                 , "einsteinR", "sigma", "sigma2", "theta", "x", "y" ]

class GenericSim:
    """
    This is a generic superclass for shared methods.
    """
    def __init__(self,param=None,name=None,outcols=None,verbose=1):
        """
        Normally the constructor should
        """
        if verbose is None: verbose=1
        self.verbose = verbose
        if verbose > 1: print( f"[GenericSim] init (verbose={verbose}) ..." )

        self.outcols = outcols

        self.name = name
        if param is None: 
            if verbose: print( "[GenericSim] No parameters given. Using defaults" )
            param = Parameters()
        self.param = param
        self.directory = param.get( "directory" )
        if self.directory:
            os.makedirs( self.directory, exist_ok=True )

        if self.verbose > 2:
            print( "[GenericSim] xireference =", self.param.get( "xireference" ) )

    def setParameters(self,row):
        """
        Reset parameters in the backend simulator, using the given data row.
        This is an auxiliary for `initSim()` and will normally have to be 
        overridden depending on the class of the backend simulator.
        """
        raise NotImplementedError()
    def initSim(self,row=None):
        """
        Run the simulator with the given data row.
        """
        if row is None: row = self.param
        if self.verbose > 1: print( "[initSim] using row" )
        self.setParameters( row )
        if self.verbose > 1: print( "index", row.get( "index", None ) )
        print( f"[initSim] type(row)={type(row)}" )
        # self.param.setRow( row )
        name = row.get( "filename" ).split(".")[0]
        self.name = name

        if self.verbose>1: print( "[initSim] item name:", self.name )

        self.runSim()

        self.image = self.getDistortedImage( )
        (self.centreimage,self.centrepoint) = centreImage(self.image)
        if self.verbose: 
            print( f"[Simulator] Centre Point ({self.centrepoint[0]:.2f},{self.centrepoint[1]:.2f})",
                "(Centre of Luminence in Planar Co-ordinates)" )
    def getDistortedImage(self):
        return  self.sim.getDistortedImage( 
                         critical=self.param.get( "criticalcurves" ),
                         showmask=self.param.get( "showmask" ) ) 
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
        Get an image with annotations showing key points and the convergence ring.
        This is incomplete and should be extended with addition annotations and
        options.
        """
        if centred is not None:
            raise NotImplementedError("centred option for getAnnotated() is not implemented yet.")
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
    def getImage(self,centred=None,cropsize=None,reflines=None):
        if centred is None: centred = self.param.get( "centred" )
        if reflines is None: reflines = self.param.get( "reflines" )
        if centred:
            im = self.centreimage.copy()
        else:
            im = self.image.copy()
        if cropsize is None: cropsize = self.param.get( "cropsize" )
        if cropsize:
            im = crop(im,int( cropsize ) )
        if reflines:
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
