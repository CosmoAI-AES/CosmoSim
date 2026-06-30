# (C) 2026: Hans Georg Schaathun <georg@schaathun.net> 

from . import CosmoSimPy as cs
from .Dictionary import *

def getSource(param,verbose=1):
    """
    Factory function to create a Source object given the parameter list.
    """
    size = int( param.get( "imagesize" ) )
    src = param.get("source")
    ltprf0 = param.get( "lightprofile", None )
    if verbose:
        print( f"[getSource] src={src}, ltprf0={ltprf0}, verbose={verbose}" )
    if src.find("/") < 0:
       mode = sourceDict[src]
       if ltprf0 is None:
           ltprf = lightProfileDict.get( src, LightProfileSpec.Gaussian ) 
           if verbose > 1: print( "[getSource] Lightprofile:", src, ltprf )
       else:
           ltprf = lightProfileDict.get( ltprf0, LightProfileSpec.Gaussian ) 
           if verbose > 1: print( "[getSource] Lightprofile:", ltprf0, ltprf )
       if verbose:
          print( f"[getSource] mode={mode}, ltprf={ltprf}" )
       if mode == sourceDict.get( "Spherical" ):
           nsersic = float(param.get("n_sersic",4))
           luminosity = float(param.get("luminosity",10))
           if verbose > 1: 
               print( "[getSource] Spherical Source - "
                     + f"n_sersic={nsersic}, luminosity={luminosity}" )
           r = SphericalSource( size, float(param.get( "sigma" )),
                               nsersic, luminosity, ltprf=ltprf,
                               verbose=verbose)
       elif mode == sourceDict.get( "Ellipsoid" ):
           r = cs.EllipsoidSource( size, float(param.get( "sigma" )),
                   float(param.get( "sigma2" )),
                   float(param.get( "theta" ))*np.pi/180, ltprf)
       elif mode == sourceDict.get( "Triangle" ):
           r = cs.TriangleSource( size, float(param.get( "sigma" )),
                   float(param.get( "theta" ))*np.pi/180 )
       elif mode == sourceDict.get( "Iamge (Einstein)" ):
           r = cs.ImageSource( getSourceFileName( ) )
       else:
           raise Exception( "Unknown Source Mode" )
    else:
        r = makeSourceConstellation(src,size)
        if verbose:
            print( "[getSource] - makeSourceConstellation() has returned" )
    if verbose>1:
        print( "getSource() returns" )
    return r 

class SphericalSource(cs.SphericalSource):
    """Spherical source model.
    This is a wrapper around the C++ class to provide default
    arguments to the constructor.
    """
    def __init__( self, size, sigma, idx=0, lum=0,
                 ltprf=LightProfileSpec.Gaussian,
                 verbose=1 ):
        super().__init__( size, sigma, idx, lum, ltprf )
        if verbose: print( "[SphericalSource] constructor done" )

