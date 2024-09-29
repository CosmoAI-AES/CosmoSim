/* (C) 2023: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Lens.h"
#include "simaux.h"

void ClusterLens::addLens( PsiFunctionLens *l ) {
   this->lens[this->nlens++] = l ;
}

double ClusterLens::psiValue( double x, double y ) const { 
   int i ;
   double r = 0 ;
   for ( i=0 ; i<this->nlens ; ++i ) {
      r += this->lens[i]->psiValue( x, y ) ;
   }
   return r ;
}
double ClusterLens::psiXvalue( double x, double y ) const {
   int i ;
   double r = 0 ;
   for ( i=0 ; i<this->nlens ; ++i ) {
      r += this->lens[i]->psiXvalue( x, y ) ;
   }
   return r ;
}
double ClusterLens::psiYvalue( double x, double y ) const { 
   int i ;
   double r = 0 ;
   for ( i=0 ; i<this->nlens ; ++i ) {
      r += this->lens[i]->psiYvalue( x, y ) ;
   }
   return r ;
}
void ClusterLens::calculateAlphaBeta( cv::Point2d xi ) {
   if (DEBUG) std::cout 
              << "[ClusterLens->calculateAlphaBeta()] " << nterms << "; " 
              << xi << "\n"  ;

   for (int m = 1; m <= nterms; m++){
         for (int s = 0; s <= (m+1); s++){
            alphas_val[m][s] = 0 ;
            betas_val[m][s] = 0 ;
         }
   }
   for ( int i=0 ; i<this->nlens ; ++i ) {
       this->lens[i]->calculateAlphaBeta( xi ) ;
       for (int m = 1; m <= nterms; m++){
         for (int s = 0; s <= (m+1); s++){
            alphas_val[m][s] += this->lens[i]->getAlphaXi(m,s) ;
            betas_val[m][s] += this->lens[i]->getBetaXi(m,s) ;
         }
       }
   }
}
cv::Point2d ClusterLens::getXi( cv::Point2d chieta ) {
   throw NotImplemented() ;
}
