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
from CosmoSim import CosmoSim,getMSheaders

from Arguments import CosmoParser
from CosmoSim.Parameters import Parameters, makeSource
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
    if row.get("config",None) != None:
        sim.setConfigMode( row["config"] )
    elif row.get("cluster",None) != None:
        print( "setCluster from CSV" )
        sim.setCluster( row["cluster"] )
    elif row.get("lens",None) != None:
        sim.setLensMode( row["lens"] )
    if row.get("model",None) != None:
        sim.setModelMode( row["model"] )
    if row.get("sampled",None) != None:
        sim.setSampled( row["sampled"] )
    if row.get("chi",None) != None:
        sim.setCHI( row["chi"] )
    if row.get("einsteinR",None) != None:
        sim.setEinsteinR( row["einsteinR"] )
    if row.get("ellipseratio",None) != None:
        sim.setRatio( row["ellipseratio"] )
    if row.get("orientation",None) != None:
        sim.setOrientation( row["orientation"] )
    if row.get("imagesize",None) != None:
        sim.setImageSize( row["imagesize"] )
        sim.setResolution( row["imagesize"] )
    if row.get("nterms",None) != None:
        sim.setNterms( row["nterms"] )

def makeSingle(sim,param,name=None,row=None,outstream=None):
    """Process a single parameter set, given either as a pandas row or
    just as args parsed from the command line.
    """
    if not row is None:
       setParameters( sim, row )
       print( "index", row["index"] )
       param.setRow( row )
       src = makeSource( param )
       sim.setSource( src )
       name = row["filename"].split(".")[0]
    elif name == None:
        name = param.get( "name" )
    print ( "[datagen.py] ready for runSim()\n" ) ;
    sys.stdout.flush()
    sim.runSim()
    print ( "[datagen.py] runSim() completed\n" ) ;
    centrepoint = makeOutput(sim,args,name,actual=args.actual,apparent=args.apparent,original=args.original,reflines=args.reflines,critical=args.criticalcurves)
    print( "[datagen.py] Centre Point", centrepoint, "(Centre of Luminence in Planar Co-ordinates)" )
    if args.join:
        # sim.setMaskMode(False)
        sim.runSim()
        print ( "[datagen.py] runSim() completed\n" ) ;
        sim.maskImage(float(args.maskscale))
        joinim = sim.getDistortedImage(critical=args.criticalcurves)
        nc = int(args.components)
        for i in range(1,nc):
           sim.moveSim(rot=2*i*np.pi/nc,scale=1)
           sim.maskImage(float(args.maskscale))
           im = sim.getDistortedImage(critical=args.criticalcurves)
           joinim = np.maximum(joinim,im)
        fn = os.path.join(args.directory,"join-" + str(name) + ".png" ) 
        if args.reflines:
            drawAxes(joinim)
        cv.imwrite(fn,joinim)
    if args.family:
        sim.moveSim(rot=-np.pi/4,scale=1)
        makeOutput(sim,args,name=f"{name}-45+1")
        sim.moveSim(rot=+np.pi/4,scale=1)
        makeOutput(sim,args,name=f"{name}+45+1")
        sim.moveSim(rot=0,scale=-1)
        makeOutput(sim,args,name=f"{name}+0-1")
        sim.moveSim(rot=0,scale=2)
        makeOutput(sim,args,name=f"{name}+0+2")
    if args.psiplot:
        a = sim.getPsiMap()
        print(a.shape, a.dtype)
        print(a)
        sys.stdout.flush()
        nx,ny = a.shape
        X, Y = np.meshgrid( range(nx), range(ny) )
        hf = plt.figure()
        ha = hf.add_subplot(111, projection='3d')
        ha.plot_surface(X, Y, a)
        fn = os.path.join(args.directory,"psi-" + str(name) + ".svg" ) 
        plt.savefig( fn )
        plt.close()
    if args.kappaplot:
        a = sim.getMassMap()
        print(a.shape, a.dtype)
        print(a)
        nx,ny = a.shape
        X, Y = np.meshgrid( range(nx), range(ny) )
        hf = plt.figure()
        ha = hf.add_subplot(111, projection='3d')
        ha.plot_surface(X, Y, a)
        fn = os.path.join(args.directory,"kappa-" + str(name) + ".svg" ) 
        plt.savefig( fn )
        plt.close()
    if outstream:
        maxm = int(args.nterms)
        print( "[datagen.py] Finding Alpha/beta; centrepoint=", centrepoint )
        sys.stdout.flush()
        r = [ row[x] for x in outcols ]
        releta = sim.getRelativeEta(centrepoint=centrepoint)
        offset = sim.getOffset(centrepoint=centrepoint)
        xioffset = sim.getXiOffset(centrepoint)
        if args.xireference:
            ab = sim.getAlphaBetas(maxm)
        else:
            ab = sim.getAlphaBetas(maxm,pt=centrepoint)
        print(r)
        r.append( centrepoint[0] )
        r.append( centrepoint[1] )
        r.append( releta[0] )
        r.append( releta[1] )
        r.append( offset[0] )
        r.append( offset[1] )
        r.append( xioffset[0] )
        r.append( xioffset[1] )
        print(ab)
        r += ab
        line = ",".join( [ str(x) for x in r ] )
        line += "\n"
        outstream.write( line )


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
    if args.reflines:
        drawAxes(im)

    fn = os.path.join(args.directory, str(name) + ".png" ) 
    cv.imwrite(fn,im)

    if actual:
       fn = os.path.join(args.directory,"actual-" + str(name) + ".png" ) 
       im = sim.getActualImage( reflines=args.reflines )
       cv.imwrite(fn,im)
    if apparent:
       fn = os.path.join(args.directory,"apparent-" + str(name) + ".png" ) 
       im = sim.getApparentImage( reflines=args.reflines )
       cv.imwrite(fn,im)
    return (cx,cy)



