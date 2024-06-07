/* (C) 2023: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Lens.h"
#include "simaux.h"

#define norm(x,y) sqrt( x*x + y*y ) 


double SIS::psifunction( double x, double y ) const {
   return einsteinR*sqrt( x*x + y*y ) ;
}
double SIS::psiXfunction( double x, double y ) const {
   double s = sqrt( x*x + y*y ) ;
   return einsteinR*x/s ;
}
double SIS::psiYfunction( double x, double y ) const {
   double s = sqrt( x*x + y*y ) ;
   return einsteinR*y/s ;
}

double SIS::criticalXi( double phi ) const {
   return einsteinR ;
}
cv::Point2d SIS::caustic( double phi ) const {

   return cv::Point2d( 0, 0 ) ;
   // return einsteinR*cv::Point2d(  cos(phi), sin(phi) ) ;
}
