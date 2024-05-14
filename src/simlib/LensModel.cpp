/* (C) 2023: Hans Georg Schaathun <georg@schaathun.net> *
 * Building on code by Simon Ingebrigtsen, Sondre Westbø Remøy,
 * Einar Leite Austnes, and Simon Nedreberg Runde
 */

#include "cosmosim/Simulator.h"
#include "simaux.h"

#include <thread>

#define DEBUG 0

double factorial_(unsigned int n);

LensModel::LensModel() :
        CHI(0.5),
        nterms(10),
        source(NULL)
{ }

LensModel::~LensModel() {
   std::cout << "Destruct lens model\n" ;
   delete source ;
}

/* Getters for the images */
cv::Mat LensModel::getActual() const {
   cv::Mat imgApparent = getSource() ;
   cv::Mat imgActual 
        = cv::Mat::zeros(imgApparent.size(), imgApparent.type());
   cv::Mat tr = (cv::Mat_<double>(2,3) << 1, 0, getEta().x, 0, 1, -getEta().y);
   cv::warpAffine(imgApparent, imgActual, tr, imgApparent.size()) ;
   return imgActual ; 

}
cv::Mat LensModel::getSource() const {
   return source->getImage() ;
}
cv::Mat LensModel::getApparent() const {
   return source->getImage() ;
}
cv::Mat LensModel::getDistorted() const {
   std::cout << "[LensModel.getDistorted()] image type "
      << imgDistorted.type() << " - " 
      << imgDistorted.size() << "\n" ;
   return imgDistorted ;
}

void LensModel::update( ) {
   updateApparentAbs() ;
   return updateInner() ;
}
void LensModel::update( cv::Point2d xi ) {
   setXi( xi ) ;
   return updateInner() ;
}
cv::Mat LensModel::getCaustic() {
   cv::Mat src = getCritical() ;
   cv::Mat img = cv::Mat::zeros(src.size(), src.type());
   undistort( src, img ) ;
   return img ;
}
cv::Mat LensModel::getCritical() {
   cv::Mat src = getSource() ;
   cv::Mat img = cv::Mat::zeros(src.size(), src.type());
   drawCritical( img ) ;
   return img ;
}
void LensModel::drawCritical() {
   drawCritical( imgDistorted ) ;
}
void LensModel::drawCritical( cv::Mat img ) {
   std::cout << "[drawCritical] \n" ;
   for ( int i=0 ; i < 360 ; ++i ) {
      double phi = i*PI/180 ;
      double xi = lens->criticalXi( phi )/CHI ;
      double x = cos(phi)*xi ;
      double y = sin(phi)*xi ;
      cv::Point2d xy = cv::Point( x, y ) ;
      cv::Point2d ij = imageCoordinate( xy, img ) ;
      std::cout << "[drawCritical] " << ij << "\n" ;
      cv::Vec3b red = (0,0,255) ;
      if ( 3 == img.channels() ) {
         img.at<cv::Vec3b>( ij.x, ij.y ) = red ;
      } else {
         img.at<uchar>( ij.x, ij.y ) = 255 ;
      }
   }
}
void LensModel::updateInner( ) {
    cv::Mat imgApparent = getApparent() ;

    std::cout << "[LensModel::updateInner()] R=" << getEtaAbs() << "; theta=" << phi
              << "; CHI=" << CHI << "\n" ;
    std::cout << "[LensModel::updateInner()] xi=" << getXi()   
              << "; eta=" << getEta() << "; etaOffset=" << etaOffset << "\n" ;
    std::cout << "[LensModel::updateInner()] nu=" << getNu()   
              << "; centre=" << getCentre() << "\n" << std::flush ;

    auto startTime = std::chrono::system_clock::now();

    this->calculateAlphaBeta() ;

    imgDistorted = cv::Mat::zeros(imgApparent.size(), imgApparent.type()) ;
    parallelDistort(imgApparent, imgDistorted);

    // Calculate run time for this function and print diagnostic output
    auto endTime = std::chrono::system_clock::now();
    std::cout << "Time to update(): " 
              << std::chrono::duration_cast<std::chrono::milliseconds>(endTime - startTime).count() 
              << " milliseconds" << std::endl << std::flush ;

}


