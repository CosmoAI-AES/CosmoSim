#! /usr/bin/env python3
# (C) 2023,2026: Hans Georg Schaathun <georg@schaathun.net>

"""
Generate an image for given parameters.
"""

import cv2 as cv
import sys
import numpy as np
import pandas as pd

from .Image import drawAxes
from .datagen import crop

from .CLI.Arguments import Parameters
from .CLI.Simulator import GenericSim 

from .RouletteAmplitudes import RouletteAmplitudes 
from .CosmoSimPy import RouletteRegenerator


class Resim(GenericSim):
    """
    Infrastructure to resimulate from roulette amplitudes.

    The class sets up the infrastructure, and provides the methods to
    run the simulator for each iaage on a CSV file.
    """
    def __init__(self,row,sim=None,**kw):
        """
        Note that `args` overrides Boolean parameters.
        """
        super().__init__(**kw)
        if self.verbose>2: print( "[Resim.__init__]" )
        if sim is None: sim = RouletteRegenerator(verbose=self.verbose)
        self.xireference = self.param.get( "xireference", True )
        self.nterms = self.param.get( "nterms" )
        if self.verbose>1: print( "[Resim] nterms =", self.nterms )

        self.sim = sim
        self.loadData( row )
        self.initSim(row)

        im = self.image
        if self.xireference:
              R = np.float32( [ [ 1, 0, row["xiX"] ], [ 0, 1, -row["xiY"] ] ] )
              m,n = im.shape
              try:
                  self.image = cv.warpAffine(im,R,(n,m))
              except Exception as e:
                  print( "Error in warpAffine.  Image", im )
                  print( "Image shape", (m,n) )
                  raise e
    def runSim( self ):
        if self.verbose>2: print( "[Resim.runSim]" )
        self.sim.makeSource( self.param )
        self.sim.update()
    def getDistortedImage(self):
        return  self.sim.getDistortedImage( )
    def setParameters( self, row ):
        """
        Reset the parameters in the backend simulator, using the
        give data row.
        """
        if self.verbose>2: print( "[setParameters]" )
        maxm = self.coefs.getNterms()
        rsim = self.sim
        
        if self.xireference:
            if self.verbose:
                print( "xi", row["xiX"], row["xiY"], row["sigma"] )
            pt = (0,0)
        else:
            try:
                pt = ( row["offsetX"], row["offsetY"] )
            except:
                raise RuntimeError( "offsetX/offsetY missing from dataset [no-xireference-mode]" )
            if self.verbose:
                print( "Offset", row["offsetX"], row["offsetY"], row["sigma"] )
                print( row )
        rsim.setCentrePy( *pt )
        if self.verbose: print( "Initialised simulator at point", pt )

        for m in range(maxm+1):
            for s in range((m+1)%2, m+2, 2):
                if self.verbose>1: print( "row is",  type( row ) )
                alpha = row.get( f"alpha[{m}][{s}]", 0.0 )
                beta = row.get( f"beta[{m}][{s}]", 0.0 )
                if self.verbose>1:
                    print( "alpha/beta are",  type( alpha ), type( beta ) )
                    print( f"alpha[{m}][{s}] = {alpha}\t\tbeta[{m}][{s}] = {beta}." )
                rsim.setAlphaXi( m, s, alpha )
                rsim.setBetaXi( m, s, beta )
        self.param.setRow( row )
        if self.verbose>1:
            print( "Source spec:", self.param.get( "source" ) )
    def loadData( self, csvfile ):
        if self.verbose>2: print( "[loadData]" )
        if isinstance(csvfile,pd.DataFrame):
            if self.verbose: print( "Received dataframe for resimulation" )
            frame = csvfile
            cols = frame.columns
        elif isinstance(csvfile,pd.Series):
            if self.verbose: print( "Received pandas series for resimulation" )
            frame = csvfile
            cols = frame.axes[0]
        else:
            if self.verbose: print( "Load CSV file:", csvfile )
            frame = pd.read_csv(csvfile,index_col="filename")
            cols = frame.columns
        if self.verbose>1: print( "columns:", cols )
    
        coefs = RouletteAmplitudes(cols)
        if self.verbose:
            print( "Number of roulette terms: ", coefs.getNterms() )
        if self.nterms:
            if self.verbose:
                print( "[Resim.loadData()] Set nterms from self", int(self.nterms) )
            self.sim.setNterms( int(self.nterms) )
        else:
            nterms = coefs.getNterms() 
            if self.verbose: print( "[Resim.loadData()] Set nterms from coefs", nterms )
            self.sim.setNterms( nterms )
        self.coefs = coefs
        self.cols = cols
        self.frame = frame

    
def processResim(frame,param,sim=None,maxcount=None,verbose=0):
    """
    Bulk simulation from a dataset.
    The `frame` is normally a pandas DataFrame, with a row for
    each lensing system.
    """
    count = 1
    print( "[processResim]", verbose )
    print( "[processResim]", param )
    if sim is None: sim = RouletteRegenerator()
    for index,row in frame.iterrows():
        if verbose: print( "[roulettegen.py] Processing", index )
        param.setRow( row )
        print( f"[processResim] {index}", param )
        imsim = Resim( row, sim, param=param, verbose=verbose )
        imsim.saveImage()

        if param.get( "actual" ): imsim.getActual()
        if param.get( "apparent" ): imsim.getApparent()

        if maxcount is not None:
            count += 1
            if count > maxcount: break


def rgen(args,param):
    """
    This is the main procedure of the script, simulating a dataset of
    roulette amplitudes based on a CLI args argument.
    """
    verbose = args.verbose
    if args.roulette:
        if verbose: print( "Load CSV file:", args.roulette )
        try:
            frame = pd.read_csv(args.roulette)
        except Exception as e:
            print( "Fails to open file:", args.roulette )
            raise e

    else:
        raise Exception( "No CSV file given." )

    # Masking is not implemented in the Resim class.
    sim = RouletteRegenerator()
    sim.setMaskMode( args.mask )
    if not args.maskradius is None:
        sim.setMaskRadius( float(args.maskradius) )

    maxcount = param.get( ("management", "maxcount" ), None )

    processResim(frame,param,sim,maxcount,verbose=verbose)

    if verbose: print( "[roulettegen.py] Done" )

if __name__ == "__main__":
    sys.exit( "[roulettegen.py] Deprecated." )
