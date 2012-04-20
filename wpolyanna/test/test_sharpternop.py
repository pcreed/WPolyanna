import unittest

from wpolyanna import Projection
from wpolyanna.sharpternop import *

class TestSharpTernary(unittest.TestCase):
    """

    A test class for sharp ternary operations (SharpTernary objects).

    """

    def setUp(self):

        self.proj = [Projection(3,3,i) for i in [0,1,2]]
        self.f = {(0,1,2):0,(0,2,1):1,(1,0,2):2,(1,2,0):0,(2,0,1):1,(2,1,0):2}
        self.g = {(0,1,2):0,(0,2,1):2,(1,0,2):1,(1,2,0):1,(2,0,1):0,(2,1,0):2}
        self.h = {(0,1,2):1,(0,2,1):2,(1,0,2):2,(1,2,0):0,(2,0,1):0,(2,1,0):1}
        
        self.maj = majority(3,self.f)
        self.min = minority(3,self.f)
        self.pixley = [pixley(3,0,self.f),pixley(3,1,self.g),pixley(3,2,self.h)]
        self.semiproj = [semiproj(3,0,self.f),semiproj(3,1,self.g),
                         semiproj(3,2,self.h)]
        self.proj = [Projection(3,3,i) for i in [0,1,2]]
        
    def test_maj(self):
        self.assertEqual(self.maj[(0,0,1)],0)
        self.assertEqual(self.maj[(0,1,0)],0)
        self.assertEqual(self.maj[(1,0,0)],0)
        self.assertEqual(self.maj[(1,2,2)],2)
        self.assertEqual(self.maj[(2,1,2)],2)
        self.assertEqual(self.maj[(2,2,1)],2)

    def test_min(self):
        self.assertEqual(self.min[(0,0,1)],1)
        self.assertEqual(self.min[(0,1,0)],1)
        self.assertEqual(self.min[(1,0,0)],1)
        self.assertEqual(self.min[(1,2,2)],1)
        self.assertEqual(self.min[(2,1,2)],1)
        self.assertEqual(self.min[(2,2,1)],1)
        
    def test_pixley(self):
        self.assertEqual(self.pixley[0][(0,0,1)],1)
        self.assertEqual(self.pixley[1][(0,0,1)],1)
        self.assertEqual(self.pixley[2][(0,0,1)],0)
        self.assertEqual(self.pixley[0][(0,1,0)],1)
        self.assertEqual(self.pixley[1][(0,1,0)],0)
        self.assertEqual(self.pixley[2][(0,1,0)],1)
        self.assertEqual(self.pixley[0][(1,0,0)],0)
        self.assertEqual(self.pixley[1][(1,0,0)],1)
        self.assertEqual(self.pixley[2][(1,0,0)],1)

    def test_semiprojection(self):
        self.assertEqual(self.semiproj[0][(0,0,1)],0)
        self.assertEqual(self.semiproj[1][(0,0,1)],0)
        self.assertEqual(self.semiproj[2][(0,0,1)],1)
        self.assertEqual(self.semiproj[0][(0,1,0)],0)
        self.assertEqual(self.semiproj[1][(0,1,0)],1)
        self.assertEqual(self.semiproj[2][(0,1,0)],0)
        self.assertEqual(self.semiproj[0][(1,0,0)],1)
        self.assertEqual(self.semiproj[1][(1,0,0)],0)
        self.assertEqual(self.semiproj[2][(1,0,0)],0)

    def test_eq(self):
        self.assertEqual(self.min,minority(3,self.f))
        self.assertNotEqual(self.min,minority(3,self.g))
        self.assertNotEqual(self.maj,self.min)

    def test_repr(self):
        self.assertEqual(self.min,eval(repr(self.min)))
        self.assertEqual(self.semiproj[2],eval(repr(self.semiproj[2])))
                         
    def test_compose(self):
        # Test composing with projections
        self.assertEqual(self.pixley[0].compose((self.proj[0],
                                                 self.proj[1],
                                                 self.proj[2],),),
                         self.pixley[0])
        self.assertEqual(self.pixley[0].compose((self.proj[2],
                                                 self.proj[0],
                                                 self.proj[1],),),
                         self.pixley[2])
        self.assertEqual(self.pixley[0].compose((self.proj[1],
                                                 self.proj[2],
                                                 self.proj[0],),),
                         self.pixley[1])

        
def suite():

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSharpTernary))
    return suite


if __name__ == '__main__':

    unittest.main()
