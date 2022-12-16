# (C) 2022: Hans Georg Schaathun <georg@schaathun.net> 

import CosmoSim.CosmoSimPy as cs
import numpy as np

LensSpec = cs.LensSpec
SourceSpec = cs.SourceSpec

lensValues = {
        "Point Mass (exact)" : LensSpec.PointMass,
        "Point Mass (roulettes)" : LensSpec.PointMassRoulettes,
        "SIS (roulettes)" : LensSpec.SIS,
        }
sourceValues = {
        "Spherical" : SourceSpec.Sphere,
        "Ellipsoid" : SourceSpec.Ellipse,
        "Triangle" : SourceSpec.Triangle }


class CosmoSim(cs.CosmoSim):
    """
    Simulator for gravitational lensing.
    This wraps the CosmoSim library written in C++.  In particular,
    it wraps functions returning images, to convert the data to 
    numpy arrays.
    """
    def __init__(self,f=None,*a,**kw):
        super().__init__(*a,**kw)
        self.callback = f
    def setCallback(self,f):
        self.callback = f
    def setSourceMode(self,s):
        return super().setSourceMode( int( sourceValues[s] ) ) 
    def setLensMode(self,s):
        return super().setLensMode( int( lensValues[s] ) ) 
    def runSimulator(self):
        self.pending = False
        print ( "runSimulator" )
        ret = self.runSim()
        if ret:
            if None != self.callback: self.callback()
            if self.pending: self.runSimulator()
        else:
            self.pending = True
            

    def getActualImage(self):
        """
        Return the Actual Image from the simulator as a numpy array.
        """
        im = np.array(self.getActual(),copy=False)
        if im.shape[2] == 1 : im.shape = im.shape[:2]
        return im
    def getDistortedImage(self):
        """
        Return the Distorted Image from the simulator as a numpy array.
        """
        im = np.array(self.getDistorted(),copy=False)
        if im.shape[2] == 1 : im.shape = im.shape[:2]
        return im
