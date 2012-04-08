import unittest

from wpolyanna.op import Projection
from wpolyanna.binop import BinaryOperation
from wpolyanna.exception import DomainError

class TestBinaryOperation(unittest.TestCase):
    """

    A test class for the operation part of the poly module.

    """
    
    def setUp(self):
        """

        Set up the data used in the tests.

        Called before each test function execution.
        
        """

        self.proj = [BinaryOperation(2,{(0,1):0, (1,0):1},False,True),
                     BinaryOperation(2,{(0,1):1, (1,0):0},False,True)]

        self.min = BinaryOperation(2,{(0,1):0},True,True)

        self.f = BinaryOperation(2,{(0,0):1,(0,1):0,(1,0):1,(1,1):0},False,False)
        self.fcopy = BinaryOperation(2,{(0,0):1,(0,1):0,(1,0):1,(1,1):0},False,False)

        self.dom3 = BinaryOperation(3,{(0,0):0,(0,1):1,(0,2):0,
                                       (1,0):1,(1,1):2,(1,2):1,
                                       (2,0):0,(2,1):2,(2,2):2},
                                    False,False)

        self.F = [self.f,self.min]
        
    def test_eq(self):
        self.assertEqual(self.f,self.fcopy)
        self.assertNotEqual(self.f,self.min)
        self.assertEqual(self.proj[0],Projection(2,2,0))

    def test_get(self):
        self.assertEqual(self.f[0,0],1)
        self.assertEqual(self.f[0,1],0)
        self.assertEqual(self.f[1,0],1)
        self.assertEqual(self.f[1,1],0)
        self.assertEqual(self.min[0,1],0)
        self.assertEqual(self.min[1,0],0)

    def test_compose(self):
        self.assertEqual(self.f.compose([self.f,self.min]),
                         BinaryOperation(2,{(0,0):1,(1,1):0,(0,1):1},
                                         True, False))
        self.assertEqual(self.proj[1].compose([self.f,self.min]),self.min)

    def test_is_projection(self):
        self.assertTrue(self.proj[0].is_projection())
        self.assertTrue(self.proj[1].is_projection())
        self.assertFalse(self.f.is_projection())

    def test_restrict(self):
        self.assertTrue(self.dom3.restrict([0,2]).idem)
        self.assertTrue(self.dom3.restrict([0,2]).comm)
        self.assertEqual(self.dom3.restrict([0,2]),self.min)
        self.assertRaises(DomainError,self.dom3.restrict,[0,1])
        self.assertFalse(self.dom3.restrict([1,2]).idem)
        self.assertFalse(self.dom3.restrict([1,2]).comm)

    def test_repr(self):
        self.assertEqual(self.f,eval(repr(self.f)))
        self.assertEqual(self.min,eval(repr(self.min)))

        
if __name__ == '__main__':

    unittest.main()
