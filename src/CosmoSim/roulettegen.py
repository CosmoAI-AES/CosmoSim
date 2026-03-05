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
from . import RouletteSim,RouletteRegenerator,makeSource

def makeSingle(sim,fn,row,reflines=False,xireference=True,showmask=False,
               actual=None,apparent=None):
    """
    Simulate a single image from roulette amplitudes.

    This is used by `main()` and thus by the script.
    For all other uses, the `Resim` class and its `makeSingle()`
    method should be used.
    """
    print( "makeSingle" )

    sim._rsim.update()

    im = sim.getDistortedImage( showmask=showmask ) 
    print( "Distorted image", type(im), im.shape )
    if xireference:
          R = np.float32( [ [ 1, 0, row["xiX"] ], [ 0, 1, -row["xiY"] ] ] )
          m,n = im.shape
          im = cv.warpAffine(im,R,(n,m))
    if reflines:
        drawAxes(im)

    cv.imwrite(fn,im)

    if actual:
       im = sim.getActualImage( reflines=reflines )
       cv.imwrite(fn,im)
    if apparent:
       im = sim.getApparentImage( reflines=reflines )
       cv.imwrite(fn,im)
    return None

def setAmplitudes( rsim, row, coefs ):
    """
    Set the roulette amplitudes in the simulator.

    This is used by `main()` and thus by the script.
    For all other uses, the `Resim` class and its `setAmplitudes()`
    method should be used.
    """
    maxm = coefs.getNterms()
    for m in range(maxm+1):
        for s in range((m+1)%2, m+2, 2):
            print( "row is",  type( row ) )
            alpha = row.get( f"alpha[{m}][{s}]", 0.0 )
            beta = row.get( f"beta[{m}][{s}]", 0.0 )
            print( "alpha/beta are",  type( alpha ), type( beta ) )
            print( f"alpha[{m}][{s}] = {alpha}\t\tbeta[{m}][{s}] = {beta}." )
            rsim.setAlphaXi( m, s, alpha )
            rsim.setBetaXi( m, s, beta )

class Resim:
    """
    Infrastructure to resimulate from roulette amplitudes.

    The class sets up the infrastructure, and provides the methods to
    run the simulator for each iaage on a CSV file.
    """
    def __init__(self,directory,args=None,cfg=None,nterms=None,xireference=True,reflines=False):
        self.sim = RouletteSim()
        self.directory = directory
        self.rsim = RouletteRegenerator()
        self.nterms = nterms 
        self.param = Parameters( args, cfg=cfg )
        self.xireference = xireference
        self.reflines = reflines
        if args is not None:
            self.xireference = args.xireference
            if nterms is None and args.nterms:
                print( "[Resim] Set nterms from args", int(args.nterms) )
                self.nterms = int(args.nterms)
            self.loadData( args.csvfile )

    def setAmplitudes( self, row ):
        maxm = self.coefs.getNterms()
        rsim = self.rsim
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
            self.rsim.setNterms( int(self.nterms) )
        else:
            print( "[Resim.loadData()] Set nterms from coefs", int(self.nterms) )
            self.rsim.setNterms( coefs.getNterms() )
        self.coefs = coefs
        self.cols = cols
        self.frame = frame
    def makeSingle(self,fn,row,showmask=False):
        print( "makeSingle" )


        if self.xireference:
            print( "xi", row["xiX"], row["xiY"], row["sigma"] )
            pt = (0,0)
        else:
            print( "Offset", row["offsetX"], row["offsetY"], row["sigma"] )
            pt = ( row["offsetX"], row["offsetY"] )
        self.rsim.setCentrePy( *pt )
        self.sim.initSim( self.rsim )
        print( "Initialised simulator at point", pt )
        self.setAmplitudes( row )
        self.param.setRow( row )
        src = makeSource( self.param )
        self.rsim.setSource( src )
    
        self.sim._rsim.update()
    
        im = self.sim.getDistortedImage( showmask=showmask ) 
        cropsize = self.param.get( "cropsize" )
        if self.xireference:
              R = np.float32( [ [ 1, 0, row["xiX"] ], [ 0, 1, -row["xiY"] ] ] )
              m,n = im.shape
              im = cv.warpAffine(im,R,(n,m))
        if self.reflines:
            drawAxes(im)
    
        if cropsize:
            print( "Cropping; cropsize =", cropsize )
            im = crop( im, cropsize )
        print( "Distorted image", type(im), im.shape )
        cv.imwrite(fn,im)
    
    def processFile(self,maxcount=None):

        count = 0
        for fn,row in self.frame.iterrows():
            print( "[roulettegen.py] Processing", fn )

            fn0 = os.path.join(self.directory, fn ) 
            self.makeSingle(fn=fn0,row=row)
            count += 1
            if maxcount is not None and count > maxcount: break
        return count
    def makeActual(self,fn,reflines=False):
        im = self.sim.getActualImage( reflines=reflines )
        cv.imwrite(fn,im)
    def makeApparent(self,fn,reflines=False):
        im = sim.getApparentImage( reflines=reflines )
        cv.imwrite(fn,im)

def main(args):
    """
    This is the main procedure of the script, simulating a dataset of
    roulette amplitudes based on a CLI args argument.
    """
    if not args.csvfile:
        raise Exception( "No CSV file given; the --csvfile option is mandatory." )

    resim = Resim( args.directory, args )

    count = 1
    if args.maxcount is None:
        maxcount = 2**30
    else:
        maxcount = int(args.maxcount)

    # Masking is not implemented in the Resim class.
    rsim = resim.rsim
    rsim.setMaskMode( args.mask )
    if not args.maskradius is None:
        rsim.setMaskRadius( float(args.maskradius) )
        
    for index,row in resim.frame.iterrows():
            print( "[roulettegen.py] Processing", index )

            fn = row.get("filename",None)
            print( "filename", fn )
            if fn is None:
                try:
                    namestem = f"image-{int(row['index']):05}" 
                except:
                    namestem = f"image-{row['index']}" 
                fn = namestem + ".png"
            else:
                namestem = fn.split(".")[0]
            fn0 = os.path.join(args.directory, fn ) 

            resim.makeSingle( fn, row, showmask=args.showmask )

            if args.actual:
               fn1 = os.path.join(args.directory,"actual-" + str(name) + ".png" ) 
               resim.makeActual( fn1, args.reflines )
            if args.apparent:
                fn2 = os.path.join(args.directory,"apparent-" + str(name) + ".png" ) 
                resim.makeApparent( fn2, args.reflines )

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
