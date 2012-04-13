import itertools
import random

import pulp
import itertools as it
from wpolyanna import CostFunction
from wpolyanna.submodular import MinMax, Submodular

def sperner(T):
    """
    Returns the Sperner family contained within T. That is, we
    remove all elements of T which are dominated by another. 
    
    :param T: A set of sets.
    :type T: :class:`set` of :class:`set` of integer
    
    :returns: The largest Sperner family contained in t
    :rtype: :class:`set` of :class:`set` of integer
    """
    i = 0
    T = list(map(lambda t: frozenset(t),T))
    while(i < len(T)):
        if sum([a <= T[i] for a in T]) >= 2:
            T.pop(i)
        else:
            i += 1
    return set(T)

def add(S,T):
    return sperner(S.union(T)) 

def mul(S,T):
    return sperner([s.union(t) for s in S for t in T])

def sperner_family(k):
        family = [sperner([set([0])])]
        for i in range(1,k):
            N = len(family)
            
            family.append(sperner([set([i])]))
            
            # x[i] and t
            for T in family[0:N]:
                family.append(mul(family[N],T))

            # x[i] or t
            for T in family[0:N]:
                family.append(add(family[N],T))

            # For each s,t with s <= t, we add s or (x[i] and t)
            for j in range(0,N):
                S = family[j]
                for T in family[j+1:N]:
                    if min([max([t <= s for t in T]) for s in S]):
                        family.append(add(S,mul(family[N],T)))
                    elif min([max([s <= t for s in S]) for t in T]):
                        family.append(add(T,mul(family[N],S)))
        return family

def glb(S):
    glb = S.pop()
    S.add(glb)
    for s in S:
        glb = glb.intersection(s)
        if len(glb) == 0:
            return glb
    return glb

def lub(S):
    lub = set([])
    for s in S:
        lub = lub.union(s)
    return lub

def toSet(x):
    return set([i for i in range(len(x)) if x[i] is 1])

class UpperFan(CostFunction):

    def __init__(self,arity,A):
        self.arity = arity
        self.dom = 2
        self.hash = -1
        self.A = set(map(lambda s: frozenset(s), A))

    def __getitem__(self,x):
        CostFunction.check_input(self,x)
        if toSet(x) >= lub(self.A):
            return -2
        elif max(toSet(x) >= a for a in self.A):
            return -1
        else:
            return 0

    def __str__(self):
        return "UpperFan(%s)" % str(list(map(lambda s: str(list(s)),self.A)))
    
class LowerFan(CostFunction):

    def __init__(self,arity,B):
        self.arity = arity
        self.dom = 2
        self.hash = -1
        self.B = set(map(lambda s: frozenset(s),B))

    def __getitem__(self,x):
        if toSet(x) <= glb(self.B):
            return -2
        elif max(toSet(x) <= b for b in self.B):
            return -1
        else:
            return 0

    def __str__(self):
        return "LowerFan(%s)" % str(list(map(lambda s: str(list(s)),self.B)))
    
def generateFans(n):    
    F = sperner_family(n)
    fans = []
    count = 0
    for S in F:
        if len(S) <= 2:
            fans.append(UpperFan(S))
            fans.append(LowerFan(S))
        elif min(s.intersection(t)==glb(S) for (s,t) in itertools.permutations(S,2)): 
            fans.append(LowerFan(S))
        elif min(s.union(t)==lub(S) for (s,t) in itertools.permutations(S,2)):
            fans.append(UpperFan(S))
        else:
            count += 1
    return fans

class Qin(CostFunction):

    def __init__(self,t):
        self.arity = 4
        self.dom = 2
        self.t = t

    def __getitem__(self,x):
        CostFunction.check_input(self,x)
        if x == (0,0,0,0) or x == (1,1,1,1):
            return -1
        elif x == self.t:
            return 1
        else:
            return 0

    def __str__(self):
        return "Qin(%s)" % str(self.t)
    
def check_submodular(gamma):

    sm = Submodular()

    if sm.improves(gamma):
        print "%s is submodular." % str(gamma)
    else:
        print "%s is not submodular." % str(gamma)

def check_bsm_express(gamma,k):

    mu0 = CostFunction(1,2,{(0,):1,(1,):0})
    mu1 = CostFunction(1,2,{(0,):0,(1,):1})
    omega = CostFunction(2,2,{(0,0,):0,(0,1,):0,(1,0,):1,(1,1,):0})

    C = MinMax.clone(k)
    result = gamma.wpol_separate([mu0,mu1,omega],k,C)
    if result:
        print "%s is not expressible over binary submodular" & str(gamma)
	print str(result)
    else:
        print "%s does not separate on arity %d" % (str(gamma),k) 
    
