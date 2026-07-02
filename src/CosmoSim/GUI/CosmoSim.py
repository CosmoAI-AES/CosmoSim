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
import numpy as np
import threading as th
import os, sys

class CosmoSim(cs.CosmoSim):
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

        self.amplitudefiles =
                 { PsiSpec.PM : getPathFN( "pm50.txt" ) )
                 , PsiSpec.SIS : getPathFN( "sis50.txt" ) )
                 , PsiSpec.SIE : getPathFN( "sie05.txt" ) )
                 }
        self.bgcolour = 0
        self.imagesize = 512
        self._sampling = False

        # Set up thread management
        self._continue = True
        self.updateEvent = th.Event()
        self.simEvent = th.Event()
        self._simThread = th.Thread(target=self.simThread)
        self._simThread.start()

    def makeSource(self,param):
        if param.get( "imagesize" ) == None:
           param.__setitem__( "imagesize", self.getImageSize() )
        self._src = getSource(param,verbose=self.verbose)
        if self.verbose:
            print( f"CosmoSim.getSource() returns (verbose={self.verbose})" )

    def setLensMode(self,lensmode,*a,**kw):
        if lensmode == PsiSpec.PM:
            lens = PointMass()
        elif lensmode == PsiSpec.SIS:
            lens = SIS()
        elif lensmode == PsiSpec.SIE:
            lens = SIE()
        else:
            raise RuntimeError( "Invalid lens mode" )
        lens.setFile( self.amplitudefiles[lensmode] )
        self._psilens = lens
        self.setSampled()
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

    def initSim(self,model,*a,**kw):
        if model == ModelSpec.Raytrace:
            sim = RaytraceModel()
        elif model == ModelSpec.Roulette:
            sim = RouletteModel()
        else:
            raise RuntimeError( "Invalid simulator mode" )
        sim.setLens( self._lens )
        self._sim = sim

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

    def setModelMode(self,s):
        if self.verbose: print( f"setModelMode({s})")
        return super().setModelMode( int( modelDict[s] ) ) 

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
               self.runSim()
               self.updateEvent.set()
    def runSim(self):
        self._src_ = self._src
        self.setSource( self._src_ )
        return super().runSim()
    def runSimulator(self):
        """
        Run the simulator; that is, tell it that the parameters
        have changed.  This triggers an event which will be handled
        when the simulator is idle.
        """
        if self.verbose: print( "CosmoSim.runSimulator() [python]" )
        self.simEvent.set()
        if self.verbose: print( "CosmoSim.runSimulator() triggered event" )

    def getApparentImage(self,reflines=True):
        """
        Return the Apparent Image from the simulator as a numpy array.
        """
        im = np.array(self.getApparent(reflines),copy=False)
        if im.shape[2] == 1 : im.shape = im.shape[:2]
        return np.maximum(im,self.bgcolour)
    def getActualImage(self,reflines=True,caustics=False):
        """
        Return the Actual Image from the simulator as a numpy array.
        """
        im = np.array(self.getActual(reflines,caustics),copy=True)
        if im.shape[2] == 1 : im.shape = im.shape[:2]
        return np.maximum(im,self.bgcolour)
    def getDistortedImage(self,reflines=False,critical=False,mask=False,showmask=False):
        """
        Return the Distorted Image from the simulator as a numpy array.
        """
        try:
            if mask: self.maskImage()
            if showmask: self.showMask()
        except:
            print( "Masking not supported for this lens model." )
        try:
            im = np.array(self.getDistorted(reflines,critical),copy=False)
        except Exception as e:
            print( "self", type(self) )
            print( "reflines", reflines )
            print( "critical", critical )
            im = np.array(self.getDistorted(),copy=False)
            raise e
        if im.shape[2] == 1:
            im.shape = im.shape[:2]
        if im.shape[0]*im.shape[1] == 0:
            print( "[getDistortedImage] No image yet" )
        return np.maximum(im,self.bgcolour)

