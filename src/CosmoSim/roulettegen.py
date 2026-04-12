#! /usr/bin/env python3
# (C) 2023: Hans Georg Schaathun <georg@schaathun.net>

"""
Generate an image for given parameters.
"""

import cv2 as cv
import sys
import os
import numpy as np
import pandas as pd

from .Image import drawAxes
from .Parameters import Parameters
from .datagen import crop

from .Arguments import CosmoParser

from .RouletteAmplitudes import RouletteAmplitudes 
from .Simulator import GenericSim 
from . import RouletteSim,RouletteRegenerator,makeSource


class Resim(GenericSim):
    """
    Infrastructure to resimulate from roulette amplitudes.

    The class sets up the infrastructure, and provides the methods to
    run the simulator for each iaage on a CSV file.
    """
    def __init__(self,sim=None,row=None,nterms=None,xireference=True,reflines=False,**kw):
        """
        Note that `args` overrides Boolean parameters.
        """
        super().__init__(param,verbose=verbose)
        if sim is None: sim = RouletteRegenerator()
        self.sim = sim
        self.initSim(row)

        self.nterms = nterms 
        self.xireference = xireference
        self.reflines = reflines
        if args is not None:
            self.xireference = args.xireference
            if nterms is None and args.nterms:
                print( "[Resim] Set nterms from args", int(args.nterms) )
                self.nterms = int(args.nterms)
            self.loadData( args.csvfile )

    def setParameters( self, row ):
        """
        Reset the parameters in the backend simulator, using the
        give data row.
        """
        maxm = self.coefs.getNterms()
        rsim = self.sim

        if self.xireference:
            print( "xi", row["xiX"], row["xiY"], row["sigma"] )
            pt = (0,0)
        else:
            print( "Offset", row["offsetX"], row["offsetY"], row["sigma"] )
            pt = ( row["offsetX"], row["offsetY"] )
        rsim.setCentrePy( *pt )
        print( "Initialised simulator at point", pt )

        self.initSim( self.sim )
    
        im = self.sim.getDistortedImage( showmask=showmask ) 
        if self.xireference:
              R = np.float32( [ [ 1, 0, row["xiX"] ], [ 0, 1, -row["xiY"] ] ] )
              m,n = im.shape
              im = cv.warpAffine(im,R,(n,m))
        self.image = im 

        for m in range(maxm+1):
            for s in range((m+1)%2, m+2, 2):
                print( "row is",  type( row ) )
                alpha = row.get( f"alpha[{m}][{s}]", 0.0 )
                beta = row.get( f"beta[{m}][{s}]", 0.0 )
                print( "alpha/beta are",  type( alpha ), type( beta ) )
                print( f"alpha[{m}][{s}] = {alpha}\t\tbeta[{m}][{s}] = {beta}." )
                rsim.setAlphaXi( m, s, alpha )
                rsim.setBetaXi( m, s, beta )
    def loadData( self, csvfile ):
        if isinstance(csvfile,pd.DataFrame):
            print( "Received dataframe for resimulation" )
            frame = csvfile
        else:
            print( "Load CSV file:", csvfile )
            frame = pd.read_csv(csvfile,index_col="filename")
        cols = frame.columns
        print( "columns:", cols )
    
        coefs = RouletteAmplitudes(cols)
        print( "Number of roulette terms: ", coefs.getNterms() )
        if self.nterms:
            print( "[Resim.loadData()] Set nterms from self", int(self.nterms) )
            self.sim.setNterms( int(self.nterms) )
        else:
            nterms = coefs.getNterms() 
            print( "[Resim.loadData()] Set nterms from coefs", nterms )
            self.sim.setNterms( nterms )
        self.coefs = coefs
        self.cols = cols
        self.frame = frame


    
def main(args):
    """
    This is the main procedure of the script, simulating a dataset of
    roulette amplitudes based on a CLI args argument.
    """
    if not args.csvfile:
        raise Exception( "No CSV file given; the --csvfile option is mandatory." )


    count = 1
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
        
    param = Parameters( args )
    resim = Resim( sim, param )

    for index,row in resim.frame.iterrows():
        print( "[roulettegen.py] Processing", index )

        imsim = Resim( sim, row=row )
        imsim.saveImage()

        if args.actual: resim.getActual()
        if args.apparent: resim.getApparent()

        count += 1
        if count > maxcount: break

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
