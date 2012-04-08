from itertools import combinations, permutations, product

from wpolyanna.op import ExplicitOperation, Operation
from wpolyanna.exception import DomainError

class BinaryOperation(ExplicitOperation):
    """ A class representing binary operations.

    :param dom: the domain size
    :type dom: int
    :param f: the dictionary defining this operations mapping
    :type f: dictionary mapping integer pairs to integers
    :param commutes: flag to say whether this operations is commutative
    :type commutes: bool
    :param idempotent: flag to say whether this operation is idempotent
    :type idempotent: bool
    """
    
    def __init__(self,dom,f,commutes=False,idempotent=False):
        ExplicitOperation.__init__(self,2,dom,f)
        self.comm = commutes
        self.idem = idempotent

    def __getitem__(self,x):
        Operation.check_input(self,x)
        (a,b) = x
        if self.idem and a==b:
            return a
        if self.comm and b < a:
            tmp = a
            a = b
            b = tmp
        return self.f[(a,b)]

    def compose(self,F):        
        Operation.check_compose(self,F)
        (f,g) = tuple(F)        
        if self.idem and f==g:
            return f
        h = dict()
        for x in product(range(self.dom),repeat=f.arity):            
            h[x] = self[(f[x],g[x])]
        if f.arity == 2:
            commutes = True
            for (a,b) in combinations(range(self.dom),2):
                if h[(a,b)] != h[(b,a)]:
                    commutes = False
            if commutes:
                for (a,b) in combinations(range(self.dom),2):
                    del h[(b,a)]
            idempotent = True
            for a in range(self.dom):
                if h[(a,a)] != a:
                    idempotent = False
            if idempotent:
                for a in range(self.dom):
                    del h[(a,a)]
            return BinaryOperation(self.dom,h,commutes,idempotent)
        else:
            return ExplicitOperation(f,arity,self.dom,h)

    def restrict(self,A):
        f = dict()
        commutes = True
        idempotent = True
        for (i,j) in combinations(range(len(A)),2):
            if not self[(A[i],A[j])] in A:
                raise DomainError(self[(A[i],A[j])])
            f[(i,j)] = A.index(self[(A[i],A[j])])
            if not self.comm:
                if not self[(A[j],A[i])] in A:
                    raise DomainError(self[(A[j],A[i])])
                f[(j,i)] = A.index(self[(A[j],A[i])])
                if f[(i,j)] != f[(j,i)]:
                    commutes = False
                
        if not self.idem:
            for i in range(len(A)):
                if not self[A[i],A[i]] in A:
                    raise DomainError(self[A[i],A[i]])                
                f[(i,i)] = A.index(self[(A[i],A[i])])
                if f[(i,i)] != i:
                    idempotent = False
                
        return BinaryOperation(len(A),f,commutes,idempotent)

    def is_projection(self):
        # Projections are idempotent but not commutative
        if not self.idem or self.comm:
            return False
        p1 = True
        p2 = True
        for (i,j) in permutations(range(self.dom),2):
            if self[i,j] != i:
                p1 = False
            if self[i,j] != j:
                p2 = False
            if not p1 and not p2:
                return False
        return True

    def is_sharp(self):
        return not self.is_projection()
    
    def __repr__(self):
        s = "BinaryOperation(" + str(self.dom) + ","           
        s += str(self.f)
        s += "," + str(self.comm)
        s += "," + str(self.idem)
        s += ")"
        return s

    def __str__(self):
        s = "* "
        s += (self.dom*"%d ") % tuple(range(self.dom))        
        for a in range(self.dom):
            s += "\n%d " % a
            s += (self.dom*"%d ") % tuple(self[(a,b)] for b in range(self.dom))
        return s + "\n"

    
