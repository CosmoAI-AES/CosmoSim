/* (C) 2024: Hans Georg Schaathun <georg@schaathun.net> */
/* Implementation of the derivatives as developed on
 * https://cosmoai-aes.github.io/math/SIE
 */

#include "cosmosim/Lens.h"
#include "simaux.h"

// \xi_0 ~ einsteinR
// NEW f
// NEW \phi
// TODO \chi_L in terms of \chi

double SIE::psifunctionPolar( double R, double phi ) {
   /* ellipseration = f */

   double sq = sqrt( 1 - ellipseratio*ellipseratio ) ; /* $f'$ */
   double sqf = sqrt( ellipseratio )/sq ;  /* $\sqrt(f)/f'$ */
   // double R = sqrt( x*x + y*y ) ;

   double x = cos( phi + orientation ) ;
   double y = sin( phi + orientation ) ;

   return einsteinR*sqf*R*(
	   y*asin( sq * y )
	   + x*asinh( x * sq/ellipseratio )
	 ) ;
}
double SIE::psifunctionAligned( double x, double y ) {
   /* ellipseration = f */

   double sq = sqrt( 1 - ellipseratio*ellipseratio ) ; /* $f'$ */
   double sqf = sqrt( ellipseratio )/sq ;  /* $\sqrt(f)/f'$ */
   double R = sqrt( x*x + y*y ) ;

   return einsteinR*sqf*(
	   y*asin( sq * y/R )
	   + x*asinh( (x/R) * (sq/ellipseratio) )
	 ) ;
}

double SIE::psifunction( double x, double y ) {
   double phi = x == 0 ? signf(y)*PI/2 : atan2(y, x);
   double R = sqrt ( x*x + y*y ) ;
   return SIE::psifunctionPolar( R, phi ) ;
}

cv::Point2d SIE::getXi( cv::Point2d chieta ) {
   throw NotImplemented() ;
   double phi = atan2(chieta.y, chieta.x); 
   return chieta + einsteinR*cv::Point2d( cos(phi), sin(phi) ) ;
}



double SIE::psiXfunction( double x, double y ) {
   double sq = sqrt( 1 - ellipseratio*ellipseratio ) ; /* $f'$ */
   double sqf = sqrt( ellipseratio )/sq ;  /* $\sqrt(f)/f'$ */

   double R = sqrt( x*x + y*y ) ;
   return einsteinR*sqf*(
      cos(orientation) *  asinh(x/R * sq/ellipseratio)
      -
      sin(orientation) * asin(y/R * sq) 
      ) ;
}
double SIE::psiYfunction( double x, double y ) {
   double sq = sqrt( 1 - ellipseratio*ellipseratio ) ; /* $f'$ */
   double sqf = sqrt( ellipseratio )/sq ;  /* $\sqrt(f)/f'$ */

   double R = sqrt( x*x + y*y ) ;
   return einsteinR*sqf*(
      sin(orientation) *  asinh(x/R * sq/ellipseratio)
      +
      cos(orientation) * asin(y/R * sq) 
      );
}

