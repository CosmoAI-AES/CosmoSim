/* (C) 2026: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Lens.h"
#include "simaux.h"

#include <symengine/parser.h>
#include <fstream>

Amplitudes::Amplitudes( std::string fn ) :
     filename(fn)
{ 
    auto x = SymEngine::symbol("x");
    auto y = SymEngine::symbol("y");
    auto g = SymEngine::symbol("g"); /* Einstein Radius */
    auto f = SymEngine::symbol("f"); /* Ellipse Ratio */
    auto p = SymEngine::symbol("p"); /* theta  */

    std::ifstream input;

    if ( filename.compare("nosuchfile") == 0 )  return ;

    input.open(filename);

    if (!input.is_open()) {
        throw std::runtime_error("Could not open file: " + filename);
    } else {
        if (DEBUG) std::cout 
           << "[Amplitudes] opened file " << filename << "\n" ;
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

    if (DEBUG>1) std::cout << "[Amplitudes] init " << filename << "\n" ;

}

Amplitudes::~Amplitudes() { 
   if (DEBUG>1) std::cout << "[Amplitudes] destructing " << filename << "\n" ;
}

double Amplitudes::alpha( cv::Point2d xi, int m, int s, double einsteinR, double ellipseratio, double theta ) {
   return alphas_l[m][s].call({xi.x, xi.y, einsteinR, ellipseratio, theta});
}
double Amplitudes::beta( cv::Point2d xi, int m, int s, double einsteinR, double ellipseratio, double theta ) {
   return betas_l[m][s].call({xi.x, xi.y, einsteinR, ellipseratio, theta});
}
