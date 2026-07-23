# (C) 26: Hans Georg Schaathun <georg@schaathun.net> 

"""
Fanctions to create lenses, sources, and simulators.
+ `getSimulator`
+ `getLens`
+ `getSource`
"""

from .. import CosmoSimPy as cs
from .. import AmplitudeManager as ampmgr
from ..Sources import *
from ..Lens import *
from CosmoSim.Dictionary import *
import numpy as np
import os, sys


def getSimulator(param,lens=None,source=None,verbose=1):
    """Factory function to create a back end simulator according
    to the paramters object provided.
    The lens must be given to instantiate closed form point mass
    simulators, but is otherwise optional.
    The source is optional.
    """
    model = param.get( ( "simulator", "model" ), None )
    if model is None:
        raise RuntimeError( "[getSimulator] No simulator model" )
    elif model == "Raytrace":
        sim = cs.RaytraceModel()
        if lens is not None:
            sim.setLens( lens )
    elif model == "Roulette":
        sim = cs.RouletteModel()
        if lens is not None:
            sim.setLens( lens )
    else:
        raise RuntimeError( f"[getSimulator] Unknown model: {model}" )
    if source is not None:
        sim.setSource( source )
    msk = param.get( "mask", None )
    if msk is not None:
        if verbose: print( "[getSimulator] sets mask", msk )
        sim.setMaskMode( msk )
    sim.setNterms( param.get( ( "simulator", "nterms" ), 5 ) )
    #   sim->setBGColour( bgcolour ) ;  # TODO
    #   sim->setMaskRadius( maskRadius ) ; # TODO
    return sim

def makeSourceConstellation(src,size,verbose=1):
    """
    Factory function to create a Source Constellation comprising several
    galaxies.  This is an auxiliary for `getSource`.
    """

    ss = src.split(";")
    sl = [ x.split("/") for x in ss ]
    if verbose:
        print( "makeSourceConstellation: src=", src, "size=", size, "sl=", sl )
    constellation = SourceConstellation(size)
    for s in sl:
        mode = sourceDict[s[0]]
        ltprf = lightProfileDict.get( s[0], LightProfileSpec.Gaussian ) 
        if mode == sourceDict.get( "Spherical" ):
            constituent = SphericalSource( size, float(s[3]), float(s[6]),
                                          float(s[7]), ltprf=ltprf,
                                          verbose=verbose )

        elif mode == sourceDict.get( "Ellipsoid" ):
            constituent = cs.EllipsoidSource( size, float(s[3]),
                    float(s[4]), float(s[5])*np.pi/180, ltprf=ltprf)
        elif mode == sourceDict.get( "Triangle" ):
            constituent = cs.TriangleSource( size, float(s[3]), float(s[4])*np.pi/180 )
        elif mode == sourceDict.get( "Iamge (Einstein)" ):
            constituent = cs.ImageSource( getSourceFileName( ) )
        else:
            raise Exception( "Unknown Source Mode" )

        constellation.addSource( constituent, float(s[1]), float(s[2]))
    if verbose>1:
        print( "makeSourceConstellation() returns" )
    return constellation

def getLens(param,verbose=1):
    lensmode = param.get( ( "lens", "mode" ), None )
    cluster = param.get( ( "lens", "cluster" ), None )
    fn = param.get( ( "lens", "amplitudefile" ) )
    if fn is not None:
        amp = ampmgr.getAmplitudes( fn )
    else: 
        amp = None
    if cluster is not None:
        lens = ClusterLens( cluster, verbose=verbose )
    elif lensDict[lensmode] == PsiSpec.PM:
        lens = cs.PointMass()
        lens.setEinsteinR( param.get( ( "lens", "einsteinradius" ) ) )
        if amp is None: 
            if verbose: print( "[getLens] Point Mass Amplitudes" )
            amp = ampmgr.getPointMassAmplitudes()
        if verbose: print( "[getLens] instantiated PointMass" )
    elif lensDict[lensmode] == PsiSpec.SIS:
        lens = cs.SIS()
        lens.setEinsteinR( param.get( ( "lens", "einsteinradius" ) ) )
        if amp is None: 
            if verbose: print( "[getLens] SIS Amplitudes" )
            amp = ampmgr.getSISAmplitudes()
        if verbose: print( "[getLens] instantiated SIS" )
    elif lensDict[lensmode] == PsiSpec.SIE:
        lens = cs.SIE()
        lens.setRatio( param.get( ( "lens", "ellipseratio" ) ) )
        lens.setOrientation( param.get( ( "lens", "orientation" ) ) )
        lens.setEinsteinR( param.get( ( "lens", "einsteinradius" ) ) )
        if amp is None: 
            amp = ampmgr.getSIEAmplitudes()
    elif lensmode is None:
        raise RuntimeError( "[getLens] No lens" )
    else:
        raise RuntimeError( "[getLens] Unknown lens specification" )
    if amp is not None:
        lens.setAmplitudes( amp )
    smp = param.get( ( "simulator", "sampled"), None )
    if smp is not None:
        size = param.get( ( "simulator", "imagesize" ), 512 )
        if verbose>1: print( "[getLens] Sampled mode is", smp )
        if smp: lens = SampledPsiFunctionLens( lens, size )
    return lens

