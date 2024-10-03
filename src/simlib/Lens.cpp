/* (C) 2023: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Lens.h"
#include "simaux.h"

#include <symengine/parser.h>
#include <fstream>

#ifndef DEBUG
#define DEBUG 0
#endif

void Lens::setEinsteinR( double r ) { einsteinR = r ; }
void Lens::setRatio( double r ) { 
   ellipseratio = r ; 
   if ( r >= 1 ) ellipseratio = 0.999 ;
   if ( r <= 0 ) ellipseratio = 0.001 ;
}
void Lens::setOrientation( double r ) { orientation = r ; }


double Lens::getEinsteinR() const {
   return einsteinR ;
}

void Lens::setFile( std::string fn ) {
   filename = fn ;
   std::cout << "setFile " << filename << "\n" ;
} 
void Lens::initAlphasBetas() {

    auto x = SymEngine::symbol("x");
    auto y = SymEngine::symbol("y");
    auto g = SymEngine::symbol("g"); /* Einstein Radius */
    auto f = SymEngine::symbol("f"); /* Ellipse Ratio */
    auto p = SymEngine::symbol("p"); /* theta  */

    std::ifstream input;
    std::cout << "Amplitudes file " << filename << "\n" ;

    if ( filename.compare("nosuchfile") == 0 )  return ;

    input.open(filename);

    if (!input.is_open()) {
        throw std::runtime_error("Could not open file: " + filename);
    } else {
       std::cout << "[initAlphasBetas] opened file " << filename << "\n" ;
    }

    while (input) {
        std::string m, s;
        std::string alpha;
        std::string beta;
        std::getline(input, m, ':');
        std::getline(input, s, ':');
        std::getline(input, alpha, ':');
        std::getline(input, beta);
        if (input) {
            auto alpha_sym = SymEngine::parse(alpha);
            auto beta_sym = SymEngine::parse(beta);
            alphas_l[std::stoi(m)][std::stoi(s)].init({x, y, g, f, p}, *alpha_sym);
            betas_l[std::stoi(m)][std::stoi(s)].init({x, y, g, f, p}, *beta_sym);
        }
    }
}

double Lens::getAlpha( cv::Point2d xi, int m, int s ) {
   double theta = orientation*PI/180 ;
   return alphas_l[m][s].call({xi.x, xi.y, einsteinR, ellipseratio, theta});
}
double Lens::getBeta( cv::Point2d xi, int m, int s ) {
   double theta = orientation*PI/180 ;
   return betas_l[m][s].call({xi.x, xi.y, einsteinR, ellipseratio, theta});
}

void Lens::calculateAlphaBeta( cv::Point2d xi ) {
   if (DEBUG) std::cout 
              << "[Lens.calculateAlphaBeta()] " << nterms << "; " 
              << einsteinR << " - " << xi << "\n"  ;

    std::cout << "[Lens.calculateAlphasBeta] f=" << ellipseratio << "; orientation=" << orientation << "\n" ;

    // calculate all amplitudes for given xi, einsteinR
    for (int m = 1; m <= nterms; m++){
        for (int s = (m+1)%2; s <= (m+1); s+=2){
            alphas_val[m][s] = getAlpha( xi, m, s ) ;
            betas_val[m][s] = getBeta( xi, m, s ) ;
            if (DEBUG) std::cout 
              << "Lens (" << m << ", " << s << ") " 
              << alphas_val[m][s]  << "/"
              << betas_val[m][s] << "\n"  ;
        }
    }
}
double Lens::getAlphaXi( int m, int s ) {
   return alphas_val[m][s] ;
}
double Lens::getBetaXi( int m, int s ) {
   return betas_val[m][s] ;
}
cv::Point2d Lens::getXi( cv::Point2d chieta ) {

   return chieta + cv::Point2d( 
         psiXvalue(chieta.x, chieta.y ),
         psiYvalue(chieta.x, chieta.y ) ) ;

}
void Lens::setNterms( int n ) {
   nterms = n ;
}

double Lens::criticalXi( double phi ) const {
   throw NotImplemented() ;
}
cv::Point2d Lens::caustic( double phi ) const {
   throw NotImplemented() ;
}
double Lens::getOrientation() const {
   return this->orientation ;
}
