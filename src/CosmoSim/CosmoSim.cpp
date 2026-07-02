/* (C) 2022-26: Hans Georg Schaathun <georg@schaathun.net> */

#include "CosmoSim.h"

#include <pybind11/pybind11.h>
#include <opencv2/opencv.hpp>

#ifndef DEBUG
#define DEBUG 0
#endif

#include <thread>


CosmoSim::CosmoSim() {
   if (DEBUG) {
      std::cout << "CosmoSim Constructor\n" ;
      std::cout << "Number of CPU cores: " << std::thread::hardware_concurrency() << std::endl ; 
   }
   rPos = -1 ;
}
CosmoSim::~CosmoSim() {
   if (DEBUG) std::cout << "[CosmoSim] Destructor\n" ;
   if (this->sim != NULL) {
      delete this->sim ;
      this->sim = NULL ;
   }
   if (DEBUG>1) std::cout << "[CosmoSim] Destructor - destructed\n" ;
}


void CosmoSim::configLens() {
   // Set lens parameters
   if ( psilens != NULL  ) {
      if ( CSIM_PSI_CLUSTER != lensmode ) {
         psilens->setEinsteinR( einsteinR ) ;
         psilens->setRatio( ellipseratio ) ;
         psilens->setOrientation( orientation ) ;
      }
      if (DEBUG) std::cout << "[configLens] ready for initAlphasBetas\n" ;
      psilens->initAlphasBetas() ;
      if (DEBUG) std::cout << "[configLens] done initAlphasBetas\n" ;
   }

   if ( sampledlens ) {
     if (DEBUG) std::cout << "[CosmoSim.configLens] ready to sample lens\n" ;
     lens = new SampledPsiFunctionLens( psilens, size ) ;
     if (DEBUG) std::cout << "[CosmoSim.configLens] lens sampled\n" ;
     sim->setLens( lens ) ;
   } else {
     if (DEBUG) std::cout << "[CosmoSim.configLens] no sampling\n" ;
   }
}

void CosmoSim::setResolution(int sz ) { 
   basesize = sz ; 
}
bool CosmoSim::runSim() { 
   if (DEBUG) std::cout  << "[runSim] starting \n" ;

   // Configure the lens
   initLens() ;   // initLens() implements changing lens and model modes
   if ( sim == NULL ) {
      if (DEBUG) std::cout << "Simulator not initialised after initLens().\n" ;
      throw std::logic_error("Simulator not initialised") ;
   }
   configLens() ; // configLens() implements parameter changes

   // Set simulation parameters
   sim->setBGColour( bgcolour ) ;
   sim->setNterms( nterms ) ;
   sim->setMaskRadius( maskRadius ) ;
   sim->setMaskMode( maskmode ) ;

   // Set source position
   if ( rPos < 0 ) {
         sim->setXY( xPos, yPos ) ;
   } else {
         sim->setPolar( rPos, thetaPos ) ;
   }
   sim->setSource( src ) ;

   // run the actal simulator
   // Py_BEGIN_ALLOW_THREADS
   if (DEBUG) std::cout << "[runSim] thread section\n" ;
   if ( sim == NULL ) {
      if (DEBUG) std::cout << "Simulator not initialised in thread section.\n" ;
      throw std::logic_error("Simulator not initialised") ;
   }
   sim->update() ;
   // Py_END_ALLOW_THREADS

   if (DEBUG) std::cout << "[runSim] completes\n" ;
   return true ;
}

cv::Mat CosmoSim::getDistorted(bool refLinesMode, bool criticalCurvesMode ) {
   if ( NULL == sim )
      throw std::bad_function_call() ;
   cv::Mat im ;
   im = sim->getDistorted() ;
   if (criticalCurvesMode) sim->drawCritical() ;
   if ( basesize < size ) {
      cv::Mat ret(cv::Size(basesize, basesize), sim->getActual().type(),
                  cv::Scalar::all(255));
      cv::resize(im,ret,cv::Size(basesize,basesize) ) ;
      im = ret ;
   } else {
      // It is necessary to clone because the distorted image is created
      // by cropping, and the pixmap is thus larger than the image,
      // causing subsequent conversion to a numpy array to be misaligned. 
      im = im.clone() ;
   }
   if (refLinesMode) refLines(im) ;
   return im;
}

