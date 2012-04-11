import itertools as it
import cdd

from wpolyanna.exception import *
import wpolyanna.wop
from wpolyanna.clone import Clone

class CostFunction:
    """ A class representing cost functions. 

    :param arity: The arity.
    :type arity: integer
    :param dom: The size of the domain.
    :type dom: integer
    :param costs: The finite costs.
    :type costs: :py:class:`dict` mapping :py:func:`tuple` of integer to
        rational 

    .. note:: At the moment, the program is only designed to handle
        cost functions in which every tuple is assigned a finite value.
    """
    
    def __init__(self,arity,dom,costs):
        """ Create a new cost function. """
        self.arity = arity
        self.dom = dom
        self.costs = costs
        self.hash = -1
        
    def __getitem__(self,x):
        """Return the cost of a particular tuple. """

        # Error checking
        if len(x) != self.arity:
            raise ArityError(len(x),self.arity)
        for d in x:
            if d < 0:
                raise DomainError(d)
            elif d >= self.dom:
                raise DomainError(d-self.dom)
            
        return self.costs[x]

    def __eq__(self,other):
        """ Test for equality. """
        return (self.dom == other.dom
                and self.arity == other.arity
                and self.costs == other.costs)
            
    def __ne__(self,other):
        """ Test for disequality. """
        return not self == other

    def __hash__(self):
        if self.hash < 0:
            self.hash = int(self.arity + self.dom + sum(self.costs.values()))
        return self.hash
    
    def __repr__(self):
        return "CostFunction(%d, %d, %s)" % (self.arity,self.dom,str(self.costs))
    
    def __str__(self):
        """Return a string representation of this cost function. """
        s = "%d %d\n" % (self.arity,self.dom)
        pairs = zip(self.costs.keys(),self.costs.values())
        for (t,c) in pairs:
            s += "%s %f\n" % (str(t),c)
        return s

    def cost_tuple(self):
        """Return the tuple of costs, in lexicographic order. """
        
        costs = []
        for t in it.product(range(self.dom),repeat=self.arity  ):
            costs.append(self[t])
        return tuple(costs)

    def wpol_ineq(self,arity,clone=None):
        """ Return the set of inequalities the weighted polymorphisms
        must satisfy.

        This method returns a matrix A, such that the set of weighted
        operations satisfying Aw <= 0 are the weighted polymorphisms
        of this cost function. 
        :param arity: The arity of the weighted polymorphisms.
        :type arity: integer
        :param clone: The supporting clone.
        :type clone: :class:`Clone`, Optional
        :returns: A set of inequalities defining the weighted
            polymorphisms.
        :rtype: :class:`cdd.Matrix`
        
        ..note:: We implicity assume that clone is a subset of the set
            of feasibility polymorphisms. If no clone is passed as an
            argument, then we use the clone containing all operations.
        """
        if clone is None:
            clone = Clone.all_operations(arity,self.dom)
            
        # N is the number of operations in the clone. We will need a
        # variable for each of these
        N = len(clone)
        ineqs = []

        # Divide the tuples into sets of zero and non-zero cost 
        r = self.arity
        D = range(self.dom)
        T = [[],[]]
        neg,pos = False,False
        for t in it.product(D,repeat=r):
            if self[t] == 0:
                T[0].append(t)
            else:
                T[1].append(t)
                if self[t] > 0:
                    pos = True
                elif self[t] < 0:
                    neg = True
        
        # Tableaus containing at least one non-zero tuple
        for comb in it.product([0,1],repeat=arity):
            if sum(comb) > 0:
                for X in it.product(*[T[i] for i in comb]):
                    row = [0 for _ in range(N+1)]   
                    for i in xrange(0,N):
                        row[i+1] = self[clone[i].apply_to_tableau(X)]
                    if not row in ineqs:
                        ineqs.append(row)

        # We only need tableaus with all zero tuples if there are some
        # positive weighted tuples
        if pos:
            for X in it.product(T[0],repeat=arity):
                row = [0 for _ in range(N+1)]
                trivial = True
                for i in xrange(0,N):
                    row[i+1] = self[clone[i].apply_to_tableau(X)]
                    if row[i+1] != 0:
                        trivial = False
                if not row in ineqs and not trivial:
                    ineqs.append(row)     

        return ineqs

    def wop_ineq(self,arity,clone=None):
        """ Returns the set of inequalities defining a weighted operation.
        """
        if clone is None:
            # |D|^(|D|^r) r-ary operations on D
            N = self.dom**(self.dom**arity)
        else:
            N = len(clone)
        ineqs = []
        # All non-projections are non-negative
        for i in xrange(arity,N):
            row = [0 for _ in range(N+1)]
            row[i+1] = -1
            ineqs.append(row)

        # All weights sum to 0
        ineqs.append([0] + [1 for _ in range(N)])
        ineqs.append([0] + [-1 for _ in range(N)])

        return ineqs
    
    def wpol(self,arity,clone=None,multimorphisms=False):
        """ Return the weighted polymorphisms.

        This method obtains the matrix of inequalities defining the
        weighted polymorphisms and uses CDD to compute a set of
        generators for the cone defined by these inequalities.
        
        :param arity: The arity.
        :type arity: integer
        :param clone: The supporting clone.
        :type clone: :class:`Clone`, Optional
        :param multimorphisms: Flag to request we only generate
            multimorphisms.
        :type multimorphisms: boolean, optional

        .. note:: We implicitly assume that any clone passed in to the
            function is a subset of the set of feasibility polymorphisms.

        .. note:: The part of the code which automatically computes the
            clone of feasibility polymorphisms is not yet implemented, so
            a user will have to compute the clone separately and pass it
            as input.
        """
        if clone is None:
            clone = Clone.all_operations(arity,self.dom)
        N = len(clone)
        ineqs = self.wop_ineq(arity,clone)
        
        # Get the weighted polymorphism inequalities
        for row in self.wpol_ineq(arity,clone):
            if not row in ineqs:
                ineqs.append(row)

        poly = cdd.Polyhedron(cdd.Matrix(ineqs))
        ray_mat = poly.get_generators()
        W = []
        for i in range(ray_mat.row_size):
            weights = []
            ops = []
            for j in range(N):
                rval = round(ray_mat[i][j+1],self.dom)
                if rval != 0:
                    weights.append(-rval)
                    ops.append(clone[j])
            W.append(wpolyanna.wop.WeightedOperation(arity,
                                                     self.dom,
                                                     ops,
                                                     weights))
        return W

    def wpol_separate(self,other,arity,clone=None):
        """ Test if other cannot be expressed over this cost function.

        :param other: the other cost function
        :returns: A separating weighted polymorphism if it exists and
        false otherwise.
        """
        if clone is None:
            clone = Clone.all_operations(self.dom,arity)
        A = self.wop.ineqs(arity,clone)
        A += self.wpol_ineqs(arity,clone)

        # For each wpol inequality of other, check if there
        # exists a wpol of this wop violating it
        for c in other.wpol_ineqs(arity,clone):

            prob = pulp.LpProblem()

            # One variable for each operation in the clone
            y = pulp.LpVariable.dicts("y",xrange(N))

            # Must satisfy all inequalities in A
            for a in A:
                prob += sum(y[i]*a[i+1] for i in xrange(N)) >= 0

            # Must violate c
            prob += sum(y[i]*c[i+1] for i in range(N)) <= 1

            prob.solve()

            if pulp.LpStatus[prob.status] == 'Optimal':
                op = []
                w = []
                for i in xrange(N):
                    yval = round(pulp.value(y[i]),self.dom)
                    if yval != 0:
                        op.append(clone[i])
                        w.append(yval)
                return WeightedOperation(self.dom,arity,op,w)
            
        # Return false if we couldn't find a separating wop
        return False
        
