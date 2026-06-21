# (C) 2026: Hans Georg Schaathun <georg@schaathun.net>

import cv2 as cv
import numpy as np
import pandas as pd

from .Arguments import Parameters
from .Simulator import GenericSim 

from CosmoSim.RouletteAmplitudes import RouletteAmplitudes 
from CosmoSim.CosmoSimPy import RouletteRegenerator

class Resim(GenericSim):
    """
    Infrastructure to resimulate from roulette amplitudes.

    The class sets up the infrastructure, and provides the methods to
    run the simulator for each iaage on a CSV file.
    """
    def __init__(self,param,row,**kw):
        """
        Note that `args` overrides Boolean parameters.
        """
        super().__init__(param,**kw)
        if self.verbose>2: print( "[Resim.__init__]" )

        self.sim = RouletteRegenerator(verbose=self.verbose)
        self.xireference = self.param.get( "xireference", True )
        self.nterms = self.param.get( "nterms" )
        if self.verbose>1: print( "[Resim] nterms =", self.nterms )

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
        self.runSim()
    def initSim(self):
        """
        Initialise the simulator with the given data row.
        """
        param = self.param
        fn = param.get( "filename" )
        if fn is None: fn = row.name
        if self.verbose > 1: print( "filename", fn )
        name = fn.split(".")[0]
        self.name = name

        if self.verbose>1: print( "[initSim] item name:", self.name )

        self.runSim()

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

