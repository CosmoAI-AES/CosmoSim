#ifndef COSMOSIM_H
#define COSMOSIM_H

#include "Source.h"
#include "Lens.h"

#if __has_include("opencv4/opencv2/opencv.hpp")
#include "opencv4/opencv2/opencv.hpp"
#else
#include "opencv2/opencv.hpp"
#endif

#define PI 3.14159265358979323846

class SimulatorModel {
private:
    cv::Point2d eta ;  // Actual position in the source plane
    cv::Point2d nu ;   // Apparent position in the source plane

    cv::Point2d referenceXi = cv::Point2d(0,0) ;   // Local origin in the lens plane

protected:
    cv::Mat imgDistorted;

    virtual void parallelDistort(const cv::Mat &src, cv::Mat &dst);
    virtual void distort(int row, int col, const cv::Mat &src, cv::Mat &dst);

    double CHI;
    SphericalSource *source ;
    ClusterLens *lens = NULL ;

    void setNu( cv::Point2d ) ;

    void updateApparentAbs() ;

    cv::Point2d getEta() const ;

public:
    SimulatorModel();
    virtual ~SimulatorModel();

    void update();

    /* Getters (images) */
    cv::Mat getActual() const ;
    virtual cv::Mat getApparent() const ;
    cv::Mat getSource() const ;
    cv::Mat getDistorted() const ;

    /* Getters (Parameters) */
    cv::Point2d getNu() const ;

    /* Setters */
    virtual void setLens( ClusterLens* ) ;

    void setXY(double, double) ;
    void setPolar(double, double) ;
    void setSource(SphericalSource*) ;

};

class RaytraceModel : public SimulatorModel { 
public:
    using SimulatorModel::SimulatorModel ;
protected:
    virtual cv::Point2d calculateEta( cv::Point2d ) ;
    virtual void parallelDistort(const cv::Mat &src, cv::Mat &dst);
    virtual void distort(int begin, int end, const cv::Mat& src, cv::Mat& dst) ;
private:
};

/* simaux */
void refLines(cv::Mat&) ;

class NotImplemented : public std::exception
{
public:
    virtual const char * what () ;
};

#endif // COSMOSIM_H
