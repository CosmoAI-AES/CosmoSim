/* (C) 2023: Hans Georg Schaathun <georg@schaathun.net> */

/* This is only used as a base class for SampledPsiFunctionLens.  */

#include "cosmosim/Lens.h"
#include "simaux.h"

cv::Point2d SampledLens::getXi( cv::Point2d chieta ) {

   cv::Point2d xi0, xi1 = chieta ;

   // cv::Mat psi, psiX, psiY ;
   int cont = 1, count = 0, maxcount = 200 ;
   double dist, dist0=pow(10,12), threshold = 0.002 ;

   // Get the lens potential 
   updatePsi() ;
   int ncols=psi.cols, nrows=psi.rows ;

   if (DEBUG) {
      std::cout << "[SampledLens] getXi()"
             << " chi*eta = " << chieta 
             << "; size: " << psi.size() << "\n" ;
   }

   // Diagnostic output 
   if (DEBUG) {
      double minVal, maxVal;
      cv::Point minLoc, maxLoc;
      minMaxLoc( psiX, &minVal, &maxVal, &minLoc, &maxLoc ) ;
      std::cout << "[SampledLens] psiX min=" << minVal << "; max=" << maxVal << "\n" ;
      minMaxLoc( psiY, &minVal, &maxVal, &minLoc, &maxLoc ) ;
      std::cout << "[SampledLens] psiY min=" << minVal << "; max=" << maxVal << "\n" ;
   }
   
   // This block makes a fix-point iteration to find \xi. 
   while ( cont ) {
      xi0 = xi1 ;
      cv::Point2d ij = imageCoordinate( xi0, psi ) ;
      double x = -psiY.at<double>( ij ), y = -psiX.at<double>( ij ) ;
      if (DEBUG) std::cout
	   << "[SampledLens] Fix pt it'n " << count
           << "; xi0=" << xi0 << "; Delta eta = " << x << ", " << y << "\n" ;
      xi1 = chieta + cv::Point2d( x, y ) ;
      dist = cv::norm( cv::Mat(xi1-xi0), cv::NORM_L2 ) ;
      if ( dist < threshold ) cont = 0 ;
      if ( ++count > maxcount ) cont = 0 ;
   }
   if (DEBUG) {
      if ( dist > threshold ) {
         std::cout << "Bad approximation of xi: xi0=" << xi0 
            << "; xi1=" << xi1 << "; dist=" << dist << "\n" ;
      } else {
         std::cout << "[SampledLens] Good approximation: xi0=" << xi0 
            << "; xi1=" << xi1 << "\n" ;
      }
   }
   return xi1 ;
}

void SampledLens::calculateAlphaBeta( cv::Point2d xi, int nterms ) {

    // Calculate all amplitudes for given X, Y, einsteinR

    int mp, m, s ;
    double C ;
    // std::cout << psi ;
    cv::Mat psi, matA, matB, matAouter, matBouter, matAx, matAy, matBx, matBy ;
    cv::Point2d ij ;

    this->updatePsi() ;
    psi = -this->getPsi() ;
    ij = imageCoordinate( xi, psi ) ;

    if (DEBUG) std::cout
              << "[SampledLens::calculateAlpaBeta] xi in image space is "
              << ij << "; nterms=" << nterms << "\n" ;

    for ( mp = 0; mp <= nterms; mp++){
        s = mp+1 ; m = mp ;
        if ( mp == 0 ) {
          // This is the outer base case, for m=0, s=1
          gradient(psi, matBouter, matAouter) ;
          // matAouter *= -1 ;
          // matBouter *= -1 ;
        } else {
          gradient(matAouter, matAy, matAx) ;
          gradient(matBouter, matBy, matBx) ;

          C = (m+1.0)/(m+1.0+s) ;
          //  if ( s == 1 ) C *= 2 ; // This is impossible, but used in the formula.

          matAouter = C*(matAx - matBy) ;
          matBouter = C*(matBx + matAy) ;
        }

        matA = matAouter.clone() ;
        matB = matBouter.clone() ;

        alphas_val[m][s] = matA.at<double>( ij ) ;
        betas_val[m][s] =  matB.at<double>( ij ) ;
        if (DEBUG) std::cout 
              << "SampledLens (" << m << ", " << s << ") " 
              << alphas_val[m][s]  << "/"
              << betas_val[m][s] << "\n"  ;

        while( s > 0 && m < nterms ) {
            ++m ; --s ;
            C = (m+1.0)/(m+1.0-s) ;
            if ( s == 0 ) C /= 2.0 ;

            gradient(matA, matAy, matAx) ;
            gradient(matB, matBy, matBx) ;

            matA = C*(matAx + matBy) ;
            matB = C*(matBx - matAy) ;

            alphas_val[m][s] = matA.at<double>( ij ) ;
            betas_val[m][s] =  matB.at<double>( ij ) ;
            if (DEBUG) std::cout 
              << "SampledLens (" << m << ", " << s << ") " 
              << alphas_val[m][s]  << "/"
              << betas_val[m][s] << "\n"  ;
        }
    }
}
double SampledLens::psiValue( double x, double y ) const { 
   cv::Point2d ij = imageCoordinate( cv::Point2d( x, y ), psi ) ;
   return psi.at<double>( ij ) ;
}
double SampledLens::psiXvalue( double x, double y ) const {
   cv::Point2d ij = imageCoordinate( cv::Point2d( x, y ), psi ) ;
   return -psiY.at<double>( ij ) ;
}
double SampledLens::psiYvalue( double x, double y ) const { 
   cv::Point2d ij = imageCoordinate( cv::Point2d( x, y ), psi ) ;
   return -psiX.at<double>( ij ) ;
}
cv::Mat SampledLens::getPsi() const {
   return psi ;
}
void SampledLens::updatePsi( ) { 
   return updatePsi( cv::Size(400,400) ) ;
}
void SampledLens::updatePsi( cv::Size size ) { 
   return ; 
}

double SampledLens::getAlpha( cv::Point2d xi, int m, int s ) {
   throw NotImplemented() ;
}
double SampledLens::getBeta( cv::Point2d xi, int m, int s ) {
   throw NotImplemented() ;
}

double SampledLens::getAlphaXi( int m, int s ) {
   return alphas_val[m][s] ;
}
double SampledLens::getBetaXi( int m, int s ) {
   return betas_val[m][s] ;
}
