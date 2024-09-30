from PyTest import *

p = PyTest()

c = Child()

c.test()
c.setTest(5)

p.setChild(c)

p.test()
