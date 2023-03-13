/* (C) 2022: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/PixMap.h"

#include <symengine/expression.h>
#include <symengine/lambda_double.h>
#include <symengine/parser.h>

#include <thread>
#include <fstream>

cv::Mat LensMap::getPsi() {
   return psi ;
}
cv::Mat LensMap::getMassMap() {
   return massMap ;
}
cv::Mat LensMap::getEinsteinMap() {
   return einsteinMap ;
}
void LensMap::setEinsteinMap( cv::Mat map ) {
   einsteinMap = map ;
   // Calculate psi and massMap here
}