if __name__ == "__main__":
    parser = CosmoParser(
          prog = 'CosmoSim makeimage',
          description = 'Generaet an image for given lens and source parameters',
          epilog = '')

    args = parser.parse_args()

    print( "[datagen.py] Instantiate Simulator ... " )
    sys.stdout.flush()
    if args.amplitudes:
       sim = CosmoSim(fn=args.amplitudes)
    elif args.nterms:
       sim = CosmoSim(maxm=int(args.nterms))
    else:
       sim = CosmoSim()
    print( "[datagen.py] Simulator initialised" )
    if args.phi:
        sim.setPolar( float(args.x), float(args.phi) )
    else:
        sim.setXY( float(args.x), float(args.y) )
    if args.source:
        sim.setSourceMode( args.source)
        sim.setSourceParameters( float(args.sigma),
            float(args.sigma2), float(args.theta) )
    if args.sampled:
        sim.setSampled( 1 )
    else:
        sim.setSampled( 0 )

    if args.config:
        sim.setConfigMode( args.config )
    elif args.cluster:
        print( "setCluster from arguments" )
        sim.setCluster( args.cluster )
    elif args.lens:
        sim.setLensMode( args.lens)

    if args.model:
        sim.setModelMode( args.model)
    if args.chi:
        sim.setCHI( float(args.chi) )
    if args.einsteinradius:
        sim.setEinsteinR( float(args.einsteinradius) )
    if args.ratio:
        sim.setRatio( float(args.ratio) )
    if args.orientation:
        sim.setOrientation( float(args.orientation) )
    if args.imagesize:
        sim.setImageSize( int(args.imagesize) )
        sim.setResolution( int(args.imagesize) )
    if args.nterms:
        sim.setNterms( int(args.nterms) )
    if args.outfile:
        outstream = open(args.outfile,"wt")
    else:
        outstream = None

    sim.setMaskMode( args.mask )

    if args.csvfile:
        print( "Load CSV file:", args.csvfile )
        frame = pd.read_csv(args.csvfile)
        cols = frame.columns
        print( "columns:", cols )
        outcols = list(frame.columns)
        if outstream != None:
           headers = ",".join( outcols + relcols + getMSheaders(int(args.nterms)) )
           headers += "\n"
           outstream.write(headers)
        for index,row in frame.iterrows():
            param = Parameters( args )
            makeSingle(sim,param,row=row,outstream=outstream)
    else:
        makeSingle(sim,args)
    sim.close()
    if outstream != None: outstream.close()
