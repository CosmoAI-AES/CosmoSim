/* (C) 2022: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/PixMap.h"

#include "simaux.h"

cv::Mat LensMap::getPsi() const {
   return psi ;
}
cv::Mat LensMap::getPsiImage() const {
   return psi ;
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
   k /= maxVal ;
   k *= 255 ;
   k.convertTo( im, CV_8S ) ;
   return im ;
}
cv::Mat LensMap::getEinsteinMap() const {
   throw NotImplemented() ;
   // return einsteinMap ;
}

void LensMap::setPsi( cv::Mat map ) {
   cv::Mat tmp, psix, psiy ;
   std::cout << "[LensMap] setPsi()\n" ;
   psi = map ;
   diffX( psi, tmp ) ; diffX( tmp, psix ) ;
   diffY( psi, tmp ) ; diffY( tmp, psiy ) ;
   massMap = ( psix + psiy ) / 2 ;

   // Calculate einsteinMap and massMap here
}
void LensMap::loadPsi( std::string fn ) {
   setPsi( cv::imread( fn ) ) ;
   // Calculate einsteinMap and massMap here
}
