import unittest

from wpolyanna.op import Operation, ExplicitOperation, Projection
from wpolyanna.exception import *

class TestOperation(unittest.TestCase):
    """

    A test class for the operation part of the poly module.

    """
    
    def setUp(self):
        """

        Set up the data used in the tests.

        Called before each test function execution.
        
        """

        self.proj = [ExplicitOperation(2,2,
                                            {(0,0):0, (0,1):0, (1,0):1, (1,1):1}),
                     ExplicitOperation(2,2,
                                            {(0,0):0, (0,1):1, (1,0):0, (1,1):1})]
        
        self.f = ExplicitOperation(2,2,
                                        {(0,0):1, (0,1):0, (1,0):0, (1,1):1})
        self.fcopy = ExplicitOperation(2,2, {(0,0):1, (0,1):0,
                                                  (1,0):0, (1,1):1}
                                            )
        self.g = ExplicitOperation(2,2,
                                        {(0,0):0, (0,1):1, (1,0):1, (1,1):1}
                                        )
        self.dom3 = ExplicitOperation(2,3,
                                           {(0,0):0, (0,1):1, (1,0):1, (1,1):1,
                                            (0,2):0, (2,0):0, (2,2):2,
                                            (1,2):1, (2,1):2})

        self.F = [
            ExplicitOperation(3,2,
                                   {(0,0,0):0, (0,0,1):1, (0,1,0):0,
                                    (0,1,1):1, (1,0,0):0, (1,0,1):1,
                                    (1,1,0):1, (1,1,1):1}),
            ExplicitOperation(3,2,
                                   {(0,0,0):0, (0,0,1):0, (0,1,0):0,
                                    (0,1,1):1, (1,0,0):0, (1,0,1):1,
                                    (1,1,0):1, (1,1,1):1})           
            ]

        self.h = ExplicitOperation(3,2,
                                        {(0,0,0):0, (0,0,1):1, (0,1,0):0,
                                         (0,1,1):1, (1,0,0):0, (1,0,1):1,
                                         (1,1,0):1, (1,1,1):1})

        self.maj = ExplicitOperation(3,2,
                                        {(0,0,0):0, (0,0,1):0, (0,1,0):0,
                                         (0,1,1):1, (1,0,0):0, (1,0,1):1,
                                         (1,1,0):1, (1,1,1):1})
    def test_eq(self):
        self.assertEqual(self.f,self.fcopy)
        self.assertNotEqual(self.f,self.g)

    def test_getitem(self):
        self.assertEqual(self.f[0,0],1)
        self.assertEqual(self.f[0,1],0)
        self.assertEqual(self.f[1,0],0)
        self.assertEqual(self.f[1,1],1)
        self.assertRaises(ArityError,self.f.__getitem__,(0,1,0))
        self.assertRaises(DomainError,self.f.__getitem__,(0,2))

    def test_compose(self):
        self.assertEqual(self.g.compose(self.F),self.h)
        self.assertRaises(ArityError,self.maj.compose,self.F)
        self.assertRaises(CompositionError,self.g.compose,[self.maj,self.g])
        
    def test_is_projection(self):
        self.assertTrue(self.proj[0].is_projection())
        self.assertTrue(self.proj[1].is_projection())
        self.assertFalse(self.f.is_projection())

    def test_is_sharp(self):
        self.assertTrue(self.maj.is_sharp())
        self.assertFalse(self.h.is_sharp())
        self.assertFalse(self.proj[0].is_sharp())

    def test_apply_to_tableau(self):
        X = [(0,1,0),(1,0,0)]
        self.assertEqual(self.g.apply_to_tableau(X),(1,1,0))
        self.assertRaises(ArityError,self.g.apply_to_tableau,[(1,1,0)])
        self.assertRaises(DomainError,self.g.apply_to_tableau,[(2,0),(0,1)])
        
    def test_restrict(self):
        self.assertEqual(self.dom3.restrict([0,1]),self.g)
        self.assertNotEqual(self.dom3.restrict([0,2]),self.g)
        self.assertNotEqual(self.dom3.restrict([1,2]),self.proj[0])

    def test_projection(self):
        proj = [Projection(2,2,0),Projection(2,2,1)]
        self.assertEqual(proj[0],self.proj[0])
        self.assertEqual(proj[1],self.proj[1])
        self.assertTrue(proj[0].is_projection())
        self.assertEqual(proj[0][(0,1)],0)
        self.assertNotEqual(proj[1][(0,1)],0)
        self.assertEqual(proj[0].compose([self.f,self.g]),self.f)
        self.assertEqual(proj[1].compose([self.f,self.g]),self.g)
        self.assertEqual(hash(proj[0]),2)
        self.assertEqual(hash(proj[1]),2)
        self.assertEqual(proj[0],eval(repr(proj[0])))
        
    def test_hash(self):
        self.assertEqual(hash(self.f),2)
        self.assertEqual(hash(self.g),3)
        self.assertEqual(hash(self.dom3),8)

    def test_repr(self):
        self.assertEqual(self.f,eval(repr(self.f)))
        
def suite():

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestOperation))
    suite.addTest(unittest.makeSuite(TestExplicitOperation))
    suite.addTest(unittest.makeSuite(TestProjection))
    return suite
        
if __name__ == '__main__':

    unittest.main()
