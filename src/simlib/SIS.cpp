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

double SIS::criticalXi( double phi ) {
   double c = cos(phi-orientation*PI/180) ;
   double s = sin(phi-orientation*PI/180) ;
   return einsteinR/2 ;
}
cv::Point2d SIS::caustic( double phi ) {

   double c = cos(phi) ;
   double s = sin(phi) ;

   return einsteinR*cv::Point2d(  c, s ) ;
}
