/* (C) 2023: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Lens.h"
#include "simaux.h"

#ifndef DEBUG
#define DEBUG 0
#endif

void Lens::setEinsteinR( double r ) { einsteinR = r ; }
void Lens::setRatio( double r ) { 
   ellipseratio = r ; 
   if ( r >= 1 ) ellipseratio = 0.999 ;
   if ( r <= 0 ) ellipseratio = 0.001 ;
}
void Lens::setOrientation( double r ) { orientation = r ; }


double Lens::getEinsteinR() const {
   return einsteinR ;
}

void Lens::setFile( std::string fn ) {
   filename = fn ;
   std::cout << "setFile " << filename << "\n" ;
} 

cv::Point2d Lens::getXi( cv::Point2d chieta ) {

   return chieta + cv::Point2d( 
         psiXvalue(chieta.x, chieta.y ),
         psiYvalue(chieta.x, chieta.y ) ) ;

}
void Lens::setNterms( int n ) {
   nterms = n ;
}

double Lens::criticalXi( double phi ) const {
   throw NotImplemented() ;
}
cv::Point2d Lens::caustic( double phi ) const {
   throw NotImplemented() ;
}
double Lens::getOrientation() const {
   return this->orientation ;
}
