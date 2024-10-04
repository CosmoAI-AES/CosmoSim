/* (C) 2023: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Lens.h"
#include "simaux.h"

#ifndef DEBUG
#define DEBUG 0
#endif

cv::Point2d Lens::getXi( cv::Point2d chieta ) {

   return chieta + cv::Point2d( 
         psiXvalue(chieta.x, chieta.y ),
         psiYvalue(chieta.x, chieta.y ) ) ;

}

void Lens::calculateAlphaBeta( cv::Point2d, int ) { throw NotImplemented() ; }
double Lens::getAlphaXi( int m, int s ) { throw NotImplemented() ; }
double Lens::getBetaXi( int m, int s ) { throw NotImplemented() ; }
double Lens::getAlpha( cv::Point2d xi, int m, int s ) { throw NotImplemented() ; }
double Lens::getBeta( cv::Point2d xi, int m, int s ) { throw NotImplemented() ; }


double Lens::criticalXi( double phi ) const {
   throw NotImplemented() ;
}
cv::Point2d Lens::caustic( double phi ) const {
   throw NotImplemented() ;
}
double Lens::psiValue( double x, double y ) const { 
   throw NotImplemented() ;
}
double Lens::psiXvalue( double x, double y ) const {
   throw NotImplemented() ;
}
double Lens::psiYvalue( double x, double y ) const { 
   throw NotImplemented() ;
}
