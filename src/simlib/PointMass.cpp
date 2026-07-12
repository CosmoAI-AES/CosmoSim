/* (C) 2023: Hans Georg Schaathun <georg@schaathun.net> */

/* Note.  This is a hack to make PointMassLens and RoulettePMLens work
 * and share the getXI() calculation.  */

#include "cosmosim/Lens.h"
#include "simaux.h"

std::string PointMass::idString() {
   return "PointMass" ;
};

double PointMass::psiValue( double x, double y ) const {
   double s = einsteinR*einsteinR ;
   s *= log( sqrt( x*x + y*y ) ) ;
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

double PointMass::psiXXvalue( double x, double y ) const {
   double s = einsteinR*einsteinR ;
   double y2 = y*y, x2 = x*x ;
   double q = x2 + y2 ;
   s *= y2 - x2 ;
   return s / (q*q) ;
}
double PointMass::psiXYvalue( double x, double y ) const {
   double s = - einsteinR*einsteinR * x*y ;
   double q = x*x + y*y ;
   return s / (q*q) ;
}
double PointMass::psiYYvalue( double x, double y ) const {
   double s = einsteinR*einsteinR ;
   double y2 = y*y, x2 = x*x ;
   double q = x2 + y2 ;
   s *= x2 - y2 ;
   return s / (q*q) ;
}

cv::Point2d PointMass::getXi( cv::Point2d eta ) {
   double c = eta.x*eta.x + eta.y*eta.y ;
   double root = sqrt(0.25*c + einsteinR*einsteinR) ; 
   cv::Point2d r =  eta/2 + root*eta/sqrt(c) ;
   if (DEBUG) std::cout << "[PointMass::getXi] " << eta << " -> " << r << "\n" ;
   return r ;
}
double PointMass::criticalXi( double phi ) const {
   return einsteinR ;
}