# Global functions
def wpol(cost_functions,arity,clone=None,multimorphisms=False):
    """ Return the weighted polymorphisms.

    This method obtains the matrix of inequalities defining the
    weighted polymorphisms and uses CDD to compute a set of
    generators for the cone defined by these inequalities.
        
    :param arity: The arity.
    :type arity: integer
    :param clone: The supporting clone.
    :type clone: :class:`Clone`, optional
    :param multimorphisms: Flag to request we only generate
        multimorphisms.
    :type multimorphisms: boolean, optional

    .. note:: We implicitly assume that any clone passed in to the
        function is a subset of the set of feasibility polymorphisms.

    .. note:: The part of the code which automatically computes the
        clone of feasibility polymorphisms is not yet implemented, so
        a user will have to compute the clone separately and pass it
        as input.
    """
    if len(cost_functions) == 0:
        return []
    d = cost_functions[0].dom
    if clone is None:
        clone = Clone.all_operations(arity,d)
    N = len(clone)
    A = cost_functions[0].wop_ineq(arity,clone)

    # If we are only looking for multimorphisms, then we
    # have all projections with weight exactly 1
    if multimorphisms:
        for i in range(arity):
            row = [1] + [0 for _ in range(N)]
            row[i+1] = 1
            A.append(row)
            row = [-1] + [0 for _ in range(N)]
            row[i+1] = -1
            A.append(row)

    # Get the weighted polymorphism inequalities for each
    # cost function
    for cf in cost_functions:
        # Get the weighted polymorphism inequalities
        for row in cf.wpol_ineq(arity,clone):
            if not row in A:
                A.append(row)
                          
    poly = cdd.Polyhedron(cdd.Matrix(A))
    ray_mat = poly.get_generators()
    W = []
    for i in range(ray_mat.row_size):
        weights = []
        ops = []
        for j in range(N):
            rval = round(ray_mat[i][j+1],d)
            if rval != 0:
                weights.append(-rval)
                ops.append(clone[j])
        W.append(wpolyanna.wop.WeightedOperation(arity,d,ops,weights))
    return W
