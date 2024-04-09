/* (C) 2023: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Lens.h"
#include "simaux.h"

// \xi_0 ~ einsteinR
// NEW f
// NEW \phi
// TODO \chi_L in terms of \chi

double SIE::psifunction( double x, double y ) {
   /* ellipseration = f */
   double sq = sqrt( 1 - ellipseratio*ellipseratio ) ; /* $f'$ */
   double sqf = sqrt( ellipseratio )/sq ;  /* $\sqrt(f)/f'$ */

   double R = sqrt( x*x + y*y ) ;
   return einsteinR*sqf*(
	   y*asin( sq * y/R )
	   + x*asinh(x/R * sq/ellipseratio)
	 ) ;
}

cv::Point2d SIE::getXi( cv::Point2d chieta ) {
   throw NotImplemented() ;
   double phi = atan2(chieta.y, chieta.x); 
   return chieta + einsteinR*cv::Point2d( cos(phi), sin(phi) ) ;
}

double KormannSIE::psiXfunction( double x, double y ) {
   throw NotImplemented() ;
}
double KormannSIE::psiYfunction( double x, double y ) {
   throw NotImplemented() ;
}
