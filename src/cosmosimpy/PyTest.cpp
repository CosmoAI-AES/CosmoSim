/* (C) 2022-23: Hans Georg Schaathun <georg@schaathun.net> */

#include <pybind11/pybind11.h>

namespace py = pybind11;


class Parent {
   private:
      int testvar = 2 ;
   public:
      void setTest( int ) ;
} ;
class Child : public Parent {
   public:
      void test() ;
} ;
class PyTest {
   private:
      Child *child = NULL ;
   public:
      void setChild( Child* ) ;
      void test() ;
} ;

void Parent::setTest( int n ) {
   testvar = n ;
}
void Child::test() {
   setTest( 4 ) ;
}
void PyTest::test() {
   child->test() ;
}
void PyTest::setChild( Child* c ) {
   child = c ;
}


PYBIND11_MODULE(CosmoSimPy, m) {
    m.doc() = "Minimal test for trouble with inheritance in pybind" ;


    py::class_<Lens>(m, "Lens")
        .def(py::init<>())
        .def("setEinsteinR", &Lens::setEinsteinR)
        .def("setNterms", &Lens::setNterms)
        .def("setFile", &Lens::setFile)
        ;
    py::class_<PsiFunctionLens, Lens>(m, "PsiFunctionLens")
        .def(py::init<>())
        ;
    py::class_<SIS,PsiFunctionLens>(m, "SIS")
        .def(py::init<>())
        ;
    py::class_<SIE,PsiFunctionLens>(m, "SIE")
        .def(py::init<>())
        .def("setOrientation", &SIE::setOrientation)
        .def("setRatio", &SIE::setRatio)
        ;
    py::class_<PointMass,PsiFunctionLens>(m, "PointMass")
        .def(py::init<>())
        ;
    py::class_<ClusterLens,PsiFunctionLens>(m, "ClusterLens")
        .def(py::init<>())
        .def("addLens", &ClusterLens::addLens)
        ;

}
