/* (C) 2023: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Lens.h"
#include "simaux.h"

#include <symengine/parser.h>
#include <fstream>


void PsiFunctionLens::setEinsteinR( double r ) { einsteinR = r ; }
double PsiFunctionLens::getEinsteinR() const { return einsteinR ; }
void PsiFunctionLens::setRatio( double r ) { 
   ellipseratio = r ; 
   if ( r >= 1 ) ellipseratio = 0.999 ;
   if ( r <= 0 ) ellipseratio = 0.001 ;
}
void PsiFunctionLens::setOrientation( double r ) { orientation = r ; }
double PsiFunctionLens::getOrientation() const { return this->orientation ; }
