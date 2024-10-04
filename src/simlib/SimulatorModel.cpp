/* (C) 2023: Hans Georg Schaathun <georg@schaathun.net> *
 * Building on code by Simon Ingebrigtsen, Sondre Westbø Remøy,
 * Einar Leite Austnes, and Simon Nedreberg Runde
 */

#include "cosmosim/Simulator.h"
#include "simaux.h"

#include <thread>

#undef DEBUG
#define DEBUG 1

SimulatorModel::SimulatorModel() :
        CHI(0.5),
        source(NULL)
{ }

SimulatorModel::~SimulatorModel() {
   delete source ;
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
   return source->getImage() ;
}
cv::Mat SimulatorModel::getApparent() const {
   return source->getImage() ;
}
cv::Mat SimulatorModel::getDistorted() const {
   return imgDistorted ;
}

void SimulatorModel::update( ) {
   updateApparentAbs() ;
   std::cout << "[SimulatorModel::update] Done updateApparentAbs()\n" ;
   return updateInner() ;
}
void SimulatorModel::update( cv::Point2d xi ) {
   setXi( xi ) ;
   std::cout << "[SimulatorModel::update] Done setXi()\n" ;
   return updateInner() ;
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

    imgDistorted = cv::Mat::zeros(imgApparent.size(), imgApparent.type()) ;
    parallelDistort(imgApparent, imgDistorted);

    // Calculate run time for this function and print diagnostic output
    auto endTime = std::chrono::system_clock::now();
    std::cout << "Time to update(): " 
              << std::chrono::duration_cast<std::chrono::milliseconds>(endTime - startTime).count() 
              << " milliseconds" << std::endl << std::flush ;

}


/* This just splits the image space in chunks and runs distort() in parallel */
void SimulatorModel::parallelDistort(const cv::Mat& src, cv::Mat& dst) {
    int n_threads = std::thread::hardware_concurrency();

    std::vector<std::thread> threads_vec;
    int lower=0, rng=dst.rows, rng1 ; 
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

void SimulatorModel::distort(int begin, int end, const cv::Mat& src, cv::Mat& dst) {
    // Iterate over the pixels in the image distorted image.
    // (row,col) are pixel co-ordinates
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

/** *** Setters *** */

/* B. Source model setter */
void SimulatorModel::setSource(Source *src) {
    if ( source != NULL ) delete source ;
    source = src ;
}

/* C. Lens Model setter */
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
   releta = eta - xi1/CHI ;
   return releta ;
}

cv::Point2d SimulatorModel::getOffset( cv::Point2d xi1 ) {
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

void SimulatorModel::updateApparentAbs( ) {
    std::cout << "[SimulatorModel::updateApparentAbs] 1\n" ;
    cv::Mat im = getActual() ;
    std::cout << "[SimulatorModel::updateApparentAbs] 2\n" ;
    cv::Point2d chieta = CHI*getEta() ;
    std::cout << "[SimulatorModel::updateApparentAbs] 3\n" ;
    cv::Point2d xi1 = lens->getXi( chieta ) ;
    std::cout << "[SimulatorModel::updateApparentAbs] 4\n" ;
    setNu( xi1/CHI ) ;
}

