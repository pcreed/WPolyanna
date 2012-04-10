import unittest

from wpolyanna import ExplicitOperation
from wpolyanna import Projection
from wpolyanna import Clone
from wpolyanna import WeightedOperation
from wpolyanna import CostFunction
from wpolyanna.submodular import Submodular
from wpolyanna.submodular import MinMax

class TestMinMax(unittest.TestCase):

    def setUp(self):
        self.min2 = MinMax(2,[[0,1]])
        self.min2copy = MinMax(2,[[0,1]])
        self.max2 = MinMax(2,[[0],[1]])

        self.proj3 = [MinMax(3,[[i]]) for i in [0,1,2]]
        self.C3 = self.proj3 + [MinMax(3,[[0,1]]),MinMax(3,[[0,2]]),MinMax(3,[[1,2]])]
        self.C3 += [MinMax(3,[[0,1,2]])]
        self.C3 += [MinMax(3,[[0],[1]]),MinMax(3,[[1],[2]]),MinMax(3,[[2],[0]])]
        self.C3 += [MinMax(3,[[0],[1,2]]),MinMax(3,[[1],[0,2]]),MinMax(3,[[2],[0,1]])]
        self.C3 += [MinMax(3,[[0,1],[1,2]]),MinMax(3,[[0,2],[0,1]]),MinMax(3,[[1,2],[0,2]])]
        self.C3 += [MinMax(3,[[0,1],[0,2],[1,2]]),MinMax(3,[[0],[1],[2]])]
        
        self.f = MinMax(3,[[0,1],[0,2]])
        self.g = MinMax(3,[[0],[1],[2]])
        self.h = MinMax(3,[[0,1]])
        self.e = MinMax(3,[[1],[0,2]])
        
    def test_getitem(self):
        self.assertEqual(self.min2[(0,1)],0)
        self.assertEqual(self.max2[(1,0)],1)

    def test_eq(self):
        self.assertNotEqual(self.min2,self.max2)
        self.assertEqual(self.min2,self.min2copy)
        self.assertEqual(self.proj3[0],Projection(3,2,0))
        self.assertEqual(Projection(3,2,0),self.proj3[0])
        
    def test_le(self):
        self.assertTrue(self.min2 < self.max2)
        self.assertTrue(self.min2 <= self.min2)
        self.assertFalse(self.max2 < self.min2)
        self.assertTrue(self.proj3[0] <= self.g)
        
        # Test for incomparable elements
        self.assertFalse(self.proj3[1] <= self.f)
        self.assertFalse(self.f <= self.proj3[1])
        
    def test_add(self):
        self.assertEqual(self.min2 + self.max2, self.max2)
        self.assertEqual(self.f + self.proj3[1], self.e)
        
    def test_mul(self):
        self.assertEqual(self.min2 * self.max2, self.min2)
        self.assertEqual(self.h * self.g, self.h)
        self.assertEqual(self.proj3[1] * self.f, self.h)

    def test_is_projection(self):
        self.assertTrue(self.proj3[0].is_projection())
        self.assertFalse(self.min2.is_projection())
        self.assertFalse(self.max2.is_projection())

    def test_compose(self):
        self.assertEqual(self.min2.compose((self.proj3[0],self.proj3[1])),
                         self.h)
        self.assertEqual(self.max2.compose([self.proj3[0],
                                            self.max2.compose(self.proj3[1:3])]
                                           ),self.g)

    def test_below(self):
        self.assertEqual(self.C3[6].below(),set([]))
        self.assertEqual(self.C3[4].below(),set([self.C3[6]]))
        self.assertEqual(self.C3[17].below(),set(self.C3[7:10]))

    def test_sperner(self):
        self.assertEqual(MinMax.sperner(set([frozenset([0,1]),frozenset([0,1,2])])),set([frozenset([0,1])]))

    def test_clone(self):
        self.assertEqual(MinMax.clone(3),Clone(self.C3))
        self.assertEqual(Clone.generate([self.min2,self.max2],3),MinMax.clone(3))

class TestSubmodular(unittest.TestCase):

    def setUp(self):
        self.sm = Submodular(2)
        self.proj3 = [MinMax(3,[[i]]) for i in [0,1,2]]
        self.f = MinMax(3,[[0,1],[0,2]])
        self.g = MinMax(3,[[0],[1],[2]])
        self.h = MinMax(3,[[0,1]])
        self.wop3 = WeightedOperation(3,2,self.proj3 + [self.f,self.g,self.h],
                                      [-1,-1,-1,1,1,1])

    def test_translations(self):
        self.assertEqual(self.sm.translations(2),[[-1,-1,1,1]])
                         
    def test_in_wclone(self):
        self.assertTrue(self.sm.in_wclone(self.wop3))
        self.assertTrue(self.wop3.in_wclone(self.sm,MinMax.clone(2)))
        
def suite():

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMinMax))
    #suite.addTest(unittest.makeSuite(TestSubmodular))
    return suite

if __name__ == '__main__':

    unittest.main()
