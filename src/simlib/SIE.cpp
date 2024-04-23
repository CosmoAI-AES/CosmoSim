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
   /* ellipseratio = f */

   if ( ellipseratio >= 1 || ellipseratio <= 0 ) {
      std::cout << "psiFunctionPolar - einsteinR = " << einsteinR << "\n" ;
      std::cout << "psiFunctionPolar - ellipseratio = " << ellipseratio << 
         "\nException!\n" ;
      throw std::logic_error("ellipseration has to be in the (0,1) interval") ;
   }
   double sq = sqrt( 1 - ellipseratio*ellipseratio ) ; /* $f'$ */
   double sqf = sqrt( ellipseratio )/sq ;  /* $\sqrt(f)/f'$ */
   // double R = sqrt( x*x + y*y ) ;

   double theta = orientation*PI/180 ;
   double x = cos( phi - theta ) ;
   double y = sin( phi - theta ) ;

   return einsteinR*sqf*R*(
	   y*asin( sq * y )
	   + x*asinh( x * sq/ellipseratio )
	 ) ;
}
double SIE::psifunctionAligned( double x, double y ) {
   /* ellipseratio = f */

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
   return psifunctionPolar( R, phi ) ;
}

/*
cv::Point2d SIE::getXi( cv::Point2d chieta ) {
   std::cerr  << "getXi() NotImplemented\n" ;
   throw NotImplemented() ;
   double phi = atan2(chieta.y, chieta.x); 
   return chieta + einsteinR*cv::Point2d( cos(phi), sin(phi) ) ;
}
*/



double SIE::psiXfunction( double x, double y ) {
   double sq = sqrt( 1 - ellipseratio*ellipseratio ) ; /* $f'$ */
   double sqf = sqrt( ellipseratio )/sq ;  /* $\sqrt(f)/f'$ */

   double R = sqrt( x*x + y*y ) ;
   double theta = orientation*PI/180 ;
   double ct = cos(theta) ;
   double st = sin(theta) ;
   double xp = ct*x + st*y ;
   double yp = - st*x + ct*y ;

   // std::cout << "SIE psiXfunction " << cv::Point2d( x,y ) << " - "
    // << cv::Point2d( xp,yp ) << " \n" ;

   return einsteinR*sqf*(
      ct * asinh(xp/R * sq/ellipseratio)
      -
      st * asin(yp/R * sq) 
      ) ;
}
double SIE::psiYfunction( double x, double y ) {
   double sq = sqrt( 1 - ellipseratio*ellipseratio ) ; /* $f'$ */
   double sqf = sqrt( ellipseratio )/sq ;  /* $\sqrt(f)/f'$ */

   double R = sqrt( x*x + y*y ) ;
   double theta = orientation*PI/180 ;
   double ct = cos(theta) ;
   double st = ellipseratio*sin(theta) ;
   double xp = ct*x + st*y ;
   double yp = - st*x + ct*y ;

   return einsteinR*sqf*(
      st * asinh(xp/R * sq/ellipseratio)
      +
      ct * asin(yp/R * sq) 
      );
}

double SIE::criticalXi( double phi ) {
   double c = cos(phi) ;
   double s = sin(phi) ;
   return sqrt( ellipseratio/(c*c + s*s) ) ;
}
