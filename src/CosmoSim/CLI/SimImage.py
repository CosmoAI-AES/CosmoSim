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
from .Arguments import Parameters

def getMS(minm,maxm=None):
    if minm is None:
        raise RuntimeError( "None argument to getMS()." )
    if maxm is None:
        maxm = minm
        minm = 0
    return [ (m,s) for m in range(minm,maxm+1)
                                    for s in range(1-m%2,m+2,2) ]
class SimImage(GenericSim):
    """
    This class simulates a single image.
    Once the simulation has been run, various kinds of image and metadata can be
    retrieved from the object.
    """
    def __init__(self,param,**kw):
        """
        In the present implementation, all the parameters must be passed as 
        a `Parameters` object.  The settings cannot be updated in an exising
        instance.
        """
        super().__init__(param,**kw)
        if self.verbose: print( f"[SimImage] init (verbose={self.verbose}) ..." )
        self.initSim()
        self.runSim()
    def getXiOffset(self,centrepoint):
        nu = self.sim.getNu()
        a = np.array(nu)
        return ( a[0] - centrepoint[0], a[1] - centrepoint[1] )

    def getRoulette(self,precision=None,fn=None,verbose=None):
        if verbose is None: verbose = self.verbose
        sim = self.sim
        if self.param.get( "centred" ):
            centrepoint = self.centrepoint
        else:
            centrepoint = (0,0)
        maxm = self.param.get( ( "simulator", "nterms" ), 16 )
        xireference = self.param.get( "xireference", True )

        releta = np.array(sim.getRelativeEta(centrepoint[0],centrepoint[1]))
        offset = np.array(sim.getOffset())
        if verbose: print( "[getRoulette] ", offset, centrepoint )

        xioffset = self.getXiOffset(centrepoint)
        if xireference:
            xi = sim.getNu()
        else:
            xi = centrepoint
        
        r1 = pd.Series(
                { "source" : self.param.get( "source" )
                , "x" : self.param.get( "x" )
                , "y" : self.param.get( "y" )
                , "sigma" : self.param.get( "sigma" )
                , "sigma2" : self.param.get( "sigma2" )
                , "theta" : self.param.get( "theta" )
                , "lensX" : -centrepoint[0]
                , "lensY" : -centrepoint[1]
                , "centreX" : centrepoint[0]
                , "centreY" : centrepoint[1]
                , "reletaX" : releta[0]
                , "reletaY" : releta[1]
                , "offsetX" : offset[0]
                , "offsetY" : offset[1]
                , "xiX" : xioffset[0]
                , "xiY"  : xioffset[1] 
                } )
        if fn is None:
            fn = self.getAmplitudeFile() 
        g = self.param.get( ( "lens", "einsteinradius" ) )
        if verbose: print( "Einstein radius", g )
        rp = RouletteParser( fn, g=g, verbose=self.verbose )
        r1 = pd.concat( [ r1,  rp.getAlphaBetas(xi,maxm=maxm) ] )
        r1.name = self.param.get( "filename" )
        if verbose > 1:
            print( f"New row (verbosity={verbose})" )
            print( r1 )
        return r1
    def initSim(self):
        """
        Initialise the simulator, using the settings from the `param` attribute.
        """
        param = self.param
        self.src = getSource(self.param,verbose=self.verbose)
        self.lens = getLens(self.param,verbose=self.verbose)
        self.sim = getSimulator(self.param,lens=self.lens,source=self.src,
                                verbose=self.verbose)
        if param.get("y") is not None:
            if self.verbose > 1:
                print( "[initSim] XY", param.get( "x" ), param.get( "y" ) )
            self.sim.setXY( param.get( "x" ), param.get( "y" ) )
        elif param.get("phi",None) != None:
            if self.verbose > 1: 
                print( "[initSim] Polar", param.get( "x" ), param.get( "phi" ) )
            self.sim.setPolar( param.get( "x" ), param.get( "phi" ) )

    def getData(self,verbose=None):
        """
        Get the data generated from the simulation, particularly the roulette
        amplitudes.  The return value is a pandas `Series` object.
        """
        if verbose is None: verbose = self.verbose
        sim = self.sim
        if self.param.get( "centred" ):
            if verbose: print( "[getData] centred" )
            centrepoint = self.centrepoint
        else:
            if verbose: print( "[getData] not centred" )
            centrepoint = (0,0)
        maxm = self.param.get( ( "simulator", "nterms" ), 16 )
        xireference = self.param.get( "xireference", True )
        if verbose > 0:
            print( "[datagen.py] Finding Alpha/beta; centrepoint=", centrepoint )
        releta = np.array(sim.getRelativeEta(centrepoint[0],centrepoint[1]))
        if verbose > 2: print( "[SimImage.getData] ", centrepoint )
        offset = np.array(sim.getOffset())
        if verbose: print( "[getData] ", offset, centrepoint )
        xioffset = self.getXiOffset(centrepoint)
        if xireference:
            if verbose>1:
                print( "[xireference=True] nterms =", maxm )
            ab = self.getAlphaBetas(maxm)
        else:
            if verbose>1:
                print( "[xireference=False] nterms =", maxm )
            ab = self.getAlphaBetas(maxm,pt=centrepoint)

        r1 = pd.Series(
                { "source" : self.param.get( "source" )
                , "x" : self.param.get( "x" )
                , "y" : self.param.get( "y" )
                , "sigma" : self.param.get( "sigma" )
                , "sigma2" : self.param.get( "sigma2" )
                , "theta" : self.param.get( "theta" )
                , "lensX" : -centrepoint[0]
                , "lensY" : -centrepoint[1]
                , "centreX" : centrepoint[0]
                , "centreY" : centrepoint[1]
                , "reletaX" : releta[0]
                , "reletaY" : releta[1]
                , "offsetX" : offset[0]
                , "offsetY" : offset[1]
                , "xiX" : xioffset[0]
                , "xiY"  : xioffset[1]
                } )
        r1 = pd.concat( [ r1, ab ] )
        if verbose > 1:
            print( f"New row (verbosity={verbose})" )
            print( r1 )
        return r1
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
    def getAmplitudeFile(self):
        fn = self.param.get( ( "lens", "amplitudefile" ) )
        if fn is None: 
            raise NotImplemented( "Not implemented lookup of default amplitudes file." )
        return fn
    def getAlphaBetas(self,maxm=2,pt=None):
        """
        Get the roulette amplitudes for a given point in the source plane.
        """
        if self.verbose>1:
            print ( "[getAlphaBetas] pt=", pt, "in Planar Co-ordinates"  )
        if pt == None:
           ab1 = { f"alpha[{m}][{s}]" : self.lens.getAlphaXi(m,s) 
                   for (m,s) in getMS(maxm) }
           ab2 = { f"beta[{m}][{s}]" : self.lens.getBetaXi(m,s)
                   for (m,s) in getMS(maxm) }
        else:
            (x,y) = pt
            # Scaling is done in getAlpha/getBeta
            ab1 = { f"alpha[{m}][{s}]" : self.lens.getAlphaPy(x,y,m,s)
                    for (m,s) in getMS(maxm) }
            ab2 = { f"beta[{m}][{s}]" : self.lens.getBetaPy(x,y,m,s)
                    for (m,s) in getMS(maxm) }
        return pd.concat( [ pd.Series( ab1 ), pd.Series( ab2 ) ] )

