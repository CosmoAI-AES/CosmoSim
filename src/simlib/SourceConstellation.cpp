/* (C) 2024: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Source.h"

SourceConstellation::~SourceConstellation() { 
   for ( int i=0 ; i<nsrc ; ++i ) {
      delete src[i] ;
   }
}

void SourceConstellation::addSource( Source *l, double x, double y ) {
   std::cout << "SourceConstellation::addSource]] " << (x,y) << "\n" ;
   this->xshift[this->nsrc] = x ;
   this->yshift[this->nsrc] = y ;
   this->src[this->nsrc++] = l ;
}
void SourceConstellation::drawParallel(cv::Mat& dst){
    for ( int i=0 ; i<nsrc ; ++i ) {
       cv::add( dst, src[i]->getImage(), dst ) ;
    }
}
