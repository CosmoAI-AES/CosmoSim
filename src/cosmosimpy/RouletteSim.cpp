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
void RouletteSim::maskImage( double scale ) {
          sim->maskImage( scale ) ;
}
void RouletteSim::showMask() {
          sim->markMask() ;
}

