#! /usr/bin/env python3
# (C) 2023: Hans Georg Schaathun <georg@schaathun.net>

"""
Generate an image for given parameters.
"""

import cv2 as cv
import sys
import os
import numpy as np
import matplotlib.pyplot as plt

from CosmoSim.Image import drawAxes
from CosmoSim import RouletteSim as CosmoSim,getMSheaders,PsiSpec,ModelSpec

from Arguments import CosmoParser
import pandas as pd

from RouletteAmplitudes import RouletteAmplitudes 

def makeSingle(sim,args,name=None,row=None):
    print( "makeSingle" )
    sys.stdout.flush()
    if name == None: name = args.name
    sim.runSim()
    print( "runSim() returned" )
    sys.stdout.flush()

    im = sim.getDistortedImage( showmask=args.showmask ) 
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

def setAmplitudes( sim, row, coefs ):
    maxm = coefs.getNterms()
    for m in range(maxm+1):
        for s in range((m+1)%2, m+2, 2):
            alpha = row[f"alpha[{m}][{s}]"]
            beta = row[f"beta[{m}][{s}]"]
            print( f"alpha[{m}][{s}] = {alpha}\t\tbeta[{m}][{s}] = {beta}." )
            sim.setAlphaXi( m, s, alpha )
            sim.setBetaXi( m, s, beta )


if __name__ == "__main__":
    print( "[roulettegen.py] Starting ..." )
    parser = CosmoParser(
          prog = 'CosmoSim makeimage',
          description = 'Generaet an image for given lens and source parameters',
          epilog = '')

    args = parser.parse_args()

    if not args.csvfile:
        raise Exception( "No CSV file given; the --csvfile option is mandatory." )

    print( "Instantiate RouletteSim object ... " )
    sim = CosmoSim()
    print( "Done" )

    if args.imagesize:
        sim.setImageSize( int(args.imagesize) )
        sim.setResolution( int(args.imagesize) )

    sim.setMaskMode( args.mask )

    print( "Load CSV file:", args.csvfile )
    frame = pd.read_csv(args.csvfile)
    cols = frame.columns
    print( "columns:", cols )
    
    coefs = RouletteAmplitudes(cols)
    if args.nterms:
        sim.setNterms( int(args.nterms) )
    else:
        sim.setNterms( coefs.getNterms() )
    print( "Number of roulette terms: ", coefs.getNterms() )

    count = 1
    if args.maxcount is None:
        maxcount = 2**30
    else:
        maxcount = int(args.maxcount)
        
    for index,row in frame.iterrows():
            print( "Processing", index )
            sys.stdout.flush()
            # print( "Relative eta", row.get("reletaX", None), row.get("reletaY",None) )
            # print( "Centre Point", row.get("centreX",None), row.get("centreY",None) )
            if args.xireference:
                print( "xi", row["xiX"], row["xiY"], row["sigma"] )
                sim.initSim( 0, 0 )
            else:
                print( "Offset", row["offsetX"], row["offsetY"], row["sigma"] )
                sim.initSim( row["offsetX"], row["offsetY"] )
            print( "Initialised simulator" )
            sys.stdout.flush()

            setAmplitudes( sim, row, coefs )
            print( "index", row["index"] )
            sys.stdout.flush()
                    
            if row.get("source",None) != None:
                sim.setSourceMode( row["source"] )
            sim.setSourceParameters( float(row["sigma"]), float(row.get("sigma2",0)),
                                     float(row.get("theta",0)) ) 
            fn = row.get("filename",None)
            if fn is None:
                namestem = f"image-{int(row['index']):05}" 
            else:
                namestem = fn.split(".")[0]
            makeSingle(sim,args,name=namestem,row=row)
            count += 1
            if count > maxcount: break

    sim.close()
    print( "[roulettegen.py] Done" )
