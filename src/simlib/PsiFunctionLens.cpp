/* (C) 2023: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Lens.h"
#include "simaux.h"

void Lens::setRatio( double r ) { 
   ellipseratio = r ; 
   if ( r >= 1 ) ellipseratio = 0.999 ;
   if ( r <= 0 ) ellipseratio = 0.001 ;
}
void Lens::setOrientation( double r ) { orientation = r ; }
double Lens::getOrientation() const {
   return this->orientation ;
}

void Lens::setEinsteinR( double r ) { einsteinR = r ; }
double Lens::getEinsteinR() const {
   return einsteinR ;
}

