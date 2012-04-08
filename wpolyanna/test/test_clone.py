import unittest

from wpolyanna.op import ExplicitOperation, Projection
from wpolyanna.clone import Clone

class TestClone(unittest.TestCase):

    def setUp(self):
        cf = dict()
        for i in range(5):
            for j in range(5):
                cf[i,j] = (3*i + 3*j) % 5
        self.f = ExplicitOperation(2,5,cf)

        cg = dict()
        for i in range(5):
            for j in range(5):
                cg[i,j] = (2*i + 4*j) % 5
        self.g = ExplicitOperation(2,5,cg)
        
        ch = dict()
        for i in range(5):
            for j in range(5):
                ch[i,j] = (4*i + 2*j) % 5
        self.h = ExplicitOperation(2,5,ch)

        self.clone = Clone([Projection(2,5,0),
                                     Projection(2,5,1),
                                     self.f,self.g,self.h])

    def test_get(self):
        self.assertEqual(self.clone[0],Projection(2,5,0))
        self.assertEqual(self.clone[1],Projection(2,5,1))
        self.assertEqual(self.clone[2],self.f)
        self.assertEqual(self.clone[3],self.g)
        self.assertEqual(self.clone[4],self.h)
        self.assertNotEqual(self.clone[0],self.f)
        self.assertNotEqual(self.clone[4],Projection(2,5,1))

    def test_len(self):
        self.assertEqual(len(self.clone),5)

    def test_generate(self):
        clone = Clone.generate([self.f],2)
        self.assertEqual(clone,self.clone)
        
def suite():

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestOperation))
    suite.addTest(unittest.makeSuite(TestClone))
    return suite

if __name__ == '__main__':

    unittest.main()
