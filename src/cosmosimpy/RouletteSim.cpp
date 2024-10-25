/* (C) 2022-23: Hans Georg Schaathun <georg@schaathun.net> */

#include "CosmoSim.h"


namespace py = pybind11;

RouletteSim::RouletteSim() {
   std::cout << "RouletteSim Constructor\n" ;
}


void RouletteSim::diagnostics() {
   if ( src ) {
      cv::Mat im = src->getImage() ;
      std::cout << "Source Image " << im.rows << "x" << im.cols 
         << "x" << im.channels() << "\n" ;
   }
   if ( sim ) {
      cv::Mat im = sim->getDistorted() ;
      std::cout << "Distorted Image " << im.rows << "x" << im.cols 
         << "x" << im.channels() << "\n" ;
   }
   return ;
}

void RouletteSim::setNterms(int c) { nterms = c ; }
void RouletteSim::setMaskRadius(double c) { maskRadius = c ; }

void RouletteSim::setMaskMode(bool b) { maskmode = b ; }
void RouletteSim::initSim( RouletteRegenerator *rsim ) {
   std::cout << "[RouletteSim.cpp] initSim\n" ;
   sim = rsim ;

   return ;
}
void RouletteSim::setImageSize(int sz ) { size = sz ; }
void RouletteSim::setResolution(int sz ) { 
   basesize = sz ; 
   std::cout << "[setResolution] basesize=" << basesize << "; size=" << size << "\n" ;
}

bool RouletteSim::runSim() { 
   std::cout << "[RouletteSim.cpp] runSim() - running similator\n" << std::flush ;
   if ( NULL == sim )
	 throw std::logic_error( "Simulator not initialised" ) ;

   sim->setMaskRadius( maskRadius ) ;
   sim->setNterms( nterms ) ;
   sim->setMaskMode( maskmode ) ;
   
   std::cout << "[runSim] set parameters, ready to run\n" << std::flush ;
   Py_BEGIN_ALLOW_THREADS
   std::cout << "[runSim] thread section\n" << std::flush ;
   if ( sim == NULL )
      throw std::logic_error("Simulator not initialised") ;
   sim->update() ;
   Py_END_ALLOW_THREADS
   std::cout << "[RouletteSim.cpp] runSim() - complete\n" << std::flush ;
   return true ;
}
cv::Mat RouletteSim::getSource(bool refLinesMode) {
   if ( NULL == sim )
      throw std::bad_function_call() ;
   cv::Mat im = sim->getSource() ;
   if (refLinesMode) {
      im = im.clone() ;
      refLines(im) ;
   }
   return im ;
}
cv::Mat RouletteSim::getActual(bool refLinesMode) {
   if ( NULL == sim )
      throw std::bad_function_call() ;
   std::cout << "[RouletteSim] getActual()\n" ;
   cv::Mat im = sim->getActual() ;
   std::cout << "basesize=" << basesize << "; size=" << size << "\n" ;
   if ( basesize < size ) {
      cv::Mat ret(cv::Size(basesize, basesize), im.type(),
                  cv::Scalar::all(255));
      cv::resize(im,ret,cv::Size(basesize,basesize) ) ;
      im = ret ;
   } else {
      im = im.clone() ;
   }
   if (refLinesMode) {
      refLines(im) ;
   }
   return im ;
}
void RouletteSim::maskImage( double scale ) {
          sim->maskImage( scale ) ;
}
void RouletteSim::showMask() {
          sim->markMask() ;
}

cv::Mat RouletteSim::getDistorted(bool refLinesMode) {
   if ( NULL == sim )
      throw std::bad_function_call() ;
   cv::Mat im ;
   if ( basesize < size ) {
      std::cout << "basesize=" << basesize << "; size=" << size << "\n" ;
      im = sim->getDistorted() ;
      cv::Mat ret(cv::Size(basesize, basesize), sim->getActual().type(),
                  cv::Scalar::all(255));
      cv::resize(im,ret,cv::Size(basesize,basesize) ) ;
      im = ret ;
   } else {
      // It is necessary to clone because the distorted image is created
      // by cropping, and the pixmap is thus larger than the image,
      // causing subsequent conversion to a numpy array to be misaligned. 
      im = sim->getDistorted().clone() ;
   }
   if (refLinesMode) refLines(im) ;
   return im;
}

