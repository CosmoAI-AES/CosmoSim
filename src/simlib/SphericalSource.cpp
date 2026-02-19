/* (C) 2022: Hans Georg Schaathun <georg@schaathun.net> */

/* The SphericalSource class implements a a Spherical, Gaussian mass, */

#include "cosmosim/Source.h"

SphericalSource::SphericalSource(int sz, double sig, LightProfileSpec lightprf) :
        Source::Source(sz),
        sigma(sig),
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
                int n = 4;  // Sersic index
                auto re = 10*sigma; // effective radius
                auto r = std::sqrt(std::pow(x, 2)+std::pow(y, 2));
                auto bn = 1.992*n - 0.3271;
                auto value = round(std::exp(-bn*((std::pow(r/re, 1.0/n))-1.0)));
                if (value > 255) {
                    value = 255;
                }
                dst.at<uchar>(row, col) = (uchar)value;
            }
        }
    }
}