class ClusterLens(cs.ClusterLens):
    def __init__(self,s,fn=None,verbose=1):
        """
        Factory function to create a cluster lens.
        This is an auxiliary for `getLens()`.
        """
        super().__init__()
        self.verbose = verbose
        if self.verbose: print( f"[CosmoSim/py] setCluster({s})")

        ll = [ x.split("/") for x in s.split(";") ]
        self.lenslist = []
        self.fn = fn
        if fn is not None:
            amp = ampmgr.getAmplitudes( fn )
        else:
            amp = None
        for lens in ll:
            lenstype = lens[0]
            lensparam = [ float(x) for x in lens[1:] ]
            if self.verbose>1: print( lenstype, ":", lensparam )
            sys.stdout.flush()
            nl = len(lensparam)
            if nl < 3:
                raise Exception( f"Too few parameters for constituent lens" )
            x, y = lensparam[0], lensparam[1] ;
            if lenstype == "SIS":
                l = cs.SIS()
                if amp is None: 
                    amp = ampmgr.getSISAmplitudes()
            elif lenstype == "SIE":
                l = cs.SIE()
                if nl < 5:
                    raise Exception( f"Too few parameters for SIE lens" )
                l.setRatio( lensparam[3] )
                l.setOrientation( lensparam[4] )
                if amp is None: 
                    amp = ampmgr.getSIEAmplitudes()
            elif lenstype == "PointMass":
                l = cs.PointMass()
                if amp is None: 
                    amp = ampmgr.getPointMassAmplitudes()
            else:
                raise Exception( f"Lens Type not Supported {lenstype}" )
            if amp is not None:
                l.setAmplitudes( amp )
            l.setEinsteinR( lensparam[2] )
            self.addLens( l, x, y )
            if verbose > 2: 
                print( "[ClusterLens] component lens instantiated" )
                print( "[ClusterLens]", lensparam  )
    def addLens(self,l,x,y):
        super().addLens( l, x, y )
        self.lenslist.append( l )
        if self.verbose > 1:
            print( "[ClusterLens] addLens", (x,y), l )

class RouletteRegenerator(cs.RouletteRegenerator):
    """
    The roulette regenerator simulates gravitational lenses based
    on pre-computed roulette amplitudes.

    This class is a wrapper around the corresponding C++ class.

    The parameter `xi` is the reference point for the roulette formalism,
    and controls where the distorted image is drawn.
    """
    def __init__(self,*a,xi=None,verbose=1,**kw):
        super().__init__(*a,**kw)
        if xi is not None:
            self.setNu( *xi )
        self.verbose = verbose
        self.bgcolour = 0
    def makeSource(self,param):
        if param.get( "imagesize" ) is None:
            raise Exception( "Image size not specified" )
        self._src = makeSource(param,verbose=self.verbose)
        self.setSource( self._src )
        if self.verbose>1:
            print( "RouletteRegenerator.makeSource() returns" )

class SourceConstellation(cs.SourceConstellation):
    def __init__(self,size,verbose=1):
        self._sources = []
        self.verbose = 1
        if verbose: print( "SourceConstellation.__init__" )
        super().__init__(size)
    def addSource(self,src,*a):
        self._sources.append(src)
        return super().addSource(src,*a)
