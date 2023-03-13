#ifndef ROULETTE_H
#define ROULETTE_H

#include "Simulator.h"

#include <symengine/expression.h>
#include <symengine/lambda_double.h>

using namespace SymEngine;

#define PI 3.14159265358979323846

class RouletteLens : public LensModel { 
public:
    using PointMassLens::PointMassLens ;
protected:
    virtual void markMask( cv::InputOutputArray ) ;
    virtual void maskImage( cv::InputOutputArray ) ;
}

class RoulettePMLens : public RouletteLens { 
public:
    using RouletteLens::RouletteLens ;
protected:
    virtual std::pair<double, double> getDistortedPos(double r, double theta) const;
    virtual void updateApparentAbs() ;
};

class SphereLens : public LensModel { 
  public:
    SphereLens();
    SphereLens(bool);
    SphereLens(std::string,bool);
    void setFile(std::string) ;
  protected:
    virtual void calculateAlphaBeta();
    virtual std::pair<double, double> getDistortedPos(double r, double theta) const;
    virtual void updateApparentAbs() ;
  private:
    std::string filename = "50.txt" ;
    void initAlphasBetas();
};

#endif // ROULETTE_H
