# (C) 2022-24: Hans Georg Schaathun <georg@schaathun.net> 

"""
The CosmoSim package comprises several components, including scripts,
a wrapper around the C++ CosmoSim library, and GUI components.
"""

import CosmoSim.CosmoSimPy as cs
import numpy as np
import threading as th
import os, sys

import traceback

ModelSpec = cs.ModelSpec
SourceSpec = cs.SourceSpec
PsiSpec = cs.PsiSpec

RouletteRegenerator = cs.RouletteRegenerator 
Point = cs.Point 

def makeSourceConstellation(src,size):
    ss = src.split(";")
    sl = [ x.split("/") for x in ss ]
    constellation = SourceConstellation(size)
    for s in sl:
        mode = sourceDict[s[0]]
        if mode == sourceDict.get( "Spherical" ):
            constituent = cs.SphericalSource( size, float(s[3]) )
        elif mode == sourceDict.get( "Ellipsoid" ):
            constituent = cs.EllipsoidSource( size, float(s[3]),
                    float(s[4]), float(s[5])*np.pi/180 )
        elif mode == sourceDict.get( "Triangle" ):
            constituent = cs.TriangleSource( size, float(s[3]), float(s[4])*np.pi/180 )
        elif mode == sourceDict.get( "Iamge (Einstein)" ):
            constituent = cs.ImageSource( getSourceFileName( ) )
        else:
            raise Exception( "Unknown Source Mode" )

        constellation.addSource( constituent, float(s[1]), float(s[2]))
    print( "makeSourceConstellation() returns" )
    return constellation

def makeSource(param):
    """
    Factory function to create a Source object given the parameter list.
    """
    size = int( param.get( "imagesize" ) )
    src = param.get("source")
    print( "makeSource", src )
    if src.find("/") < 0:
       mode = sourceDict[src]
       if mode == sourceDict.get( "Spherical" ):
           r = cs.SphericalSource( size, float(param.get( "sigma" )) )
       elif mode == sourceDict.get( "Ellipsoid" ):
           r = cs.EllipsoidSource( size, float(param.get( "sigma" )),
                   float(param.get( "sigma2" )), float(param.get( "theta" ))*np.pi/180 )
       elif mode == sourceDict.get( "Triangle" ):
           r = cs.TriangleSource( size, float(param.get( "sigma" )),
                   float(param.get( "theta" ))*np.pi/180 )
       elif mode == sourceDict.get( "Iamge (Einstein)" ):
           r = cs.ImageSource( getSourceFileName( ) )
       else:
           raise Exception( "Unknown Source Mode" )
    else:
        r = makeSourceConstellation(src,size)
        print( "makeSource() - makeSourceConstellation() has returned" )
    print( "makeSource() returns" )
    return r 

lensDict = {
        "SIS" : PsiSpec.SIS,
        "PM" : PsiSpec.PM,
        "Cluster" : PsiSpec.Cluster,
        "SIE" : PsiSpec.SIE,
        }
modelDict = {
        "Raytrace" : ModelSpec.Raytrace,
        "Roulette" : ModelSpec.Roulette,
        "RouletteRegenerator" : ModelSpec.RouletteRegenerator,
        "Point Mass (exact)" : ModelSpec.PointMassExact,
        "Point Mass (roulettes)" : ModelSpec.PointMassRoulettes,

        "ray" : ModelSpec.Raytrace,
        "rou" : ModelSpec.Roulette,
        "pmx" : ModelSpec.PointMassExact,
        "pmr" : ModelSpec.PointMassRoulettes,
        }
