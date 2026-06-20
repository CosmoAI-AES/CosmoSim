# (C) 2026: Hans Georg Schaathun <georg@schaathun.net>

import cv2 as cv
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from ..Image import centreImage, drawAxes, crop, annotatePoint, annotateCircle, translateImage

from .Generators import getSimulator, getLens, getSource

from .Simulator import GenericSim
from .Arguments import setParameters,Parameters

def getMS(minm,maxm=None):
    if minm is None:
        raise RuntimeError( "None argument to getMS()." )
    if maxm is None:
        maxm = minm
        minm = 0
    return [ (m,s) for m in range(minm,maxm+1)
                                    for s in range(1-m%2,m+2,2) ]
def getMSheaders(maxm): 
    if maxm is None:
        raise RuntimeError( "None argument to getMSheaders()." )
    r = [ ( f"alpha[{m}][{s}]", f"beta[{m}][{s}]") for (m,s) in getMS(maxm) ]
    return [ x for p in r for x in p ]


class SimImage(GenericSim):
    """
    This class simulates a single image.
    Once the simulation has been run, various kinds of image and metadata can be
    retrieved from the object.
    """
    def __init__(self,param,sim=None,**kw):
        super().__init__(param,**kw)
        if self.verbose: print( f"[SimImage] init (verbose={self.verbose}) ..." )
        self.initSim()

    def initSim(self):
        param = self.param
        self.sim = getSimulator(self.param,verbose=self.verbose)
        self.src = getSource(self.param,verbose=self.verbose)
        self.lens = getLens(self.param,verbose=self.verbose)
        if row.get("y") is not None:
            if verbose > 1:
                print( "[setParameters] XY", row.get( "x" ), row.get( "y" ) )
            sim.setXY( row.get( "x" ), row.get( "y" ) )
        elif row.get("phi",None) != None:
            if verbose > 1: print( "Polar", row.get( "x" ), row.get( "phi" ) )
            sim.setPolar( row.get( "x" ), row.get( "phi" ) )

    def close(self):
        self.sim.close()
    def setParameters(self,row):
        """
        Reset parameters in the underlying `CosmoSim` simulator, using the
        given data row.
        """
        if self.verbose: print( "[SimImage] setParameters()" )
        return setParameters(self.sim,row,verbose=self.verbose)
    def getData(self,verbose=None):
        if verbose is None: verbose = self.verbose
        sim = self.sim
        if self.param.get( "centred" ):
            if verbose: print( "[getData] centred" )
            centrepoint = self.centrepoint
        else:
            if verbose: print( "[getData] not centred" )
            centrepoint = (0,0)
        maxm = self.param.get( "nterms", 16 )
        xireference = self.param.get( "xireference", True )
        if verbose > 0:
            print( "[datagen.py] Finding Alpha/beta; centrepoint=", centrepoint )
        # r = pd.Series([ row[x] for x in self.outcols ], index=self.outcols )
        releta = sim.getRelativeEta(centrepoint=centrepoint)
        if verbose > 2: print( "[SimImage.getData] ", centrepoint )
        offset = sim.getOffset(centrepoint=centrepoint)
        if verbose: print( "[getData] ", offset, centrepoint )
        xioffset = sim.getXiOffset(centrepoint)
        if xireference:
            if verbose>1:
                print( "[xireference=True] nterms =", maxm )
            ab = sim.getAlphaBetas(maxm)
        else:
            if verbose>1:
                print( "[xireference=False] nterms =", maxm )
            ab = sim.getAlphaBetas(maxm,pt=centrepoint)
        relcols = [ "centreX", "centreY",
                   "reletaX", "reletaY",
                   "offsetX", "offsetY",
                   "xiX", "xiY" ]
        r1 = pd.Series(
                { "filename" : self.param.get( "filename" )
                , "source" : self.param.get( "source" )
                , "x" : self.param.get( "x" )
                , "y" : self.param.get( "y" )
                , "sigma" : self.param.get( "sigma" )
                , "sigma2" : self.param.get( "sigma2" )
                , "theta" : self.param.get( "theta" )
                } )
        r2 = pd.Series(
              [ centrepoint[0], centrepoint[1], releta[0], releta[1],
               offset[0], offset[1], xioffset[0], xioffset[1] ],
              index=relcols ) 
        r3 = pd.Series( ab, index=getMSheaders(maxm)) 
        r1 = pd.concat( [ r1, r2, r3 ] )
        if verbose > 1:
            print( f"New row (verbosity={verbose})" )
            print( r1 )
        return r1
    def join(self):
        """
        Merge images simulated different reference points for
        the roulette expansion.  This has not been tested since the early
        work where we tried to get accurate simulations using roulette. 
        """
        # sim.setMaskMode(False)
        sim = self.sim
        maskscale = float(self.param.get( "maskscale" ))
        criticalcurves = self.param.get( "criticalcurves" )
        nc = int(self.param.get( "components" ))
        sim.runSim()
        print ( "[datagen.py] runSim() completed\n" ) ;
        sim.maskImage(maskscale)
        joinim = sim.getDistortedImage(critical=criticalcurves)
        for i in range(1,nc):
           sim.moveSim(rot=2*i*np.pi/nc,scale=1)
           sim.maskImage(maskscale)
           im = sim.getDistortedImage(critical=criticalcurves)
           joinim = np.maximum(joinim,im)
        fn = os.path.join(self.directory,"join-" + str(self.name) + ".png" ) 
        if self.param.get( "reflines" ):
            drawAxes(joinim)
        cv.imwrite(fn,joinim)
    def family(self):
        """
        Run a family of simulations with different reference points for
        the roulette expansion.  This has not been tested since the early
        work where we tried to get accurate simulations using roulette. 
        """
        sim = self.sim
        self.moveImage(rot=-np.pi/4,scale=1,name=f"{self.name}-45+1")
        self.moveImage(rot=+np.pi/4,scale=1,name=f"{self.name}+45+1")
        self.moveImage(rot=0,scale=-1,name=f"{self.name}+0-1")
        self.moveImage(rot=0,scale=2,name=f"{self.name}+0+2")
    def moveImage(self,rot,scale,name):
        """
        Simulate with a different reference point.  This only makes
        sense for roulette models.
        """
        sim = self.sim
        param = self.param
        sim.moveSim(rot,scale)
        im = sim.getDistortedImage( 
                 critical=param.get( "criticalcurves" ),
                 showmask=param.get( "showmask" ) ) 
        print( "getDistortedImage() has returned", type(im) )

        if param.get( "centred" ):
            if self.verbose: print( "[movedImage] centred" )
            (im,(cx,cy)) = centreImage(im)
        if param.get( "cropsize" ):
            cs = param.get( "cropsize", None )
            if cs is not None:
                im = crop( int( cs ), verbose=self.verbose  )
        if param.get( "reflines" ):
            drawAxes(im)

        fn = os.path.join(param.get("directory"), str(name) + ".png" ) 
        cv.imwrite(fn,im)
        return im

    def psiplot(self):
        a = self.sim.getPsiMap()
        if self.verbose:
            print("[SimImage] psiplot", a.shape, a.dtype)
            print(a)
        sys.stdout.flush()
        nx,ny = a.shape
        X, Y = np.meshgrid( range(nx), range(ny) )
        hf = plt.figure()
        ha = hf.add_subplot(111, projection='3d')
        ha.plot_surface(X, Y, a)
        fn = os.path.join(self.directory,"psi-" + str(self.name) + ".svg" ) 
        plt.savefig( fn )
        plt.close()
    def kappaplot(self):
        a = self.sim.getMassMap()
        if self.verbose:
            print("[SimImage] kappaplot", a.shape, a.dtype)
            print(a)
        nx,ny = a.shape
        X, Y = np.meshgrid( range(nx), range(ny) )
        hf = plt.figure()
        ha = hf.add_subplot(111, projection='3d')
        ha.plot_surface(X, Y, a)
        fn = os.path.join(self.directory,"kappa-" + str(self.name) + ".svg" ) 
        plt.savefig( fn )
        plt.close()
