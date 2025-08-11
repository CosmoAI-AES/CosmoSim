#! /usr/bin/env python3
# (C) 2025: Hans Georg Schaathun <georg@schaathun.net>
# Generate a set of lens/source parameters

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
    r = toml["lens"].get( "mode", [ "e" ] )
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

    # Lens
    einsteinR = uniform( toml["lens"], "einstein", (10,50) )

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

    src = random.choice( srcmode(toml) )
    cfg = random.choice( configs(toml) )
    return f'"{idx:04}","image-{idx:04}.png",{src},{cfg},{chi},' \
         + f'{R},{phi},{einsteinR},{sigma},{sigma2},{theta},{nterms},{x},{y}'

header = ( "index,filename,source,config,chi,"
         + "R,phi,einsteinR,sigma,sigma2,theta,nterms,x,y\n"
         )

def tomlReaad(infile):
    with open(infile, 'rb') as f:
        toml = tl.load(f)
    tomldefaults(toml)
    print(toml)
    print(configs(toml))
    print(srcmode(toml))
    return(toml)
def datasetgen(infile=None,toml=None,outfile=None):
    if toml is None:
        toml = tomlRead(infile)
    elif: not infile is None
        raise Exception("Conflicting arguments, both toml object and input file given.")
    n = toml["simulator"].get( "size", 10000 )
    sets = toml["simulator"].get( "datasets" )
    if sets:
        for s in sets:
            n1 = set[s].get( "size", n )
            outfile = set[s].get( "filename", outfile )
            datasetgen1(toml,outfile,n1)
    elif outfile:
        return datasetgen1(toml,outfile,n)
    else: 
        raise Exception("No output file given.")

def datasetgen1(toml,outfile,n,start=1):
    with open(outfile, 'w') as f:
      f.write(header)
      idx = start
      for i in range(n):
        l = getline(idx+1,toml)
        f.write(l)
        f.write("\n")
        idx += 1
      return idx
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
          prog = 'Dataset generator for CosmoSim',
          description = 'Generate CSV files for the datagen image generator',
          epilog = '')
    parser.add_argument('infile',help="Input file")
    parser.add_argument('outfile',nargs="?",help="Output file")
    args = parser.parse_args()
    datasetgen(args.infile,args.outfile)

