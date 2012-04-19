import string, copy
import itertools as it
import cdd, pulp

from wpolyanna.util import binary_search
from wpolyanna.op import Operation
from wpolyanna.clone import Clone
import wpolyanna.cost_function
from wpolyanna.cost_function import CostFunction

"""
This module contains the basic classes and functions for reasoning
about weighted polymorphisms. 
"""
class WeightedOperation:
    """
    A class representing a weighted operation. 

    :param arity: The arity.
    :type arity: integer
    :param dom: The domain size.
    :type dom: integer
    :param ops: The operations given non-zero weight.
    :type ops: :py:func:`list` of :class:`Operation`
    :param weights: The weights.
    :type weights: :py:func:`list` of rationals

    .. note:: For a WeightedOperation object to represent a true
              weighted operation, we require that projections are
              the only operations assigned negative weight.
    """

    def __init__(self,arity,dom,ops,weights):
        """
        Create a new weighted operation.
        """
        self.hash = -1
        self.arity = arity
        self.dom = dom
        self.ops = ops
        for f in self.ops:
            if f.dom != self.dom:
                raise DomainError(f.dom-self.dom)
            if f.arity != self.arity:
                raise ArityError(f.arity,self.arity)
        # Record all non-zero weights
        self.weight = dict()
        for (w,f) in zip(weights,ops):
            if f not in self.weight and w != 0:
                self.weight[f] = w
            elif w != 0:
                self.weight[f] += w
        #self.weights = weights
        #for i in range(len(self.weights)):
        #    if self.weights[i] == 0:
        #        del self.ops[i]
        #        del self.weights[i]

    def get_weight(self,f):
        """ Return the weight of a particular operation.

        :param f: the operation
        :returns: the weight, or 0 if f is not assigned any weight
        """
        try:
            return self.weight[f]
        except KeyError:
            return 0

    def get_support(self):
        """ Return the list of supporting operations. """
        return self.weight.keys()

    def weight_iter(self):
        """ Return an iterator over (operation,weight) pairs. """
        return self.weight.iteritems()

    def __eq__(self,other):
        """ Test for equality. """
        return ( self.dom == other.dom
                 and self.arity == other.arity
                 and self.weight == other.weight)
            
    def __ne__(self,other):
        """ Test for disequality. """
        return not self == other
    
    def __repr__(self):
        ops = []
        weights = []
        for f in self.weight:
            ops.append(f)
            weights.append(self.get_weight(f))
        return "WeightedOperation(%d, %d, %s, %s)" % (self.arity,self.dom,
                                                   ops,weights)
    
    def __str__(self):
        """ Return a string containing a description of this weighted
        operation.

        :returns: A string listing the operations and their associated
        weights.
        :rtype: :py:class:`string`
        """
        pairs = [(w,f) for (f,w) in self.weight_iter()]
        pairs.sort()
        s = "{0}\n{1})\n"
        return string.join([s.format(w,f) for (w,f) in pairs],"")

    def __hash__(self):
        if self.hash < 0:
            self.hash = int(sum(w*hash(f) for (f,w) in self.weight_iter()))
        return self.hash
    
    def imp_ineq(self,r,index=None):
        """ Generate the set of inequalities cost functions improved
        by this weighted operation must satisfy.         

        This method returns a matrix A representing the set 
        of cost function of arity r improved by this weighted operation.
        The method imp uses the double description 
        method to compute the set of extreme rays of the polyhedron
        Ax <= 0, which correspond to a minimal set of cost functions
        that can be used to generate the set of cost functions improved by
        this weighted operation.
        
        :param r: The arity of the cost functions to be generated
        :type r: integer
        :param index: Dictionary mapping tuples to their index, in
            lexicographic order.
        :type index: :py:class:`dict`, Optional
        :returns: The inequality matrix.
        :rtype: :py:func:`list` of :py:func:`list` of integer            
        """
        
        if index is None:
            # Compute an index for the tuples
            index = dict()
            i = 0
            for x in it.product(range(self.dom),repeat=r):
                index[x] = i
                i += 1

        # The inequalities Ax <= 0 will define the cone of cost functions
        A = []        

        # Iterate over the tableaux
        # For each such X, we compute the tableau
        # obtained by applying the operations to X
        # We then generate the constraint this imposes
        # on a cost function, and add this to our matrix,
        # as long as it is non-zero
        D = range(self.dom)
        for X in it.combinations_with_replacement(
            it.product(D,repeat=r),self.arity):
            row = [0 for _ in range(self.dom**r)]
            for f in self.get_support():
                y = f.apply_to_tableau(X)
                row[index[y]] += self.get_weight(f)
            #Y = [f.apply_to_tableau(X) for f in self.ops]
            #for i in range(len(Y)):
            #    row[index[Y[i]]] += self.weights[i]
            if max([i != 0 for i in row]):
                if len(A) == 0:
                    A = [row]
                else:
                    i = binary_search(A,row)
                    if i == len(A) or A[i] != row:
                        A.insert(i,row)
        return A
    
    def imp(self,r,maxcsp=False):
        """ Generate the set of cost functions improved by this
        weighted operation. 
        
        :param r: The arity of the cost functions.
        :type r: integer
        :param maxcsp: Flag to request only {0,1} cost functions are
            returned. 
        :type maxcsp: boolean, optional
        :returns: A minimal generating set for the set of r-ary
            cost functions improved by this weighted operation.
        :rtype: :py:class:`set` of :class:`CostFunction`
        """

        A = []
        
        # All costs >= 0
        for i in range(self.dom**r):
            row = [0 for _ in range(self.dom**r+1)]
            row[i+1] = 1
            A.append(row)

        # If MaxCSP we have all costs <= 1
        if maxcsp:
            for i in range(self.dom**r):
                row = [0 for _ in range(self.dom**r+1)]
                row[i+1] = -1
                row[0] = -1
            A.append(row)
            
        # Get the imp inequalities
        for row in self.imp_ineq(r):
            if not row in A:
                A.append([0] + map(lambda x: -x, row))
                
        ineq_matrix = cdd.Matrix(A)
        imp_polyhedron = cdd.Polyhedron(ineq_matrix)
        ray_mat = imp_polyhedron.get_generators()
        cost_functions = []
        D = range(self.dom)
        for c in range(ray_mat.row_size):
            cf = dict()
            i = 1
            for x in it.product(D,repeat=r):
                # We round to dom places after the decimal point
                cf[x] = round(ray_mat[c][i],self.dom)
                i += 1            
            cost_functions.append(CostFunction(r,self.dom,cf))
        return cost_functions

    def improves(self,cf):
        """ Test if this weighted operation improves a particular cost
        function. If the cost function is not improved, then we return
        a certificate of this fact.

        :param cf: The cost function we are checking.
        :type cf: :class:`CostFunction`
        :returns: The first violated inequality, if cf is not improved
            by this weighted operation, and an empty list otherwise.
        :rtype: :py:func:`list` of rational
        """
        r = cf.arity
        D = range(self.dom)
        # Compute an ordered list of tuples
        tuples = []
        for x in it.product(D,repeat=r):
            tuples.append(x)
        for e in self.imp_ineq(r):
            if sum(cf[tuples[i]]*e[i] for i in range(len(e)) if e[i] != 0) > 0:
                return False,e
        return True
    
    def translations(self,arity,clone=None):
        """ Return the set of translations by elements of a clone.

        :param clone: The clone we want to translate by.
        :type clone: :class:`Clone`, Optional
        :returns: The matrix of translations, with columns index by the
            clone. Each row corresponds to a single translation,
            storing the weight assigned to the i-th operation in the
            clone at the i-th location.
        :rtype: :class:`cdd.Matrix`

        .. note:: If no clone is passed as input, we use the smallest
            clone containing all the elements of self.ops.
        """

        if clone is None:
            clone = Clone.generate(self.ops,arity)
        
        # Generate an index for the elements of the clone
        N = len(clone)
        index = dict()
        for i in range(N):
            index[clone[i]] = i
        
        # Each tuple of terms in the clone gives rise to a generator
        A = []
        for t in it.product(range(N),repeat=self.arity):
            F = [clone[i] for i in t]
            row = [0 for _ in range(N)]
            for (f,w) in self.weight_iter():#zip(self.ops,self.weights):
                try: 
                    row[index[f.compose(F)]] += w
                except KeyError:
                    raise KeyError
            # Add non-zero rows if they are are not already in A.
            # We keep A sorted to make this check more efficient
            if min(row) != 0:
                if len(A) == 0:
                    A = [row]
                else:
                    i = binary_search(A,row)
                    if i == len(A) or A[i] != row:
                        A.insert(i,row)
        return A
    
    def in_wclone(self,other,clone=None):
        """ Test if another weighted operation is in the weighted
        clone generated by this weighted operation. 

        :param other: The other weighted operation.
        :type other: :class:`WeightedOperation`
        :param clone: The supporting clone (this must be of the same
            arity as other) and all operations of w must be contained
            in clone.  
        :type clone: :class:`Clone`, Optional
        :returns: True if other is contained in the weighted clone,
            False otherwise. If True, we also return a certificate,
            which is a list of pairs of weights and translations. If
            False, we return a separating cost function.  
        :rtype: (boolean,:py:func:`list`)

        .. note: If no clone is passed as input, we use the method
            Clone.generate to obtain the clone.
        """
        
        if clone is None:
            # Use the clone generated by the operations in self.ops
            clone = Clone.generate(self.ops,other.arity)

        # All operations in other must be contained in the clone
        for f in other.ops:
            if not f in clone:
                return False
            
        N = len(clone)
        A = self.translations(other.arity,clone)

        prob = pulp.LpProblem()

        # A variable for each non-redundant translation
        y = pulp.LpVariable.dicts("y",range(len(A)),0)

        # No objective function
        prob += 0

        for j in range(N):
            #k = other.ops.index(clone[j])
            prob += (sum([A[i][j]*y[i] for i in range(len(A))])
                     == other.get_weight(clone[j]))            

        prob.solve()

        if pulp.LpStatus[prob.status] == 'Optimal':
            cert = []
            for i in range(len(A)):
                val = round(pulp.value(y[i]),self.dom)
                if val != 0:
                    cert.append((val,
                                 [(A[i][j],str(clone[j])) for j in range(N)
                                  if A[i][j] != 0]))
            return (True,cert)
        # If no solution, then solve the dual
        # Need to figure out better method than this. Should be able
        # to use values of primal variables on termination.
        else:
            prob = pulp.LpProblem()

            # A variable for each non-redundant translation
            z = pulp.LpVariable.dicts("z",range(N),0)

            # No objective function
            prob += 0

            for i in range(len(A)):
                prob += (pulp.lpSum([A[i][j]*z[j] for j in range(N)]) <= 0, "")
            prob += pulp.lpSum([w*z[clone.index(f)]
                           for (f,w) in other.weight_iter()]) >= 1,""
            prob.solve()
            costs = dict()
            for i in range(N):
                costs[clone[i].value_tuple()] = round(pulp.value(z[i]),
                                                      self.dom)                
            return (False,CostFunction(len(costs.keys()[0]),self.dom,costs))

    def wclone(self,k,clone=None,log=False):
        """ Returns the weighted clone generated by this weighted
        operation.   

        :param k: The arity.
        :type k: integer
        :param clone: The supporting clone.    
        :type clone: :class:`Clone`, optional
        :returns: A list of k-ary weighted operations which added together
            to get any k-ary element of the weighted clone.
        :rtype: :py:func:`list` of :class:`WeightedOperation`
            
        .. note::
            At the moment, this is implemented rather crudely, requiring
            two calls to CDD. The first obtains a set of inequalities
            defining the cone generated by the translations. Then,
            inequalities to ensure that only projections receive positive
            weight are added and this new set of inequalities are used to
            obtain a set of generators for the cone of k-ary elements in
            the weighted clone.
        """

        if clone is None:
            clone = Clone.generate(self.ops,k)
            if log:
                print "Computed Clone"
            
        # First, get the inequalities defining the cone generated by
        # the translations
        T = self.translations(k,clone)        
        T = map(lambda row: [0] + row, T)
        
            
        trans_mat = cdd.Matrix(T)
        trans_mat.rep_type = cdd.RepType.GENERATOR
        trans_mat.canonicalize()
        if log:
            print "Computed Translations"
            for r in T:
                print r
            
        trans_poly = cdd.Polyhedron(trans_mat)
        A = trans_poly.get_inequalities()        
            
        # Next, add inequalities to ensure that non-projections cannot
        # receive negitive weight.
        # Recall that the projections will always be the first k
        # elements of the clone
        wop_ineq = [[0 for _ in range(len(clone)+1)]
                    for _ in range(k,len(clone))]
        for i in range(k,len(clone)):
            wop_ineq[i-k][i+1] = 1
        A.extend(wop_ineq)
        A.canonicalize()
        if log:
            print "Computed Inequalities"
            for a in A:
                print a

        # Finally, compute generators for the weighted clone
        wclone_mat = cdd.Matrix(A)
        wclone_poly = cdd.Polyhedron(A)
        wclone_gen = wclone_poly.get_generators()

        if log:
            print "Computed Generators"
        wclone = []
        for r in wclone_gen:
            ops = []
            weights = []
            if log:
                print r
            for i in range(1,len(r)):
                rval = round(r[i],self.dom)
                if rval != 0:
                    ops.append(clone[i-1])
                    weights.append(rval)
            wclone.append(WeightedOperation(k,self.dom,ops,weights))
        return wclone
