/* (C) 2022-23: Hans Georg Schaathun <georg@schaathun.net> */


#include "CosmoSim.h"

#include <pybind11/pybind11.h>
#include <opencv2/opencv.hpp>

#undef DEBUG
#ifndef DEBUG
#define DEBUG 1
#endif

#include <thread>

namespace py = pybind11;

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

      if ( NULL != psilens )
          return psilens->getAlphaXi( m, s ) ;
      else if ( NULL != lens )
          return lens->getAlphaXi( m, s ) ;
      else throw NotSupported();
}
double CosmoSim::getBetaXi( int m, int s ) {
   // cv::Point2d xi = lens->getXi( sim->getEta() ) ;
   cv::Point2d xi = sim->getXi( ) ;
   if (DEBUG) std::cout << "[getBetaXi] xi = " << xi << std::endl ;
   xi /= chi ;
   return getBeta( xi.x, xi.y, m, s ) ;
      if ( NULL != psilens )
          return psilens->getBetaXi( m, s ) ;
      else if ( NULL != lens )
          return lens->getBetaXi( m, s ) ;
      else throw NotSupported();
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
      // sim = NULL ;
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
   if ( sampledlens ) {
     lens = new SampledPsiFunctionLens( psilens ) ;
     psilens->setFile(filename[lensmode]) ;
   }
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
void CosmoSim::initSource( ) {
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
       case CSIM_SOURCE_EXTERN:
         std::cerr << "Externally defined source!\n" ;
         break ;
       default:
         std::cerr << "No such source mode!\n" ;
         throw NotImplemented();
    }
    if (sim) {
       std::cout  << "[initSource] setting source (" << (NULL==sim) << ")\n" ;
       cv::Mat im = sim->getDistorted() ;
       std::cout  << "[initSource] setting source (" << (NULL==sim) << ")\n" ;
       sim->setSource( src ) ;
    } else {
       std::cout  << "[initSource] no simulator\n" ;
    }
}
int CosmoSim::setSource( Source *src ) {
    std::cout  << "[setSource]\n" ;
    srcmode = CSIM_SOURCE_EXTERN ;
    this->src = src ;
    /*
    if (sim) {
       std::cout  << "[setSource] setting source\n" ;
       sim->setSource( src ) ;
       return 1 ; 
    } else {
       std::cout  << "[setSource] no simulator\n" ;
       return 0 ;
    }
    */
    return 1 ; 
}
bool CosmoSim::runSim() { 
   std::cout  << "[runLens] starting \n" ;
   if ( running ) {
      return false ;
   }
   std::cout << "[runSim]\n" ;
   initLens() ;
   if ( sim == NULL ) {
      throw std::bad_function_call() ;
   }
   initSource() ;
   sim->setBGColour( bgcolour ) ;
   sim->setNterms( nterms ) ;
   sim->setMaskRadius( maskRadius ) ;
   std::cout << "[runSim] initialised\n" ;
   sim->setMaskMode( maskmode ) ;
   std::cout << "[runSim] " << CSIM_PSI_CLUSTER << " - " << CSIM_MODEL_ROULETTE << "\n" ; 
   std::cout << "[runSim] " << lensmode << " - " << modelmode << 
      " (" << (psilens == NULL) << ")\n" ; 
   if ( CSIM_NOPSI_ROULETTE != lensmode ) {
      sim->setCHI( chi ) ;
      if ( rPos < 0 ) {
         sim->setXY( xPos, yPos ) ;
      } else {
         sim->setPolar( rPos, thetaPos ) ;
      }
      if ( psilens != NULL && CSIM_PSI_CLUSTER != lensmode ) {
         psilens->setEinsteinR( einsteinR ) ;
         psilens->setRatio( ellipseratio ) ;
         psilens->setOrientation( orientation ) ;
      }
      if ( psilens != NULL ) {
         std::cout << "[runSim] ready for initAlphasBetas\n" ;
         psilens->initAlphasBetas() ;
         std::cout << "[runSim] done initAlphasBetas\n" ;
      }
   }
   Py_BEGIN_ALLOW_THREADS
   if (DEBUG) std::cout << "[runSim] thread section\n" ;
   if ( sim == NULL ) {
      std::cout << "Simulator not initialised\n" ;
      throw std::logic_error("Simulator not initialised") ;
   }
   sim->update() ;
   if (DEBUG) std::cout << "[CosmoSim.cpp] end of thread section\n" ;
   Py_END_ALLOW_THREADS
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

PYBIND11_MODULE(CosmoSimPy, m) {
    m.doc() = "Wrapper for the CosmoSim simulator" ;

    py::class_<CosmoSim>(m, "CosmoSim")
        .def(py::init<>())
        .def("getLens", &CosmoSim::getLens)
        .def("setLensMode", &CosmoSim::setLensMode)
        .def("setModelMode", &CosmoSim::setModelMode)
        .def("setSampled", &CosmoSim::setSampled)
        .def("setEinsteinR", &CosmoSim::setEinsteinR)
        .def("setRatio", &CosmoSim::setRatio)
        .def("setOrientation", &CosmoSim::setOrientation)
        .def("setNterms", &CosmoSim::setNterms)
        .def("setMaskRadius", &CosmoSim::setMaskRadius)
        .def("setCHI", &CosmoSim::setCHI)
        .def("setXY", &CosmoSim::setXY)
        .def("setPolar", &CosmoSim::setPolar)
        .def("getActual", &CosmoSim::getActual)
        .def("getApparent", &CosmoSim::getSource)
        .def("getDistorted", &CosmoSim::getDistorted)
        .def("runSim", &CosmoSim::runSim)
        .def("moveSim", &CosmoSim::moveSim)
        .def("diagnostics", &CosmoSim::diagnostics)
        .def("maskImage", &CosmoSim::maskImage)
        .def("showMask", &CosmoSim::showMask)
        .def("setMaskMode", &CosmoSim::setMaskMode)
        .def("setImageSize", &CosmoSim::setImageSize)
        .def("getImageSize", &CosmoSim::getImageSize)
        .def("setResolution", &CosmoSim::setResolution)
        .def("setBGColour", &CosmoSim::setBGColour)
        .def("setFile", &CosmoSim::setFile)
        .def("getFile", &CosmoSim::getFile)
        .def("setSource", &CosmoSim::setSource)
        .def("getAlpha", &CosmoSim::getAlpha)
        .def("getBeta", &CosmoSim::getBeta)
        .def("getAlphaXi", &CosmoSim::getAlphaXi)
        .def("getBetaXi", &CosmoSim::getBetaXi)
        .def("getChi", &CosmoSim::getChi)
        .def("getOffset", &CosmoSim::getOffset)
        .def("getNu", &CosmoSim::getNu)
        .def("getRelativeEta", &CosmoSim::getRelativeEta)
        .def("setLens", &CosmoSim::setLens)
        ;

    py::class_<Source>(m, "Source")
        .def(py::init<int>())
        .def("getImage", &Source::getImage)
        ;
    py::class_<SphericalSource,Source>(m, "SphericalSource")
        .def(py::init<int,double>())
        ;
    py::class_<EllipsoidSource,Source>(m, "EllipsoidSource")
        .def(py::init<int,double,double,double>())
        ;
    py::class_<SourceConstellation,Source>(m, "SourceConstellation")
        .def(py::init<int>())
        .def("addSource", &SourceConstellation::addSource)
        ;
    py::class_<TriangleSource,Source>(m, "TriangleSource")
        .def(py::init<int,double,double>())
        ;
    py::class_<ImageSource,Source>(m, "ImageSource")
        .def(py::init<int,std::string>())
        ;
    py::class_<Lens>(m, "Lens")
        .def(py::init<>())
        .def("calculateAlphaBeta", &Lens::calculateAlphaBeta)
        .def("getAlphaXi", &Lens::getAlphaXi)
        .def("getBetaXi", &Lens::getBetaXi)
        .def("getAlpha", &Lens::getAlpha)
        .def("getBeta", &Lens::getBeta)
        .def("getXi", &Lens::getXi)
        .def("psiValue", &Lens::psiValue)
        .def("psiXvalue", &Lens::psiXvalue)
        .def("psiYvalue", &Lens::psiYvalue)
        .def("criticalXi", &Lens::criticalXi)
        .def("caustic", &Lens::caustic)
        ;
    py::class_<PsiFunctionLens,Lens>(m, "PsiFunctionLens")
        .def(py::init<>())
        .def("calculateAlphaBeta", &PsiFunctionLens::calculateAlphaBeta)
        .def("getAlphaXi", &PsiFunctionLens::getAlphaXi)
        .def("getBetaXi", &PsiFunctionLens::getBetaXi)
        .def("getAlpha", &PsiFunctionLens::getAlpha)
        .def("getBeta", &PsiFunctionLens::getBeta)
        .def("setEinsteinR", &PsiFunctionLens::setEinsteinR)
        .def("setOrientation", &SIE::setOrientation)
        .def("setRatio", &SIE::setRatio)
        .def("setFile", &PsiFunctionLens::setFile)
        ;
    py::class_<SIS,PsiFunctionLens>(m, "SIS")
        .def(py::init<>())
        .def("psiValue", &SIS::psiValue)
        .def("psiXvalue", &SIS::psiXvalue)
        .def("psiYvalue", &SIS::psiYvalue)
        .def("getXi", &ClusterLens::getXi)
        ;
    py::class_<SIE,PsiFunctionLens>(m, "SIE")
        .def(py::init<>())
        .def("psiValue", &SIE::psiValue)
        .def("psiXvalue", &SIE::psiXvalue)
        .def("psiYvalue", &SIE::psiYvalue)
        .def("getXi", &ClusterLens::getXi)
        ;
    py::class_<PointMass,PsiFunctionLens>(m, "PointMass")
        .def(py::init<>())
        .def("psiValue", &PointMass::psiValue)
        .def("psiXvalue", &PointMass::psiXvalue)
        .def("psiYvalue", &PointMass::psiYvalue)
        .def("getXi", &PointMass::getXi)
        ;
    py::class_<ClusterLens,PsiFunctionLens>(m, "ClusterLens")
        .def(py::init<>())
        .def("addLens", &ClusterLens::addLens)
        .def("calculateAlphaBeta", &ClusterLens::calculateAlphaBeta)
        .def("psiValue", &ClusterLens::psiValue)
        .def("psiXvalue", &ClusterLens::psiXvalue)
        .def("psiYvalue", &ClusterLens::psiYvalue)
        ;

    py::class_<RouletteSim>(m, "RouletteSim")
        .def(py::init<>())
        .def("setSourceMode", &RouletteSim::setSourceMode)
        .def("setNterms", &RouletteSim::setNterms)
        .def("setMaskRadius", &RouletteSim::setMaskRadius)
        .def("setSourceParameters", &RouletteSim::setSourceParameters)
        .def("getActual", &RouletteSim::getActual)
        .def("getApparent", &RouletteSim::getSource)
        .def("getDistorted", &RouletteSim::getDistorted)
        .def("runSim", &RouletteSim::runSim)
        .def("initSim", &RouletteSim::initSim)
        .def("diagnostics", &RouletteSim::diagnostics)
        .def("maskImage", &RouletteSim::maskImage)
        .def("showMask", &RouletteSim::showMask)
        .def("setMaskMode", &RouletteSim::setMaskMode)
        .def("setImageSize", &RouletteSim::setImageSize)
        .def("setResolution", &RouletteSim::setResolution)
        .def("setBGColour", &RouletteSim::setBGColour)
        .def("setAlphaXi", &RouletteSim::setAlphaXi)
        .def("setBetaXi", &RouletteSim::setBetaXi) ;

    pybind11::enum_<PsiSpec>(m, "PsiSpec") 
       .value( "SIE", CSIM_PSI_SIE )
       .value( "SIS", CSIM_PSI_SIS )
       .value( "Cluster", CSIM_PSI_CLUSTER )
       .value( "PM", CSIM_NOPSI_PM ) 
       .value( "Roulette", CSIM_NOPSI_ROULETTE ) 
       .value( "NoPsi", CSIM_NOPSI ) ;
    pybind11::enum_<SourceSpec>(m, "SourceSpec") 
       .value( "Sphere", CSIM_SOURCE_SPHERE )
       .value( "Ellipse", CSIM_SOURCE_ELLIPSE )
       .value( "Image", CSIM_SOURCE_IMAGE )
       .value( "Triangle", CSIM_SOURCE_TRIANGLE ) ;
    pybind11::enum_<ModelSpec>(m, "ModelSpec") 
       .value( "Raytrace", CSIM_MODEL_RAYTRACE )
       .value( "Roulette", CSIM_MODEL_ROULETTE  )
       .value( "RouletteRegenerator", CSIM_MODEL_ROULETTE_REGEN  )
       .value( "PointMassExact", CSIM_MODEL_POINTMASS_EXACT )
       .value( "PointMassRoulettes", CSIM_MODEL_POINTMASS_ROULETTE ) 
       .value( "NoModel", CSIM_NOMODEL  )  ;

    // cv::Mat binding from https://alexsm.com/pybind11-buffer-protocol-opencv-to-numpy/
    pybind11::class_<cv::Mat>(m, "Image", pybind11::buffer_protocol())
        .def_buffer([](cv::Mat& im) -> pybind11::buffer_info {
              int t = im.type() ;
              if ( (t&CV_64F) == CV_64F ) {
                if (DEBUG) std::cout << "[CosmoSimPy] CV_64F\n" ;
                return pybind11::buffer_info(
                    // Pointer to buffer
                    im.data,
                    // Size of one scalar
                    sizeof(double),
                    // Python struct-style format descriptor
                    pybind11::format_descriptor<double>::format(),
                    // Number of dimensions
                    3,
                        // Buffer dimensions
                    { im.rows, im.cols, im.channels() },
                    // Strides (in bytes) for each index
                    {
                        sizeof(double) * im.channels() * im.cols,
                        sizeof(double) * im.channels(),
                        sizeof(unsigned char)
                    }
                    );
              } else { // default is 8bit integer
                return pybind11::buffer_info(
                    // Pointer to buffer
                    im.data,
                    // Size of one scalar
                    sizeof(unsigned char),
                    // Python struct-style format descriptor
                    pybind11::format_descriptor<unsigned char>::format(),
                    // Number of dimensions
                    3,
                        // Buffer dimensions
                    { im.rows, im.cols, im.channels() },
                    // Strides (in bytes) for each index
                    {
                        sizeof(unsigned char) * im.channels() * im.cols,
                        sizeof(unsigned char) * im.channels(),
                        sizeof(unsigned char)
                    }
                 );
              } ;
        });
    // Note.  The cv::Mat object returned needs to by wrapped in python:
    // `np.array(im, copy=False)` where `im` is the `Mat` object.

    pybind11::class_<cv::Point2d>(m, "Point", pybind11::buffer_protocol())
        .def_buffer([](cv::Point2d& pt) -> pybind11::buffer_info {
                return pybind11::buffer_info(
                    // Pointer to buffer
                    & pt,
                    // Size of one scalar
                    sizeof(double),
                    // Python struct-style format descriptor
                    pybind11::format_descriptor<double>::format(),
                    // Number of dimensions
                    1,
                        // Buffer dimensions
                    { 2 },
                    // Strides (in bytes) for each index
                    {
                        sizeof(double)
                    }
                 );
        });

}
