/* (C) 2023: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Lens.h"
#include "simaux.h"

void ClusterLens::addLens( Lens *l ) {
   lens[nlens++] = l ;
}

double SampledLens::psiValue( double x, double y ) const { 
   int i ;
   double r = 0 ;
   for ( i=0 ; i<nlens ; ++i ) {
      r += lens[i].psiValue( x, y ) ;
   }
   return r ;
}
double SampledLens::psiXvalue( double x, double y ) const {
   int i ;
   double r = 0 ;
   for ( i=0 ; i<nlens ; ++i ) {
      r += lens[i].psiXvalue( x, y ) ;
   }
   return r ;
}
double SampledLens::psiYvalue( double x, double y ) const { 
   int i ;
   double r = 0 ;
   for ( i=0 ; i<nlens ; ++i ) {
      r += lens[i].psiYvalue( x, y ) ;
   }
   return r ;
}
void ClusterLens::calculateAlphaBeta( cv::Point2d xi ) {
   if (DEBUG) std::cout 
              << "[ClusterLens.calculateAlphaBeta()] " << nterms << "; " 
              << xi << "\n"  ;

   for (int m = 1; m <= nterms; m++){
         for (int s = 0; s <= (m+1); s++){
            alphas_val[m][s] = 0 ;
            betas_val[m][s] = 0 ;
         }
   }
   for ( i=0 ; i<nlens ; ++i ) {
       lens[i].calculateAlphaBeta( xi ) ;
       for (int m = 1; m <= nterms; m++){
         for (int s = 0; s <= (m+1); s++){
            alphas_val[m][s] += lens[i].getAlphaXi(m,s) ;
            betas_val[m][s] += lens[i].getBetaXi(m,s) ;
         }
       }
   }
}
cv::Point2d ClusterLens::getXi( cv::Point2d chieta ) {
   throw NotImplemented() ;
}
