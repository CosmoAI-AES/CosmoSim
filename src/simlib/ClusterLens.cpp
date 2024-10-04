/* (C) 2023: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Lens.h"
#include "simaux.h"

/*
void ClusterLens::addLens( PsiFunctionLens *l ) {
   return this->addLens( l, 0, 0 ) ;
}
*/
void ClusterLens::addLens( PsiFunctionLens *l, double x, double y ) {
   std::cout << "ClusterLEns::addLens]] " << (x,y) << "\n" ;
   this->xshift[this->nlens] = x ;
   this->yshift[this->nlens] = y ;
   this->lens[this->nlens++] = l ;
}

double ClusterLens::psiValue( double x, double y ) const { 
   int i ;
   double r = 0 ;
   for ( i=0 ; i<this->nlens ; ++i ) {
      r += this->lens[i]->psiValue( x-this->xshift[i], y-this->yshift[i] ) ;
   }
   return r ;
}
double ClusterLens::psiXvalue( double x, double y ) const {
   int i ;
   double r = 0 ;
   std::cout << "[ClusterLens::psiXvalue] " << nlens << "\n" ;
   for ( i=0 ; i<this->nlens ; ++i ) {
      double x1=x-this->xshift[i], 
             y1=y-this->yshift[i]  ;
      r += this->lens[i]->psiXvalue( x1, y1 ) ;
   }
   return r ;
}
double ClusterLens::psiYvalue( double x, double y ) const { 
   int i ;
   double r = 0 ;
   std::cout << "[ClusterLens::psiYvalue] " << nlens << "\n" ;
   for ( i=0 ; i<this->nlens ; ++i ) {
      r += this->lens[i]->psiYvalue( x-this->xshift[i], y-this->yshift[i] ) ;
   }
   return r ;
}
void ClusterLens::calculateAlphaBeta( cv::Point2d xi, int nterms ) {
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
       this->lens[i]->calculateAlphaBeta( xi, nterms ) ;
       for (int m = 1; m <= nterms; m++){
         for (int s = 0; s <= (m+1); s++){
            alphas_val[m][s] += this->lens[i]->getAlphaXi(m,s) ;
            betas_val[m][s] += this->lens[i]->getBetaXi(m,s) ;
         }
       }
   }
}
