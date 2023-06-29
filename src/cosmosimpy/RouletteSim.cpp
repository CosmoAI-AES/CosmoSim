/* (C) 2022-23: Hans Georg Schaathun <georg@schaathun.net> */

#include "CosmoSim.h"


namespace py = pybind11;

RouletteSim::RouletteSim() {
   std::cout << "RouletteSim Constructor\n" ;
}


void RouletteSim::setCentre( double x, double y ) {
   centrepoint = cv::Point2d( x, y ) ;
}
void RouletteSim::setAlphaXi( int m, int s, double val ) {
      if ( NULL == lens )
	 throw std::logic_error( "Lens Model not initialised" ) ;
      return lens->setAlphaXi( m, s, val ) ;
}
void RouletteSim::setBetaXi( int m, int s, double val ) {
      if ( NULL == lens )
	 throw std::logic_error( "Lens Model not initialised" ) ;
      return lens->setBetaXi( m, s, val ) ;
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

void RouletteSim::setSourceMode(int m) { srcmode = m ; }
void RouletteSim::setMaskMode(bool b) { maskmode = b ; }
void RouletteSim::setBGColour(int b) { bgcolour = b ; }
void RouletteSim::initSim() {
   std::cout << "[RouletteSim.cpp] initSim\n" ;

   if ( sim ) delete sim ;
   if ( lens ) delete lens ;

   lens = new RouletteLens() ;

   std::cout << "Running Roulette Regenerator; "
                << "centrepoint=" << centrepoint << "\n" ;
   sim = new RouletteRegenerator() ;
   sim->setLens(lens) ;
   sim->setCentre( centrepoint ) ;

   return ;
}
void RouletteSim::setImageSize(int sz ) { size = sz ; }
void RouletteSim::setResolution(int sz ) { 
   basesize = sz ; 
   std::cout << "[setResolution] basesize=" << basesize << "; size=" << size << "\n" ;
}
void RouletteSim::setSourceParameters(double s1, double s2, double theta ) {
   sourceSize = s1 ;
   if ( s2 >= 0 ) sourceSize2 = s2 ;
   if ( theta >= 0 ) sourceTheta = theta ;
   // srcmode = mode ;
}
void RouletteSim::initSource( ) {
   std::cout << "[RouletteSim.cpp] initSource()\n" ;
   // Deleting the source object messes up the heap and causes
   // subsequent instantiation to fail.  This is probably because
   // the imgApparent (cv:;Mat) is not freed correctly.
   // if ( src ) delete src ;
   switch ( srcmode ) {
       case CSIM_SOURCE_SPHERE:
         src = new SphericalSource( size, sourceSize ) ;
         break ;
       case CSIM_SOURCE_ELLIPSE:
         src = new EllipsoidSource( size, sourceSize,
               sourceSize2, sourceTheta*PI/180 ) ;
         break ;
       case CSIM_SOURCE_TRIANGLE:
         src = new TriangleSource( size, sourceSize, sourceTheta*PI/180 ) ;
         break ;
       default:
         std::cout << "No such source mode!\n" ;
         throw NotImplemented();
    }
    if (sim) sim->setSource( src ) ;
    std::cout << "[RouletteSim.cpp] initSource() completes\n" ;
}
bool RouletteSim::runSim() { 
   if ( running ) {
      std::cout << "[RouletteSim.cpp] runSim() - simulator already running.\n" ;
      return false ;
   }
   std::cout << "[RouletteSim.cpp] runSim() - running similator\n" ;
   if ( NULL == sim )
	 throw std::logic_error( "Simulator not initialised" ) ;
   if ( NULL == lens )
	 throw std::logic_error( "Lens Model not initialised" ) ;
   initSource() ;
   sim->setBGColour( bgcolour ) ;
   sim->setNterms( nterms ) ;
   lens->setNterms( nterms ) ;
   sim->setMaskMode( maskmode ) ;
   
   std::cout << "[runSim] set parameters, ready to run\n" ;
   Py_BEGIN_ALLOW_THREADS
   std::cout << "[runSim] thread section\n" ;
   if ( sim == NULL )
      throw std::logic_error("Simulator not initialised") ;
   sim->update() ;
   Py_END_ALLOW_THREADS
   std::cout << "[RouletteSim.cpp] runSim() - complete\n" ;
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

