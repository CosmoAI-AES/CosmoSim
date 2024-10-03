/* (C) 2023: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Lens.h"
#include "simaux.h"


#ifndef DEBUG
#define DEBUG 0
#endif

void Lens::setFile( std::string fn ) {
   filename = fn ;
   std::cout << "setFile " << filename << "\n" ;
} 
void Lens::initAlphasBetas() {
   std::cout << "[Lens.initAlphaBeta()] does nothing\n" ;
}


void Lens::calculateAlphaBeta( cv::Point2d xi ) {
   throw NotImplemented() ;
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
