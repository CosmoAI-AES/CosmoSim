/* (C) 2022: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/Source.h"
#include <thread>

SphericalSource::SphericalSource(int sz,double sig) :
        size(sz),
        sigma(sig)
{ 
    drawn = 0 ;
    imgApparent = cv::Mat(size, size, CV_8UC1, cv::Scalar(0, 0, 0)) ;
}

/* Draw the source image.  The sourceSize is interpreted as the standard deviation in a Gaussian distribution */
void SphericalSource::drawSource(int begin, int end, cv::Mat& dst) {
    for (int row = begin; row < end; row++) {
        for (int col = 0; col < dst.cols; col++) {
            int x = col - dst.cols/2;
            int y = row - dst.rows/2;
            auto value = (uchar)round(255 * exp((-x * x - y * y) / (2.0*sigma*sigma)));
            dst.at<uchar>(row, col) = value;
        }
    }
}

void SphericalSource::drawParallel(cv::Mat& dst){
    int n_threads = std::thread::hardware_concurrency();
    std::vector<std::thread> threads_vec;
    for (int i = 0; i < n_threads; i++) {
        int begin = dst.rows / n_threads * i;
        int end = dst.rows / n_threads * (i + 1);
        std::thread t([begin, end, &dst, this]() { this->drawSource(begin, end, dst ); });
        threads_vec.push_back(std::move(t));
    }
    for (auto& thread : threads_vec) {
        thread.join();
    }
}

cv::Mat SphericalSource::getImage() {
   if ( ! drawn ) {
      drawParallel( imgApparent ) ;
      drawn = 1 ;
   }
   return imgApparent ;
}

