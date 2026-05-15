# (C) 2023,2026: Hans Georg Schaathun <georg@schaathun.net> 

"""
This defines the `ArgumentParser` for the CosmoSim scripts.
Several scripts use the same arguments, and thus share this module.

The argument list is not complete.  For ease of maintenance, we should
abandon support for command line arguments and refer to CSV and TOML 
files instead.

`paramap` is a mapping from the command line options into the
structure of the TOML config files.  The key is the parameter
name used in CSV and on the command line, while the value is
the key used in TOML and nested `dict`s.
"""

import argparse
from cascadict import CascaDict

skel = { "simulator" : { "config" : {} }
         , "source" : {}
         , "lens" : {}
         , "dataset" : {}
         , "annotation" : {}
         }

paramap = {
        "config" : ( "simulator", "config", "mode" ), # renamed
        "lens" : ( "simulator", "config", "lens" ),
        "model" : ( "simulator", "config", "model" ),
        "sampled" : ( "simulator", "config", "sampled" ),
        "nterms" : ( "simulator", "nterms" ),
        "imagesize" : ( "simulator", "imagesize" ),
        "cropsize" : ( "simulator", "cropsize" ),
        "xireference" : ( "simulator", "xireference" ), # new
        "centred" : ( "simulator", "centred" ), # new
        "source" : ( "source", "mode" ), # used differently

        "chi" : ( "lens", "chi" ),
        "einsteinradius" : ( "lens", "einsteinradius" ),
        "orientation" : ( "lens", "orientation" ),
        "ratio" : ( "lens", "ellipseratio" ), # relabelled

        "sigma" :  ( "source", "sigma" ),
        "sigma2" : ( "source", "sigma2" ),
        "theta" : ( "source", "theta" ),
        "directory" : ( "dataset", "directory" ) ,
        "reflines" : ( "annotation", "reflines" ),
        "criticalcurves" : ( "annotation", "criticalcurves" ),
        }

"""
CLI options to be refactored into TOML structure.
+ [source] -> position is implicit

+ [position]
        "x" : 1,
        "y" : 1,
        "phi" : 45,
        # r is equal to x

            
+ [masking] not yet in TOML
    "maskradius" : None,
    "mask" : False,
    "showmask" : False,
    "maskscale" : 0.9,

+ Not implemented yet
        "cluster" : None,

CLI options never used in main parameter structure
    "toml" : None,        # Source
    "maxcount" : None,
    "amplitudes" : None,  # Amplitudes file
    "mldata" : False,
    "csvfile" : None,
    "outfile" : None,
    "name" : "test",

CLI options currently unsupported
    "psiplot" : False,
    "kappaplot" : False,
    "family" : False,
    "components" : 6,
    "join" : False,
    "apparent" : False, 
    "actual" : False, 
"""

