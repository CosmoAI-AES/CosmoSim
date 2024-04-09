/* (C) 2024: Hans Georg Schaathun <georg@schaathun.net> */
/* Implementation using our own derivation */

#include "cosmosim/Lens.h"
#include "simaux.h"


double OurSIE::psiXfunction( double x, double y ) {
   double sq = sqrt( 1 - ellipseratio*ellipseratio ) ; /* $f'$ */
   double sqf = sqrt( ellipseratio )/sq ;  /* $\sqrt(f)/f'$ */

   double R = sqrt( x*x + y*y ) ;
   return einsteinR*sqf*(
	   + asinh(x/R * sq/ellipseratio)
           - (x*y*y)*(  1/(R*(R*R-sq*sq*y*y))
                       - 1/(R*(R*R+sqf*sqf*y*y) ) )
	 ) ;
}
double OurSIE::psiYfunction( double x, double y ) {
   double sq = sqrt( 1 - ellipseratio*ellipseratio ) ; /* $f'$ */
   double sqf = sqrt( ellipseratio )/sq ;  /* $\sqrt(f)/f'$ */

   double R = sqrt( x*x + y*y ) ;
   return einsteinR*sqf*(
	   + asin(y/R * sq)
           - (x*x*y)*(  1/(R*(R*R+sqf*sqf*x*x))
                       - 1/(R*(R*R-sq*sq*y*y) ) )
	 ) ;
}

