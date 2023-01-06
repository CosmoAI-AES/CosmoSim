/* (C) 2022: Hans Georg Schaathun <georg@schaathun.net> *
 * Building on code by Simon Ingebrigtsen, Sondre Westbø Remøy,
 * Einar Leite Austnes, and Simon Nedreberg Runde
 */

#include "cosmosim/Simulator.h"

#include <symengine/expression.h>
#include <symengine/lambda_double.h>
#include <thread>
#include <symengine/parser.h>
#include <fstream>

#define DEBUG 0

double factorial_(unsigned int n);

LensModel::LensModel() :
        LensModel(false)
{ }
LensModel::LensModel(bool centred) :
        CHI(0.5),
        einsteinR(20),
        nterms(10),
        centredMode(centred),
        source(NULL)
{ }
LensModel::~LensModel() {
   std::cout << "Destruct lens model\n" ;
   delete source ;
}

/* Getters for the images */
cv::Mat LensModel::getActual() { 
   cv::Mat imgApparent = getApparent() ;

   if ( actualX == 0 && actualY == 0 ) {
      return getApparent() ;
   } else {
     cv::Mat imgActual 
        = cv::Mat::zeros(imgApparent.size(), imgApparent.type());

     // (x0,y0) is the centre of the image in pixel coordinates 
     double x0 = imgApparent.cols/2 ;
     double y0 = imgApparent.rows/2 ;

     cv::Point2f srcTri[3], dstTri[3];
     srcTri[0] = cv::Point2f( x0, y0 );
     dstTri[0] = cv::Point2f( x0+actualX, y0-actualY );
     srcTri[1] = cv::Point2f( x0-actualAbs, y0 );
     dstTri[1] = cv::Point2f( x0, y0 );
     srcTri[2] = cv::Point2f( x0-actualAbs, y0-actualAbs );
     dstTri[2] = cv::Point2f( x0-actualY, y0-actualX );
     cv::Mat rot = cv::getAffineTransform( srcTri, dstTri );

     std::cout << "getActual() (x,y)=(" << actualX << "," << actualY << ")\n" 
               << rot << "\n" ;

     cv::warpAffine(imgApparent, imgActual, rot, imgApparent.size()) ;
     return imgActual ; 
   }
   exit(1) ;
}
cv::Mat LensModel::getApparent() { return source->getImage() ; }
cv::Mat LensModel::getDistorted() { return imgDistorted ; }

cv::Mat LensModel::getDistorted( double app ) { 
   /* This is intended to change the centre of the convergence ring,
    * and draw a different section of the image.
    * TESTING ONLY.
    * The logic is probably faulty. */ 
   apparentAbs = app ;
   this->update() ;
   return imgDistorted ; 
}

cv::Mat LensModel::getSecondary() { 
   /* This only makes sense in the Point Mass model.
    * It uses the same logic as getDistorted(double) above, and
    * is probably faulty. 
    */
   apparentAbs = apparentAbs2 ;
   this->update() ;
   return imgDistorted ; }

void LensModel::update() {

    auto startTime = std::chrono::system_clock::now();
    
    cv::Mat imgApparent = getApparent() ;

    std::cout << "update() x=" << actualX << "; y= " << actualY 
              << "; R=" << actualAbs << "; theta=" << phi
              << "; R_E=" << einsteinR << "; CHI=" << CHI << "\n" ;

    this->calculateAlphaBeta() ;

    int nrows = imgApparent.rows ;
    int ncols = imgApparent.cols ;

    // Make Distorted Image
    // We work in a double sized image to avoid cropping
    cv::Mat imgD = cv::Mat(nrows*2, ncols*2, imgApparent.type() ) ;
    parallelDistort(imgApparent, imgD);

    // Correct the rotation applied to the source image
    cv::Mat rot = cv::getRotationMatrix2D(cv::Point(nrows, ncols), phi*180/PI, 1);
    cv::warpAffine(imgD, imgD, rot, cv::Size(2*nrows, 2*ncols));    // crop distorted image
    imgDistorted = imgD(cv::Rect(nrows/2, ncols/2, nrows, ncols));

    std::cout << "update() (x,y) = (" << actualX << ", " << actualY << ")\n" ;
    std::cout << rot << "\n" ;

    // Calculate run time for this function and print diagnostic output
    auto endTime = std::chrono::system_clock::now();
    std::cout << "Time to update(): " 
              << std::chrono::duration_cast<std::chrono::milliseconds>(endTime - startTime).count() 
              << " milliseconds" << std::endl;

}


/* This just splits the image space in chunks and runs distort() in parallel */
void LensModel::parallelDistort(const cv::Mat& src, cv::Mat& dst) {
    int n_threads = std::thread::hardware_concurrency();
    if ( DEBUG ) std::cout << "Running with " << n_threads << " threads.\n" ;
    std::vector<std::thread> threads_vec;
    if ( maskRadius > dst.rows/2.0 ) maskRadius = dst.rows/2.0 ;
    int lower = maskMode ? floor( dst.rows/2.0 - maskRadius ) : 0,
         rng = maskMode ? ceil( 2.0*maskRadius ) + 1 : dst.rows,
         rng1 = ceil( rng/ n_threads ) ;
    for (int i = 0; i < n_threads; i++) {
        int begin = lower+rng1*i, end = begin+rng1 ;
        std::thread t([begin, end, src, &dst, this]() { distort(begin, end, src, dst); });
        threads_vec.push_back(std::move(t));
    }

    for (auto& thread : threads_vec) {
        thread.join();
    }
}


