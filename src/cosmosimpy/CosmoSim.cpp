/* (C) 2022-23: Hans Georg Schaathun <georg@schaathun.net> */


#include "CosmoSim.h"

#include <pybind11/pybind11.h>
#include <opencv2/opencv.hpp>

#ifndef DEBUG
#define DEBUG 0
#endif

#include <thread>


CosmoSim::CosmoSim() {
   std::cout << "CosmoSim Constructor\n" ;
   std::cout << "Number of CPU cores: " << std::thread::hardware_concurrency() << std::endl ; 
   rPos = -1 ;
}


PsiFunctionLens *CosmoSim::getLens( int lensmode ) { 
   switch ( lensmode ) {
      case CSIM_PSI_SIE:
         return new SIE() ;
      case CSIM_PSI_SIS:
         return new SIS() ;
      case CSIM_PSI_CLUSTER:
         return new ClusterLens() ;
      default:
         throw NotImplemented() ;
   }
} ;

double CosmoSim::getChi( ) { return chi ; } ;
cv::Point2d CosmoSim::getRelativeEta( double x, double y ) {
   // Input (x,y) is the centre point $\nu$
   cv::Point2d pt = sim->getRelativeEta( cv::Point2d( x,y )*chi ) ; 
   if (DEBUG) std::cout << "[CosmoSim::getRelativeEta] " << pt << "\n" ;
   return pt ;
} ;
cv::Point2d CosmoSim::getOffset( double x, double y ) {
   // Input (x,y) is the centre point $\nu$ 
   cv::Point2d pt = sim->getOffset( cv::Point2d( x,y )*chi ) ; 
   if (DEBUG) std::cout << "[CosmoSim::getOffset] " << pt << "\n" ;
   return pt ;
} ;
cv::Point2d CosmoSim::getNu( ) {
   return sim->getNu() ;
} ;

double CosmoSim::getAlphaXi( int m, int s ) {

   // cv::Point2d xi = lens->getXi( sim->getEta() ) ;
   cv::Point2d xi = sim->getXi() ;
   if (DEBUG) std::cout << "[getAlphaXi] xi = " << xi << std::endl ;
   xi /= chi ;
   return getAlpha( xi.x, xi.y, m, s ) ;

}
double CosmoSim::getBetaXi( int m, int s ) {
   // cv::Point2d xi = lens->getXi( sim->getEta() ) ;
   cv::Point2d xi = sim->getXi( ) ;
   if (DEBUG) std::cout << "[getBetaXi] xi = " << xi << std::endl ;
   xi /= chi ;
   return getBeta( xi.x, xi.y, m, s ) ;
}
double CosmoSim::getAlpha(
      double x, double y, int m, int s 
 ) {
      double r ;
      cv::Point2d xi = cv::Point2d( x, y )*chi ;
      if ( NULL != psilens )
          r = psilens->getAlpha( xi, m, s ) ;
      else if ( NULL != lens )
          r = lens->getAlpha( xi, m, s ) ;
      else throw NotSupported();
      return r ;
}
double CosmoSim::getBeta( 
      double x, double y, int m, int s 
) {
      double r ;
      cv::Point2d xi = cv::Point2d( x, y )*chi ;
      if ( NULL != psilens )
          r = psilens->getBeta( xi, m, s ) ;
      else if ( NULL != lens )
          r = lens->getBeta( xi, m, s ) ;
      else throw NotSupported();
      return r ;
}

void CosmoSim::diagnostics() {
   if ( src ) {
      cv::Mat im = src->getImage() ;
      if (DEBUG) std::cout << "Source Image " << im.rows << "x" << im.cols 
         << "x" << im.channels() << "\n" ;
   }
   if ( sim ) {
      cv::Mat im = sim->getDistorted() ;
      if (DEBUG) std::cout << "Distorted Image " << im.rows << "x" << im.cols 
         << "x" << im.channels() << "\n" ;
   }
   return ;
}

void CosmoSim::setFile( int key, std::string fn ) {
    filename[key] = fn ;
} 
std::string CosmoSim::getFile( int key ) {
    return filename[key] ;
} 

