/* (C) 2022: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Roulette.h"

#include <thread>

#include "simaux.h"

void SampledLens::calculateAlphaBeta() {

    // Calculate all amplitudes for given X, Y, einsteinR

    cv::Mat matA, matB, matAouter, matBouter, matAx, matAy, matBx, matBy ;
    int mp, m, s ;
    double C, x = CHI*getXiAbs(), y = 0 ;
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


void SampledLens::updateApparentAbs( ) {
   cv::Point2f eta( actualAbs, 0 ) ;
   cv::Point2f xi1, xi0( actualAbs, 0 ) ;
   cv::Mat alpha, beta ;
   int cont = 1, count = 0 ;
   double dist, threshold = 0.1 ;

   diffX( psi, alpha ) ;
   diffY( psi, beta ) ;

   while ( cont ) {
      double x = alpha.at<double>( xi0 ), y = beta.at<double>( xi0 ) ;
      std::cout << "xi = " << x << ", " << y << "\n" ;
      xi1 = CHI*eta + cv::Point2f( x, y ) ;
      dist = cv::norm( cv::Mat(xi1-xi0), cv::NORM_L2 ) ;
      if ( dist < threshold ) cont = 0 ;
      if ( ++count > 1000 ) cont = 0 ;
      xi0 = xi1 ;
   }
   if ( dist > threshold ) {
      std::cout << "Bad approximation of xi: xi0=" << xi0 
            << "; xi1=" << xi1 << "\n" ;
   }
   xi = xi1 ;

   maskRadius = getXiAbs() ;
}

double SampledLens::getXiAbs() const {
   return cv::norm( cv::Mat(xi), cv::NORM_L2 ) ;
}
cv::Point2f SampledLens::getXi() const {
   return xi ;
}

/* Getters for the images */
cv::Mat SampledLens::getActual() { 
   cv::Mat imgApparent = getApparent() ;

   cv::Mat imgActual 
        = cv::Mat::zeros(imgApparent.size(), imgApparent.type());

   cv::Mat tr = (cv::Mat_<double>(2,3) << 1, 0, actualX, 0, 1, -actualY);

   std::cout << "getActual() (x,y)=(" << actualX << "," << actualY << ")\n" ;

   cv::warpAffine(imgApparent, imgActual, tr, imgApparent.size()) ;
   return imgActual ; 
}

void SampledLens::update( cv::Mat imgApparent ) {

    auto startTime = std::chrono::system_clock::now();
    
    std::cout << "update() x=" << actualX << "; y= " << actualY 
              << "; R=" << actualAbs << "; theta=" << phi
              << "; R_E=" << einsteinR << "; CHI=" << CHI << "\n" ;

    // Make Distorted Image
    parallelDistort(imgApparent, imgDistorted);

    std::cout << "update() (x,y) = (" << actualX << ", " << actualY << ")\n" ;

    // Calculate run time for this function and print diagnostic output
    auto endTime = std::chrono::system_clock::now();
    std::cout << "Time to update(): " 
              << std::chrono::duration_cast<std::chrono::milliseconds>(endTime - startTime).count() 
              << " milliseconds" << std::endl;

}
