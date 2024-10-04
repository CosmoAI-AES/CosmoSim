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

from CosmoSim.Image import centreImage, drawAxes
from CosmoSim import CosmoSim

from Arguments import CosmoParser, setParameters
import pandas as pd

defaultoutcols = [ "index", "filename", "source", "lens", "chi", "R", "phi", "einsteinR", "sigma", "sigma2", "theta", "x", "y" ]
relcols = [ "centreX", "centreY", "reletaX", "reletaY", "offsetX", "offsetY", "xiX", "xiY" ]
def setParameters(sim,row):
    print( row ) 
    if row.get("y",None) != None:
        print( "XY", row["x"], row["y"] )
        sim.setXY( row["x"], row["y"] )
    elif row.get("phi",None) != None:
        print( "Polar", row["x"], row["phi"] )
        sim.setPolar( row["x"], row["phi"] )
    if row.get("sigma",None) != None:
        sim.setSourceParameters( row["sigma"],
            row.get("sigma2",-1), row.get("theta",-1) )
    elif row.get("cluster",None) != None:
        sim.setCluster( row["cluster"] )

def makeSingle(sim,args,name=None,row=None):
    """Process a single parameter set, given either as a pandas row or
    just as args parsed from the command line.
    """
    if not row is None:
       setParameters( sim, row )
       print( "index", row["index"] )
       name=row["filename"].split(".")[0]
    elif name == None:
        name = args.name
    print ( "[datagen.py] ready for runSim()\n" ) ;
    sim.runSim()
    print ( "[datagen.py] runSim() completed\n" ) ;
    centrepoint = makeOutput(sim,args,name,actual=args.actual,apparent=args.apparent,original=args.original,reflines=args.reflines,critical=args.criticalcurves)
    print( "[datagen.py] Centre Point", centrepoint, "(Centre of Luminence in Planar Co-ordinates)" )

def makeOutput(sim,args,name=None,rot=0,scale=1,actual=False,apparent=False,original=False,reflines=False,critical=False):
    im = sim.getDistortedImage( critical=critical, showmask=args.showmask ) 

    (cx,cy) = 0,0
    if args.centred:
        (centreIm,(cx,cy)) = centreImage(im)
        if original:
           fn = os.path.join(args.directory,"original-" + str(name) + ".png" ) 
           if reflines: drawAxes(im)
           cv.imwrite(fn,im)
        im = centreIm
    if args.cropsize:
        csize = int(args.cropsize)
        (m,n) = im.shape
        if csize < min(m,n):
            assert m == n
            c = (m-csize)/2
            c1 = int(np.floor(c))
            c2 = int(np.ceil(c))
            im = im[c1:-c2,c1:-c2]
            assert csize == im.shape[0]
            assert csize == im.shape[1]

    fn = os.path.join(args.directory, str(name) + ".png" ) 
    cv.imwrite(fn,im)

    return (cx,cy)



if __name__ == "__main__":
    parser = CosmoParser(
          prog = 'CosmoSim makeimage',
          description = 'Generaet an image for given lens and source parameters',
          epilog = '')

    args = parser.parse_args()

    print( "Instantiate Simulator ... " )
    if args.amplitudes:
       sim = CosmoSim(fn=args.amplitudes)
    elif args.nterms:
       sim = CosmoSim(maxm=int(args.nterms))
    else:
       sim = CosmoSim()
    print( "Done" )

    if args.phi:
        sim.setPolar( float(args.x), float(args.phi) )
    else:
        sim.setXY( float(args.x), float(args.y) )

    sim.setSourceParameters( float(args.sigma),
            float(args.sigma2), float(args.theta) )

    if args.csvfile:
        print( "Load CSV file:", args.csvfile )
        frame = pd.read_csv(args.csvfile)
        cols = frame.columns
        print( "columns:", cols )
        outcols = list(frame.columns)
        for index,row in frame.iterrows():
            makeSingle(sim,args,row=row)
    else:
        print( "not supported!" )
    sim.close()
