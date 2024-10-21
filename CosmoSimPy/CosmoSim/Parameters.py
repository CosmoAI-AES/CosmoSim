
from CosmoSim.CosmoSimPy import SphericalSource, EllipsoidSource, TriangleSource, ImageSource
from CosmoSim import sourceDict
import numpy as np

class Parameters:
    """
    The Parameters class wraps the commandline arguments as well as a CSV 
    row as a dict-like object.
    """
    def __init__(self,args):
        self._args = args
        self._row = {}
    def setRow(self,row):
        self._row = row
    def get(self,key,default=None):
        print( "Parameters.get(", key, ")" )
        try:
            r = self._args.__dict__[key]
        except AttributeError:
            print( self._args )
            r = default
        print( "Parameters.get() args ->", r )
        r = self._row.get(key,r)
        print( "Parameters.get() row ->", r )
        return r
    def __getitem__(self,key):
        return get(key)


def makeSource(param):
    """
    Factory function to create a Source object given the parameter list.
    """
    mode = sourceDict[ param.get("source") ]
    size = param.get( "imagesize" )
    if mode == sourceDict.get( "Spherical" ):
        return SphericalSource( size, param.get( "sigma" ) )
    elif mode == sourceDict.get( "Ellipsoid" ):
        return EllipsoidSource( size, param.get( "sigma" ),
                param.get( "sigma2" ), param.get( "theta" )*np.pi/180 )
    elif mode == sourceDict.get( "Triangle" ):
        return TriangleSource( size, param.get( "sigma" ),
                param.get( "theta" )*np.pi/180 )
    elif mode == sourceDict.get( "Iamge (Einstein)" ):
        return ImageSource()
    else:
        raise Exception( "Unknown Source Mode" )
