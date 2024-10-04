/* (C) 2022: Hans Georg Schaathun <georg@schaathun.net> */

#ifndef COSMOSIM_FACADE_H
#define COSMOSIM_FACADE_H

#include "cosmosim/Simulator.h"
#include "cosmosim/Source.h"
#include "cosmosim/Lens.h"

#include <pybind11/pybind11.h>
#include <opencv2/opencv.hpp>


class CosmoSim {
private:
    int size=512, basesize=512 ;
    double chi=0.5 ;
    double ellipseratio=0.5, orientation=0, einsteinR=20 ;
    int modelchanged = 1 ;
    int sourceSize=20 ;
    double xPos=10, yPos=0, rPos=10, thetaPos=0; ;
    cv::Point2d centrepoint ;
    SimulatorModel *sim = NULL ;
    SphericalSource *src = NULL ;
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

    void setXY(double, double) ;
    void setPolar(int, int) ;

    void setLens(PsiFunctionLens*);
    void setSourceParameters(double,double,double);

    bool runSim();
};

#endif // COSMOSIM_FACADE_H