/* This just splits the image space in chunks and runs distort() in parallel */
void LensModel::parallelDistort(const cv::Mat& src, cv::Mat& dst) {
    int n_threads = std::thread::hardware_concurrency();
    std::cout << "[parallelDistort] Running with " << n_threads << " threads (maskMode="
       << maskMode << ")\n" ;

    std::vector<std::thread> threads_vec;
    double maskRadius = getMaskRadius() ;
    int lower=0, rng=dst.rows, rng1 ; 
    if ( maskMode ) {
        double mrng ;
        cv::Point2d origin = getCentre() ;
        cv::Point2d ij = imageCoordinate( origin, dst ) ;
        if (DEBUG) std::cout << "mask " << ij << " - " << origin << "\n" ;
        lower = floor( ij.x - maskRadius ) ;
        if ( lower < 0 ) lower = 0 ;
        mrng = dst.rows - lower ;
        rng = ceil( 2.0*maskRadius ) + 1 ;
        if ( rng > mrng ) rng = mrng ;
        if (DEBUG) std::cout << maskRadius << " - " << lower << "/" << rng << "\n" ;
    } else {
        std::cout << "[LensModel] No mask \n" ;
    } 
    rng1 = ceil( (double) rng / (double) n_threads ) ;
    if (DEBUG) std::cout << "[parallelDistort] lower=" << lower << "; rng=" << rng
            << "; rng1=" << rng1 << std::endl ;
    for (int i = 0; i < n_threads; i++) {
        int begin = lower+rng1*i, end = begin+rng1 ;
        if ( end > dst.rows ) end = dst.rows ;
        std::thread t([begin, end, src, &dst, this]() { distort(begin, end, src, dst); });
        threads_vec.push_back(std::move(t));
    }

    for (auto& thread : threads_vec) {
        thread.join();
    }
}

void LensModel::distort(int begin, int end, const cv::Mat& src, cv::Mat& dst) {
    // Iterate over the pixels in the image distorted image.
    // (row,col) are pixel co-ordinates
    double maskRadius = getMaskRadius()*CHI ;
    cv::Point2d xi = getXi() ;
    for (int row = begin; row < end; row++) {
        for (int col = 0; col < dst.cols; col++) {

            cv::Point2d pos, ij ;

            // Set coordinate system with origin at the centre of mass
            // in the distorted image in the lens plane.
            double x = (col - dst.cols / 2.0 ) * CHI - xi.x;
            double y = (dst.rows / 2.0 - row ) * CHI - xi.y;
            // (x,y) are coordinates in the lens plane, and hence the
            // multiplication by CHI

            // Calculate distance and angle of the point evaluated 
            // relative to CoM (origin)
            double r = sqrt(x * x + y * y);

            if ( maskMode && r > maskRadius ) {
            } else {
              double theta = x == 0 ? signf(y)*PI/2 : atan2(y, x);
              pos = this->getDistortedPos(r, theta);
              pos += etaOffset ;

              // Translate to array index in the source plane
              ij = imageCoordinate( pos, src ) ;
  
              // If the pixel is within range, copy value from src to dst
              if (ij.x < src.rows-1 && ij.y < src.cols-1 && ij.x >= 0 && ij.y >= 0) {
                 if ( 3 == src.channels() ) {
                    dst.at<cv::Vec3b>(row, col) = src.at<cv::Vec3b>( ij.x, ij.y );
                 } else {
                    dst.at<uchar>(row, col) = src.at<uchar>( ij.x, ij.y );
                 }
              }
            }
        }
    }
}
void LensModel::undistort(const cv::Mat& src, cv::Mat& dst) {
    throw NotImplemented() ;
    // Iterate over the pixels in the apparent image src and create
    // a corresponding source image dst.
    // This is intended for use to draw the caustics.
    cv::Point2d xi = getXi() ;
    for (int row = 0; row < dst.rows; row++) {
        for (int col = 0; col < dst.cols; col++) {

            cv::Point2d pos, ij ;

            // Set coordinate system with origin at the centre of mass
            // in the distorted image in the lens plane.
            double x = (col - dst.cols / 2.0 ) * CHI - xi.x;
            double y = (dst.rows / 2.0 - row ) * CHI - xi.y;
            // (x,y) are coordinates in the lens plane, and hence the
            // multiplication by CHI

            
            double r = sqrt(x * x + y * y);
            double theta = x == 0 ? signf(y)*PI/2 : atan2(y, x);

            pos = this->getDistortedPos(r, theta);

            // Translate to array index in the source plane
            ij = imageCoordinate( pos, src ) ;
  
            // If the pixel is within range, copy value from src to dst
            if (ij.x < src.rows-1 && ij.y < src.cols-1 && ij.x >= 0 && ij.y >= 0) {
               if ( 3 == src.channels() ) {
                  dst.at<cv::Vec3b>(ij.x, ij.y) = src.at<cv::Vec3b>( row, col ) ;
                  
               } else {
                  dst.at<uchar>(ij.x, ij.y ) = src.at<uchar>(  row, col ) ;
               }
            }
        }
    }
}

