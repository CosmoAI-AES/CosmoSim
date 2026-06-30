# (C) 2022-26: Hans Georg Schaathun <georg@schaathun.net> 

"""
The CosmoSim package comprises several components, including scripts,
GUI, and API.

The root module provides wrappers around most of the C++ classes,
to make the python API more streamlined.
"""

import CosmoSim.CosmoSimPy as cs
import numpy as np
import pandas as pd
import threading as th
import os, sys
from .CLI import Arguments
from .CLI.Generators import makeSource, makeSourceConstellation
from .Dictionary import *

Parameters = Arguments.Parameters

import traceback

__version__ = "3.1.0"

maxmlist = [ 50, 100, 200 ]
def getFileName(maxm):
    """
    Get the filename for the amplitudes files.
    The argument `maxm` is the maximum number of terms (nterms) to be
    used in the simulator.
    """
    dir = os.path.dirname(os.path.abspath(__file__))
    for m in maxmlist:
        m0 = m
        if maxm <= m:
            return( os.path.join( dir, f"sis{m}.txt" ) )
    raise Exception( f"Cannot support m > {m0}." )

class CosmoSim(cs.CosmoSim):
    """
    Simulator for gravitational lensing.
    This wraps the CosmoSim library written in C++.  In particular,
    it wraps functions returning images, to convert the data to 
    numpy arrays.
    """
    def __init__(self,*a,maxm=50,fn=None,verbose=1,**kw):
        super().__init__(*a,**kw)
        self.verbose = verbose
        if self.verbose>1: print( f"[CosmoSim] init (verbose={self.verbose}) ..." )
        dir = os.path.dirname(os.path.abspath(__file__))
        if fn is None:
            super().setFile( PsiSpec.SIS, getFileName( maxm ) )
            super().setFile( PsiSpec.SIE, os.path.join( dir, "sie05.txt" ) )
            super().setFile( PsiSpec.PM, os.path.join( dir, "pm50.txt" ) )
        else:
            if verbose: print( "Amplitudes file:", fn )
            super().setFile( PsiSpec.SIS, fn )
            super().setFile( PsiSpec.SIE, fn )
            super().setFile( PsiSpec.PM, fn )
        self._continue = True
        self.updateEvent = th.Event()
        self.simEvent = th.Event()
        self._simThread = th.Thread(target=self.simThread)
        self._simThread.start()
        self.bgcolour = 0
    def makeSource(self,param):
        if param.get( "imagesize" ) == None:
           param.__setitem__( "imagesize", self.getImageSize() )
        self._src = makeSource(param,verbose=self.verbose)
        if self.verbose:
            print( f"CosmoSim.makeSource() returns (verbose={self.verbose})" )
    def getRelativeEta(self,centrepoint):
        # print ( "[getRelativeEta] centrepoint=", centrepoint, "in Planar Co-ordinates"  )
        r = super().getRelativeEta(centrepoint[0],centrepoint[1])
        a = np.array(r)
        # print ( "[getRelativeEta] r=", a )
        return (a[0],a[1])
    def getXiOffset(self,centrepoint):
        nu = super().getNu()
        a = np.array(nu)
        return ( a[0] - centrepoint[0], a[1] - centrepoint[1] )
    def getOffset(self,centrepoint):
        if self.verbose > 2:
            print ( "[getOffset] centrepoint=", centrepoint, "in Planar Co-ordinates"  )
        r = super().getOffset(centrepoint[0],centrepoint[1])
        a = np.array(r)
        if self.verbose > 2:
            print ( "[getOffset] r=", a )
        return (a[0],a[1])

    def getAlphaBetas(self,maxm=2,pt=None):
        """
        Get the roulette amplitudes for a given point in the source plane.
        """
        if self.verbose>1:
            print ( "[getAlphaBetas] pt=", pt, "in Planar Co-ordinates"  )
        if pt == None:
           ab1 = { f"alpha[{m}][{s}]" : self.getAlphaXi(m,s) 
                   for (m,s) in getMS(maxm) }
           ab2 = { f"beta[{m}][{s}]" : self.getBetaXi(m,s) 
                   for (m,s) in getMS(maxm) }
        else:
            (x,y) = pt
            # Scaling is done in getAlpha/getBeta
            ab1 = { f"alpha[{m}][{s}]" : self.getAlpha(x,y,m,s) 
                    for (m,s) in getMS(maxm) }
            ab2 = { f"beta[{m}][{s}]" : self.getBeta(x,y,m,s) 
                    for (m,s) in getMS(maxm) }
        return pd.concat( [ pd.Series( ab1 ), pd.Series( ab2 ) ] )
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
    def moveSim(self,rot,scale):
        return super().moveSim( float(rot), float(scale) )
    def maskImage(self,scale=1):
        return super().maskImage( float(scale) )
    def setCluster(self,s):
        if self.verbose: print( f"[CosmoSim/py] setCluster({s})")
        sys.stdout.flush()
        ll = [ x.split("/") for x in s.split(";") ]
        self.lenslist = []
        cluster = cs.ClusterLens()
        for lens in ll:
            lenstype = lens[0]
            lensparam = [ float(x) for x in lens[1:] ]
            if self.verbose: print( lenstype, ":", lensparam )
            sys.stdout.flush()
            nl = len(lensparam)
            if nl < 3:
                raise Exception( f"Too few parameters for constituent lens" )
            x, y = lensparam[0], lensparam[1] ;
            if lenstype == "SIS":
                l = cs.SIS()
                l.setFile( super().getFile( PsiSpec.SIS ) )
            elif lenstype == "SIE":
                l = cs.SIE()
                if nl < 5:
                    raise Exception( f"Too few parameters for SIE lens" )
                l.setRatio( lensparam[3] )
                l.setOrientation( lensparam[4] )
                l.setFile( super().getFile( PsiSpec.SIE ) )
            elif lenstype == "PointMass":
                l = cs.PointMass()
                l.setFile( super().getFile( PsiSpec.PM ) )
            else:
                raise Exception( f"Lens Type not Supported {lenstype}" )
            l.setEinsteinR( lensparam[2] )
            self.lenslist.append( l )
            cluster.addLens( l, x, y )
        self.cluster = cluster
        if self.verbose: print( f"[CosmoSim/py] setCluster calls setLens")
        sys.stdout.flush()
        super().setLens(cluster)
        return
    def setLensMode(self,s):
        if self.verbose: print( f"setLensMode({s})")
        return super().setLensMode( int( lensDict[s] ) ) 
    def setModelMode(self,s):
        if self.verbose: print( f"setModelMode({s})")
        # traceback.print_stack()
        return super().setModelMode( int( modelDict[s] ) ) 
    def setConfigMode(self,s,verbose=None):
        """
        Set lens and simulation models based on the config string.
        """
        if verbose is None: 
            verbose = self.verbose
        if verbose > 1: 
            print( f"setConfigMode({s})")
        (model,lens,sampleMode) = configDict[s]
        if verbose > 1:
            print( f"[setConfigMode] configDict[{s}]:", (model,lens,sampleMode) )
        self.setSampled( sampleMode ) 
        super().setLensMode( int( lens ) ) 
        return super().setModelMode( int( model ) ) 
    def setSampled(self,s):
        if self.verbose: print( f"[setSampled] {s}" )
        if s is not None:
            super().setSampled( int( s ) ) 
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
    def getPsiMap(self):
        """
        Return a matrix representation of the sampled lensing potential.
        """
        im = np.array(super().getPsiMap(),copy=False)
        if im.shape[2] == 1 : im.shape = im.shape[:2]
        return im
    def getMassMap(self):
        """
        Return a matrix representation of the sampled mass density.
        """
        im = np.array(super().getMassMap(),copy=False)
        if im.shape[2] == 1 : im.shape = im.shape[:2]
        return im[2:-2,2:-2]
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
        if im.shape[2] == 1 : im.shape = im.shape[:2]
        return np.maximum(im,self.bgcolour)
