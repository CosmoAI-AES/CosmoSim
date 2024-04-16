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

cv::Point2d SIS::getXi( cv::Point2d chieta ) {
   double s = norm(chieta.x, chieta.y) ;
   return chieta + einsteinR*cv::Point2d( chieta.x/s, chieta.y/s ) ;
   /*
   double phi = atan2(chieta.y, chieta.x); 
   return chieta + einsteinR*cv::Point2d( cos(phi), sin(phi) ) ;
   */
}
