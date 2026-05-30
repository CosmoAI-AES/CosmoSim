#! /usr/bin/env python3
# (C) 2024: Hans Georg Schaathun <georg@schaathun.net>

"""
Generate an image for given parameters.
"""

import tomllib as tl
from cascadict import CascaDict

import cv2 as cv
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from .dataset import datasetgen

from .Image import centreImage, drawAxes, crop, annotatePoint, annotateCircle, translateImage
from . import getMSheaders,CosmoSim,__version__

from .CLI.Simulator import GenericSim
from .CLI.Arguments import setParameters,Parameters

import pandas as pd

defaultoutcols = [ "index", "filename", "source", "lens", "chi", "R", "phi", "einsteinR", "sigma", "sigma2", "theta", "n_sersic", "luminosity", "x", "y" ]


class SimImage(GenericSim):
    """
    This class simulates a single image.
    Once the simulation has been run, various kinds of image and metadata can be
    retrieved from the object.
    """
    def __init__(self,param,**kw):
        super().__init__(param,**kw)
        if self.verbose: print( f"[SimImage] init (verbose={self.verbose}) ..." )

        self.sim = CosmoSim(verbose=self.verbose)
        msk = self.param.get( "mask", None )
        if msk is not None:
            print( "[SimImage] sets mask", msk )
            self.sim.setMaskMode( msk )
        self.initSim()
        if self.verbose>2:
            print( "[SimImage] Verbosity", self.verbose )

    def close(self):
        self.sim.close()
    def setParameters(self,row):
        """
        Reset parameters in the underlying `CosmoSim` simulator, using the
        given data row.
        """
        print( "[SimImage] setParameters()" )
        return setParameters(self.sim,row,verbose=self.verbose)
    def getData(self):
        sim = self.sim
        if self.param.get( "centred" ):
            centrepoint = self.centrepoint
        else:
            centrepoint = (0,0)
        maxm = self.param.get( "nterms" )
        xireference = self.param.get( "xireference", True )
        if self.verbose > 0:
            print( "[datagen.py] Finding Alpha/beta; centrepoint=", centrepoint )
        # r = pd.Series([ row[x] for x in self.outcols ], index=self.outcols )
        releta = sim.getRelativeEta(centrepoint=centrepoint)
        offset = sim.getOffset(centrepoint=centrepoint)
        xioffset = sim.getXiOffset(centrepoint)
        if xireference:
            if self.verbose>1:
                print( "[xireference=True] nterms =", maxm )
            ab = sim.getAlphaBetas(maxm)
        else:
            if self.verbose>1:
                print( "[xireference=False] nterms =", maxm )
            ab = sim.getAlphaBetas(maxm,pt=centrepoint)
        relcols = [ "centreX", "centreY",
                   "reletaX", "reletaY",
                   "offsetX", "offsetY",
                   "xiX", "xiY" ]
        r2 = pd.Series(
              [ centrepoint[0], centrepoint[1], releta[0], releta[1],
               offset[0], offset[1], xioffset[0], xioffset[1] ],
              index=relcols ) 
        r3 = pd.Series( ab, index=getMSheaders(maxm)) 
        r1 = pd.concat( [ self.row, r2, r3 ] )
        if self.verbose > 1:
            print( f"New row (verbosity={self.verbose})" )
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
            (im,(cx,cy)) = centreImage(im)
        if param.get( "cropsize" ):
            cs = param.get( "cropsize", None )
            if cs is not None:
                im = crop( int( cs ) )
        if param.get( "reflines" ):
            drawAxes(im)

        fn = os.path.join(param.get("directory"), str(name) + ".png" ) 
        cv.imwrite(fn,im)
        return im

    def psiplot(self):
        a = self.sim.getPsiMap()
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

def makeSingle(param=None,name=None,outcols=None,verbose=0):
    """Process a single parameter set, given either as a pandas row or
    just as args parsed from the command line.
    """
    if param is None: param = Parameters()
    imsim = SimImage(param=param,name=name,outcols=outcols,verbose=verbose)
    imsim.saveImage()
    if param.get( "join" ): imsim.join()
    if param.get( "family" ): imsim.family()
    if param.get( "psiplot" ): imsim.psiplot()
    if param.get( "kappaplot" ): imsim.kappaplot()
    if param.get( "apparent" ): imsim.getApparent()
    if param.get( "actual" ): imsim.getActual()
    print( "makeSingle() returns" )
    return imsim

def datagen(args,param=None):

    if args.rnd:
        if not args.csvfile:
            raise Exception("The --toml option also requires --csvfile")
        datasetgen(args.toml,args.csvfile)

    if args.csvfile:
        print( "Load CSV file:", args.csvfile )
        frame = pd.read_csv(args.csvfile)
    else:
        raise RuntimeError( "CSV file needed for batch mode" )

    outcols = list(frame.columns)
    print( "columns:", outcols )
    dfs = []
    for index,row in frame.iterrows():
        param.setRow( row )
        imsim = makeSingle(param,name=args.name,outcols=outcols)
        if args.outfile:
            dfs.append( imsim.getData() )
        imsim.close()
    df = pd.DataFrame( dfs )
    if args.outfile:
           if args.mldata:
               dropcol = [ "index", "source", "config", "nterms",
                         "centreX", "centreY", "reletaX", "reletaY",
                         "offsetX", "offsetY" ]
               print( df.columns )
               for c in dropcol:
                   try:
                       df.drop( columns=c, inplace=True )
                   except:
                       print( "No column", c )
           df.to_csv(args.outfile, sep=",", index=False)
    print( "ready to close simulator" )
    print( "simulator closed" )

if __name__ == "__main__":
    sys.exit( "[CosmoSim] datagen - deprecated." )
