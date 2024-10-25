/* (C) 2023: Hans Georg Schaathun <georg@schaathun.net> *
 * Building on code by Simon Ingebrigtsen, Sondre Westbø Remøy,
 * Einar Leite Austnes, and Simon Nedreberg Runde
 */

#include "cosmosim/Simulator.h"
#include "simaux.h"

#include <thread>
#include <pybind11/pybind11.h>
namespace py = pybind11;

SimulatorModel::SimulatorModel() :
        CHI(0.5),
        nterms(10),
        source(NULL)
{ }

SimulatorModel::~SimulatorModel() {
    // delete source ;
    // delete segfaults on object created in python
}

/* Getters for the images */
cv::Mat SimulatorModel::getActual() const {
   cv::Mat imgApparent = getSource() ;
   cv::Mat imgActual 
        = cv::Mat::zeros(imgApparent.size(), imgApparent.type());
   cv::Mat tr = (cv::Mat_<double>(2,3) << 1, 0, getEta().x, 0, 1, -getEta().y);
   cv::warpAffine(imgApparent, imgActual, tr, imgApparent.size()) ;
   return imgActual ; 

}
cv::Mat SimulatorModel::getSource() const {
   std::cout << "[SimulatorModel::getSource()]\n" ;
   if ( NULL == source ) {
       std::cout << "[SimulatorModel::getSource()] Source not defined.\n" ;
   }
   return source->getImage() ;
}
cv::Mat SimulatorModel::getApparent() const {
   return source->getImage() ;
}
cv::Mat SimulatorModel::getDistorted() const {
   return imgDistorted ;
}

void SimulatorModel::update( ) {
   if ( DEBUG && lens != NULL ) {
      std::cout << "[SimulatorModel::update] Lens: " << lens->idString() << "\n" ;
      std::cout << "[SimulatorModel::update] CHI=" << CHI << "\n" ;
   } ;
   updateApparentAbs() ;
   if (DEBUG) std::cout << "[SimulatorModel::update] Done updateApparentAbs()\n" ;
   Py_BEGIN_ALLOW_THREADS
   std::cout << "[SimulatorModel::update] thread section\n" << std::flush ;
   updateInner() ;
   Py_END_ALLOW_THREADS
}

void SimulatorModel::update( cv::Point2d xi ) {
   setXi( xi ) ;
   if (DEBUG) std::cout << "[SimulatorModel::update] Done setXi()\n" ;
   return updateInner() ;
}

cv::Mat SimulatorModel::getCaustic() {
   cv::Mat src = getCritical() ;
   cv::Mat img = cv::Mat::zeros(src.size(), src.type());
   undistort( src, img ) ;
   return img ;
}
cv::Mat SimulatorModel::getCritical() {
   cv::Mat src = getSource() ;
   cv::Mat img = cv::Mat::zeros(src.size(), src.type());
   drawCritical( img ) ;
   return img ;
}
void SimulatorModel::drawCaustics( cv::Mat img ) {
   try {
      for ( int i=0 ; i < 360*5 ; ++i ) {
         double phi = i*PI/(180*5) ;
         cv::Point2d xy = lens->caustic( phi )/CHI ;
         cv::Point2d ij = imageCoordinate( xy, img ) ;
         cv::Vec3b red = (0,0,255) ;
         if ( 3 == img.channels() ) {
            img.at<cv::Vec3b>( ij.x, ij.y ) = red ;
         } else {
            img.at<uchar>( ij.x, ij.y ) = 255 ;
         }
      }
   } catch ( NotImplemented e ) {
      std::cerr << e.what() << std::endl ;
      std::cerr << "Caustics not drawn" << std::endl ;
   }
}
void SimulatorModel::drawCritical() {
   drawCritical( imgDistorted ) ;
}
void SimulatorModel::drawCritical( cv::Mat img ) {
   try {
      for ( int i=0 ; i < 360*5 ; ++i ) {
         double phi = i*PI/(180*5) ;
         double xi = lens->criticalXi( phi )/CHI ;
         double x = cos(phi)*xi ;
         double y = sin(phi)*xi ;
         cv::Point2d xy = cv::Point( x, y ) ;
         cv::Point2d ij = imageCoordinate( xy, img ) ;
         cv::Vec3b red = (0,0,255) ;
         if ( 3 == img.channels() ) {
            img.at<cv::Vec3b>( ij.x, ij.y ) = red ;
         } else {
            img.at<uchar>( ij.x, ij.y ) = 255 ;
         }
      }
   } catch ( NotImplemented e ) {
      std::cerr << e.what() << std::endl ;
      std::cerr << "Critical Curves not drawn" << std::endl ;
   }
}
void SimulatorModel::updateInner( ) {
    cv::Mat imgApparent = getApparent() ;

    if ( DEBUG ) {
      std::cout << "[SimulatorModel::updateInner()] R=" << getEtaAbs() 
              << "; CHI=" << CHI << "\n" ;
      std::cout << "[SimulatorModel::updateInner()] xi=" << getXi()   
              << "; eta=" << getEta() << "; etaOffset=" << etaOffset << "\n" ;
      std::cout << "[SimulatorModel::updateInner()] nu=" << getNu()   
              << "; centre=" << getCentre() << "\n" << std::flush ;
    }

    auto startTime = std::chrono::system_clock::now();

    this->calculateAlphaBeta() ;

    imgDistorted = cv::Mat::zeros(imgApparent.size(), imgApparent.type()) ;
    parallelDistort(imgApparent, imgDistorted);

    // Calculate run time for this function and print diagnostic output
    auto endTime = std::chrono::system_clock::now();
    if (DEBUG) std::cout << "Time to update(): " 
              << std::chrono::duration_cast<std::chrono::milliseconds>(endTime - startTime).count() 
              << " milliseconds" << std::endl << std::flush ;

}


