#ifndef LENS_H
#define LENS_H

#if __has_include("opencv4/opencv2/opencv.hpp")
#include "opencv4/opencv2/opencv.hpp"
#else
#include "opencv2/opencv.hpp"
#endif

#define MAXCLUSTER 50

class Lens {
public:
    virtual cv::Point2d getXi( cv::Point2d ) ;

    virtual double psiValue( double, double ) const ; /* Not Implemented */
    virtual double psiXvalue( double, double ) const ; /* Not Implemented */
    virtual double psiYvalue( double, double ) const ; /* Not Implemented */

};

class PsiFunctionLens : public Lens {
protected:
    double einsteinR /* R_E or \xi_0 */,
           ellipseratio=1 /* f */,
	   orientation=0 /* \phi */ ;
public:
    void setEinsteinR( double ) ;
} ;

class PointMass : public PsiFunctionLens { 

private:

public:
    virtual double psiValue( double, double ) const ;
    virtual double psiXvalue( double, double ) const ;
    virtual double psiYvalue( double, double ) const ;

    virtual cv::Point2d getXi( cv::Point2d ) ;
};
class SIS : public PsiFunctionLens { 
public:
    virtual double psiValue( double, double ) const ;
    virtual double psiXvalue( double, double ) const ;
    virtual double psiYvalue( double, double ) const ;
};

class SIE : public PsiFunctionLens { 
private:
    double psifunctionPolar( double, double ) const ;

public:
    virtual double psiValue( double, double ) const ;
    virtual double psiXvalue( double, double ) const ;
    virtual double psiYvalue( double, double ) const ;
};

class ClusterLens : public PsiFunctionLens {
private:
    PsiFunctionLens *lens[MAXCLUSTER] ;
    double xshift[MAXCLUSTER], yshift[MAXCLUSTER] ;
    int nlens = 0 ;
public:
    // virtual void addLens( PsiFunctionLens* );
    virtual void addLens( PsiFunctionLens*, double, double );
    virtual cv::Point2d getXi( cv::Point2d ) ;

    virtual double psiValue( double, double ) const ;
    virtual double psiXvalue( double, double ) const ;
    virtual double psiYvalue( double, double ) const ;
} ;

#endif // LENS_H
