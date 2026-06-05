from . import __version__

import os

from .roulettegen import rgen
from .datagen import datagen,makeSingle

from .CLI.Arguments import CosmoParser,Parameters

def main(args,cfg):
    
    if args.toml:
        with open(args.toml, 'rb') as f:
            toml = tl.load(f)
    else:
        toml = {}

    param = Parameters( cfg, toml )

    if args.directory:
            os.makedirs( args.directory, exist_ok=True )
    if args.roulette:
            rgen(args,param)
    elif args.csvfile:
            datagen(args,param)
    else:
        imsim = makeSingle(param,verbose=args.verbose)
        imsim.close()

if __name__ == "__main__":
    print( "[CosmoSim] batch generator ..." )
    parser = CosmoParser(
          prog = 'CosmoSim makeimage',
          description = 'Bulk simulation of gravitational lensing',
          epilog = '')

    args = parser.parse_args()
    if args.version:
        print( "CosmoSim version", __version__ )
    else:
        cfg = parser.getConfig()
        main( args, cfg )
        print( "[CosmoSim] done." )
