/* (C) 2022: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Simulator.h"

// Add some lines to the image for reference
void refLines(cv::Mat& ) ;
double factorial_(unsigned int) ;
void diffX(cv::InputArray, cv::OutputArray ) ;
void diffY(cv::InputArray, cv::OutputArray ) ;

cv::Point2f pointCoordinate( cv::Point2f pt, cv::Mat im ) ;
cv::Point2f imageCoordinate( cv::Point2f pt, cv::Mat im ) ;
