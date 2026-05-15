/* (C) 2022: Hans Georg Schaathun <georg@schaathun.net> */

/* The SphericalSource class implements a a Spherical, Gaussian mass, */

#include "cosmosim/Source.h"

SphericalSource::SphericalSource(int sz, double sig, double idx, double mag, LightProfileSpec lightprf) :
        Source::Source(sz),
        sigma(sig),
        n_sersic(idx),
        magnitude(mag),
        lightprofile(lightprf)
{ 
        if (lightprofile == LightProfileSpec::CSIM_LIGHT_GAUSSIAN) {
	   std::cout << "[SphericalSource] GAUSS\n" ;
        } else if (lightprofile == LightProfileSpec::CSIM_LIGHT_SERSIC) {
	   std::cout << "[SphericalSource] SERSIC\n" ;
	}
}

/* Draw the source image.  The sourceSize is interpreted as the standard deviation in a Gaussian distribution */
void SphericalSource::drawSource(int begin, int end, cv::Mat& dst) {
    for (int row = begin; row < end; row++) {
        for (int col = 0; col < dst.cols; col++) {
            int x = col - dst.cols/2;
            int y = row - dst.rows/2;
            if (lightprofile == LightProfileSpec::CSIM_LIGHT_GAUSSIAN) {
                auto value = (uchar)round(255 * exp((-x * x - y * y) / (2.0*sigma*sigma)));
                dst.at<uchar>(row, col) = (uchar)value;
            } 
            else if (lightprofile == LightProfileSpec::CSIM_LIGHT_SERSIC) {
                float zp = 25; //zero point
                float re = sigma; // effective radius
                float r = std::sqrt(std::pow(x, 2)+std::pow(y, 2)); //source position
                float bn = 1.992*n_sersic - 0.3271;
                float F = std::pow(10, -0.4 * (magnitude - zp));
                float pi = 3.141592;
                float I_eff = F*std::pow(bn, 2.0 * n_sersic)/(2 * pi * std::pow(re, 2.0) * n_sersic * std::exp(bn) * std::tgamma(2.0 * n_sersic));
                float value = round(I_eff*std::exp(-bn*((std::pow(r/re, 1.0/n_sersic))-1.0)));
                if (value > 255) {
                    value = 255;
                }
                dst.at<uchar>(row, col) = (uchar)value;
            }
        }
    }
}

