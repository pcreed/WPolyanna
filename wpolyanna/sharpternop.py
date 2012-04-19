from itertools import product, permutations
import wpolyanna
from wpolyanna import Operation, Projection


class SharpTernary(Operation):
    """
    This is a class for a sharp ternary operations. These are
    important as all known tractable VCSP languages are defined by
    weighted operations whose positively weighted operations are
    binary or ternary sharp operations.

    :param pos: the array giving the position of the input whose
    value is returned for each of the three cases where two
    inputs are equal
    :param vals: the mapping for all distinct tuples
    """

    def __init__(self,dom,pos,vals):
        Operation.__init__(self,3,dom)
        self.pos = tuple(pos)
        self.vals = vals

    def __getitem__(self,x):
        Operation.check_input(self,x)
        if x[0] == x[1]:
            return x[self.pos[0]]
        elif x[0] == x[2]:
            return x[self.pos[1]]
        elif x[1] == x[2]:
            return x[self.pos[2]]
        else:
            return self.vals[x]
    
    def __eq__(self,other):
        if other.__class__.__name__ == "SharpTernary":
            return (self.dom == other.dom 
                    and self.pos == other.pos
                    and self.vals == other.vals)
        else:
            return Operation.__eq__(self,other)

    def __repr__(self):
        return "SharpTernary(%d,%s,%s)" % (self.dom,str(self.pos),str(self.vals))

    def compose(self,F):
        F = list(F)
        
        # Convert all projections to SharpTernary objects
        for i in [0,1,2]: 
            if F[i].__class__.__name__ == "Projection":
                F[i] = SharpTernary(F[i].dom,[F[i].index for _ in [0,1,2]],
                              {x:x[F[i].index] for x in permutations([0,1,2],3)})

        # Compute the positions for the 3 cases for equal inputs
        pos = [0,0,0]
        a = [F[0].pos[0],F[1].pos[0],F[2].pos[0]]
        for i in [0,1,2]:
            if a[i] == 1:
                a[i] = 0
        pos[0] = self[a]

        b = [F[0].pos[1],F[1].pos[1],F[2].pos[1]]
        for i in [0,1,2]:
            if b[i] == 2:
                b[i] = 0
        pos[1] = self[b]

        c = [F[0].pos[2],F[1].pos[2],F[2].pos[2]]
        for i in [0,1,2]:
            if c[i] == 2:
                c[i] = 1
        pos[2] = self[c]

        # Compute the values for distinct inputs
        vals = {}
        for x in permutations(range(self.dom),3):
            vals[x] = self[F[0][x],F[1][x],F[2][x]]
        
        return SharpTernary(self.dom,pos,vals)

# Functions for creating the sharp ternary operations of the different types
def majority(dom,vals):
    return SharpTernary(dom,[0,0,1],vals)

def minority(dom,vals):
    return SharpTernary(dom,[2,1,0],vals)

def semiproj(dom,index,vals):
    return SharpTernary(dom,[index,index,index],vals)

def pixley(dom,index,vals):
    if index == 0:
        return SharpTernary(dom,(2,1,1),vals)
    elif index == 1:
        return SharpTernary(dom,(2,0,0),vals)
    elif index == 2:
        return SharpTernary(dom,(0,1,0),vals)

