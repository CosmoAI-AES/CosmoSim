/* (C) 2023: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Lens.h"
#include "simaux.h"

void PsiFunctionLens::updatePsi( cv::Size size ) { 
   // cv::Mat im = getApparent() ;
   int nrows = size.height ;
   int ncols = size.width ;

   std::cout << "[PsiFunctionLens] updatePsi\n" ;

   psi = cv::Mat::zeros(size, CV_64F );
   psiX = cv::Mat::zeros(size, CV_64F );
   psiY = cv::Mat::zeros(size, CV_64F );

   for ( int i=0 ; i<nrows ; ++i ) {
      for ( int j=0 ; j<ncols ; ++j ) {
         cv::Point2d ij( i, j ) ;
         cv::Point2d xy = pointCoordinate( ij, psi ) ;
	 psi.at<double>( ij ) = psifunction( xy.x, xy.y ) ;
	 psiX.at<double>( ij ) = psiXfunction( xy.x, xy.y ) ;
	 psiY.at<double>( ij ) = psiYfunction( xy.x, xy.y ) ;
      }
   }

   std::cout << "[PsiFunctionLens] updatePsi() returns\n" ;
   return ; 
}

double PsiFunctionLens::psiValue( double x, double y ) { 
   return psifunction( x, y ) ;
}
double PsiFunctionLens::psiXvalue( double x, double y ) { 
   return psiXfunction( x, y ) ;
}
double PsiFunctionLens::psiYvalue( double x, double y ) { 
   return psiYfunction( x, y ) ;
}

cv::Point2d PsiFunctionLens::getXi( cv::Point2d chieta ) {

   /*
   double s = norm(chieta.x, chieta.y) ;
   return chieta + einsteinR*cv::Point2d( chieta.x/s, chieta.y/s ) ;
   /**/

   return chieta + cv::Point2d( 
         psiXfunction(chieta.x, chieta.y ),
         psiYfunction(chieta.x, chieta.y ) ) ;

   /*
   double phi = atan2(chieta.y, chieta.x); 
   return chieta + einsteinR*cv::Point2d( cos(phi), sin(phi) ) ;
   */
}
