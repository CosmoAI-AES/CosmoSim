/* (C) 2022-23: Hans Georg Schaathun <georg@schaathun.net> */

#include "CosmoSim.h"

#include <pybind11/pybind11.h>
#include <opencv2/opencv.hpp>

#ifndef DEBUG
#define DEBUG 0
#endif

namespace py = pybind11;

LensWrapper::LensWrapper() {
   if (DEBUG) std::cout << "LensWrapper Constructor\n" ;
   rPos = -1 ;
}


double LensWrapper::getChi( ) { return chi ; } ;

double LensWrapper::getAlphaXi( int m, int s ) {

   // cv::Point2d xi = lens->getXi( sim->getEta() ) ;
   cv::Point2d xi = sim->getXi() ;
   if (DEBUG) std::cout << "[getAlphaXi] xi = " << xi << std::endl ;
   xi /= chi ;
   return getAlpha( xi.x, xi.y, m, s ) ;

}
double LensWrapper::getBetaXi( int m, int s ) {
   // cv::Point2d xi = lens->getXi( sim->getEta() ) ;
   cv::Point2d xi = sim->getXi( ) ;
   if (DEBUG) std::cout << "[getBetaXi] xi = " << xi << std::endl ;
   xi /= chi ;
   return getBeta( xi.x, xi.y, m, s ) ;
}
double LensWrapper::getAlpha(
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
 double LensWrapper::getBeta( 
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

void LensWrapper::diagnostics() {
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

void LensWrapper::setFile( int key, std::string fn ) {
    filename[key] = fn ;
} 

cv::Mat LensWrapper::getPsiMap( ) {
   cv::Mat im = lens->getPsi() ;
   return im ;
} 
cv::Mat LensWrapper::getMassMap( ) {
   throw NotImplemented();
   // cv::Mat im = lens->getMassMap() ;
   // return im ;
} 

void LensWrapper::setNterms(int c) { nterms = c ; }

void LensWrapper::setLensMode(int m) { 
   if ( lensmode != m ) {
       if (DEBUG) std::cout << "[LensWrapper.cpp] setLensMode(" << lensmode 
         << " -> " << m << ")\n" ;
      lensmode = m ; 
      modelchanged = 1 ;
   } else {
       if (DEBUG) std::cout << "[LensWrapper.cpp] setLensMode(" << lensmode << ") unchanged\n" ;
   }
}
void LensWrapper::setSampled(int m) { 
   if ( sampledlens != m ) {
       if (DEBUG) std::cout << "[LensWrapper.cpp] setSampled(" << m 
         << " -> " << m << ")\n" ;
      sampledlens = m ; 
      modelchanged = 1 ;
   }
}
void LensWrapper::initLens() {
   if (DEBUG) std::cout << "[initLens] ellipseratio = " << ellipseratio << "\n" ;
   if ( ! modelchanged ) return ;
   if ( sim ) delete sim ;
   psilens = NULL ;
   switch ( lensmode ) {
       case CSIM_PSI_SIE:
          lens = psilens = new SIE() ;
          lens->setFile(filename[CSIM_PSI_SIE]) ;
          break ;
       case CSIM_PSI_SIS:
          lens = psilens = new SIS() ;
          lens->setFile(filename[CSIM_PSI_SIS]) ;
          break ;
       case CSIM_NOPSI_PM:
          lens = psilens = new PointMass() ;
          break ;
       case CSIM_NOPSI:
          if (DEBUG) std::cout << "[initLens] Point Mass or No Lens (" 
                << lensmode << ")\n" ;
          lens = NULL ;
          break ;
       default:
         std::cerr << "No such lens model!\n" ;
         throw NotImplemented();
   }
   if ( sampledlens ) {
     lens = new SampledPsiFunctionLens( psilens ) ;
     lens->setFile(filename[lensmode]) ;
   }
   switch ( modelmode ) {
       case CSIM_MODEL_POINTMASS_ROULETTE:
         if (DEBUG) std::cout << "Running Roulette Point Mass Lens (mode=" 
                   << modelmode << ")\n" ;
         sim = new PointMassRoulette() ;
         sim->setLens(lens) ;
         break ;
       case CSIM_MODEL_POINTMASS_EXACT:
         if (DEBUG) std::cout << "Running Point Mass Lens (mode=" << modelmode << ")\n" ;
         sim = new PointMassExact() ;
         sim->setLens(lens) ;
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
    return ;
}

void LensWrapper::setImageSize(int sz ) { size = sz ; }
void LensWrapper::setResolution(int sz ) { 
   basesize = sz ; 
}

void LensWrapper::initSource( ) {
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
       case CSIM_SOURCE_IMAGE:
         src = new ImageSource( size, sourcefile ) ;
         break ;
       case CSIM_SOURCE_TRIANGLE:
         src = new TriangleSource( size, sourceSize, sourceTheta*PI/180 ) ;
         break ;
       default:
         std::cerr << "No such source mode!\n" ;
         throw NotImplemented();
    }
    if (sim) sim->setSource( src ) ;
}
bool LensWrapper::runSim() { 
   if ( running ) {
      return false ;
   }
   initLens() ;
   if ( sim == NULL ) {
      throw std::bad_function_call() ;
   }
   initSource() ;
   sim->setBGColour( bgcolour ) ;
   sim->setNterms( nterms ) ;
   sim->setMaskRadius( maskRadius ) ;
   if ( lens != NULL ) lens->setNterms( nterms ) ;
   sim->setMaskMode( maskmode ) ;
   if ( CSIM_NOPSI_ROULETTE != lensmode ) {
      sim->setCHI( chi ) ;
      if ( rPos < 0 ) {
         sim->setXY( xPos, yPos ) ;
      } else {
         sim->setPolar( rPos, thetaPos ) ;
      }
      if ( lens != NULL ) {
         lens->setEinsteinR( einsteinR ) ;
         lens->setRatio( ellipseratio ) ;
         lens->setOrientation( orientation ) ;
         lens->initAlphasBetas() ;
      }
   }
   Py_BEGIN_ALLOW_THREADS
   if (DEBUG) std::cout << "[runSim] thread section\n" ;
   if ( sim == NULL ) throw std::logic_error("Simulator not initialised") ;
   sim->update() ;
   if (DEBUG) std::cout << "[LensWrapper.cpp] end of thread section\n" ;
   Py_END_ALLOW_THREADS
   return true ;
}
bool LensWrapper::moveSim( double rot, double scale ) { 
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

PYBIND11_MODULE(CosmoSimPy, m) {
    m.doc() = "Wrapper for the CosmoSim simulator" ;

    py::class_<LensWrapper>(m, "LensWrapper")
        .def(py::init<>())
        .def("setLensMode", &LensWrapper::setLensMode)
        .def("setModelMode", &LensWrapper::setModelMode)
        .def("setSampled", &LensWrapper::setSampled)
        .def("setSourceMode", &LensWrapper::setSourceMode)
        .def("setEinsteinR", &LensWrapper::setEinsteinR)
        .def("setRatio", &LensWrapper::setRatio)
        .def("setOrientation", &LensWrapper::setOrientation)
        .def("setNterms", &LensWrapper::setNterms)
        .def("setMaskRadius", &LensWrapper::setMaskRadius)
        .def("setCHI", &LensWrapper::setCHI)
        .def("setSourceParameters", &LensWrapper::setSourceParameters)
        .def("setXY", &LensWrapper::setXY)
        .def("setPolar", &LensWrapper::setPolar)
        .def("getActual", &LensWrapper::getActual)
        .def("getApparent", &LensWrapper::getSource)
        .def("getDistorted", &LensWrapper::getDistorted)
        .def("runSim", &LensWrapper::runSim)
        .def("moveSim", &LensWrapper::moveSim)
        .def("diagnostics", &LensWrapper::diagnostics)
        .def("maskImage", &LensWrapper::maskImage)
        .def("showMask", &LensWrapper::showMask)
        .def("setMaskMode", &LensWrapper::setMaskMode)
        .def("setImageSize", &LensWrapper::setImageSize)
        .def("setResolution", &LensWrapper::setResolution)
        .def("setBGColour", &LensWrapper::setBGColour)
        .def("setFile", &LensWrapper::setFile)
        .def("setSourceFile", &LensWrapper::setSourceFile)
        .def("getPsiMap", &LensWrapper::getPsiMap)
        .def("getMassMap", &LensWrapper::getMassMap)
        .def("getAlpha", &LensWrapper::getAlpha)
        .def("getBeta", &LensWrapper::getBeta)
        .def("getAlphaXi", &LensWrapper::getAlphaXi)
        .def("getBetaXi", &LensWrapper::getBetaXi)
        .def("getChi", &LensWrapper::getChi)
        .def("getOffset", &LensWrapper::getOffset)
        .def("getNu", &LensWrapper::getNu)
        .def("getRelativeEta", &LensWrapper::getRelativeEta)
        ;


}
