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
   std::cout << "[SimulatorModel::update] start\n" ;
   updateApparentAbs() ;
   std::cout << "[SimulatorModel::update] Done updateApparentAbs()\n" ;
   cv::Mat imgApparent = getApparent() ;
   imgDistorted = cv::Mat::zeros(imgApparent.size(), imgApparent.type()) ;
   parallelDistort(imgApparent, imgDistorted);
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
}

/** *** Setters *** */

/* B. Source model setter */
void SimulatorModel::setSource(SphericalSource *src) {
    if ( source != NULL ) delete source ;
    source = src ;
}

/* D. Position (eta) setters */

/* Set the actual positions in the source plane using Cartesian Coordinates */
void SimulatorModel::setXY( double X, double Y ) {
    eta = cv::Point2d( X, Y ) ;
}


/* Set the actual positions in the source plane using Polar Coordinates */
void SimulatorModel::setPolar( double R, double theta ) {
    double phi = PI*theta/180 ;
    eta = cv::Point2d( R*cos(phi), R*sin(phi) ) ;
}

/* Getters */
cv::Point2d SimulatorModel::getNu() const { 
   return nu ;
}
double SimulatorModel::getNuAbs() const { 
   return sqrt( nu.x*nu.x + nu.y*nu.y ) ;
}
cv::Point2d SimulatorModel::getEta() const {
   return eta ;
}
double SimulatorModel::getEtaAbs() const {
   return sqrt( eta.x*eta.x + eta.y*eta.y ) ;
}
void SimulatorModel::setNu( cv::Point2d n ) {
   nu = n ;
}
void SimulatorModel::setLens( ClusterLens *l ) {
   lens = l ;
}

void SimulatorModel::updateApparentAbs( ) {
    std::cout << "[SimulatorModel::updateApparentAbs] 1\n" ;
    cv::Mat im = getActual() ;
    std::cout << "[SimulatorModel::updateApparentAbs] 2\n" ;
    cv::Point2d chieta = CHI*getEta() ;
    std::cout << "[SimulatorModel::updateApparentAbs] 3\n" ;
    lens->addLens( new SIS(), 0, 0 ) ;
    std::cout << "[SimulatorModel::updateApparentAbs] 4\n" ;
    cv::Point2d xi1 = lens->getXi( chieta ) ;
    std::cout << "[SimulatorModel::updateApparentAbs] 5\n" ;
    setNu( xi1/CHI ) ;
}

