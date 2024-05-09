/* (C) 2023: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Lens.h"
#include "simaux.h"

#define norm(x,y) sqrt( x*x + y*y ) 


double SIS::psifunction( double x, double y ) {
   return einsteinR*sqrt( x*x + y*y ) ;
}
double SIS::psiXfunction( double x, double y ) {
   double s = sqrt( x*x + y*y ) ;
   return einsteinR*x/s ;
}
double SIS::psiYfunction( double x, double y ) {
   double s = sqrt( x*x + y*y ) ;
   return einsteinR*y/s ;
}

double SIE::criticalXi( double phi ) {
   double c = cos(phi-orientation*PI/180) ;
   double s = sin(phi-orientation*PI/180) ;
   double xicrit = sqrt(f)*einsteinR ;
   xicrit /= 2 ;
   return xicrit ;
}