modelValues = {
        "Point Mass (exact)" : (ModelSpec.PointMassExact,PsiSpec.PM,False),
        "Point Mass (roulettes)" : (ModelSpec.PointMassRoulettes,PsiSpec.PM,False),
        "Sampled Roulette SIS" : (ModelSpec.Roulette,PsiSpec.SIS,True),
        "Sampled Roulette SIE" : (ModelSpec.Roulette,PsiSpec.SIE,True),
        "Sampled Raytrace SIS" : (ModelSpec.Raytrace,PsiSpec.SIS,True),
        "Sampled Raytrace SIE" : (ModelSpec.Raytrace,PsiSpec.SIE,True),
        "Roulette SIS" : (ModelSpec.Roulette,PsiSpec.SIS,False),
        "Roulette SIE" : (ModelSpec.Roulette,PsiSpec.SIE,False),
        "Raytrace SIS" : (ModelSpec.Raytrace,PsiSpec.SIS,False),
        "Raytrace SIE" : (ModelSpec.Raytrace,PsiSpec.SIE,False),
        }
configDict = modelValues.copy()
configDict["p"] = configDict["Point Mass (exact)"]
configDict["r"] = configDict["Point Mass (roulettes)"]
configDict["ss"] = configDict["Sampled Roulette SIS"]
configDict["pss"] = configDict["Sampled Raytrace SIS"]
configDict["fs"] = configDict["Roulette SIS"]
configDict["rs"] = configDict["Raytrace SIS"]
configDict["srousie"] = configDict["Sampled Roulette SIE"]
configDict["sraysie"] = configDict["Sampled Raytrace SIE"]
configDict["rousie"] = configDict["Roulette SIE"]
configDict["raysie"] = configDict["Raytrace SIE"]

sourceDict = {
        "Spherical" : SourceSpec.Sphere,
        "Ellipsoid" : SourceSpec.Ellipse,
        "Image (Einstein)" : SourceSpec.Image,
        "Triangle" : SourceSpec.Triangle,
        "s" : SourceSpec.Sphere,
        "e" : SourceSpec.Ellipse,
        "t" : SourceSpec.Triangle,
        }
sourceValues = {
        "Spherical" : SourceSpec.Sphere,
        "Ellipsoid" : SourceSpec.Ellipse,
        "Image (Einstein)" : SourceSpec.Image,
        "Triangle" : SourceSpec.Triangle,
        }

def getMS(maxm): return [ (m,s) for m in range(maxm+1)
                                    for s in range(1-m%2,m+2,2) ]
def getMSheaders(maxm): 
    r = [ ( f"alpha[{m}][{s}]", f"beta[{m}][{s}]") for (m,s) in getMS(maxm) ]
    return [ x for p in r for x in p ]

maxmlist = [ 50, 100, 200 ]
def getFileName(maxm):
    """
    Get the filename for the amplitudes files.
    The argument `maxm` is the maximum number of terms (nterms) to be
    used in the simulator.
    """
    dir = os.path.dirname(os.path.abspath(__file__))
    for m in maxmlist:
        m0 = m
        if maxm <= m:
            return( os.path.join( dir, f"sis{m}.txt" ) )
    raise Exception( f"Cannot support m > {m0}." )
def getSourceFileName():
    """
    Get the filename for an image source.
    """
    dir = os.path.dirname(os.path.abspath(__file__))
    return( os.path.join( dir, f"einstein.png" ) )
    

class SourceConstellation(cs.SourceConstellation):
    def __init__(self,size):
        self._sources = []
        print( "SourceConstellation.__init__" )
        super().__init__(size)
    def addSource(self,src,*a):
        self._sources.append(src)
        return super().addSource(src,*a)
