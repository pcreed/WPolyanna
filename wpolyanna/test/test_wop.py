import unittest

import wpolyanna.op
import wpolyanna.wop
import wpolyanna.cost_function
from wpolyanna.op import ExplicitOperation, Projection
from wpolyanna.wop import WeightedOperation
from wpolyanna.cost_function import CostFunction

class TestWeightedOperation(unittest.TestCase):

    def setUp(self):
        self.min2 = ExplicitOperation(2,2,{(0,0):0, (0,1):0, (1,0):0, (1,1):1})
        self.max2 = ExplicitOperation(2,2,{(0,0):0, (0,1):1, (1,0):1, (1,1):1})
        self.proj2 = [Projection(2,2,0),Projection(2,2,1)]
        self.sm = WeightedOperation(2,2,self.proj2  + [self.min2, self.max2],
                                    [-1,-1,1,1])
        self.smcopy = WeightedOperation(2,2,self.proj2  + [self.max2,self.min2],
                                    [-1,-1,1,1])
        self.nsm = WeightedOperation(2,2,self.proj2 + [self.min2, self.max2],
                                     [-2,-2,1,3]) 
        self.max = WeightedOperation(2,2,self.proj2 + [self.max2, self.max2],
                                    [-1,-1,1,1])
        
        self.cf1 = CostFunction(2,2,{(0,0):0,(0,1):0,(1,0):1,(1,1):1})
        self.cf2 = CostFunction(2,2,{(0,0):1,(0,1):1,(1,0):0,(1,1):0})
        self.cf3 = CostFunction(3,2,{(0,0,0):1,(0,0,1):0,(0,1,0):1,(0,1,1):0,
                                     (1,0,0):1,(1,0,1):0,(1,1,0):0,(1,1,1):0})

    def test_get_weight(self):
        self.assertEqual(self.sm.get_weight(self.proj2[0]),-1)
        self.assertEqual(self.sm.get_weight(self.min2),1)
        self.assertEqual(self.max.get_weight(self.min2),0)
        self.assertEqual(self.max.get_weight(self.max2),2)

    def test_get_support(self):
        self.assertEqual(set(self.sm.get_support()),set(self.proj2 + [self.min2,self.max2]))

    def test_weight_iter(self):
        W1 = set(self.sm.weight_iter())
        W2 = {(self.proj2[0],-1),(self.proj2[1],-1),(self.min2,+1),(self.max2,+1)}
        self.assertEqual(W1,W2)

    def test_eq(self):
        self.assertEqual(self.sm,self.smcopy)
        self.assertNotEqual(self.sm,self.max)

    def test_repr(self):
        self.assertEqual(self.sm,eval(repr(self.sm)))
        self.assertEqual(self.max,eval(repr(self.max)))

    def test_imp_ineq(self):
        self.assertEqual(self.sm.imp_ineq(2),[[1,-1,-1,1]])
        self.assertEqual(self.sm.imp_ineq(3),
                         sorted([[1,-1,-1,1,0,0,0,0],
                         [1,-1,0,0,-1,1,0,0],
                         [1,-1,0,0,0,0,-1,1],
                         [1,0,-1,0,-1,0,1,0],
                         [1,0,-1,0,0,-1,0,1],
                         [1,0,0,-1,-1,0,0,1],
                         [0,1,0,-1,0,-1,0,1],
                         [0,0,1,-1,0,0,-1,1],
                         [0,0,0,0,1,-1,-1,1]]))
        self.assertEqual(self.nsm.imp_ineq(2),
                         sorted([[-1,1,0,0],
                         [-1,0,1,0],
                         [-1,0,0,1],
                         [1,-2,-2,3],
                         [0,-1,0,1],
                         [0,0,-1,1]]))

    def test_imp(self):
        bsm = []
        bsm.append(CostFunction(2,2,{(0,0):0,(0,1):0,(1,0):1,(1,1):1}))
        bsm.append(CostFunction(2,2,{(0,0):0,(0,1):1,(1,0):0,(1,1):1}))
        bsm.append(CostFunction(2,2,{(0,0):1,(0,1):1,(1,0):0,(1,1):0}))
        bsm.append(CostFunction(2,2,{(0,0):1,(0,1):0,(1,0):1,(1,1):0}))
        bsm.append(CostFunction(2,2,{(0,0):0,(0,1):0,(1,0):1,(1,1):0}))
        bsm.append(CostFunction(2,2,{(0,0):0,(0,1):1,(1,0):0,(1,1):0}))
        self.assertEqual(set(bsm),set(self.sm.imp(2)))
    
    def test_improves(self):
        self.assertEqual(self.sm.improves(self.cf1),True)
        self.assertEqual(self.nsm.improves(self.cf1),(False,[-1,0,0,1]))
        self.assertEqual(self.sm.improves(self.cf3),(False,[0,0,0,0,1,-1,-1,1]))
    
    def test_translations(self):
        self.assertEqual(self.sm.translations(2),[[-1,-1,1,1]])
        
    def test_in_wclone(self):
        (ans,cert) = self.sm.in_wclone(self.nsm)
        self.assertFalse(ans)
        F = [ExplicitOperation(3,2,{(0,0,0):0,(0,0,1):1,(0,1,0):1,(0,1,1):1,
                                    (1,0,0):1,(1,0,1):1,(1,1,0):1,(1,1,1):1}),
             ExplicitOperation(3,2,{(0,0,0):0,(0,0,1):0,(0,1,0):0,(0,1,1):0,
                                    (1,0,0):0,(1,0,1):0,(1,1,0):1,(1,1,1):1}),
             ExplicitOperation(3,2,{(0,0,0):0,(0,0,1):0,(0,1,0):0,(0,1,1):1,
                                    (1,0,0):0,(1,0,1):1,(1,1,0):0,(1,1,1):1})]
        proj = [Projection(3,2,i) for i in [0,1,2]]
        omega = WeightedOperation(3,2,proj + F,[-1,-1,-1,1,1,1])
        (ans2,cert2) = self.sm.in_wclone(omega)
        self.assertTrue(ans2)
    
    def test_wclone(self):
        self.assertEqual(self.sm.wclone(2),[self.sm])
        W = [self.nsm,
             WeightedOperation(2,2,[self.proj2[0],self.max2],[-1,1]),
             WeightedOperation(2,2,[self.proj2[1],self.max2],[-1,1]),
             ]
        self.assertEqual(set(self.nsm.wclone(2)),set(W))

        
def suite():

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestWeightedOperation))
    return suite

if __name__ == '__main__':

    unittest.main()
