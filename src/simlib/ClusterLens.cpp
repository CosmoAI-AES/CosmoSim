/* (C) 2023: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Lens.h"
#include "simaux.h"

/*
void ClusterLens::addLens( PsiFunctionLens *l ) {
   return this->addLens( l, 0, 0 ) ;
}
*/
void ClusterLens::addLens( PsiFunctionLens *l, double x, double y ) {
   std::cout << "ClusterLEns::addLens]] " << (x,y) << "\n" ;
   this->xshift[this->nlens] = x ;
   this->yshift[this->nlens] = y ;
   this->lens[this->nlens++] = l ;
}

double ClusterLens::psiValue( double x, double y ) const { 
   int i ;
   double r = 0 ;
   for ( i=0 ; i<this->nlens ; ++i ) {
      r += this->lens[i]->psiValue( x-this->xshift[i], y-this->yshift[i] ) ;
   }
   return r ;
}
double ClusterLens::psiXvalue( double x, double y ) const {
   int i ;
   double r = 0 ;
   for ( i=0 ; i<this->nlens ; ++i ) {
      r += this->lens[i]->psiXvalue( x-this->xshift[i], y-this->yshift[i] ) ;
   }
   return r ;
}
double ClusterLens::psiYvalue( double x, double y ) const { 
   int i ;
   double r = 0 ;
   for ( i=0 ; i<this->nlens ; ++i ) {
      r += this->lens[i]->psiYvalue( x-this->xshift[i], y-this->yshift[i] ) ;
   }
   return r ;
}
cv::Point2d ClusterLens::getXi( cv::Point2d chieta ) {
   std::cout << "[ClusterLens::getXi] not implemented\n" ;
   // return chieta ;
   throw NotImplemented() ;
}
