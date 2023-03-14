/* (C) 2022: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Roulette.h"

#include <symengine/expression.h>
#include <symengine/lambda_double.h>
#include <symengine/parser.h>

#include <thread>
#include <fstream>

void diffX(cv::InputArray src, cv::OutputArray out) {
   return Sobel(src, out, -1, 1, 0 ) ;
   // Sobel(src, out, ddepth, 1, 0, ksize, scale, delta, BORDER_DEFAULT);
}
void diffY(cv::InputArray src, cv::OutputArray out) {
   return Sobel(src, out, -1, 0, 1 ) ;
   // Sobel(src, out, ddepth, 0, 1, ksize, scale, delta, BORDER_DEFAULT);
}

void RoulettePMCLens::calculateAlphaBeta() {

    // Calculate all amplitudes for given X, Y, einsteinR

    cv::Mat matA, matB, matAouter, matBouter, matAx, matAy, matBx, matBy ;
    int mp=1, m=0, s=1 ;
    double x = CHI*apparentAbs, y = 0 ;
    cv::Mat psi = getPsi() ;

    std::cout << "RoulettePMCLens calculateAlphaBeta\n" ;

    diffX(psi, matA) ;
    diffY(psi, matB) ;

    // Note! The lens potential \psi is negative; in the code psi refers
    // to the absolute value of \psi.

    // This is the outer base case, for m=0, s=1
    alphas_val[m][s] = matA.at<double>( x, y ) ;
    betas_val[m][s] =  matB.at<double>( x, y ) ;

    for ( mp = 1; mp <= nterms; mp++){
        s = mp+1 ; m = mp ;
        diffX(matAouter, matAx) ;
        diffY(matAouter, matAy) ;
        diffX(matBouter, matBx) ;
        diffY(matBouter, matBy) ;

        double C = (m+1)/(m+1+s) ;
        //  if ( s != 1 ) C *= 2 ; // This is impossible, but used in the formula.

        // matA = matAouter = C*(matAx - matBy)
        // matB = matBouter = C*(matBx + matAy)

        alphas_val[m][s] = matA.at<double>( x, y ) ;
        betas_val[m][s] =  matB.at<double>( x, y ) ;

        while( s > 0 && m < nterms ) {
            ++m ; --s ;
            C = (m+1)/(m+1-s) ;
            if ( s > 0 ) C /= 2 ;

            diffX(matA, matAx) ;
            diffY(matA, matAy) ;
            diffX(matB, matBx) ;
            diffY(matB, matBy) ;

            // matA = C*(matAx + matBy)
            // matB = C*(matBx - matAy)

            alphas_val[m][s] = matA.at<double>( x, y ) ;
            betas_val[m][s] =  matB.at<double>( x, y ) ;
        }
    }
}


void RoulettePMCLens::updateApparentAbs( ) {
    maskRadius = apparentAbs = actualAbs + einsteinR/CHI ;
}
