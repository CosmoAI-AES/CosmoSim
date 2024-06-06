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
      std::cerr << "psiFunctionPolar - einsteinR = " << einsteinR << "\n" ;
      std::cerr << "psiFunctionPolar - ellipseratio = " << ellipseratio << 
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

double SIE::psiValue( double x, double y ) {
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



double SIE::psiXvalue( double x, double y ) {
   double sq = sqrt( 1 - ellipseratio*ellipseratio ) ; /* $f'$ */
   double sqf = sqrt( ellipseratio )/sq ;  /* $\sqrt(f)/f'$ */

   double R = sqrt( x*x + y*y ) ;
   double theta = orientation*PI/180 ;
   double ct = cos(theta) ;
   double st = sin(theta) ;
   double xp = ct*x + st*y ;
   xp /= R ;
   xp *= sq ;
   xp /= ellipseratio ;
   double yp = - st*x + ct*y ;
   yp /= R ;
   yp *= sq ;

   return einsteinR*sqf*( ct * asinh(xp) - st * asin(yp)) ;
}
double SIE::psiYvalue( double x, double y ) {
   double sq = sqrt( 1 - ellipseratio*ellipseratio ) ; /* $f'$ */
   double sqf = sqrt( ellipseratio )/sq ;  /* $\sqrt(f)/f'$ */

   double R = sqrt( x*x + y*y ) ;
   double theta = orientation*PI/180 ;
   double ct = cos(theta) ;
   double st = sin(theta) ;
   double xp = ct*x + st*y ;
   xp /= R ;
   xp *= sq ;
   xp /= ellipseratio ;
   double yp = - st*x + ct*y ;
   yp /= R ;
   yp *= sq ;

   return einsteinR*sqf*( st * asinh( xp ) + ct * asin( yp ));
}

double SIE::criticalXi( double phi ) {
   double c = cos(phi-orientation*PI/180) ;
   double s = sin(phi-orientation*PI/180) ;
   double f = ellipseratio ;
   double xicrit = sqrt(f)*einsteinR ;
   // xicrit /= 2 ;
   xicrit /= sqrt( c*c + f*f*s*s) ;
   return xicrit ;
}
cv::Point2d SIE::caustic( double phi ) {
   double f = ellipseratio ;
   double sq = sqrt( 1 - f*f ) ; /* $f'$ */
   double sqf = sqrt( f )/sq ;  /* $\sqrt(f)/f'$ */
   double th = orientation*PI/180 ;

   double c = cos(phi-th) ;
   double s = sin(phi-th) ;


   cv::Point2d p1 = cv::Point2d(  c, s ) ;
   cv::Point2d p2 = cv::Point2d( asinh( (sq/f)*c ), asin( sq*s ) ) ;
   p2 /= sq ;
   p1 /= sqrt( c*c + f*f*s*s ) ;
   p1 -= p2 ;

   double c2 = cos(th) ;
   double s2 = sin(th) ;

   cv::Point2d pt = cv::Point2d( p1.x*c2 - p1.y*s2,
                                p1.x*s2 + p1.y*c2 ) ;
   return pt*einsteinR*sqrt(f) ;
}
