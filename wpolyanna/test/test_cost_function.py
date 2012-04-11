import unittest

from wpolyanna import CostFunction
from wpolyanna import Projection
from wpolyanna import ExplicitOperation
from wpolyanna import WeightedOperation
from wpolyanna import wpol
from wpolyanna.exception import *

class TestCostFunction(unittest.TestCase):

    def setUp(self):
        self.unary = [CostFunction(1,2,{(0,):1,(1,):0}),
                      CostFunction(1,2,{(0,):0,(1,):1})]

        self.softimp = CostFunction(2,2,{(0,0,):0,(0,1,):0,(1,0,):1,(1,1,):0})
        self.softimp2 = CostFunction(2,2,{(0,0,):0,(0,1,):0,(1,0,):1,(1,1,):0})

        self.proj2 = [Projection(2,2,0),Projection(2,2,1)]
        f = ExplicitOperation(2,2,{(0,0,):0,(0,1,):0,(1,0,):0,(1,1,):1})
        g = ExplicitOperation(2,2,{(0,0,):0,(0,1,):1,(1,0,):1,(1,1,):1})
        self.sm = WeightedOperation(2,2,self.proj2 + [f,g], [-1,-1,1,1])
        
    def test_getitem(self):
        self.assertEqual(self.softimp[(0,1,)],0)
        self.assertEqual(self.softimp[(1,0,)],1)
        self.assertRaises(ArityError,self.softimp.__getitem__,(0,0,0,))
        self.assertRaises(DomainError,self.softimp.__getitem__,(0,2,))
        self.assertRaises(DomainError,self.softimp.__getitem__,(0,-2,))

    def test_eq(self):
        self.assertEqual(self.softimp,self.softimp2)
        self.assertNotEqual(self.softimp,self.unary[0])
        self.assertNotEqual(self.unary[1],self.unary[0])

    def test_hash(self):
        self.assertEqual(hash(self.unary[0]),4)
        self.assertEqual(hash(self.unary[1]),4)
        self.assertEqual(hash(self.softimp),5)

    def test_repr(self):
        self.assertEqual(self.softimp,eval(repr(self.softimp)))
        self.assertNotEqual(self.unary[0],eval(repr(self.unary[1])))

    def test_cost_tuple(self):
        self.assertEqual(self.softimp.cost_tuple(),(0,0,1,0))
        self.assertEqual(self.unary[0].cost_tuple(),(1,0))
        self.assertEqual(self.unary[1].cost_tuple(),(0,1))

    def test_wop_ineq(self):
        self.assertEqual(self.unary[0].wop_ineq(1),
                         [[0,0,-1,0,0],[0,0,0,-1,0],[0,0,0,0,-1],
                          [0,1,1,1,1],[0,-1,-1,-1,-1]])
        
    def test_wpol_ineq(self):
        self.assertEqual(self.unary[0].wpol_ineq(1),[[0,1,1,0,0],[0,0,1,1,0]])
        self.assertEqual(self.unary[1].wpol_ineq(1),[[0,1,0,0,1],[0,0,0,1,1]])

    def test_wpol(self):
        self.assertEqual(self.unary[0].wpol(1),[WeightedOperation(1, 2,
                         [Projection(1, 2, 0),
                          ExplicitOperation(1, 2, {(0,): 1, (1,): 1})],
                         [-1.0, 1.0])])
        self.assertEqual(wpol(self.unary,1),[])
        self.assertEqual(wpol(self.unary,2),[self.sm])
        
def suite():

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCostFunction))
    return suite

if __name__ == '__main__':

    unittest.main()
