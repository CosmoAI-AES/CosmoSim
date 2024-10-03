#ifndef LENS_H
#define LENS_H

#if __has_include("opencv4/opencv2/opencv.hpp")
#include "opencv4/opencv2/opencv.hpp"
#else
#include "opencv2/opencv.hpp"
#endif

#include <symengine/expression.h>
#include <symengine/lambda_double.h>

using namespace SymEngine;

class Lens {



protected:
    double einsteinR /* R_E or \xi_0 */,
           ellipseratio=1 /* f */,
	   orientation=0 /* \phi */ ;
    std::string filename = "nosuchfile" ;

    int nterms=20;

public:
    virtual void setEinsteinR( double ) ;
    virtual void setOrientation( double ) ;
    virtual void setRatio( double ) ;


    virtual void initAlphasBetas() = 0 ;
    virtual void calculateAlphaBeta( cv::Point2d xi ) = 0;
    void setFile(std::string) ;
    void setNterms(int) ;

    virtual double getAlpha( cv::Point2d xi, int m, int s ) = 0 ;
    virtual double getBeta( cv::Point2d xi, int m, int s ) = 0 ;
    virtual double getAlphaXi( int m, int s ) = 0 ;
    virtual double getBetaXi( int m, int s ) = 0 ;
    double getEinsteinR( ) const ;

    double getOrientation( ) const ;

    virtual cv::Point2d getXi( cv::Point2d ) ;

    virtual double psiValue( double, double ) const = 0 ;
    virtual double psiXvalue( double, double ) const = 0 ;
    virtual double psiYvalue( double, double ) const = 0 ;

    virtual double criticalXi( double ) const ;
    virtual cv::Point2d caustic( double ) const ;
};

class SampledLens : public Lens {
private:
    std::array<std::array<double, 202>, 201> alphas_val;
    std::array<std::array<double, 202>, 201> betas_val;
protected:
    cv::Mat psi, psiX, psiY ;
public:
    virtual void initAlphasBetas();
    virtual void calculateAlphaBeta( cv::Point2d xi );
    virtual cv::Point2d getXi( cv::Point2d ) ;

    virtual double getAlphaXi( int m, int s ) ;
    virtual double getBetaXi( int m, int s ) ;
    virtual double getAlpha( cv::Point2d xi, int m, int s ) ;
    virtual double getBeta( cv::Point2d xi, int m, int s ) ;

    virtual double psiValue( double, double ) const ;
    virtual double psiXvalue( double, double ) const ;
    virtual double psiYvalue( double, double ) const ;

    virtual void updatePsi( cv::Size ) ;
    virtual void updatePsi( ) ;
    cv::Mat getPsi( ) const ;
} ;

class PsiFunctionLens : public Lens {
private:
    std::array<std::array<LambdaRealDoubleVisitor, 202>, 201> alphas_l;
    std::array<std::array<LambdaRealDoubleVisitor, 202>, 201> betas_l;
    std::array<std::array<double, 202>, 201> alphas_val;
    std::array<std::array<double, 202>, 201> betas_val;
public:
    virtual void initAlphasBetas();
    virtual void calculateAlphaBeta( cv::Point2d xi );

    virtual double getAlpha( cv::Point2d xi, int m, int s ) ;
    virtual double getBeta( cv::Point2d xi, int m, int s ) ;
    virtual double getAlphaXi( int m, int s ) ;
    virtual double getBetaXi( int m, int s ) ;
} ;

class SampledPsiFunctionLens : public SampledLens {
   private:
      PsiFunctionLens *lens ;
   public:
      SampledPsiFunctionLens(PsiFunctionLens*) ;
      virtual void updatePsi( cv::Size ) ;
      virtual void setEinsteinR( double ) ;
      virtual void setOrientation( double ) ;
      virtual void setRatio( double ) ;
      virtual double criticalXi( double ) const ;
      virtual cv::Point2d caustic( double phi ) const ;
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

private:

public:
    virtual double psiValue( double, double ) const ;
    virtual double psiXvalue( double, double ) const ;
    virtual double psiYvalue( double, double ) const ;

    virtual double criticalXi( double ) const ;
    virtual cv::Point2d caustic( double ) const ;
};

class SIE : public PsiFunctionLens { 

private:
    double psifunctionPolar( double, double ) const ;
    // double psifunctionAligned( double, double ) const ;

public:
    virtual double psiValue( double, double ) const ;
    virtual double psiXvalue( double, double ) const ;
    virtual double psiYvalue( double, double ) const ;

    virtual double criticalXi( double ) const ;
    virtual cv::Point2d caustic( double ) const ;

};


#endif // LENS_H
