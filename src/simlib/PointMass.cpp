/* (C) 2023: Hans Georg Schaathun <georg@schaathun.net> */

/* Note.  This is a hack to make PointMassLens and RoulettePMLens work
 * and share the getXI() calculation.  */

#include "cosmosim/Lens.h"
#include "simaux.h"

double PointMass::psiValue( double x, double y ) const {
   double s = einsteinR*einsteinR ;
   s *= log( sqrt( x*x + y*y )/einsteinR ) ;
   return s ;
}
double PointMass::psiXvalue( double x, double y ) const {
   double s = einsteinR*einsteinR ;
   s /= x*x + y*y ;
   return s*x ;
}
double PointMass::psiYvalue( double x, double y ) const {
   double s = einsteinR*einsteinR ;
   s /= x*x + y*y ;
   return s*y ;
}

cv::Point2d PointMass::getXi( cv::Point2d chieta ) {
   double c = chieta.x*chieta.x + chieta.y*chieta.y ;
   double root = sqrt(0.25*c + einsteinR*einsteinR) ; // /CHI
   return chieta/2 + root*chieta/sqrt(c) ;
}
