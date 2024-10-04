#ifndef COSMOSIM_SOURCE_H
#define COSMOSIM_SOURCE_H

#if __has_include("opencv4/opencv2/opencv.hpp")
#include "opencv4/opencv2/opencv.hpp"
#else
#include "opencv2/opencv.hpp"
#endif

class Source {

protected:
    cv::Mat imgApparent;
    int size ;
    int drawn ;

public:
    Source(int) ;
    virtual ~Source();
    virtual cv::Mat getImage() ;

protected:
    virtual void drawParallel(cv::Mat &img) ;
    virtual void drawSource(int, int, cv::Mat &) = 0 ;
};

class SphericalSource : public Source {

private:
    double sigma ;

public:
    SphericalSource(int,double) ;

protected:
    virtual void drawSource(int, int, cv::Mat &) ;
};
#endif // COSMOSIM_SOURCE_H

