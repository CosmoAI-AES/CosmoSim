/* (C) 2024: Hans Georg Schaathun <georg@schaathun.net> */


#include <pybind11/pybind11.h>
#include <iostream>

namespace py = pybind11;


class Parent {
   private:
      int testvar = 2 ;
   public:
      void setTest( int ) ;
} ;
class Child : public Parent {
   public:
      virtual void test() ;
} ;
class PyTest {
   private:
      Child *child = NULL ;
   public:
      void setChild( Child* ) ;
      void test() ;
} ;

void Parent::setTest( int n ) {
   std::cout << "[Parent::setTest] " << testvar << " -> " << n << "\n" ;
   testvar = n ;
}
void Child::test() {
   setTest( 4 ) ;
}
void PyTest::test() {
   child->setTest(5) ;
}
void PyTest::setChild( Child* c ) {
   child = c ;
}


PYBIND11_MODULE(PyTest, m) {
    m.doc() = "Minimal test for trouble with inheritance in pybind" ;


    py::class_<Parent>(m, "Lens")
        .def(py::init<>())
        .def("setTest", &Parent::setTest)
        ;
    py::class_<Child, Parent>(m, "Child")
        .def(py::init<>())
        .def("test", &Child::test)
        ;
    py::class_<PyTest>(m, "PyTest")
        .def(py::init<>())
        .def("test", &PyTest::test)
        .def("setChild", &PyTest::setChild)
        ;

}
