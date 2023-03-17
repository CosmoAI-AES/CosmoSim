/* (C) 2022: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Roulette.h"

#include <symengine/expression.h>
#include <symengine/lambda_double.h>
#include <symengine/parser.h>

#include <thread>
#include <fstream>

void diffX(cv::InputArray src, cv::OutputArray out) {
   return Sobel(src, out, -1, 1, 0 ) ;
   // Sobel(src, out, ddepth, 1, 0, ksize, scale, delta, BORDER_DEFAULT);
}
void diffY(cv::InputArray src, cv::OutputArray out) {
   return Sobel(src, out, -1, 0, 1 ) ;
   // Sobel(src, out, ddepth, 0, 1, ksize, scale, delta, BORDER_DEFAULT);
}

void RoulettePMCLens::calculateAlphaBeta() {

    // Calculate all amplitudes for given X, Y, einsteinR

    cv::Mat matA, matB, matAouter, matBouter, matAx, matAy, matBx, matBy ;
    int mp, m, s ;
    double C, x = CHI*apparentAbs, y = 0 ;
    cv::Mat psi = getPsi() ;

    std::cout << "RoulettePMCLens calculateAlphaBeta\n" ;

    for ( mp = 0; mp <= nterms; mp++){
        s = mp+1 ; m = mp ;
        if ( mp > 0 ) {
          diffX(matAouter, matAx) ;
          diffY(matAouter, matAy) ;
          diffX(matBouter, matBx) ;
          diffY(matBouter, matBy) ;

          C = (m+1)/(m+1+s) ;
          //  if ( s != 1 ) C *= 2 ; // This is impossible, but used in the formula.

          matA = matAouter = C*(matAx - matBy) ;
          matB = matBouter = C*(matBx + matAy) ;
        } else {
          // This is the outer base case, for m=0, s=1
          diffX(psi, matAouter) ;
          diffY(psi, matBouter) ;
          // Note! The lens potential \psi is negative; in the code psi refers
          // to the absolute value of \psi.
        }

        alphas_val[m][s] = matAouter.at<double>( x, y ) ;
        betas_val[m][s] =  matBouter.at<double>( x, y ) ;

        while( s > 0 && m < nterms ) {
            ++m ; --s ;
            C = (m+1)/(m+1-s) ;
            if ( s > 0 ) C /= 2 ;

            diffX(matA, matAx) ;
            diffY(matA, matAy) ;
            diffX(matB, matBx) ;
            diffY(matB, matBy) ;

            matA = C*(matAx + matBy) ;
            matB = C*(matBx - matAy) ;

            alphas_val[m][s] = matA.at<double>( x, y ) ;
            betas_val[m][s] =  matB.at<double>( x, y ) ;
        }
    }
}


void RoulettePMCLens::updateApparentAbs( ) {
   cv::Point2f eta( actualAbs, 0 ) ;
   cv::Point2f xi0( actualAbs, 0 ) ;
   cv::Mat alpha, beta ;
   int cont = 1, count = 0 ;
   double dist, threshold = 0.1 ;

   diffX( psi, alpha ) ;
   diffY( psi, beta ) ;

   while ( cont ) {
      double x = alpha.at<double>( xi0 ), y = beta.at<double>( xi0 ) ;
      std::cout << "xi = " << x << ", " << y << "\n" ;
      cv::Point2f xi = CHI*eta + cv::Point2f( x, y ) ;
      dist = cv::norm( cv::Mat(xi-xi0), cv::NORM_L2 ) ;
      if ( dist < threshold ) cont = 0 ;
      if ( ++count > 1000 ) cont = 0 ;
   }

   maskRadius = apparentAbs ;
}
