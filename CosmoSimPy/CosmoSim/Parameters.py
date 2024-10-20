
from CosmoSimPy import SphericalSource, EllipsoidSource, TriangleSource, ImageSource
from CosmoSim import sourceDict

class Parameters:
    """
    The Parameters class wraps the commandline arguments as well as a CSV 
    row as a dict-like object.
    """
    def __init__(self,args):
        self._args = args
        self._row = {}
    def setRpw(self,row):
        self._row = row
    def get(self,key,default=None):
        try:
            r = self._args.key
        except AttributeError:
            r = default
        return self._row.get(key,r)
    def __getitem__(self,key):
        return get(key)


def makeSource(param):
    """
    Factory function to create a Source object given the parameter list.
    """
    mode = sourceDict( param.get("source") )
    size = param.get( "imagesize" )
    if mode == sourceDict.get( "Spherical" ):
        return SphericalSource( size, param.get( "sigma" ) )
    elif mode == sourceDict.get( "Ellipsoid" ):
        return SphericalSource( size, param.get( "sigma" ), param.get( "sigma2" ), param.get( "theta" ) )
    elif mode == sourceDict.get( "Triangle" ):
        return SphericalSource( size, param.get( "sigma" ), param.get( "theta" ) )
    elif mode == sourceDict.get( "Iamge (Einstein)" ):
        return ImageSource()
    else:
        raise Exception( "Unknown Source Mode" )