void LensModel::setMaskMode(bool b) {
   maskMode = b ; 
}
void LensModel::setBGColour(int b) { bgcolour = b ; }
void LensModel::setCentred(bool b) { centredMode = b ; }
void LensModel::distort(int begin, int end, const cv::Mat& src, cv::Mat& dst) {
    // Iterate over the pixels in the image distorted image.
    // (row,col) are pixel co-ordinates
    int R = getCentre() ;
    for (int row = begin; row < end; row++) {
        for (int col = 0; col < dst.cols; col++) {

            int row_, col_;  // pixel co-ordinates in the apparent image
            std::pair<double, double> pos ;

            // Set coordinate system with origin at the centre of mass
            // in the distorted image in the lens plane.
            double x = (col - dst.cols / 2.0 - R) * CHI;
            double y = (dst.rows / 2.0 - row) * CHI;
            // (x,y) are coordinates in the lens plane, and hence the
            // multiplication by CHI

            // Calculate distance and angle of the point evaluated 
            // relative to CoM (origin)
            double r = sqrt(x * x + y * y);

            if ( maskMode && r > maskRadius*CHI ) {
            } else {
              double theta = x == 0 ? PI/2 : atan2(y, x);
              pos = this->getDistortedPos(r, theta);

              // Translate to array index in the source plane
              row_ = (int) round(src.rows / 2.0 - pos.second);
              col_ = (int) round(src.cols / 2.0 + pos.first);
  
              // If (x', y') within source, copy value to imgDistorted
              if (row_ < src.rows && col_ < src.cols && row_ >= 0 && col_ >= 0) {
                 if ( 3 == src.channels() ) {
                    dst.at<cv::Vec3b>(row, col) = src.at<cv::Vec3b>(row_, col_);
                 } else {
                    dst.at<uchar>(row, col) = src.at<uchar>(row_, col_);
                 }
              }
            }
        }
    }
}

void LensModel::updateNterms(int n) {
   nterms = n ;
   update() ;
}
void LensModel::setNterms(int n) {
   nterms = n ;
}
void LensModel::setCHI(double chi) {
   CHI = chi ;
   updateApparentAbs() ;
}
void LensModel::setEinsteinR(double r) {
   einsteinR = r ;
   updateApparentAbs() ;
}
void LensModel::updateAll( double X, double Y, double er, double chi, int n) {
   nterms = n ;
   updateXY(X,Y,chi,er);
}


void LensModel::setSource(Source *src) {
    if ( source != NULL ) delete source ;
    source = src ;
}

/* Default implementation doing nothing.
 * This is correct for any subclass that does not need the alpha/beta tables. */
void LensModel::calculateAlphaBeta() { }

/* Re-calculate co-ordinates using updated parameter settings from the GUI.
 * This is called from the update() method.                                  */
void LensModel::setXY( double X, double Y, double chi, double er ) {

    CHI = chi ;
    einsteinR = er ;
    // Actual position in source plane
    actualX = X ;
    actualY = Y ;

    // Calculate Polar Co-ordinates
    actualAbs = sqrt(actualX * actualX + actualY * actualY); 
    phi = atan2(actualY, actualX); // Angle relative to x-axis

    std::cout << "[setXY] Set position x=" << actualX << "; y=" << actualY
              << "; R=" << actualAbs << "; theta=" << phi << ".\n" ;
    updateApparentAbs() ;
}
void LensModel::updateXY( double X, double Y, double chi, double er ) {
    setXY( X, Y, chi, er ) ;
    update() ;
}
/* Re-calculate co-ordinates using updated parameter settings from the GUI.
 * This is called from the update() method.                                  */
void LensModel::setPolar( double R, double theta, double chi, double er ) {

    CHI = chi ;
    einsteinR = er ;

    actualAbs = R ;
    phi = PI*theta/180 ;

    // Actual position in source plane
    actualX = R*cos(phi) ;
    actualY = R*sin(phi) ;

    std::cout << "[setPolar] Set position x=" << actualX << "; y=" << actualY
              << "; R=" << actualAbs << "; theta=" << phi << ".\n" ;

    updateApparentAbs() ;
}
void LensModel::maskImage( ) {
    maskImage( imgDistorted ) ;
}
void LensModel::markMask( ) {
    markMask( imgDistorted ) ;
}
void LensModel::maskImage( cv::InputOutputArray r ) {
   throw NotImplemented() ;
}
void LensModel::markMask( cv::InputOutputArray r ) {
   throw NotImplemented() ;
}
double LensModel::getCentre( ) {
  return centredMode ? tentativeCentre : apparentAbs ;
}