class CosmoSim(cs.CosmoSim):
    """
    Simulator for gravitational lensing.
    This wraps the CosmoSim library written in C++.  In particular,
    it wraps functions returning images, to convert the data to 
    numpy arrays.
    """
    def __init__(self,*a,maxm=50,fn=None,**kw):
        super().__init__(*a,**kw)
        dir = os.path.dirname(os.path.abspath(__file__))
        if fn == None:
            super().setFile( PsiSpec.SIS, getFileName( maxm ) )
            super().setFile( PsiSpec.SIE, os.path.join( dir, "sie05.txt" ) )
        else:
            print( "Amplitudes file:", fn )
            super().setFile( PsiSpec.SIS, fn )
            super().setFile( PsiSpec.SIE, fn )
        self._continue = True
        self.updateEvent = th.Event()
        self.simEvent = th.Event()
        self._simThread = th.Thread(target=self.simThread)
        self._simThread.start()
        self.bgcolour = 0
    def makeSource(self,param):
        if param.get( "imagesize" ) == None:
           param.__setitem__( "imagesize", self.getImageSize() )
        self._src = makeSource(param)
        print( "CosmoSim.makeSource() returns" )
    def getRelativeEta(self,centrepoint):
        # print ( "[getRelativeEta] centrepoint=", centrepoint, "in Planar Co-ordinates"  )
        r = super().getRelativeEta(centrepoint[0],centrepoint[1])
        a = np.array(r)
        # print ( "[getRelativeEta] r=", a )
        return (a[0],a[1])
    def getXiOffset(self,centrepoint):
        nu = super().getNu()
        a = np.array(nu)
        return ( a[0] - centrepoint[0], a[1] - centrepoint[1] )
    def getOffset(self,centrepoint):
        # print ( "[getOffset] centrepoint=", centrepoint, "in Planar Co-ordinates"  )
        r = super().getOffset(centrepoint[0],centrepoint[1])
        a = np.array(r)
        # print ( "[getOffset] r=", a )
        return (a[0],a[1])
    def getAlphaBetas(self,maxm=2,pt=None):
        """
        Get the roulette amplitudes for a given point in the source plane.
        """
        # print ( "[getAlphaBetas] pt=", pt, "in Planar Co-ordinates"  )
        if pt == None:
           r = [ (self.getAlphaXi(m,s),self.getBetaXi(m,s)) for (m,s) in getMS(maxm) ]
        else:
            (x,y) = pt
            # Scaling is done in getAlpha/getBeta
            r = [ (self.getAlpha(x,y,m,s),self.getBeta(x,y,m,s)) 
                    for (m,s) in getMS(maxm) ]
        return [ x for p in r for x in p ]

    def close(self):
        """
        Terminate the worker thread.
        This should be called before terminating the program,
        because stale threads would otherwise block.
        """
        self._continue = False
        self.simEvent.set()
        self._simThread.join()
    def getUpdateEvent(self):
        return self.updateEvent
    def moveSim(self,rot,scale):
        return super().moveSim( float(rot), float(scale) )
    def maskImage(self,scale=1):
        return super().maskImage( float(scale) )
    def setCluster(self,s):
        print( f"[CosmoSim/py] setCluster({s})")
        sys.stdout.flush()
        ll = [ x.split("/") for x in s.split(";") ]
        self.lenslist = []
        cluster = cs.ClusterLens()
        for lens in ll:
            lenstype = lens[0]
            lensparam = [ float(x) for x in lens[1:] ]
            print( lenstype, ":", lensparam )
            sys.stdout.flush()
            nl = len(lensparam)
            if nl < 3:
                raise Exception( f"Too few parameters for constituent lens" )
            x, y = lensparam[0], lensparam[1] ;
            if lenstype == "SIS":
                l = cs.SIS()
                l.setFile( super().getFile( PsiSpec.SIS ) )
            elif lenstype == "SIE":
                l = cs.SIE()
                if nl < 5:
                    raise Exception( f"Too few parameters for SIE lens" )
                l.setRatio( lensparam[3] )
                l.setOrientation( lensparam[4] )
                l.setFile( super().getFile( PsiSpec.SIE ) )
            elif lenstype == "PointMass":
                l = cs.PointMass()
            else:
                raise Exception( f"Lens Type not Supported {lenstype}" )
            l.setEinsteinR( lensparam[2] )
            self.lenslist.append( l )
            cluster.addLens( l, x, y )
        self.cluster = cluster
        print( f"[CosmoSim/py] setCluster calls setLens")
        sys.stdout.flush()
        super().setLens(cluster)
        return
    def setLensMode(self,s):
        print( f"setLensMode({s})")
        return super().setLensMode( int( lensDict[s] ) ) 
    def setModelMode(self,s):
        print( f"setModelMode({s})")
        # traceback.print_stack()
        return super().setModelMode( int( modelDict[s] ) ) 
    def setConfigMode(self,s):
        print( f"setConfigMode({s})")
        (model,lens,sampleMode) = configDict[s]
        super().setSampled( int( sampleMode ) ) 
        super().setLensMode( int( lens ) ) 
        return super().setModelMode( int( model ) ) 
    def setBGColour(self,s):
        self.bgcolour = s
    def simThread(self):
        """
        This function repeatedly runs the simulator when the parameters
        have changed.  It is intended to run in a dedicated thread.
        """
        while self._continue:
            self.simEvent.wait()
            if self._continue:
               self.simEvent.clear()
               self.runSim()
               self.updateEvent.set()
    def runSim(self):
        self._src_ = self._src
        self.setSource( self._src_ )
        return super().runSim()
    def runSimulator(self):
        """
        Run the simulator; that is, tell it that the parameters
        have changed.  This triggers an event which will be handled
        when the simulator is idle.
        """
        print( "CosmoSim.runSimulator() [python]" )
        self.simEvent.set()

    def getApparentImage(self,reflines=True):
        """
        Return the Apparent Image from the simulator as a numpy array.
        """
        im = np.array(self.getApparent(reflines),copy=False)
        if im.shape[2] == 1 : im.shape = im.shape[:2]
        return np.maximum(im,self.bgcolour)
    def getActualImage(self,reflines=True,caustics=False):
        """
        Return the Actual Image from the simulator as a numpy array.
        """
        im = np.array(self.getActual(reflines,caustics),copy=True)
        if im.shape[2] == 1 : im.shape = im.shape[:2]
        return np.maximum(im,self.bgcolour)
    def getPsiMap(self):
        """
        Return a matrix representation of the sampled lensing potential.
        """
        im = np.array(super().getPsiMap(),copy=False)
        if im.shape[2] == 1 : im.shape = im.shape[:2]
        return im
    def getMassMap(self):
        """
        Return a matrix representation of the sampled mass density.
        """
        im = np.array(super().getMassMap(),copy=False)
        if im.shape[2] == 1 : im.shape = im.shape[:2]
        return im[2:-2,2:-2]
    def getDistortedImage(self,reflines=False,critical=False,mask=False,showmask=False):
        """
        Return the Distorted Image from the simulator as a numpy array.
        """
        try:
            if mask: self.maskImage()
            if showmask: self.showMask()
        except:
            print( "Masking not supported for this lens model." )
        im = np.array(self.getDistorted(reflines,critical),copy=False)
        if im.shape[2] == 1 : im.shape = im.shape[:2]
        return np.maximum(im,self.bgcolour)
