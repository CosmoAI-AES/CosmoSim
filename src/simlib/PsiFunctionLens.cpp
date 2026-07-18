/* (C) 2024: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Lens.h"
#include "simaux.h"

#include <symengine/parser.h>
#include <fstream>

PsiFunctionLens::PsiFunctionLens() { 
   if (DEBUG>1) std::cout << "[PsiFunctionLens] init " << this->idString() << "\n" ;
}
PsiFunctionLens::~PsiFunctionLens() { 
   if ( local ) {
       delete amp ;
   }
   if (DEBUG>1) std::cout << "[PsiFunctionLens] destructing " << idString() << "\n" ;
}

std::string PsiFunctionLens::idString() {
   return "PsiFunctionLens" ;
};


void PsiFunctionLens::calculateAlphaBeta( cv::Point2d xi, int nterms ) {
    if (DEBUG) std::cout 
              << "[PsiFunctionLens.calculateAlphaBeta()] " << nterms << "; " 
              << einsteinR << " - " << xi << "\n"  ;

    // calculate all amplitudes for given xi, einsteinR
    for (int m = 0; m <= nterms; m++) {
        for (int s = (m+1)%2; s <= (m+1); s+=2) {
            alphas_val[m][s] = getAlpha( xi, m, s ) ;
            betas_val[m][s] = getBeta( xi, m, s ) ;
        }
    }
}

double PsiFunctionLens::getAlpha( cv::Point2d xi, int m, int s ) {
   double theta = orientation*PI/180 ;
   return amp->alpha( xi, m, s, einsteinR, ellipseratio, theta );
}
double PsiFunctionLens::getBeta( cv::Point2d xi, int m, int s ) {
   double theta = orientation*PI/180 ;
   return amp->beta( xi, m, s, einsteinR, ellipseratio, theta );
}

double PsiFunctionLens::getAlphaXi( int m, int s ) {
   return alphas_val[m][s] ;
}
double PsiFunctionLens::getBetaXi( int m, int s ) {
   return betas_val[m][s] ;
}

void PsiFunctionLens::setAmplitudes( Amplitudes *a ) {
   if ( local ) {
      delete amp ;
      local = false ;
   }
   amp = a ;
}
void PsiFunctionLens::setFile( std::string fn ) {
   if ( local ) {
      delete amp ;
   } else {
      local = true ;
   }
   if (DEBUG) std::cout << "setFile " << fn << "\n" ;
   amp = new Amplitudes( fn ) ;
} 

void PsiFunctionLens::setEinsteinR( double r ) { einsteinR = r ; }
double PsiFunctionLens::getEinsteinR() const { return einsteinR ; }
void PsiFunctionLens::setRatio( double r ) { 
   ellipseratio = r ; 
   if ( r >= 1 ) ellipseratio = 0.999 ;
   if ( r <= 0 ) ellipseratio = 0.001 ;
}
void PsiFunctionLens::setOrientation( double r ) { orientation = r ; }
double PsiFunctionLens::getOrientation() const { return this->orientation ; }
