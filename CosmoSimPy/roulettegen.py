#! /usr/bin/env python3
# (C) 2023: Hans Georg Schaathun <georg@schaathun.net>

"""
Generate an image for given parameters.
"""

import cv2 as cv
import sys
import os
import numpy as np

from CosmoSim.Image import drawAxes
from CosmoSim.Parameters import Parameters
import CosmoSim as cs

from Arguments import CosmoParser
import pandas as pd

from RouletteAmplitudes import RouletteAmplitudes 

def makeSingle(sim,args,name=None,row=None):
    print( "makeSingle" )

    if name == None: name = args.name
    sim._rsim.update()

    im = sim.getDistortedImage( showmask=args.showmask ) 
    print( "Distorted image", type(im), im.shape )
    if args.xireference:
          R = np.float32( [ [ 1, 0, row["xiX"] ], [ 0, 1, -row["xiY"] ] ] )
          m,n = im.shape
          im = cv.warpAffine(im,R,(n,m))
    if args.reflines:
        drawAxes(im)

    fn = os.path.join(args.directory, str(name) + ".png" ) 
    cv.imwrite(fn,im)

    if args.actual:
       fn = os.path.join(args.directory,"actual-" + str(name) + ".png" ) 
       im = sim.getActualImage( reflines=args.reflines )
       cv.imwrite(fn,im)
    if args.apparent:
       fn = os.path.join(args.directory,"apparent-" + str(name) + ".png" ) 
       im = sim.getApparentImage( reflines=args.reflines )
       cv.imwrite(fn,im)
    return None

def setAmplitudes( rsim, row, coefs ):
    maxm = coefs.getNterms()
    for m in range(maxm+1):
        for s in range((m+1)%2, m+2, 2):
            alpha = row[f"alpha[{m}][{s}]"]
            beta = row[f"beta[{m}][{s}]"]
            print( f"alpha[{m}][{s}] = {alpha}\t\tbeta[{m}][{s}] = {beta}." )
            rsim.setAlphaXi( m, s, alpha )
            rsim.setBetaXi( m, s, beta )


def main(args):
    if not args.csvfile:
        raise Exception( "No CSV file given; the --csvfile option is mandatory." )

    print( "Instantiate RouletteSim object ... " )
    sim = cs.RouletteSim()

    print( "Load CSV file:", args.csvfile )
    frame = pd.read_csv(args.csvfile)
    cols = frame.columns
    print( "columns:", cols )
    
    coefs = RouletteAmplitudes(cols)
    print( "Number of roulette terms: ", coefs.getNterms() )

    count = 1
    if args.maxcount is None:
        maxcount = 2**30
    else:
        maxcount = int(args.maxcount)

    rsim = cs.RouletteRegenerator()
    rsim.setMaskMode( args.mask )
    if not args.maskradius is None:
        rsim.setMaskRadius( float(args.maskradius) )
    if args.nterms:
        rsim.setNterms( int(args.nterms) )
    else:
        rsim.setNterms( coefs.getNterms() )
        
    param = Parameters( args )
    for index,row in frame.iterrows():
            print( "[roulettegen.py] Processing", index )

            if args.xireference:
                print( "xi", row["xiX"], row["xiY"], row["sigma"] )
                pt = (0,0)
            else:
                print( "Offset", row["offsetX"], row["offsetY"], row["sigma"] )
                pt = ( row["offsetX"], row["offsetY"] )
            rsim.setCentrePy( *pt )
            sim.initSim( rsim )
            print( "Initialised simulator at point", pt )
            sys.stdout.flush()

            setAmplitudes( rsim, row, coefs )
            print( "index", row["index"] )
            sys.stdout.flush()
                    
            param.setRow( row )
            src = cs.makeSource( param )
            rsim.setSource( src )

            fn = row.get("filename",None)
            if fn is None:
                namestem = f"image-{int(row['index']):05}" 
            else:
                namestem = fn.split(".")[0]
            makeSingle(sim,args,name=namestem,row=row)
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
    main(args)
