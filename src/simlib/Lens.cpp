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
   std::cout << "[Lens.calculateAlphaBeta()] does nothing" ;
}


void Lens::calculateAlphaBeta( cv::Point2d xi ) {
   throw NotImplemented() ;
}

double Lens::getAlphaXi( int m, int s ) {
   return alphas_val[m][s] ;
}
double Lens::getBetaXi( int m, int s ) {
   return betas_val[m][s] ;
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
