/* (C) 2023: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Lens.h"
#include "simaux.h"

double EIS::psifunction( double x, double y ) {
   return einsteinR*sqrt( x*x + y*y ) ;
}
double EIS::psiXfunction( double x, double y ) {
   double s = sqrt( x*x + y*y ) ;
   return einsteinR*x/s ;
}
double EIS::psiYfunction( double x, double y ) {
   double s = sqrt( x*x + y*y ) ;
   return einsteinR*y/s ;
}

double EIS::getXiAbs( double e ) {
   return (e + einsteinR) ;
}
cv::Point2d EIS::getXi( cv::Point2d chieta ) {
   double phi = atan2(chieta.y, chieta.x); 
   return chieta + einsteinR*cv::Point2d( cos(phi), sin(phi) ) ;
}
void EIS::setEllipticRatio( double r ) { ellipticRatio = r ; }
