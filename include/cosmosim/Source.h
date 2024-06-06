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

class EllipsoidSource : public Source {

private:
    double sigma1, sigma2, theta ;

public:
    EllipsoidSource(int,double,double) ;
    EllipsoidSource(int,double,double,double) ;

protected:
    virtual void drawSource(int, int, cv::Mat &) ;
    virtual void drawParallel(cv::Mat &img) ;

};

class TriangleSource : public Source {

private:
    double sigma, theta ;

public:
    TriangleSource(int,double) ;
    TriangleSource(int,double,double) ;
    virtual cv::Mat getImage() ;

protected:
    virtual void drawSource(int, int, cv::Mat &) ;
    virtual void drawParallel(cv::Mat &img) ;

};

class ImageSource : public Source {
   public:
      ImageSource( int, std::string ) ;
      virtual cv::Mat getImage() ;
   protected:
      std::string filename ;
      virtual void drawSource(int, int, cv::Mat &) ;
};


#endif // COSMOSIM_SOURCE_H

