#ifndef PIXMAP_H
#define PIXMAP_H

#include "Simulator.h"


class PixMapLens : public LensModel { 

protected:
    cv::Mat psi, einsteinMap, massMap ;

private:

public:
    using LensModel::LensModel ;

    void setEinsteinMap( cv::Mat ) ;
    cv::Mat getPsi( ) ;
    cv::Mat getMassMap( ) ;
    cv::Mat getEinsteinMap( ) ;

};

class PMCLens : public PixMapLens { 

public:
    using PixMapLens::PixMapLens ;

protected:
    virtual std::pair<double, double> getDistortedPos(double r, double theta) const;
    virtual void updateApparentAbs() ;

};


#endif // PIXMAP_H
