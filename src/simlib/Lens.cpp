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

cv::Point2d Lens::getXi( cv::Point2d chieta ) {

   return chieta + cv::Point2d( 
         psiXvalue(chieta.x, chieta.y ),
         psiYvalue(chieta.x, chieta.y ) ) ;

}
void Lens::setNterms( int n ) {
   std::cout << "[Lens::setNterms] " << n << "\n" ;
   std::cout << "[Lens::setNterms] " << nterms << "\n" ;
   this->nterms = n ;
   std::cout << "[Lens::setNterms] returns\n" ;
}

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
