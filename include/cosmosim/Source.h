#ifndef COSMOSIM_SOURCE_H
#define COSMOSIM_SOURCE_H

#if __has_include("opencv4/opencv2/opencv.hpp")
#include "opencv4/opencv2/opencv.hpp"
#else
#include "opencv2/opencv.hpp"
#endif

class SphericalSource  {
private:
    double sigma ;
    cv::Mat imgApparent;
    int size ;
    int drawn ;
    void drawSource(int, int, cv::Mat &) ;
    void drawParallel(cv::Mat &img) ;

public:
    SphericalSource(int,double) ;
    cv::Mat getImage() ;


};
#endif // COSMOSIM_SOURCE_H

