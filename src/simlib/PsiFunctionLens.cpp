/* (C) 2023: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Lens.h"
#include "simaux.h"

#include <symengine/parser.h>
#include <fstream>


void PsiFunctionLens::setEinsteinR( double r ) { einsteinR = r ; }
double PsiFunctionLens::getEinsteinR() const { return einsteinR ; }
