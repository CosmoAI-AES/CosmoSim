/* (C) 2022-23: Hans Georg Schaathun <georg@schaathun.net> */

#include <pybind11/pybind11.h>

namespace py = pybind11;


class Parent {
   private:
      int testvar = 2 ;
   public:
      void setTest( int ) ;
}
class Child : public Parent {
   public:
      void test() ;
}
class PyTest {
   private:
      Child *child = NULL ;
   public:
      void test() ;
      void setChild( Child* ) ;
}

void Parent::setTest( int n ) {
   testvar = n ;
}
void Child::test() {
   setTest( 4 ) ;
}
void PyTest::test() {
   child->test() ;
}
void PyTest::setChild( Child* c ) ;
   child = c ;
}