class CosmoParser(argparse.ArgumentParser):
  """Argument Parser for CosmoSim.
  The class provides standardised CLI options for many scripts
  in the CosmoSim suite.  
  """
  def getArgs(self,*a,**kw):
      """Parse the arguments and return the resulting `args` object.
      """
      if not hasattr(self,"_args"):
          self._args = super().parse_args(*a,**kw)
      return self._args
  def getConfig(self,*a,**kw):
      """Return the configuration as a nested `dict` structure.
      The arguments are parsed if required.
      """
      if not hasattr(self,"_args"):
          self._args = super().parse_args(*a,**kw)
      cfg = CascaDict( skel )
      for k in self._args.__dict__:
          if k in paramap:
              key = paramap[k]
              d = cfg
              for subkey in key[:-1]:
                  try:
                     d = d[subkey]
                  except KeyError:
                      d[subkey] = {}
                      d = d[subkey]
              d[key[-1]] = self._args.__dict__[k]
      return cfg
  def __init__(self,*a,**kw):
    super().__init__(*a,**kw)

    # Model selection
    self.add_argument('-l', '--lens',
            help="lens model")
    self.add_argument('--cluster', help="cluster lens")
    self.add_argument('-L', '--model',
            help="simulation model")
    self.add_argument('-S', '--source',
            default="Spherical", help="source model")
    self.add_argument('-G', '--sampled', action='store_true',
            default=False, help="Sample the lens model")

    # Model Parameters
    self.add_argument('-x', '--x', default=0, help="x coordinate")
    self.add_argument('-y', '--y', default=0, help="y coordinate")
    self.add_argument('-T', '--phi', help="polar coordinate angle (phi)")

    self.add_argument('-s', '--sigma', default=20, help="source size (sigma)")
    self.add_argument('-2', '--sigma2', default=10, help="secondary source size (sigma2)")
    self.add_argument('-t', '--theta', default=45, help="source rotation angle (theta)")

    self.add_argument('-X', '--chi', default=50, help="lens distance ratio (chi)")
    self.add_argument('-E', '--einsteinradius', default=20, help="Einstein radius")
    self.add_argument('-r', '--ratio', help="Ratio (usually Elliptic eccentricity)")
    self.add_argument('--orientation', default=0, help="Orientation of the lens")
    self.add_argument('--config', default=0, help="Configuration (Model and Lens)")

    # Other parameters
    self.add_argument('-n', '--nterms', type=int,
                      help="Number of Roulettes terms", default=15)
    self.add_argument('-Z', '--imagesize', default=512, help="image size for calculations")
    self.add_argument('-z', '--cropsize', help="Final image size")

    # Output configuration 
    self.add_argument('-R', '--reflines',action='store_true',
            help="Add reference (axes) lines")
    self.add_argument( '--criticalcurves',action='store_true',
            help="Add critical curves to the distorted image")
    self.add_argument('-C', '--centred',action='store_true', help="centre image")
    self.add_argument('--maskradius',
            help="Set explicit masking radius")
    self.add_argument('-M', '--mask',action='store_true',
            help="Mask out the convergence circle")
    self.add_argument('-m', '--showmask',action='store_true',
            help="Mark the convergence circle")
    self.add_argument('-O', '--maskscale',default="0.9",
            help="Scaling factor for the mask radius")
    self.add_argument('-P', '--psiplot',action='store_true',default=False,
            help="Plot lens potential as 3D surface")
    self.add_argument('-K', '--kappaplot',action='store_true',default=False,
            help="Plot mass distribution as 3D surface")
    self.add_argument('-f', '--family',action='store_true',
            help="Several images moving the viewpoint")
    self.add_argument('-F', '--amplitudes',help="Amplitudes file")
    self.add_argument('-A', '--apparent',action='store_true',help="write apparent image")
    self.add_argument('--mldata',action='store_true',help="Make roulette output for ML without redundant colums")
    self.add_argument('-a', '--actual',action='store_true',help="write actual image")

    # Output file names
    self.add_argument('-N', '--name', default="test",
            help="simulation name")
    self.add_argument('-D', '--directory',default="./",
            help="directory path (for output files)")

    # Joining images
    self.add_argument('-c', '--components',default="6",
            help="Number of components for joined image")
    self.add_argument('-J', '--join',action='store_true',
            help="Join several images from different viewpoints")

    # Using CSV data sets
    self.add_argument('-o', '--outfile',
            help="Output CSV file")
    self.add_argument('-i', '--csvfile',
            help="Dataset to generate (CSV file)")
    self.add_argument('--toml',
            help="TOML file defining a random dataset to generate.")

    self.add_argument('--maxcount',
            help="Maximum number of images to process")
    self.add_argument('--xireference',default=True, action=argparse.BooleanOptionalAction,
            help="Use apparent position as reference for roulette amplitudes")

def setParameters(sim,row):
    print( row ) 
    if row.get("y",None) != None:
        print( "XY", row["x"], row["y"] )
        sim.setXY( row["x"], row["y"] )
    elif row.get("phi",None) != None:
        print( "Polar", row["x"], row["phi"] )
        sim.setPolar( row["x"], row["phi"] )
    if row.get("lens",None) != None:
        sim.setModelMode( row["lens"] )
    if row.get("chi",None) != None:
        sim.setCHI( row["chi"] )
    if row.get("ellipseratio",None) != None:
        sim.setRatio( row["ellipseratio"] )
    if row.get("orientation",None) != None:
        sim.setOrientation( row["orientation"] )
    if row.get("einsteinR",None) != None:
        sim.setEinsteinR( row["einsteinR"] )
    if row.get("imagesize",None) != None:
        sim.setImageSize( row["imagesize"] )
        sim.setResolution( row["imagesize"] )
    if row.get("nterms",None) != None:
        sim.setNterms( row["nterms"] )
    if row.get("lightprofile",None) != None:
        sim.setLightProfile( row["lightprofile"] )
