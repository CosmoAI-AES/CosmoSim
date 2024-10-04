/* (C) 2023: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Lens.h"
#include "simaux.h"

#ifndef DEBUG
#define DEBUG 0
#endif

cv::Point2d Lens::getXi( cv::Point2d chieta ) {

   return chieta + cv::Point2d( 
         psiXvalue(chieta.x, chieta.y ),
         psiYvalue(chieta.x, chieta.y ) ) ;

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
