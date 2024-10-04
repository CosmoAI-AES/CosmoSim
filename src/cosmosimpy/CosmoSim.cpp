/* (C) 2022-23: Hans Georg Schaathun <georg@schaathun.net> */

#include "CosmoSim.h"

#include <pybind11/pybind11.h>
#include <opencv2/opencv.hpp>

#ifndef DEBUG
#define DEBUG 1
#endif

namespace py = pybind11;

CosmoSim::CosmoSim() {
   if (DEBUG) std::cout << "CosmoSim Constructor\n" ;
   rPos = -1 ;
}

void CosmoSim::setXY( double x, double y) { xPos = x ; yPos = y ; rPos = -1 ; }
void CosmoSim::setPolar(int r, int theta) { rPos = r ; thetaPos = theta ; }

void CosmoSim::setLens(PsiFunctionLens *l) { 
   std::cout << "[CosmoSim::setLens]\n" ;
   lensmode = CSIM_CLUSTER ; 
   modelchanged = 1 ;
   lens = psilens = l ;
   std::cout << "[CosmoSim::setLens] returning\n" ;
}

void CosmoSim::setSourceParameters(double s1, double s2, double theta ) {
   sourceSize = s1 ;
   if ( s2 >= 0 ) sourceSize2 = s2 ;
   if ( theta >= 0 ) sourceTheta = theta ;
   // srcmode = mode ;
}

bool CosmoSim::runSim() { 
   std::cout  << "[runLens] starting \n" ;
   if ( running ) {
      return false ;
   }
   std::cout << "[runSim]\n" ;
   psilens = NULL ;
   sim = new RaytraceModel() ;
   sim->setLens(lens) ;
   if ( sim == NULL ) {
      throw std::bad_function_call() ;
   }
   src = new SphericalSource( size, sourceSize ) ;
   if (sim) sim->setSource( src ) ;

   if ( rPos < 0 ) {
         sim->setXY( xPos, yPos ) ;
   } else {
         sim->setPolar( rPos, thetaPos ) ;
   }

   Py_BEGIN_ALLOW_THREADS
   if (DEBUG) std::cout << "[runSim] thread section\n" ;
   if ( sim == NULL ) throw std::logic_error("Simulator not initialised") ;
   sim->update() ;
   if (DEBUG) std::cout << "[CosmoSim.cpp] end of thread section\n" ;
   Py_END_ALLOW_THREADS
   return true ;
}


PYBIND11_MODULE(CosmoSimPy, m) {
    m.doc() = "Wrapper for the CosmoSim simulator" ;

    py::class_<CosmoSim>(m, "CosmoSim")
        .def(py::init<>())
        .def("setSourceParameters", &CosmoSim::setSourceParameters)
        .def("setXY", &CosmoSim::setXY)
        .def("setPolar", &CosmoSim::setPolar)
        .def("runSim", &CosmoSim::runSim)
        .def("setLens", &CosmoSim::setLens)
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
        ;
    py::class_<PsiFunctionLens,Lens>(m, "PsiFunctionLens")
        .def(py::init<>())
        .def("calculateAlphaBeta", &PsiFunctionLens::calculateAlphaBeta)
        .def("getAlphaXi", &PsiFunctionLens::getAlphaXi)
        .def("getBetaXi", &PsiFunctionLens::getBetaXi)
        .def("getAlpha", &PsiFunctionLens::getAlpha)
        .def("getBeta", &PsiFunctionLens::getBeta)
        .def("setEinsteinR", &PsiFunctionLens::setEinsteinR)
        .def("setOrientation", &PsiFunctionLens::setOrientation)
        .def("setRatio", &PsiFunctionLens::setRatio)
        .def("setFile", &PsiFunctionLens::setFile)
        ;
    py::class_<SIS,PsiFunctionLens>(m, "SIS")
        .def(py::init<>())
        .def("psiValue", &SIS::psiValue)
        .def("psiXvalue", &SIS::psiXvalue)
        .def("psiYvalue", &SIS::psiYvalue)
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
        .def("getXi", &ClusterLens::getXi)
        .def("psiValue", &ClusterLens::psiValue)
        .def("psiXvalue", &ClusterLens::psiXvalue)
        .def("psiYvalue", &ClusterLens::psiYvalue)
        ;


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
