/* (C) 2022: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Simulator.h"

// Add some lines to the image for reference
void refLines(cv::Mat& target) {
    int rsize = target.rows;
    int csize = target.cols;
    std::cout << "refLines " << rsize << "x" << csize << "\n" ;
    cv::line( target, cv::Point( 0, csize /2 ),
                      cv::Point( rsize, csize /2 ),
                      {60, 60, 60},
                      1 ) ;
    cv::line( target, cv::Point( rsize/2-1, 0 ),
                      cv::Point( rsize/2-1, csize ),
                      {60, 60, 60},
                      1 ) ;
    cv::line( target, cv::Point( 0, csize-1 ),
                      cv::Point( rsize, csize-1 ),
                      {255, 255, 255},
                      1 ) ;
    cv::line( target, cv::Point( rsize-1, 0 ),
                      cv::Point( rsize-1, csize ),
                      {255, 255, 255},
                      1 ) ;
    cv::line( target, cv::Point( 0, 0 ),
                      cv::Point( rsize, 0 ),
                      {255, 255, 255},
                      1 ) ;
    cv::line( target, cv::Point( 0, 0 ),
                      cv::Point( 0, csize ),
                      {255, 255, 255},
                      1 ) ;
}

/* Calculate n! (n factorial) */
double factorial_(unsigned int n){
    double a = 1.0;
    for (int i = 2; i <= n; i++){
        a *= i;
    }
    return a;
}

void diffX(cv::InputArray src, cv::OutputArray out) {
   return Sobel(src, out, -1, 1, 0 ) ;
   // Sobel(src, out, ddepth, 1, 0, ksize, scale, delta, BORDER_DEFAULT);
}
void diffY(cv::InputArray src, cv::OutputArray out) {
   return Sobel(src, out, -1, 0, 1 ) ;
   // Sobel(src, out, ddepth, 0, 1, ksize, scale, delta, BORDER_DEFAULT);
}

cv::Point2f imageCoordinate( cv::Point2f pt, cv::Mat im ) {
   int ncols=im.cols, nrows=im.rows ;
   return cv::Point2f( nrows/2 - pt.y, pt.x + ncols/2 ) ;
}
cv::Point2f pointCoordinate( cv::Point2f pt, cv::Mat im ) {
   int ncols=im.cols, nrows=im.rows ;
   return cv::Point2f( pt.y - ncols/2, nrows/2 - pt.x ) ;
}
