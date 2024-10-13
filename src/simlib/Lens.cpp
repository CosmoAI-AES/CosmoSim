/* (C) 2024: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Lens.h"
#include "simaux.h"

#ifndef DEBUG
#define DEBUG 1
#endif

cv::Point2d Lens::getXi( cv::Point2d chieta ) {

   cv::Point2d xi0, xi1 = chieta ;
   int cont = 1, count = 0, maxcount = 200 ;
   double dist, dist0=pow(10,12), threshold = 0.02 ;

   std::cout << "[Lens::getXi]\n" ;
   std::cout << "[Lens::getXi] " << chieta << "\n" ;

   /** This block makes a fix-point iteration to find \xi. */
   while ( cont ) {
      xi0 = xi1 ;
      double x = psiXvalue( xi0.x, xi0.y ),
             y = psiYvalue( xi0.x, xi0.y ) ;
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

void Lens::calculateAlphaBeta( cv::Point2d, int ) { throw NotImplemented() ; }
double Lens::getAlphaXi( int m, int s ) { throw NotImplemented() ; }
double Lens::getBetaXi( int m, int s ) { throw NotImplemented() ; }
double Lens::getAlpha( cv::Point2d xi, int m, int s ) { throw NotImplemented() ; }
double Lens::getBeta( cv::Point2d xi, int m, int s ) { throw NotImplemented() ; }

double Lens::criticalXi( double phi ) const { throw NotImplemented() ; }
cv::Point2d Lens::caustic( double phi ) const { throw NotImplemented() ; }
double Lens::psiValue( double x, double y ) const { throw NotImplemented() ; }
double Lens::psiXvalue( double x, double y ) const { throw NotImplemented() ; }
double Lens::psiYvalue( double x, double y ) const { throw NotImplemented() ; }

std::string Lens::idString() {
   return "Lens (Superclass)" ;
};
