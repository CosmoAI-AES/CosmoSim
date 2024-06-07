/* (C) 2023: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Lens.h"
#include "simaux.h"

cv::Point2d PsiFunctionLens::getXi( cv::Point2d chieta ) {

   /*
   double s = norm(chieta.x, chieta.y) ;
   return chieta + einsteinR*cv::Point2d( chieta.x/s, chieta.y/s ) ;
   /**/

   return chieta + cv::Point2d( 
         psiXvalue(chieta.x, chieta.y ),
         psiYvalue(chieta.x, chieta.y ) ) ;

   /*
   double phi = atan2(chieta.y, chieta.x); 
   return chieta + einsteinR*cv::Point2d( cos(phi), sin(phi) ) ;
   */
}
