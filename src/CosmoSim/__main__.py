from . import __version__


from .roulettegen import main as roulette
from .datagen import main as gen

if __name__ == "__main__":
    print( "[CosmoSim] batch generator ..." )
    parser = CosmoParser(
          prog = 'CosmoSim makeimage',
          description = 'Bulk simulation of gravitational lensing',
          epilog = '')

    args = parser.parse_args()
    cfg = parser.getConfig()
    if args.version:
        print( "CosmoSim version", __version__ )
    elif:
        if args.directory:
            os.makedirs( args.directory, exist_ok=True )
        if args.roulette:
            roulette(main,cfg)
        else:
            gen(main,cfg)
        print( "[CosmoSim] done." )
