#! /usr/bin/env python3
# (C) 2023: Hans Georg Schaathun <georg@schaathun.net>

"""
Generate an image for given parameters.
"""

import os
import argparse
from CosmoSim import CosmoSim
import pandas as pd

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
    if row.get("cluster",None) != None:
        print( "Cluster", row["cluster"] )
        sim.setCluster( row["cluster"] )

def makeSingle(sim,args,row):
    """Process a single parameter set, given either as a pandas row or
    just as args parsed from the command line.
    """
    setParameters( sim, row )
    print( "index", row["index"] )
    name=row["filename"].split(".")[0]

    print ( "[datagen.py] ready for runSim()\n" ) ;
    sim.runSim()
    print ( "[datagen.py] runSim() completed\n" ) ;

if __name__ == "__main__":


    parser = argparse.ArgumentParser(
          prog = 'CosmoSim makeimage',
          description = 'Generaet an image for given lens and source parameters',
          epilog = '')
    parser.add_argument('-i', '--csvfile',
            help="Dataset to generate (CSV file)")

    args = parser.parse_args()

    print( "Instantiate Simulator ... " )
    sim = CosmoSim()
    print( "Done" )

    if args.csvfile:
        print( "Load CSV file:", args.csvfile )
        frame = pd.read_csv(args.csvfile)


        for index,row in frame.iterrows():
            makeSingle(sim,args,row=row)
    else:
        print( "not supported!" )
    sim.close()
