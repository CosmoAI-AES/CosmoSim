# (C) 2026: Hans Georg Schaathun <georg@schaathun.net> 

from . import CosmoSimPy as cs

"""
The module provides dictionaries of the different model identifiers,
both lens, simulator, and source models.  They are used as lookup tables
for the different strings used in configuration files and command line 
arguments.
"""

ModelSpec = cs.ModelSpec
SourceSpec = cs.SourceSpec
PsiSpec = cs.PsiSpec
LightProfileSpec = cs.LightProfileSpec
Point = cs.Point 

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

# Note that the source names are looked up in two dictionaries,
# both the `sourceDict` and the `lightProfileDict`.
sourceDict = {
        "Spherical" : SourceSpec.Sphere,
        "Ellipsoid" : SourceSpec.Ellipse,
        "SersicSphere" : SourceSpec.Sphere,
        "SersicEllipsoid" : SourceSpec.Ellipse,
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
lightProfileDict = {
        "Gaussian" : LightProfileSpec.Gaussian,
        "Sersic" : LightProfileSpec.Sersic,
        "Spherical" : LightProfileSpec.Gaussian,
        "Ellipsoid" : LightProfileSpec.Gaussian,
        "SersicSphere" : LightProfileSpec.Sersic,
        "SersicEllipsoid" : LightProfileSpec.Sersic,
        # "g" : LightProfileSpec.Gaussian,
        # "s" : LightProfileSpec.Sersic,
        }


