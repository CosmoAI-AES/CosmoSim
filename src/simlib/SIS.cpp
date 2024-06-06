/* (C) 2023: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Lens.h"
#include "simaux.h"

#define norm(x,y) sqrt( x*x + y*y ) 


double SIS::psiValue( double x, double y ) {
   return einsteinR*sqrt( x*x + y*y ) ;
}
double SIS::psiXvalue( double x, double y ) {
   double s = sqrt( x*x + y*y ) ;
   return einsteinR*x/s ;
}
double SIS::psiYvalue( double x, double y ) {
   double s = sqrt( x*x + y*y ) ;
   return einsteinR*y/s ;
}

double SIS::criticalXi( double phi ) {
   return einsteinR ;
}
cv::Point2d SIS::caustic( double phi ) {

   return cv::Point2d( 0, 0 ) ;
   // return einsteinR*cv::Point2d(  cos(phi), sin(phi) ) ;
}