/* Initialiser.  The default implementation does nothing.
 * This is correct for any subclass that does not need the alpha/beta tables. */
void LensModel::calculateAlphaBeta() { }


/** *** Setters *** */

/* A.  Mode setters */
void LensModel::setMaskMode(bool b) {
   maskMode = b ; 
}
void LensModel::setBGColour(int b) { bgcolour = b ; }

/* B. Source model setter */
void LensModel::setSource(Source *src) {
    if ( source != NULL ) delete source ;
    source = src ;
}

/* C. Lens Model setter */
void LensModel::setNterms(int n) {
   nterms = n ;
}
void LensModel::setCHI(double chi) {
   CHI = chi ;
}

/* D. Position (eta) setters */

/* Re-calculate co-ordinates using updated parameter settings from the GUI.
 * This is called from the update() method.                                  */
void LensModel::setXY( double X, double Y ) {

    // Actual position in source plane
    eta = cv::Point2d( X, Y ) ;

    // Calculate Polar Co-ordinates
    phi = atan2(eta.y, eta.x); // Angle relative to x-axis

    if (DEBUG) std::cout << "[setXY] eta=" << eta 
              << "; R=" << getEtaAbs() << "; theta=" << phi << ".\n" ;
}

/* Re-calculate co-ordinates using updated parameter settings from the GUI.
 * This is called from the update() method.                                  */
void LensModel::setPolar( double R, double theta ) {

    phi = PI*theta/180 ;

    // Actual position in source plane
    eta = cv::Point2d( R*cos(phi), R*sin(phi) ) ;

    if (DEBUG) std::cout << "[setPolar] Set position x=" << eta.x << "; y=" << eta.y
              << "; R=" << getEtaAbs() << "; theta=" << phi << ".\n" ;

}