void CosmoSim::setCHI(double c) { chi = c/100.0 ; }
void CosmoSim::setNterms(int c) { nterms = c ; }
void CosmoSim::setMaskRadius(double c) { maskRadius = c ; }
void CosmoSim::setXY( double x, double y) { xPos = x ; yPos = y ; rPos = -1 ; }
void CosmoSim::setPolar(int r, int theta) { rPos = r ; thetaPos = theta ; }
void CosmoSim::setModelMode(int m) { 
   if ( modelmode != m ) {
      if (DEBUG) std::cout << "[CosmoSim.cpp] setModelMode(" << modelmode 
         << " -> " << m << ")\n" ;
      modelmode = m ; 
      modelchanged = 1 ;
   }
}
void CosmoSim::setLensMode(int m) { 
   if ( lensmode != m ) {
      std::cout << "[CosmoSim.cpp] setLensMode(" << lensmode 
         << " -> " << m << ")\n" ;
      lensmode = m ; 
      modelchanged = 1 ;
   } else {
      std::cout << "[CosmoSim.cpp] setLensMode(" << lensmode << ") unchanged\n" ;
   }
}
void CosmoSim::setLens(PsiFunctionLens *l) { 
   std::cout << "[CosmoSim::setLens]\n" ;
   lensmode = CSIM_PSI_CLUSTER ; 
   modelchanged = 1 ;
   lens = psilens = l ;
   std::cout << "[CosmoSim::setLens] returning\n" ;
}
void CosmoSim::setSampled(int m) { 
   if ( sampledlens != m ) {
      std::cout << "[CosmoSim.cpp] setSampled(" << m << " -> " << m << ")\n" ;
      sampledlens = m ; 
      modelchanged = 1 ;
   }
}
void CosmoSim::setMaskMode(bool b) { maskmode = b ; }
void CosmoSim::setBGColour(int b) { bgcolour = b ; }
void CosmoSim::initLens() {
   if (DEBUG) std::cout << "[initLens] ellipseratio = " << ellipseratio << "\n" ;
   if ( ! modelchanged ) return ;
   if ( sim ) {
      std::cout << "[initLens] delete sim\n" ;
      delete sim ;
   }
   std::cout << "switch( lensmode )\n" ;
   switch ( lensmode ) {
       case CSIM_PSI_CLUSTER:
          std::cout << "[initLens] ClusterLens - no further init\n" ;
          break ;
       case CSIM_PSI_SIE:
          lens = psilens = new SIE() ;
          psilens->setFile(filename[CSIM_PSI_SIE]) ;
          break ;
       case CSIM_PSI_SIS:
          lens = psilens = new SIS() ;
          psilens->setFile(filename[CSIM_PSI_SIS]) ;
          break ;
       case CSIM_NOPSI_PM:
          lens = psilens = new PointMass() ;
          std::cout << "CSIM_NOPSI_PM\n" ;
          break ;
       case CSIM_NOPSI:
          if (DEBUG) std::cout << "[initLens] Point Mass or No Lens (" 
                << lensmode << ")\n" ;
          lens = psilens = NULL ;
          break ;
       default:
         std::cerr << "No such lens model!\n" ;
         throw NotImplemented();
   }
   std::cout << "[initLens] instantiated lens\n" ;

   std::cout << "switch( modelmode )\n" ;
   switch ( modelmode ) {
       case CSIM_MODEL_POINTMASS_ROULETTE:
         if (DEBUG) std::cout << "Running Roulette Point Mass Lens (mode=" 
                   << modelmode << ")\n" ;
         sim = new PointMassRoulette( psilens ) ;
         std::cout << "CSIM_MODEL_POINTMASS_ROULETTE\n" ;
         break ;
       case CSIM_MODEL_POINTMASS_EXACT:
         if (DEBUG) std::cout << "Running Point Mass Lens (mode=" << modelmode << ")\n" ;
         sim = new PointMassExact( psilens ) ;
         std::cout << "CSIM_MODEL_POINTMASS_EXACT\n" ;
         break ;
       case CSIM_MODEL_RAYTRACE:
         if (DEBUG) std::cout << "Running Raytrace Lens (mode=" << modelmode << ")\n" ;
         sim = new RaytraceModel() ;
         sim->setLens(lens) ;
         break ;
       case CSIM_MODEL_ROULETTE:
         if (DEBUG) std::cout << "Running Roulette Lens (mode=" << modelmode << ")\n" ;
         sim = new RouletteModel() ;
         sim->setLens(lens) ;
         break ;
       case CSIM_NOMODEL:
         std::cerr << "Specified No Model.\n" ;
         throw NotImplemented();
       default:
         std::cerr << "No such lens mode!\n" ;
         throw NotImplemented();
    }
    modelchanged = 0 ;
    std::cout  << "[initLens] returning \n" ;
    return ;
}