class RouletteSim:
    """
    Simulator for gravitational lensing.
    This wraps the CosmoSim library written in C++.  In particular,
    it wraps functions returning images, to convert the data to 
    numpy arrays.
    """
    def __init__(self,*a,maxm=50,**kw):
        super().__init__(*a,**kw)

        self.bgcolour = 0

    def setBGColour(self,s):
        self.bgcolour = s

    def getApparentImage(self,reflines=True):
        """
        Return the Apparent Image from the simulator as a numpy array.
        """
        im = np.array(self._rsim.getApparent(),copy=False)
        if im.shape[2] == 1 : im.shape = im.shape[:2]
        return np.maximum(im,self.bgcolour)
    def getActualImage(self,reflines=True,caustics=False):
        """
        Return the Actual Image from the simulator as a numpy array.
        """
        im = np.array(self._rsim.getActual(),copy=False)
        if im.shape[2] == 1 : im.shape = im.shape[:2]
        return np.maximum(im,self.bgcolour)
    def initSim(self,rsim):
        self._rsim = rsim

    def getDistortedImage(self,reflines=False,mask=False,showmask=False):
        """
        Return the Distorted Image from the simulator as a numpy array.
        """
        try:
            if mask: self._rsim.maskImage()
            if showmask: self._rsim.showMask()
        except:
            print( "Masking not supported for this lens model." )
        im = np.array(self._rsim.getDistorted(),copy=False)
        if im.shape[2] == 1 : im.shape = im.shape[:2]
        return np.maximum(im,self.bgcolour)
