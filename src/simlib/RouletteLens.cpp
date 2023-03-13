/* (C) 2022: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Roulette.h"

void RouletteLens::maskImage( cv::InputOutputArray imgD ) {
      std::cout << "RouletteLens::maskImage\n" ;
      int R = getCentre() ;
      cv::Mat mask( imgD.size(), CV_8UC1, cv::Scalar(255) ) ;
      cv::Mat black( imgD.size(), imgD.type(), cv::Scalar(0) ) ;
      cv::Point origo(
            R*cos(phi) + imgD.cols()/2,
            - R*sin(phi) + imgD.rows()/2) ;
      cv::circle( mask, origo, maskRadius, cv::Scalar(0), cv::FILLED ) ;
      black.copyTo( imgD, mask ) ;
}
void RouletteLens::markMask( cv::InputOutputArray imgD ) {
      std::cout << "RouletteLens::maskImage\n" ;
      int R = getCentre() ;
      cv::Point origo(
            R*cos(phi) + imgD.cols()/2,
            - R*sin(phi) + imgD.rows()/2) ;
      cv::circle( imgD, origo, maskRadius, cv::Scalar(255), 1 ) ;
      cv::circle( imgD, origo, 3, cv::Scalar(0), 1 ) ;
      cv::circle( imgD, origo, 1, cv::Scalar(0), cv::FILLED ) ;
}
