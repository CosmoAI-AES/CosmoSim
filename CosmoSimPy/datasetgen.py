#! /usr/bin/env python2
# (C) 2023: Hans Georg Schaathun <georg@schaathun.net>
# Generate a set of lens/source parameters

import numpy as np

from random import randint

n = 24000
i = int(n / 250)

fn = "Datasets/dataset.csv"
srcmodes = "s"
configs = ["rs"]


def getline(idx,chi=0,nterms=16):
    if 0 == chi:
        chi = randint(30,70)

    # Source
    sigma = randint(1,60)
    sigma2 = 0
    theta = 0

    # Lens
    einsteinR = randint(10,50)

    # Polar Source Co-ordinates
    phi = randint(0,359)
    R = randint(einsteinR,100)

    # Cartesian Co-ordinates
    x = R*np.cos(np.pi*phi/180)
    y = R*np.sin(np.pi*phi/180)

    srcmode = srcmodes[randint(0,len(srcmodes)-1)]
    config = configs[randint(0,len(configs)-1)]
    return f'{idx},"image-{idx:04}.png",{srcmode},{config},{chi},' \
         + f'{R},{phi},{einsteinR},{sigma},{sigma2},{theta},{nterms},{x},{y}'

header = ( "index,filename,source,config,chi,"
         + "R,phi,einsteinR,sigma,sigma2,theta,nterms,x,y\n"
         )

def main():
    with open(fn, 'w') as f:
      f.write(header)
      for i in range(n):
        l = getline(i+1)
        f.write(l)
        f.write("\n")

if __name__ == "__main__":
   main()
