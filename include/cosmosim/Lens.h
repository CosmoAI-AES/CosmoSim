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

private:
    std::array<std::array<LambdaRealDoubleVisitor, 202>, 201> alphas_l;
    std::array<std::array<LambdaRealDoubleVisitor, 202>, 201> betas_l;


protected:
    double einsteinR /* R_E or \xi_0 */,
           ellipseratio=1 /* f */,
	   orientation=0 /* \phi */ ;
    std::string filename = "50.txt" ;
    cv::Mat psi, psiX, psiY, einsteinMap ;

    std::array<std::array<double, 202>, 201> alphas_val;
    std::array<std::array<double, 202>, 201> betas_val;
    int nterms=20;

public:
    virtual void updatePsi( cv::Size ) ;
    virtual void updatePsi( ) ;
    virtual void setEinsteinR( double ) ;
    virtual void setOrientation( double ) ;
    virtual void setRatio( double ) ;

    cv::Mat getPsi( ) const ;
    cv::Mat getPsiX( ) const ;
    cv::Mat getPsiY( ) const ;
    cv::Mat getMassMap( ) const ;
    cv::Mat getEinsteinMap( ) const ; // Not implemented
    cv::Mat getPsiImage( ) const ;  // Discouraged
    cv::Mat getMassImage() const ;  // Discouraged

    virtual void initAlphasBetas();
    virtual void calculateAlphaBeta( cv::Point2d xi );
    void setFile(std::string) ;
    void setNterms(int) ;

    // std::array<std::array<double, 202>, 201> getAlphas( cv::Point2d xi ) ;
    // std::array<std::array<double, 202>, 201> getBetas( cv::Point2d xi ) ;
    double getAlpha( cv::Point2d xi, int m, int s ) ;
    double getBeta( cv::Point2d xi, int m, int s ) ;
    double getAlphaXi( int m, int s ) ;
    double getBetaXi( int m, int s ) ;
    double getEinsteinR( ) const ;

    virtual cv::Point2d getXi( cv::Point2d ) ;

    virtual double psiValue( double, double ) const ;
    virtual double psiXvalue( double, double ) const ;
    virtual double psiYvalue( double, double ) const ;

    virtual double criticalXi( double ) const ;
    virtual cv::Point2d caustic( double ) const ;
};

class SampledLens : public Lens {
public:
    virtual void calculateAlphaBeta( cv::Point2d xi );
    virtual cv::Point2d getXi( cv::Point2d ) ;
} ;

class PsiFunctionLens : public Lens {
public:
    virtual void updatePsi( cv::Size ) ;

    virtual cv::Point2d getXi( cv::Point2d ) ;
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
    double psifunctionAligned( double, double ) const ;

public:
    virtual double psiValue( double, double ) const ;
    virtual double psiXvalue( double, double ) const ;
    virtual double psiYvalue( double, double ) const ;

    virtual double criticalXi( double ) const ;
    virtual cv::Point2d caustic( double ) const ;

};


#endif // LENS_H
