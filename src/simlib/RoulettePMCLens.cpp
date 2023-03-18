/* (C) 2022: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/PixMap.h"

#include <symengine/expression.h>
#include <symengine/lambda_double.h>
#include <symengine/parser.h>

#include <thread>
#include <fstream>

double factorial_(unsigned int n);

/*
RoulettePMCLens::RoulettePMCLens() :
   PixMapLens::PixMapLens()
{ 
    std::cout << "Instantiating RoulettePMCLens ... \n" ;
    initAlphasBetas();
}
RoulettePMCLens::RoulettePMCLens(bool centred) :
   PixMapLens::PixMapLens(centred)
{ 
    std::cout << "Instantiating RoulettePMCLens ... \n" ;
    initAlphasBetas();
}
RoulettePMCLens::RoulettePMCLens(std::string fn, bool centred) :
   filename(fn),
   PixMapLens::PixMapLens(centred)
{ 
    std::cout << "Instantiating RoulettePMCLens ... \n" ;
    initAlphasBetas();
}
void RoulettePMCLens::setFile( std::string fn ) {
    filename = fn ;
} 
*/
void RoulettePMCLens::initAlphasBetas() {

    auto x = SymEngine::symbol("x");
    auto y = SymEngine::symbol("y");
    auto g = SymEngine::symbol("g");
    auto c = SymEngine::symbol("c");

    std::ifstream input;
    input.open(filename);

    if (!input.is_open()) {
        throw std::runtime_error("Could not open file: " + filename);
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
            // The following two variables are unused.
            // SymEngine::LambdaRealDoubleVisitor alpha_num, beta_num;
            alphas_l[std::stoi(m)][std::stoi(s)].init({x, y, g}, *alpha_sym);
            betas_l[std::stoi(m)][std::stoi(s)].init({x, y, g}, *beta_sym);
        }
    }
}

void RoulettePMCLens::calculateAlphaBeta() {
    std::cout << "RoulettePMCLens calculateAlphaBeta\n" ;

    // calculate all amplitudes for given X, Y, einsteinR
    // This is done here to before the code is parallellised
    for (int m = 1; m <= nterms; m++){
        for (int s = (m+1)%2; s <= (m+1); s+=2){
            alphas_val[m][s] = alphas_l[m][s].call({apparentAbs*CHI, 0, einsteinR});
            betas_val[m][s] = betas_l[m][s].call({apparentAbs*CHI, 0, einsteinR});
        }
    }
}

// Calculate the main formula for the SIS model
std::pair<double, double> RoulettePMCLens::getDistortedPos(double r, double theta) const {
    double nu1 = r*cos(theta) ;
    double nu2 = r*sin(theta) ;

    for (int m=1; m<=nterms; m++){
        double frac = pow(r, m) / factorial_(m);
        double subTerm1 = 0;
        double subTerm2 = 0;
        for (int s = (m+1)%2; s <= (m+1); s+=2){
            double alpha = alphas_val[m][s];
            double beta = betas_val[m][s];
            int c_p = 1 + s/(m + 1);
            int c_m = 1 - s/(m + 1);
            subTerm1 += 0.5*( (alpha*cos((s-1)*theta) + beta*sin((s-1)*theta))*c_p 
                            + (alpha*cos((s+1)*theta) + beta*sin((s+1)*theta))*c_m );
            subTerm2 += 0.5*( (-alpha*sin((s-1)*theta) + beta*cos((s-1)*theta))*c_p 
                            + (alpha*sin((s+1)*theta) - beta*cos((s+1)*theta))*c_m);
        }
        nu1 += frac*subTerm1;
        nu2 += frac*subTerm2;
    }
    // The return value should be normalised coordinates in the source plane.
    // We have calculated the coordinates in the lens plane.
    nu1 /= CHI ;
    nu2 /= CHI ;
    return {nu1, nu2};
}

void RoulettePMCLens::updateApparentAbs( ) {
    maskRadius = apparentAbs = actualAbs + einsteinR/CHI ;
}
void RoulettePMCLens::maskImage( cv::InputOutputArray imgD ) {
      std::cout << "RoulettePMCLens::maskImage\n" ;
      int R = getCentre() ;
      cv::Mat mask( imgD.size(), CV_8UC1, cv::Scalar(255) ) ;
      cv::Mat black( imgD.size(), imgD.type(), cv::Scalar(0) ) ;
      cv::Point origo(
            R*cos(phi) + imgD.cols()/2,
            - R*sin(phi) + imgD.rows()/2) ;
      cv::circle( mask, origo, maskRadius, cv::Scalar(0), cv::FILLED ) ;
      black.copyTo( imgD, mask ) ;
}
void RoulettePMCLens::markMask( cv::InputOutputArray imgD ) {
      std::cout << "RoulettePMCLens::maskImage\n" ;
      int R = getCentre() ;
      cv::Point origo(
            R*cos(phi) + imgD.cols()/2,
            - R*sin(phi) + imgD.rows()/2) ;
      cv::circle( imgD, origo, maskRadius, cv::Scalar(255), 1 ) ;
      cv::circle( imgD, origo, 3, cv::Scalar(0), 1 ) ;
      cv::circle( imgD, origo, 1, cv::Scalar(0), cv::FILLED ) ;
}