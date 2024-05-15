/* (C) 2023: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Lens.h"
#include "simaux.h"

#include <symengine/parser.h>
#include <fstream>

void Lens::updatePsi( ) { 
   return updatePsi( cv::Size(400,400) ) ;
}
void Lens::updatePsi( cv::Size size ) { 
   return ; 
}
void Lens::setEinsteinR( double r ) { einsteinR = r ; }
void Lens::setRatio( double r ) { 
   ellipseratio = r ; 
   std::cout << "[SampledPsiFunctionLens] setRatio(" << ellipseratio << ")\n" ;
   if ( r >= 1 ) ellipseratio = 0.999 ;
   if ( r <= 0 ) ellipseratio = 0.001 ;
}
void Lens::setOrientation( double r ) { orientation = r ; }

cv::Mat Lens::getPsi() const {
   return psi ;
}
cv::Mat Lens::getPsiX() const {
   return psiX ;
}
cv::Mat Lens::getPsiY() const {
   return psiY ;
}
double Lens::getEinsteinR() const {
   return einsteinR ;
}
cv::Mat Lens::getPsiImage() const {
   cv::Mat im, ps = getPsi() ;
   double minVal, maxVal;
   cv::Point minLoc, maxLoc;
   minMaxLoc( ps, &minVal, &maxVal, &minLoc, &maxLoc ) ;
   double s = std::max(-minVal,maxVal)*128 ;
   ps /= s ;
   ps += 128 ;
   ps.convertTo( im, CV_8S ) ;
   return im ;
}
cv::Mat Lens::getMassMap() const {
   cv::Mat psiX2, psiY2 ;
   Sobel(psi,psiX,CV_64FC1, 2, 0, 3, 1.0/8) ;
   Sobel(psi,psiY,CV_64FC1, 0, 2, 3, 1.0/8) ;
   return ( psiX + psiY ) / 2 ;
}
cv::Mat Lens::getMassImage() const {
   cv::Mat im, k ;
   double minVal, maxVal;
   cv::Point minLoc, maxLoc;

   k = getMassMap() ;
   minMaxLoc( k, &minVal, &maxVal, &minLoc, &maxLoc ) ;
   assert ( minVal >= 0 ) ;
   if ( maxVal > 255 ) {
     k /= maxVal ;
     k *= 255 ;
   }
   k.convertTo( im, CV_8S ) ;
   return im ;
}
cv::Mat Lens::getEinsteinMap() const {
   std::cout << "[Lens.getEinsteinMap() not implemented\n" ;
   throw NotImplemented() ;
   // return einsteinMap ;
}

void Lens::setFile( std::string fn ) {
   std::cout << "[Lens.setFile()] " << fn << "\n" ;
   filename = fn ;
} 
void Lens::initAlphasBetas() {

    auto x = SymEngine::symbol("x");
    auto y = SymEngine::symbol("y");
    auto g = SymEngine::symbol("g"); /* Einstein Radius */
    auto f = SymEngine::symbol("f"); /* Ellipse Ratio */
    auto p = SymEngine::symbol("p"); /* Orientation (phi) */

    std::ifstream input;
    input.open(filename);

    if (!input.is_open()) {
        throw std::runtime_error("Could not open file: " + filename);
    }
    std::cout << "[Lens.initAlphasBetas()] " << filename << "\n" ;

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
   return alphas_l[m][s].call({xi.x, xi.y, einsteinR, ellipseratio, orientation});
}
double Lens::getBeta( cv::Point2d xi, int m, int s ) {
   return betas_l[m][s].call({xi.x, xi.y, einsteinR, ellipseratio, orientation});
}

void Lens::calculateAlphaBeta( cv::Point2d xi ) {
    std::cout << "[Lens.calculateAlphaBeta()] " << nterms << "; " 
              << einsteinR << " - " << xi << "\n"  ;

    // calculate all amplitudes for given xi, einsteinR
    for (int m = 1; m <= nterms; m++){
        for (int s = (m+1)%2; s <= (m+1); s+=2){
            alphas_val[m][s] = alphas_l[m][s].call({xi.x, xi.y, einsteinR, ellipseratio, orientation});
            betas_val[m][s] = betas_l[m][s].call({xi.x, xi.y, einsteinR, ellipseratio, orientation});
        }
    }
}
double Lens::getAlphaXi( int m, int s ) {
   return alphas_val[m][s] ;
}
double Lens::getBetaXi( int m, int s ) {
   return betas_val[m][s] ;
}
cv::Point2d Lens::getXi( cv::Point2d e ) {
   std::cout << "[Lens.getXi() not implemented\n" ;
   throw NotImplemented() ;
}
void Lens::setNterms( int n ) {
   nterms = n ;
}

double Lens::psiValue( double x, double y ) { 
   cv::Point2d ij = imageCoordinate( cv::Point2d( x, y ), psi ) ;
   return psi.at<double>( ij ) ;
}
double Lens::psiXvalue( double x, double y ) { 
   cv::Point2d ij = imageCoordinate( cv::Point2d( x, y ), psi ) ;
   return -psiY.at<double>( ij ) ;
}
double Lens::psiYvalue( double x, double y ) { 
   cv::Point2d ij = imageCoordinate( cv::Point2d( x, y ), psi ) ;
   return -psiX.at<double>( ij ) ;
}
double Lens::criticalXi( double phi ) {
   throw NotImplemented() ;
}
cv::Point2d Lens::caustic( double phi ) {
   throw NotImplemented() ;
}