void CosmoSim::configLens() {
   // Set lens parameters
   if ( psilens != NULL  ) {
      if ( CSIM_PSI_CLUSTER != lensmode ) {
         psilens->setEinsteinR( einsteinR ) ;
         psilens->setRatio( ellipseratio ) ;
         psilens->setOrientation( orientation ) ;
      }
      if (DEBUG) std::cout << "[runSim] ready for initAlphasBetas\n" ;
      psilens->initAlphasBetas() ;
      if (DEBUG) std::cout << "[runSim] done initAlphasBetas\n" ;
   }

   std::cout << "[initLens] ready to sample lens\n" ;
   if ( sampledlens ) {
     lens = new SampledPsiFunctionLens( psilens ) ;
     std::cout << "[initLens] lens sampled\n" ;
     sim->setLens( lens ) ;
   }
}
void CosmoSim::setEinsteinR(double r) { einsteinR = r ; }
void CosmoSim::setRatio(double r) { 
   ellipseratio = r ; 
}
void CosmoSim::setOrientation(double r) { orientation = r ; }
void CosmoSim::setImageSize(int sz ) { size = sz ; }
int CosmoSim::getImageSize() { return size ; }
void CosmoSim::setResolution(int sz ) { 
   basesize = sz ; 
}
int CosmoSim::setSource( Source *src ) {
    std::cout  << "[setSource]\n" ;
    srcmode = CSIM_SOURCE_EXTERN ;
    this->src = src ;
    return 1 ; 
}
bool CosmoSim::runSim() { 
   std::cout  << "[runSim] starting \n" ;

   // Configure the lens
   initLens() ;   // initLens() implements changing lens and model modes
   if ( sim == NULL ) {
      std::cout << "Simulator not initialised after initLens().\n" ;
      throw std::logic_error("Simulator not initialised") ;
   }
   configLens() ; // configLens() implements parameter changes

   // Set simulation parameters
   sim->setCHI( chi ) ;
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
      std::cout << "Simulator not initialised in thread section.\n" ;
      throw std::logic_error("Simulator not initialised") ;
   }
   sim->update() ;
   // Py_END_ALLOW_THREADS

   std::cout << "[runSim] completes\n" ;
   return true ;
}
bool CosmoSim::moveSim( double rot, double scale ) { 
   cv::Point2d xi = sim->getTrueXi(), xi1 ;
   xi1 = cv::Point2d( 
           xi.x*cos(rot) - xi.y*sin(rot),
           xi.x*sin(rot) + xi.y*cos(rot)
         );
   xi1 *= scale ;
   Py_BEGIN_ALLOW_THREADS
   if ( sim == NULL )
      throw std::logic_error("Simulator not initialised") ;
   sim->update( xi1 ) ;
   Py_END_ALLOW_THREADS
   return true ;
}
cv::Mat CosmoSim::getSource(bool refLinesMode) {
   if ( NULL == sim )
      throw std::bad_function_call() ;
   cv::Mat im = sim->getSource() ;
   if (refLinesMode) {
      im = im.clone() ;
      refLines(im) ;
   }
   return im ;
}
cv::Mat CosmoSim::getActual(bool refLinesMode, bool causticMode) {
   if ( NULL == sim )
      throw std::bad_function_call() ;
   cv::Mat im = sim->getActual() ;
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
   if (causticMode) {
      sim->drawCaustics( im ) ;
      /*
      cv::Mat caus = sim->getCaustic( ) ;
      cv::Mat im2 ;
      cv::addWeighted(im,1,caus,1,0,im2) ;
      im = im2 ;
      */
   }
   return im ;
}
void CosmoSim::maskImage( double scale ) {
          sim->maskImage( scale ) ;
}
void CosmoSim::showMask() {
          sim->markMask() ;
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

