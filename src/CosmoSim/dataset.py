#! /usr/bin/env python3
# (C) 2025: Hans Georg Schaathun <georg@schaathun.net>

"""
Generate random sets of lens/source parameters.
The module can be run as a script, taking a TOML file as input
and producing a CSV file as output.
Alternatively, the datasetgen() function can be imported and
used from other modules.
"""

import numpy as np
import tomllib as tl
import numbers

import random 
import argparse

def isnumeric(x): return isinstance(x, numbers.Number )

def tomldefaults(toml):
    toml["simulator"] = toml.get( "simulator", {} )
    toml["position"] = toml.get( "position", {} )
    toml["source"] = toml.get( "source", {} )
    toml["lens"] = toml.get( "lens", {} )


def configs(toml):
    r = toml["simulator"].get( "configs", [ "ss" ] )
    if isinstance(r, str): r = [ r ] 
    return r
def srcmode(toml):
    r = toml["source"].get( "mode", [ "e" ] )
    if isinstance(r, str): r = [ r ] 
    return r
def uniform(toml,key,rng=(0,50)):
    if key in toml: return toml[key]
    mn = toml.get( f"{key}-min", rng[0] )
    mx = toml.get( f"{key}-max", rng[1] )
    return random.randint(mn,mx)

def getline(idx,toml):

    nterms = toml["simulator"].get( "nterms", 16 )
    chi = toml["lens"].get( "chi", random.randint(30,70) )

    # Source
    sigma = uniform( toml["source"], "sigma", (1,60) )
    sigma2 = uniform( toml["source"], "sigma2", (1,40) )
    theta = uniform( toml["source"], "theta", (0,179) )
    coor = toml["source"].get( "position", "cartesian" )

    # Lens
    einsteinR = uniform( toml["lens"], "einstein", (10,50) )

    if coor == "polar":
        # Polar Source Co-ordinates
        phi = uniform( toml["position"], "phi", (0,359) )
        rmin = toml["position"].get( "r-min" )
        rmax = toml["position"].get( "r-max" )
        if not isnumeric(rmin): rmin = einsteinR
        if not isnumeric(rmax): rmax = 2.5*rmin

        R =  random.randint(rmin,rmax)

        # Cartesian Co-ordinates
        x = R*np.cos(np.pi*phi/180)
        y = R*np.sin(np.pi*phi/180)
    else:
        # Cartesian Co-ordinates
        (x,y) = (0,0)
        while (x,y) == (0,0):
            x = uniform( toml["position"], "x", (-100,+100) )
            y = uniform( toml["position"], "y", (-100,+100) )
        R = np.sqrt( x*x + y*y )
        phi = np.atan2(x,y)

    src = random.choice( srcmode(toml) )
    cfg = random.choice( configs(toml) )
    return f'"{idx:04}","image-{idx:04}.png",{src},{cfg},{chi},' \
         + f'{R},{phi},{einsteinR},{sigma},{sigma2},{theta},{nterms},{x},{y}'

header = ( "index,filename,source,config,chi,"
         + "R,phi,einsteinR,sigma,sigma2,theta,nterms,x,y\n"
         )

def datasetgen(infile,outfile):
    with open(infile, 'rb') as f:
        toml = tl.load(f)
    tomldefaults(toml)
    print(toml)
    print(configs(toml))
    print(srcmode(toml))

    with open(outfile, 'w') as f:
      f.write(header)
      n = toml["simulator"].get( "size", 10000 )
      for i in range(n):
        l = getline(i+1,toml)
        f.write(l)
        f.write("\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
          prog = 'Dataset generator for CosmoSim',
          description = 'Generate CSV files for the datagen image generator',
          epilog = '')
    parser.add_argument('infile',help="Input file")
    parser.add_argument('outfile',help="Output file")
    args = parser.parse_args()
    datasetgen(args.infile,args.outfile)

