/* (C) 2022: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Roulette.h"

#include <symengine/expression.h>
#include <symengine/lambda_double.h>
#include <symengine/parser.h>

#include <thread>
#include <fstream>

/* The following is a default implementation for the point mass lens. 
 * It would be better to make the class abstract and move this definition to the 
 * subclass. */
std::pair<double, double> RoulettePMLens::getDistortedPos(double r, double theta) const {
    double R = apparentAbs * CHI ;

    double nu1 = r*cos(theta) ;
    double nu2 = r*sin(theta) ;
    double frac = (einsteinR * einsteinR) / R ;
    double rf = r/R ;

    for (int m=1; m<=nterms; m++){
       double sign = m%2 ? -1 : +1 ;
       double f = sign*pow(rf, m) ;
       nu1 -= frac * f * cos(m*theta) ;
       nu2 += frac * f * sin(m*theta) ;
    }
    // The return value should be normalised coordinates in the source plane.
    // We have calculated the coordinates in the lens plane.
    nu1 /= CHI ;
    nu2 /= CHI ;
    return {nu1, nu2};
}

void RoulettePMLens::updateApparentAbs( ) {
    // The apparent position is the solution to a quadratic equation.
    // thus there are two solutions.
    // This is overridden only to set maskRadius.
    double root = sqrt(0.25*actualAbs*actualAbs + einsteinR*einsteinR/(CHI*CHI));

    maskRadius = apparentAbs = actualAbs/2 + root ;
    apparentAbs2 = actualAbs/2 - root ;
    tentativeCentre = apparentAbs ;
}
