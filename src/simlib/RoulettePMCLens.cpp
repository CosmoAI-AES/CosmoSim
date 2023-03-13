/* (C) 2022: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Roulette.h"

#include <symengine/expression.h>
#include <symengine/lambda_double.h>
#include <symengine/parser.h>

#include <thread>
#include <fstream>

void RoulettePMCLens::calculateAlphaBeta() {
    std::cout << "RoulettePMCLens calculateAlphaBeta\n" ;

    // calculate all amplitudes for given X, Y, einsteinR
    // This is done here to before the code is parallellised
    for (int m = 1; m <= nterms; m++){
        for (int s = (m+1)%2; s <= (m+1); s+=2){
            alphas_val[m][s] = 0 ;
            betas_val[m][s] =  0 ;
        }
    }
}


void RoulettePMCLens::updateApparentAbs( ) {
    maskRadius = apparentAbs = actualAbs + einsteinR/CHI ;
}
