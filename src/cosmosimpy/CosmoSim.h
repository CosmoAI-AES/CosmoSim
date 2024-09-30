/* (C) 2022: Hans Georg Schaathun <georg@schaathun.net> */

#ifndef COSMOSIM_FACADE_H
#define COSMOSIM_FACADE_H

#include "cosmosim/Roulette.h"
#include "cosmosim/Simulator.h"
#include "cosmosim/Source.h"
#include "cosmosim/Lens.h"

#include <pybind11/pybind11.h>
#include <opencv2/opencv.hpp>

enum SourceSpec { CSIM_SOURCE_SPHERE,
                  CSIM_SOURCE_ELLIPSE,
                  CSIM_SOURCE_IMAGE,
                  CSIM_SOURCE_TRIANGLE } ;
enum ModelSpec { CSIM_MODEL_RAYTRACE,
                  CSIM_MODEL_ROULETTE,
                  CSIM_MODEL_ROULETTE_REGEN,
                  CSIM_MODEL_POINTMASS_EXACT,
                  CSIM_MODEL_POINTMASS_ROULETTE,
                  CSIM_NOMODEL } ;
enum PsiSpec    { CSIM_PSI_SIS,
                  CSIM_PSI_SIE,
                  CSIM_CLUSTER,
                  CSIM_NOPSI_ROULETTE,
                  CSIM_NOPSI_PM,
                  CSIM_NOPSI } ;

class CosmoSim {
private:
    int size=512, basesize=512 ;
    double chi=0.5 ;
    int modelmode=CSIM_MODEL_POINTMASS_EXACT ;
    double ellipseratio=0.5, orientation=0, einsteinR=20 ;
    int sampledlens = 0, modelchanged = 1 ;
    int lensmode=CSIM_NOPSI_PM ;
    int srcmode=CSIM_SOURCE_SPHERE, sourceSize=20, sourceSize2=10,
        sourceTheta=0 ;
    double xPos=10, yPos=0, rPos=10, thetaPos=0; ;
    cv::Point2d centrepoint ;
    double maskRadius=0 ;
    int nterms=16 ;
    int bgcolour=0 ;
    SimulatorModel *sim = NULL ;
    Source *src = NULL ;
    bool running = false ;
    bool maskmode ;

    void initSource() ;
    void initLens() ;
    std::string filename[10], sourcefile = "einstein.png" ;

    Lens *lens = NULL ;
    PsiFunctionLens *psilens = NULL ;

public:
    CosmoSim();

    PsiFunctionLens *getLens( int ) ;

    void setFile(int,std::string) ;
    void setSourceFile(std::string) ;
    void setXY(double, double) ;
    void setPolar(int, int) ;
    void setCHI(double);
    void setNterms(int);
    void setMaskRadius(double);
    void setImageSize(int);
    void setResolution(int);
    void setBGColour(int);

    void setSourceMode(int);
    void setModelMode(int);
    void setLensMode(int);
    void setCluster(ClusterLens*);
    void setSampled(int);
    void setEinsteinR(double);
    void setRatio(double);
    void setOrientation(double);
    void setSourceParameters(double,double,double);

    bool runSim();
    bool moveSim( double, double ) ;
    void diagnostics();

    void maskImage(double) ;
    void showMask() ;
    void setMaskMode(bool) ;

    cv::Mat getSource(bool) ;
    cv::Mat getActual(bool,bool) ;
    cv::Mat getDistorted(bool,bool) ;

    cv::Mat getPsiMap() ;
    cv::Mat getMassMap() ;

    cv::Point2d getOffset( double x, double y ) ;
    cv::Point2d getNu( ) ;
    cv::Point2d getRelativeEta( double x, double y ) ;
    double getChi( ) ;
    double getAlpha( double x, double y, int m, int s ) ;
    double getBeta( double x, double y, int m, int s ) ;
    double getAlphaXi( int m, int s ) ;
    double getBetaXi( int m, int s ) ;
};

class RouletteSim {
private:
    int size=512, basesize=512 ;
    int srcmode=CSIM_SOURCE_SPHERE, sourceSize=20, sourceSize2=10,
        sourceTheta=0 ;
    cv::Point2d centrepoint ;
    double maskRadius=0 ;
    int nterms=16 ;
    int bgcolour=0 ;
    Source *src = NULL ;
    bool running = false ;
    bool maskmode ;

    void initSource() ;

    RouletteRegenerator *sim = NULL ;

public:
    RouletteSim();
    void initSim( double, double ) ;

    void setNterms(int);
    void setMaskRadius(double);
    void setImageSize(int);
    void setResolution(int);
    void setBGColour(int);

    void setSourceMode(int);
    void setSourceParameters(double,double,double);

    bool runSim();
    void diagnostics();

    void maskImage(double) ;
    void showMask() ;
    void setMaskMode(bool) ;

    cv::Mat getSource(bool) ;
    cv::Mat getActual(bool) ;
    cv::Mat getDistorted(bool) ;

    void setAlphaXi( int m, int s, double val ) ;
    void setBetaXi( int m, int s, double val ) ;
};

#endif // COSMOSIM_FACADE_H
