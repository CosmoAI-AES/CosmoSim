#ifndef ROULETTE_H
#define ROULETTE_H

#include "Simulator.h"

#include <symengine/expression.h>
#include <symengine/lambda_double.h>

using namespace SymEngine;

#define PI 3.14159265358979323846

class RouletteLens : public LensModel { 
public:
    using LensModel::LensModel ;
protected:
    std::array<std::array<double, 202>, 201> alphas_val;
    std::array<std::array<double, 202>, 201> betas_val;

    virtual std::pair<double, double> getDistortedPos(double r, double theta) const;
    virtual void markMask( cv::InputOutputArray ) ;
    virtual void maskImage( cv::InputOutputArray ) ;
};

class RoulettePMLens : public RouletteLens { 
public:
    using RouletteLens::RouletteLens ;
protected:
    virtual std::pair<double, double> getDistortedPos(double r, double theta) const;
    virtual void updateApparentAbs() ;
};

class SphereLens : public RouletteLens { 
  public:
    SphereLens();
    SphereLens(bool);
    SphereLens(std::string,bool);
    void setFile(std::string) ;

  protected:
    virtual void calculateAlphaBeta();
    virtual void updateApparentAbs() ;
  private:
    std::array<std::array<LambdaRealDoubleVisitor, 202>, 201> alphas_l;
    std::array<std::array<LambdaRealDoubleVisitor, 202>, 201> betas_l;

    std::string filename = "50.txt" ;
    void initAlphasBetas();
};

class RoulettePMCLens : public RouletteLens { 
public:
    using RouletteLens::RouletteLens ;
protected:
    virtual void calculateAlphaBeta();
    virtual void updateApparentAbs() ;
};

#endif // ROULETTE_H
