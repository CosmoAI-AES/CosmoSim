#! /usr/bin/env python3
# (C) 2023-24: Hans Georg Schaathun <georg@schaathun.net>

"""
Manager for Amplitudes objects holding the symbolic formulas for
roulette amplitudes loaded from text files.

This module exists to make sure that each file is loaded only once,
so that the suspected memory leak in symengine is minimised.
"""

from .CosmoSimPy import Amplitudes
from . import getPathFN

_amp = {}

def getPathFN(fn):
    """
    Get the absolute path name for file given relative to the location of
    the referencing file.
    """
    dir = os.path.dirname(os.path.abspath(__file__))
    return  os.path.join( dir, fn )

def getPointMassAmplitudes():
    """Get the default Amplitudes object for PointMass."""
    return getAmplitudes( getPathFN( "pm50.txt" ) )

def getSISAmplitudes():
    """Get the default Amplitudes object for SIS."""
    return getAmplitudes( getPathFN( "sis50.txt" ) )

def getSIEAmplitudes():
    """Get the default Amplitudes object for SIE."""
    return getAmplitudes( getPathFN( "sie05.txt" ) )

def getAmplitudesByMode( mode ):
    if mode == PsiSpec.PM:
        return getPointMassAmplitudes()
    elif mode == PsiSpec.SIS:
        return getSISAmplitudes()
    elif mode == PsiSpec.SIE:
        return getSIEAmplitudes()
    else:
        raise RuntimeError( "[getAmplitudesByMode] No such lens model" )

def getAmplitudes(filename):
    """Get an Amplitudes object created from the given file."""
    if not filename in _amp:
        _amp[filename] = Amplitudes(filename)
    return _amp[filename]

