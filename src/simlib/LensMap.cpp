/* (C) 2023: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/PixMap.h"

#include "simaux.h"

cv::Mat LensMap::getPsi() const {
   return psi ;
}
cv::Mat LensMap::getPsiImage() const {
   cv::Mat im, ps = getPsi() ;
   double minVal, maxVal;
   cv::Point minLoc, maxLoc;
   minMaxLoc( ps, &minVal, &maxVal, &minLoc, &maxLoc ) ;
   double s = std::max(-minVal,maxVal)/128 ;
   std::cout << "[LensMap::getPsiImage] " << s << " [" << minVal << "," << maxVal << "]\n" ;
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

   k = max( getMassMap(), 0 ) ;
   minMaxLoc( k, &minVal, &maxVal, &minLoc, &maxLoc ) ;
   std::cout << "[LensMap::getMassImage] [" << minVal << "," << maxVal << "]\n" ;
   // assert ( minVal >= 0 ) ;

   k /= maxVal ;
   k *= 255 ;
   k.convertTo( im, CV_8U ) ;
   std::cout << "[LensMap] k is " << k.size() << " - " << k.type() << "\n" ;
   return im ;
}
cv::Mat LensMap::getEinsteinMap() const {
   throw NotImplemented() ;
   // return einsteinMap ;
}

void LensMap::setPsi( cv::Mat map ) {
   double minVal, maxVal;
   cv::Point minLoc, maxLoc;
   cv::Mat tmp, psix, psiy ;
   psi = map ;

   Sobel(psi,psix,CV_64FC1, 2, 0, 3, 1.0/8) ;
   Sobel(psi,psiy,CV_64FC1, 0, 2, 3, 1.0/8) ;
   massMap = - ( psix + psiy ) / 2 ;

   // cv::Laplacian(psi,massMap,-1) ;
   //
   minMaxLoc( massMap, &minVal, &maxVal, &minLoc, &maxLoc ) ;
   std::cout << "[LensMap::setPsi] [" << minVal << "," << maxVal << "]\n" ;
   std::cout << "[LensMap::setPsi] " << minLoc << " - " << maxLoc << "\n" ;
   int a = massMap.rows, b = massMap.cols ;
   std::cout << massMap(cv::Rect(a/2-2,b/2-2,5,5)) << "\n" ;

   minMaxLoc( psix, &minVal, &maxVal, &minLoc, &maxLoc ) ;
   std::cout << "[LensMap::setPsi] psix in [" << minVal << "," << maxVal << "]\n" ;
   minMaxLoc( psiy, &minVal, &maxVal, &minLoc, &maxLoc ) ;
   std::cout << "[LensMap::setPsi] psiy in [" << minVal << "," << maxVal << "]\n" ;

   // Calculate einsteinMap 
}
void LensMap::loadPsi( std::string fn ) {
   setPsi( cv::imread( fn ) ) ;
   // Calculate einsteinMap and massMap here
}
