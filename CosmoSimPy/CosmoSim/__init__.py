# (C) 2022-23: Hans Georg Schaathun <georg@schaathun.net> 

import CosmoSim.CosmoSimPy as cs
import numpy as np
import threading as th
import os

import traceback


class CosmoSim(cs.CosmoSim):
    """
    Simulator for gravitational lensing.
    This wraps the CosmoSim library written in C++.  In particular,
    it wraps functions returning images, to convert the data to 
    numpy arrays.
    """
    def __init__(self,*a,maxm=50,fn=None,**kw):
        super().__init__(*a,**kw)

        self._continue = True
        self.updateEvent = th.Event()
        self.simEvent = th.Event()
        self.simThread = th.Thread(target=self.simThread)
        self.simThread.start()

    def close(self):
        """
        Terminate the worker thread.
        This should be called before terminating the program,
        because stale threads would otherwise block.
        """
        self._continue = False
        self.simEvent.set()
        self.simThread.join()
    def getUpdateEvent(self):
        return self.updateEvent

    def setCluster(self,s):
        print( f"setLens({s})")
        ll = [ x.split("/") for x in s.split(";") ]
        cluster = cs.ClusterLens()
        ll = []
        for lens in ll:
            lenstype = lens[0]
            lensparam = [ float(x) for x in lens[1:] ]
            print( lenstype, ":", lensparam )
            nl = len(lensparam)
            if nl < 3:
                raise Exception( f"Too few parameters for constituent lens" )
            x, y = lensparam[0], lensparam[1] ;
            if lenstype == "SIS":
                l = cs.SIS()
            elif lenstype == "PointMass":
                l = cs.PointMass()
            else:
                raise Exception( f"Lens Type not Supported {lenstype}" )
            l.setEinsteinR( lensparam[2] )
            cluster.addLens( l, x, y )
        self.cluster = cluster
        print ("setCluster returns")
        return super().setLens(cluster)

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
    def runSimulator(self):
        """
        Run the simulator; that is, tell it that the parameters
        have changed.  This triggers an event which will be handled
        when the simulator is idle.
        """
        self.simEvent.set()

