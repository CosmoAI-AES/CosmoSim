#ifndef PIXMAP_H
#define PIXMAP_H

#include "Simulator.h"

class LensMap { 

protected:
    cv::Mat psi, einsteinMap, massMap ;

private:

public:
    void setEinsteinMap( cv::Mat ) ;
    cv::Mat getPsi( ) ;
    cv::Mat getMassMap( ) ;
    cv::Mat getEinsteinMap( ) ;

};

class PMCLens : public LensMap, public LensModel { 

public:
    using LensModel::LensModel ;

protected:
    virtual std::pair<double, double> getDistortedPos(double r, double theta) const;
    virtual void updateApparentAbs() ;

};


#endif // PIXMAP_H
