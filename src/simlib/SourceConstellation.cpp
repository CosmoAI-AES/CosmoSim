/* (C) 2024: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Source.h"

SourceConstellation::~SourceConstellation() { 
   for ( int i=0 ; i<nsrc ; ++i ) {
      delete src[i] ;
   }
}

void SourceConstellation::addSource( Source *l, double x, double y ) {
   std::cout << "SourceConstellation::addSource]] " << cv::Point2d(x,y) << "\n" ;
   this->xshift[this->nsrc] = x ;
   this->yshift[this->nsrc] = y ;
   this->src[this->nsrc++] = l ;
   std::cout << "SourceConstellation::addSource]] returns\n" ;
}
void SourceConstellation::drawParallel(cv::Mat& dst){
    for ( int i=0 ; i<nsrc ; ++i ) {
       cv::Mat tr = (cv::Mat_<double>(2,3) << 1, 0, xshift[i], 0, 1, yshift[i]);
       cv::Mat s = src[i]->getImage() ;
       cv::Mat tmp = cv::Mat::zeros(s.size(), s.type());
       cv::warpAffine(s, tmp, tr, s.size()) ;
       cv::add( dst, tmp, dst ) ;
    }
}
