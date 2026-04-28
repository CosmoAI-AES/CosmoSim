#! /usr/bin/env python3
# (C) 2023,2026: Hans Georg Schaathun <georg@schaathun.net>

"""
Generate an image for given parameters.
"""

import cv2 as cv
import sys
import os
import numpy as np
import pandas as pd

from .Image import drawAxes
from . import Parameters
from .datagen import crop

from .Arguments import CosmoParser

from .RouletteAmplitudes import RouletteAmplitudes 
from .Simulator import GenericSim 
from . import RouletteRegenerator


class Resim(GenericSim):
    """
    Infrastructure to resimulate from roulette amplitudes.

    The class sets up the infrastructure, and provides the methods to
    run the simulator for each iaage on a CSV file.
    """
    def __init__(self,sim=None,df=None,row=None,**kw):
        """
        Note that `args` overrides Boolean parameters.
        """
        super().__init__(**kw)
        if self.verbose>2: print( "[Resim.__init__]" )
        if sim is None: sim = RouletteRegenerator()
        self.xireference = self.param.get( "xireference" )
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
            if self.verbose:
                print( "Offset", row["offsetX"], row["offsetY"], row["sigma"] )
            pt = ( row["offsetX"], row["offsetY"] )
        rsim.setCentrePy( *pt )
        print( "Initialised simulator at point", pt )

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
            print( "Received dataframe for resimulation" )
            frame = csvfile
            cols = frame.columns
        elif isinstance(csvfile,pd.Series):
            print( "Received dataframe for resimulation" )
            frame = csvfile
            cols = frame.axes[0]
        else:
            print( "Load CSV file:", csvfile )
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
def processResim( frame, sim=None, args=None, cfg=None, maxcount=2**30 ):

    count = 1
    for index,row in frame.iterrows():
        print( "[roulettegen.py] Processing", index )
        param = Parameters( args=args, cfg=cfg )

        imsim = Resim( sim, param=param, row=row )
        imsim.saveImage()

        if args.actual: imsim.getActual()
        if args.apparent: imsim.getApparent()

        count += 1
        if count > maxcount: break
    
def main(args):
    """
    This is the main procedure of the script, simulating a dataset of
    roulette amplitudes based on a CLI args argument.
    """
    if args.csvfile:
        frame = pd.read_csv(args.csvfile)
    else:
        raise Exception( "No CSV file given; the --csvfile option is mandatory." )

    if args.maxcount is None:
        maxcount = 2**30
    else:
        maxcount = int(args.maxcount)
    param = Parameters(args)

    # Masking is not implemented in the Resim class.
    sim = RouletteRegenerator()
    sim.setMaskMode( args.mask )
    if not args.maskradius is None:
        sim.setMaskRadius( float(args.maskradius) )

        
    processResim( frame, sim=sim, args=args, maxcount=maxcount )


    print( "[roulettegen.py] Done" )

if __name__ == "__main__":
    print( "[roulettegen.py] Starting ..." )
    parser = CosmoParser(
          prog = 'CosmoSim makeimage',
          description = 'Generaet an image for given lens and source parameters',
          epilog = '')

    args = parser.parse_args()
    if args.directory:
        os.makedirs( args.directory, exist_ok=True )
    main(args)
