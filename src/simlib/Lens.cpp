/* (C) 2023: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/PixMap.h"
#include "cosmosim/Lens.h"
#include "simaux.h"

void Lens::updatePsi( ) { 
   return updatePsi( cv::Size(400,400) ) ;
}
void Lens::updatePsi( cv::Size size ) { 
   return ; 
}
void Lens::setEinsteinR( double r ) { einsteinR = r ; }

cv::Mat LensMap::getPsi() const {
   return psi ;
}
cv::Mat LensMap::getPsiImage() const {
   cv::Mat im, ps = getPsi() ;
   double minVal, maxVal;
   cv::Point minLoc, maxLoc;
   minMaxLoc( ps, &minVal, &maxVal, &minLoc, &maxLoc ) ;
   double s = std::max(-minVal,maxVal)*128 ;
   ps /= s ;
   ps += 128 ;
   ps.convertTo( im, CV_8S ) ;
   return im ;
}
cv::Mat LensMap::getMassMap() const {
   return massMap ;
}
cv::Mat LensMap::getMassImage() const {
   cv::Mat im, k ;
   double minVal, maxVal;
   cv::Point minLoc, maxLoc;

   k = getMassMap() ;
   minMaxLoc( k, &minVal, &maxVal, &minLoc, &maxLoc ) ;
   assert ( minVal >= 0 ) ;
   if ( maxVal > 255 ) {
     k /= maxVal ;
     k *= 255 ;
   }
   k.convertTo( im, CV_8S ) ;
   return im ;
}
cv::Mat LensMap::getEinsteinMap() const {
   throw NotImplemented() ;
   // return einsteinMap ;
}

void LensMap::updatePsi() { 
   return ;
}
