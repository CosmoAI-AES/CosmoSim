/* (C) 2023: Hans Georg Schaathun <georg@schaathun.net> */

#include "cosmosim/SampledLens.h"

#include <thread>
#include "simaux.h"

PureSampledModel::PureSampledModel() :
   LensModel::LensModel()
{ 
    std::cout << "Instantiating PureSampledModel ... \n" ;
    rotatedMode = false ;
}
PureSampledModel::PureSampledModel(bool centred) :
   LensModel::LensModel(centred)
{ 
    std::cout << "Instantiating PureSampledModel ... \n" ;
    rotatedMode = false ;
}

void PureSampledModel::updateApparentAbs( ) {
    std::cout << "[PureSampledModel] updateApparentAbs() updates psi.\n" ;
    cv::Mat im = getActual() ;
    lens->updatePsi(im.size()) ;
}
cv::Point2d PureSampledModel::calculateEta( cv::Point2d xi ) {
   cv::Point2d chieta, xy, ij ; 
   cv::Mat psi = lens->getPsi() ;
   cv::Mat psiX = lens->getPsiX() ;
   cv::Mat psiY = lens->getPsiY() ;

   ij = imageCoordinate( xi, psi ) ;
   xy = cv::Point2d( -psiY.at<double>( ij ), -psiX.at<double>( ij ) );
   chieta = xi - xy ;

   return chieta/CHI ;
}
void PureSampledModel::distort(int begin, int end, const cv::Mat& src, cv::Mat& dst) {

    // std::cout << "[PureSampledModel] distort().\n" ;
    for (int row = begin; row < end; row++) {
        for (int col = 0; col < dst.cols; col++) {

            cv::Point2d eta, xi, ij, targetPos ;

            targetPos = cv::Point2d( col - dst.cols / 2.0,
                  dst.rows / 2.0 - row ) ;
            xi = -CHI*targetPos ;
            eta = calculateEta( xi ) + getEta() ;
            ij = imageCoordinate( eta, src ) ;
  
            if (ij.x < src.rows && ij.y < src.cols && ij.x >= 0 && ij.y >= 0) {
                 if ( 3 == src.channels() ) {
                    dst.at<cv::Vec3b>(row, col) = src.at<cv::Vec3b>( ij );
                 } else {
                    dst.at<uchar>(row, col) = src.at<uchar>( ij );
                 }
            }
        }
    }
}

/* getDistortedPos() is not used for the sampled lens model, but
 * it has to be defined, since it is declared for the superclass.  */
cv::Point2d PureSampledModel::getDistortedPos(double r, double theta) const {
   throw NotImplemented() ;
};
void PureSampledModel::setLens( Lens *l ) {
   lens = l ;
}
