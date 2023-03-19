/* (C) 2022: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Roulette.h"

double psifunction( double x, double y ) {
   psi = - einsteinR*sqrt( x**2 + y**2 ) ;
}

void SampledLens::updatePsi() { 
   cv::Mat im = getApparent() ;
   int nrows = im.rows ;
   int ncols = im.cols ;

   psi = cv::Mat::zeros(im.size(), CV_64F );

   for ( int i=0 ; i<nrows ; ++i ) {
      int y = nrows/2-i ;
      for ( int j=0 ; j<ncols ; ++j ) {
	 int x = j-ncols/2 ;
	 psi.at<double>( i, j ) = psifunction( x, y ) ;

      }
   }

   return ; 
}
