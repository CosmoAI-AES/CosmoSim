# (C) 2022-26: Hans Georg Schaathun <georg@schaathun.net> 

"""
The CosmoSim package comprises several components, including scripts,
GUI, and API.

The root module provides wrappers around most of the C++ classes,
to make the python API more streamlined.
"""

from .. import CosmoSimPy as cs, getPathFN
from ..Sources import *
from ..Lens import *
from ..Dictionary import *
from ..CosmoSimPy import RouletteModel,RaytraceModel
from ..Image import drawAxes
import numpy as np
import threading as th
import os, sys

class CosmoSim:
    """
    Simulator for gravitational lensing.
    This wraps the CosmoSim library written in C++.  In particular,
    it wraps functions returning images, to convert the data to 
    numpy arrays.
    """
    def __init__(self,*a,maxm=50,verbose=1,**kw):
        super().__init__(*a,**kw)
        self.verbose = verbose
        if self.verbose>1: print( f"[CosmoSim] init (verbose={self.verbose}) ..." )
        if self.verbose > 3:
            cs.setDebug( self.verbose - 3 )
        else:
            cs.setDebug( 0 )

        self.amplitudefiles = { PsiSpec.PM : getPathFN( "pm50.txt" )
                 , PsiSpec.SIS : getPathFN( "sis50.txt" )
                 , PsiSpec.SIE : getPathFN( "sie05.txt" )
                 }
        self.bgcolour = 0
        self.imagesize = 512
        self.resolution = self.imagesize
        self._sampling = False

        self.simparam = { "nterms" : 5
             , "maskmode" : False
             } 
        self.lensparam = { "einsteinradius" : 30
             , "ellipseratio" : 0.6
             , "orientation" : 45
             } 

        self.srcparam = { "source" : "Spherical", "sigma" : 10 }
        self.lensmode = PsiSpec.SIS 
        self.simmode = ModelSpec.Raytrace 
        self._sim = None

        self.setLensMode( self.lensmode )
        self.makeSource( )
        self.setModelMode( self.simmode )

        # Set up thread management
        self._continue = True
        self.updateEvent = th.Event()
        self.simEvent = th.Event()
        self._simThread = th.Thread(target=self.simThread)
        self._simThread.start()



    def setSimParameters(self, param ):
        if param is None:
            param = self.simparam 
        else:
            self.simparam = param
        nterms = param.get( "nterms", None ) 
        if nterms is not None:
              self._sim.setNterms( nterms )
        mm = param.get( "maskmode", None ) 
        if mm is not None:
              self._sim.setMaskMode( mm )
        mr = param.get( "maskradius", None )
        if mr is not None:
              self._sim.setMaskRadius( mr )
    def setImageSize(self, size ):
        if sz is not None: self.imagesize = size
    def setImageParameters(self, param=None ):
        self.resolution = param.get( "resolution", self.resolution )
        self.bgcolour = param.get( "bgcolour", self.bgcolour )
        self.imagesize = param.get( "imagesize", self.imagesize )

    def setLensParameters(self, param=None ):
        if self.verbose:
            print( "[setLensParameters]", param )
        if param is None:
            param = self.lensparam 
        else:
            self.lensparam = param
        einsteinR = param.get( "einsteinR", None )
        if einsteinR is not None:
              self._psilens.setEinsteinR( einsteinR )
        ratio = param.get( "ratio", None ) 
        if ratio is not None:
              self._psilens.setRatio( ratio )
        orientation = param.get( "orientation", None ) 
        if orientation is not None:
              self._psilens.setOrientation( orientation )
        if self.verbose:
            print( "[setLensParameters] returns" )
    def makeSource(self,param=None):
        """
        Instantiate a new source according to the given parameters `param`.
        If a simulator is defined, the new source is added thereto.
        """
        if param is None:
            param = self.srcparam
        else:
            self.srcparam = param
        if param.get( "imagesize" ) == None:
           param.__setitem__( "imagesize", self.imagesize )
        self._src = getSource(param,verbose=self.verbose)
        if self._sim is not None:
            if self.verbose:
                print( f"GUI.CosmoSim.makeSource() add source to simulator" )

            self._sim.setSource( self._src )
        if self.verbose:
            print( f"GUI.CosmoSim.makeSource() returns (verbose={self.verbose})" )

    def setXY(self,x,y): return self._sim.setXY(x,y)
    def setPolar(self,x,y): return self._sim.setPolar(x,y)
    def setLensMode(self,lensmode,*a,**kw):
        """
        Instantiate a new lens of the given mode.
        If a simulator is defined, the new lens is added thereto.
        """
        if self.verbose:
            print( f"[setLensMode({lensmode})] instantiate" )
        self.lensmode = lensmode
        if lensmode == PsiSpec.PM:
            lens = PointMass()
        elif lensmode == PsiSpec.SIS:
            lens = SIS()
        elif lensmode == PsiSpec.SIE:
            lens = SIE()
        else:
            raise RuntimeError( "Invalid lens mode" )
        self._psilens = lens
        if self._sim is not None:
            if self.verbose:
                print( f"[setLensMode({lensmode})] add lens to simulator" )
            self._sim.setLens( lens )
        self._lens = lens
        self.setLensParameters()
        lens.setFile( self.amplitudefiles[lensmode] )
        self.setSampled()
        if self.verbose:
            print( f"[setLensMode({lensmode})] returns" )
    def setSampled(self,sampling=None,**kw):
        if sampling is None:
            sampling = self._sampling
        else:
            self._sampling = sampling
        if sampling:
            size = self.imagesize
            if self.verbose>1: print( f"[initLens] Sampling (imagesize {size})" )
            self._lens = SampledPsiFunctionLens( self._psilens, size )
        else:
            self._lens = self._psilens

    def close(self):
        """
        Terminate the worker thread.
        This should be called before terminating the program,
        because stale threads would otherwise block.
        """
        self._continue = False
        self.simEvent.set()
        self._simThread.join()
    def getUpdateEvent(self):
        return self.updateEvent
    def maskImage(self,scale=1):
        return super().maskImage( float(scale) )

    def setModelMode(self,model):
        self.simmode = model
        if self.verbose:
            print( f"[setModelMode ({model})] instantiate new simulator")

        if model == ModelSpec.Raytrace:
            sim = RaytraceModel()
        elif model == ModelSpec.Roulette:
            sim = RouletteModel()
        else:
            raise RuntimeError( "Invalid simulator mode" )
        sim.setLens( self._lens )
        sim.setSource( self._src )
        self._sim = sim
        if self.verbose:
            print( f"[setModelMode ({model})] returns")

    def setBGColour(self,s):
        self.bgcolour = s
    def simThread(self):
        """
        This function repeatedly runs the simulator when the parameters
        have changed.  It is intended to run in a dedicated thread.
        """
        while self._continue:
            self.simEvent.wait()
            if self._continue:
               self.simEvent.clear()
               self._sim.update()
               self.updateEvent.set()
    def runSimulator(self):
        """
        Run the simulator; that is, tell it that the parameters
        have changed.  This triggers an event which will be handled
        when the simulator is idle.
        """
        if self.verbose: print( "CosmoSim.runSimulator() [python]" )
        self.simEvent.set()
        if self.verbose: print( "CosmoSim.runSimulator() triggered event" )

    def getActualImage(self,reflines=True,caustics=False):
        """
        Return the Actual Image from the simulator as a numpy array.
        """
        im = self._sim.getActual()
        if self.resolution < self.imagesize:
            im = cv.resize( im, ( self.resolution, self.resolution ) )
        if caustics:
            sim.drawCaustics( im )
        im = np.array(im)
        if reflines:
            csimg.drawAxes( im )
        if im.shape[2] == 1 :
            im.shape = im.shape[:2]
        return np.maximum(im,self.bgcolour)
    def showMask(self): return self._sim.markMask()
    def maskImage(self,scale): return self._sim.maskImage( scale )
    def getDistortedImage(self,reflines=False,critical=False,mask=False,showmask=False):
        """
        Return the Distorted Image from the simulator as a numpy array.
        """
        try:
            if mask: self.maskImage()
            if showmask: self.showMask()
        except:
            print( "Masking not supported for this lens model." )
        im = self._sim.getDistorted()
        if self.resolution < self.imagesize:
            im = cv.resize( im, ( self.resolution, self.resolution ) )
        if critical:
            self._sim.drawCritical( im )
        im = np.array(im)
        if reflines:
            drawAxes( im )
        if im.shape[2] == 1:
            im.shape = im.shape[:2]
        if im.shape[0]*im.shape[1] == 0:
            print( "[getDistortedImage] No image yet" )
        return np.maximum(im,self.bgcolour)