/* Masking */
void LensModel::maskImage( ) {
    maskImage( imgDistorted, 1 ) ;
}
void LensModel::maskImage( double scale ) {
    maskImage( imgDistorted, scale ) ;
}
void LensModel::markMask( ) {
    markMask( imgDistorted ) ;
}
void LensModel::maskImage( cv::InputOutputArray imgD, double scale ) {
   std::cout << "[LensModel.maskImage()] image type\n" ;
   // throw NotImplemented() ;
      // std::cout << "RouletteModel::maskImage\n" ;
      cv::Mat imgDistorted = getDistorted() ;
      cv::Point2d origo = imageCoordinate( getCentre(), imgDistorted ) ;
      origo = cv::Point2d( origo.y, origo.x ) ;
      cv::Mat mask( imgD.size(), CV_8UC1, cv::Scalar(255) ) ;
      cv::Mat black( imgD.size(), imgD.type(), cv::Scalar(0) ) ;
      cv::circle( mask, origo, scale*getMaskRadius(), cv::Scalar(0), cv::FILLED ) ;
      black.copyTo( imgD, mask ) ;
}
void LensModel::markMask( cv::InputOutputArray imgD ) {
   std::cout << "[LensModel.markMask()] image type\n" ;
      cv::Mat imgDistorted = getDistorted() ;
      cv::Point2d origo = imageCoordinate( getCentre(), imgDistorted ) ;
      origo = cv::Point2d( origo.y, origo.x ) ;
      cv::circle( imgD, origo, getMaskRadius(), cv::Scalar(255), 1 ) ;
      cv::circle( imgD, origo, 3, cv::Scalar(0), 1 ) ;
      cv::circle( imgD, origo, 1, cv::Scalar(0), cv::FILLED ) ;
}

/* Getters */
cv::Point2d LensModel::getCentre( ) const {
   cv::Point2d xichi =  getXi()/CHI ;
   return xichi ;
}
cv::Point2d LensModel::getXi() const { 
   return xi ;
}
double LensModel::getXiAbs() const { 
   cv::Point2d xi = getXi() ;
   return sqrt( xi.x*xi.x + xi.y*xi.y ) ;
}
cv::Point2d LensModel::getTrueXi() const { 
   return CHI*nu ;
}
cv::Point2d LensModel::getNu() const { 
   return nu ;
}
double LensModel::getNuAbs() const { 
   return sqrt( nu.x*nu.x + nu.y*nu.y ) ;
}
cv::Point2d LensModel::getEta() const {
   return eta ;
}
double LensModel::getEtaSquare() const {
   return eta.x*eta.x + eta.y*eta.y ;
}
double LensModel::getEtaAbs() const {
   return sqrt( eta.x*eta.x + eta.y*eta.y ) ;
}
double LensModel::getMaskRadius() const { return 1024*1024 ; }
void LensModel::setNu( cv::Point2d n ) {
   nu = n ;
   xi = nu*CHI ;
   etaOffset = cv::Point2d( 0, 0 ) ;
   if (DEBUG) std::cout << "[setNu] etaOffset set to zero.\n" ;
}
void LensModel::setXi( cv::Point2d x ) {
      std::cout << "[LensModel.setXi()] image type\n" ;
      throw NotImplemented() ;
}
void LensModel::setLens( Lens *l ) {
   lens = l ;
}

cv::Point2d LensModel::getRelativeEta( cv::Point2d xi1 ) {
   // returns $\vec\eta''$
   cv::Point2d releta ;
   releta = eta - xi1/CHI ;
   std::cout << "[getRelativeEta] releta=" << releta << std::endl ;
   return releta ;
}

cv::Point2d LensModel::getOffset( cv::Point2d xi1 ) {
   cv::Point2d releta, eta, r ; 

   releta = xi1 - cv::Point2d( lens->psiXvalue( xi1.x, xi1.y ),
                       lens->psiYvalue( xi1.x, xi1.y ) ) ;
   eta = getEta() ;
   r = releta/CHI - eta ;

   std::cout << "[getOffset] eta=" << eta << "; xi1=" << xi1
             << "; releta=" << releta 
             << "; return " << r << std::endl ;

   // return is the difference between source point corresponding to the
   // reference point in the lens plane and the actual source centre
   return r ;
}

void LensModel::updateApparentAbs( ) {
    std::cout << "[LensModel] updateApparentAbs() updates psi.\n" ;
    cv::Mat im = getActual() ;
    lens->updatePsi(im.size()) ;
    cv::Point2d chieta = CHI*getEta() ;
    cv::Point2d xi1 = lens->getXi( chieta ) ;
    setNu( xi1/CHI ) ;
}
