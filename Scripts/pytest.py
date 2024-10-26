from PyTest import *

p = PyTest()

c = Child()

c.test()
c.setTest(7)

p.setChild(c)

p.test()
