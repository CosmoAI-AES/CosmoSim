/* (C) 2022: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/PixMap.h"

#include "simaux.h"

cv::Mat LensMap::getPsi() {
   return psi ;
}
cv::Mat LensMap::getMassMap() {
   return massMap ;
}
cv::Mat LensMap::getEinsteinMap() {
   throw NotImplemented() ;
   // return einsteinMap ;
}

void LensMap::setPsi( cv::Mat map ) {
   cv::Mat tmp, psix, psiy ;
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