/* This just splits the image space in chunks and runs distort() in parallel */
void SimulatorModel::parallelDistort(const cv::Mat& src, cv::Mat& dst) {
    int n_threads = std::thread::hardware_concurrency() ;
    if (DEBUG) std::cout << "[SimulatorModel::parallelDistort] " << n_threads << " threads (maskMode="
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
    } else if (DEBUG) {
        std::cout << "[SimulatorModel] No mask \n" ;
    } 
    rng1 = ceil( (double) rng / (double) n_threads ) ;
    if (DEBUG) std::cout << "[SimulatorModel::parallelDistort] lower=" << lower << "; rng=" << rng
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

void SimulatorModel::distort(int begin, int end, const cv::Mat& src, cv::Mat& dst) {
    // Iterate over the pixels in the image distorted image.
    // (row,col) are pixel co-ordinates
    double maskRadius = getMaskRadius()*CHI ;
    cv::Point2d xi = getXi() ;
    if (DEBUG) std::cout << "[SimulatorModel::distort] begin=" << begin << "; end=" << end
            << std::endl ;
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
void SimulatorModel::undistort(const cv::Mat& src, cv::Mat& dst) {
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
void SimulatorModel::calculateAlphaBeta() { 

    if ( lens == NULL ) {
        std::cout << "[calculateAlphaBeta] No lens - does nothing.\n" ;
    } else {
        cv::Point2d xi = getXi() ;
        std::cout << "[calculateAlphaBeta] [" << xi << "] ... \n" ;
        lens->calculateAlphaBeta( xi, nterms ) ;
    }
}


/** *** Setters *** */

/* A.  Mode setters */
void SimulatorModel::setMaskMode(bool b) {
   maskMode = b ; 
}
void SimulatorModel::setBGColour(int b) { bgcolour = b ; }

/* B. Source model setter */
void SimulatorModel::setSource(Source *src) {
    // if ( source != NULL ) delete source ;
    // delete segfaults on object created in python
    if ( NULL == src ) {
       std::cout << "[SimulatorModel::setSource] NULL source\n" ;
    } else {
       std::cout << "[SimulatorModel::setSource] setting source\n" ;
    }
    source = src ;
}

/* C. Lens Model setter */
void SimulatorModel::setNterms(int n) {
   nterms = n ;
}
void SimulatorModel::setCHI(double chi) {
   CHI = chi ;
}

/* D. Position (eta) setters */

/* Set the actual positions in the source plane using Cartesian Coordinates */
void SimulatorModel::setXY( double X, double Y ) {

    eta = cv::Point2d( X, Y ) ;

}

double SimulatorModel::getPhi( ) const {
    return atan2(eta.y, eta.x); // Angle relative to x-axis
}

/* Set the actual positions in the source plane using Polar Coordinates */
void SimulatorModel::setPolar( double R, double theta ) {
    double phi = PI*theta/180 ;
    eta = cv::Point2d( R*cos(phi), R*sin(phi) ) ;
}


/* Masking */
void SimulatorModel::maskImage( ) {
    maskImage( imgDistorted, 1 ) ;
}
void SimulatorModel::maskImage( double scale ) {
    maskImage( imgDistorted, scale ) ;
}
void SimulatorModel::markMask( ) {
    markMask( imgDistorted ) ;
}
void SimulatorModel::maskImage( cv::InputOutputArray imgD, double scale ) {

      cv::Mat imgDistorted = getDistorted() ;
      cv::Point2d origo = imageCoordinate( getCentre(), imgDistorted ) ;
      origo = cv::Point2d( origo.y, origo.x ) ;
      cv::Mat mask( imgD.size(), CV_8UC1, cv::Scalar(255) ) ;
      cv::Mat black( imgD.size(), imgD.type(), cv::Scalar(0) ) ;
      cv::circle( mask, origo, scale*getMaskRadius(), cv::Scalar(0), cv::FILLED ) ;
      black.copyTo( imgD, mask ) ;
}
void SimulatorModel::markMask( cv::InputOutputArray imgD ) {
      cv::Mat imgDistorted = getDistorted() ;
      cv::Point2d origo = imageCoordinate( getCentre(), imgDistorted ) ;
      origo = cv::Point2d( origo.y, origo.x ) ;
      cv::circle( imgD, origo, getMaskRadius(), cv::Scalar(255), 1 ) ;
      cv::circle( imgD, origo, 3, cv::Scalar(0), 1 ) ;
      cv::circle( imgD, origo, 1, cv::Scalar(0), cv::FILLED ) ;
}

/* Getters */
cv::Point2d SimulatorModel::getCentre( ) const {
   cv::Point2d xichi =  getXi()/CHI ;
   return xichi ;
}
cv::Point2d SimulatorModel::getXi() const { 
   return referenceXi ;
}
double SimulatorModel::getXiAbs() const { 
   cv::Point2d xi = getXi() ;
   return sqrt( xi.x*xi.x + xi.y*xi.y ) ;
}
cv::Point2d SimulatorModel::getTrueXi() const { 
   return CHI*nu ;
}
cv::Point2d SimulatorModel::getNu() const { 
   return nu ;
}
double SimulatorModel::getNuAbs() const { 
   return sqrt( nu.x*nu.x + nu.y*nu.y ) ;
}
cv::Point2d SimulatorModel::getEta() const {
   return eta ;
}
double SimulatorModel::getEtaSquare() const {
   return eta.x*eta.x + eta.y*eta.y ;
}
double SimulatorModel::getEtaAbs() const {
   return sqrt( eta.x*eta.x + eta.y*eta.y ) ;
}
double SimulatorModel::getMaskRadius() const { 
   // return 1024*1024 ; 
   if ( maskRadius > 0 ) {
      return maskRadius ;
   } else {
      return getXiAbs()/CHI ; 
   }
}
void SimulatorModel::setNu( cv::Point2d n ) {
   nu = n ;
   referenceXi = nu*CHI ;
   etaOffset = cv::Point2d( 0, 0 ) ;
   if (DEBUG) std::cout << "[setNu] etaOffset set to zero.\n" ;
}
void SimulatorModel::setXi( cv::Point2d xi1 ) {
   // xi1 is an alternative reference point \xi'
   referenceXi = xi1 ;   // reset \xi

   // etaOffset is the difference between source point corresponding to the
   // reference point in the lens plane and the actual source centre
   etaOffset = getOffset( xi1 ) ;
}
void SimulatorModel::setLens( Lens *l ) {
   lens = l ;
}

cv::Point2d SimulatorModel::getRelativeEta( cv::Point2d xi1 ) {
   // returns $\vec\eta''$
   cv::Point2d releta ;
   releta = getEta() - xi1/CHI ;
   return releta ;
}

cv::Point2d SimulatorModel::getOffset( cv::Point2d xi1 ) {
   cv::Point2d releta, eta, r ; 

   releta = xi1 - cv::Point2d( lens->psiXvalue( xi1.x, xi1.y ),
                       lens->psiYvalue( xi1.x, xi1.y ) ) ;
   eta = getEta() ;
   r = releta/CHI - eta ;

   if (DEBUG) {
     std::cout << "[getOffset] eta=" << eta << "; xi1=" << xi1
             << "; releta=" << releta 
             << "; return " << r << std::endl ;
   }

   // return is the difference between source point corresponding to the
   // reference point in the lens plane and the actual source centre
   return r ;
}

void SimulatorModel::updateApparentAbs( ) {
    cv::Mat im = getActual() ;
    cv::Point2d chieta = CHI*getEta() ;
    cv::Point2d xi1 = lens->getXi( chieta ) ;
    setNu( xi1/CHI ) ;
}

void SimulatorModel::setMaskRadius( double r ) {
   maskRadius = r ;
}
cv::Point2d SimulatorModel::getDistortedPos(double r, double theta) const { throw NotImplemented() ; }
