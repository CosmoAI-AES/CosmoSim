//
// Created by simon on 07.04.2022.
//

#ifndef SPHERICAL_SIMULATOR_H
#define SPHERICAL_SIMULATOR_H

#include "opencv2/opencv.hpp"
//#include <symengine/expression.h>
//#include <symengine/lambda_double.h>
#include <ginac/ginac.h>
#include <mutex>

//using namespace SymEngine;
//using namespace GiNaC;


class Simulator {
private:
    int size;
    int sourceSize;
    int mode;
    int einsteinR;
    double GAMMA;
    int xPosSlider;
    int yPosSlider;
    int CHI_percent;
    double CHI;
    double actualX{};
    double actualY{};
    double apparentX{};
    double apparentY{};
    double apparentX2{};
    double apparentY2{};
    double X{};
    double Y{};
    double phi{};
    double actualAbs{};
    double apparentAbs{};
    double apparentAbs2{};
    double R{};
    const static int n = 10;
    GiNaC::symbol x, y, c, g;
    GiNaC::lst syms;

//    RCP<const Symbol> xSym, ySym, gammaSym, chiSym;
//    std::vector<std::vector<RCP<const Basic>>> alphas;
//    std::vector<std::vector<RCP<const Basic>>> betas;
    std::vector<std::vector<GiNaC::ex>> alphas;
    std::vector<std::vector<GiNaC::ex>> betas;



//    lst syms = {x, y, c, g};


//    std::array<std::array<LambdaRealDoubleVisitor, n>, n> alphas_l;
//    std::array<std::array<LambdaRealDoubleVisitor, n>, n> betas_l;

public:
    Simulator();

    void update();

    void initGui();

private:
    void calculate();

//    void drawSource(cv::Mat& img, double xPos, double yPos) const;

    [[nodiscard]] std::pair<double, double> pointMass(double r, double theta) const;

    std::pair<double, double> spherical(double r, double theta) const;

    void initAlphasBetas();

    static void update_dummy(int, void*);

    cv::Mat formatImg(cv::Mat &imgDistorted, cv::Mat &imgActual, int displaySize) const;

    static void refLines(cv::Mat &target);

    void distort(int row, int col, const cv::Mat &src, cv::Mat &dst, std::mutex& m);

    void parallelDistort(const cv::Mat &src, cv::Mat &dst);
};


#endif //SPHERICAL_SIMULATOR_H
