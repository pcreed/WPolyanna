from itertools import product, combinations

from wpolyanna.exception import *

class Operation:
    """
    Abstract class for operation object. Each operation has
    a domain and an arity. Methods for changing or applying the
    function are left to be defined in subclasses.
    """

    def __init__(self,arity,dom):
        """
        Creates the abstract part of the instance of Operation.

        :param k: The arity of the operation
        :param dom: The size of the domain
        """
        self.arity = arity
        self.dom = dom

    def __eq__(self,other):
        """         
        :param other: another operation
        :returns: True if both operations are identical, and False otherwise. 

        .. note:: Subclasses should override this operation if there
            is a more efficient implementation for that operation. 
        """
        if self.arity != other.arity or self.dom != other.dom:
            return False
        else:            
            for x in product(range(self.dom),repeat=self.arity):
                if self[x] != other[x]:
                    return False
            return True

    def __hash__(self):
        """ 
        :returns: the hash value of this operation
        :rtype: integer
        
        .. note:: This method must return the sum of the tuple of output values
        of this Operation. This is to ensure that we can compare
        instances of subclasses that are equal, but have different
        classes.
        .. warning:: This method is *abstract* and must be implemented by
            every subclass. 
        """
        return sum(self.value_tuple())

    def __getitem__(self,x):
        """ 
        :param x: an input tuple
        :type x: :tuple of integers
        :returns: the result of applying this operation to x
        :rtype: integer
        :raises: ArityError, DomainError
        
        .. warning:: This method is *abstract* and must be implemented by
        every subclass. 
        """
        abstract
        
    def apply_to_tableau(self,X):
        """ Apply this operation to the columns of a tableau
        
        :param X: matrix of values from the domain with self.arity rows.
        :returns: The tuple resulting from applying this operation to each
        column of the matrix X.
        :rtype: a tuple of integers
        """

        # Error checking
        if len(X) != self.arity:
            raise ArityError(len(X),self.arity)
        for x in X:
            for val in x:
                if val < 0:
                    raise DomainError(val)
                elif val >= self.dom:
                    raise DomainError(val-self.dom)
                
        r = len(X[0])            
        return tuple([self[tuple(X[i][j] for i in range(self.arity))]
                      for j in range(r)])

    def is_projection(self):
        """ Test is this operation is a projection.
        
        :returns: True if this is a projection, i.e., there exists i in [k] such that self(x) = x[i] for all x in [dom]^k, and False otherwise.
        :rtype: boolean
        
        .. note:: This method is expensive and should not be called too
            often. It iterates over all possible inputs and returns false
            as soon as it has verified that this operation cannot be a
            projection. If it manages to iterate over all inputs without
            verifying this, then it returns false, since the operation
            must be a projection.
        """
        p = [True for _ in range(self.arity)]
        for x in product(range(self.dom), repeat=self.arity):
            for i in range(self.arity):
                if self[x] != x[i]:
                    p[i] = False
            if not max(p):
                return False
        return True

    def is_sharp(self):
        """ Test if this operation is sharp
        
        :returns: True if this operation is sharp, i.e. equating any two inputs gives rise to a Projection.
        :rtype: boolean
        """
        if self.is_projection():
            return False
        k = self.arity
        p = [Projection(k-1,self.dom,i) for i in range(k-1)]
        for (a,b) in combinations(range(k),2):
            t = []
            i = 0
            while i < b:
                t.append(p[i])
                i += 1
            t.append(p[a])
            i += 1
            while i < k:
                t.append(p[i-1])
                i += 1
            if not self.compose(t).is_projection():
                return False
        return True

    def check_compose(self,F):
        """ Error handling for composition """
        if len(F) != self.arity:
            raise ArityError(len(F),self.arity)
        if (len(F) > 1
            and not min([F[i].arity == F[i+1].arity
                         for i in range(self.arity-1)])): 
            raise CompositionError([F[i].arity for i in range(self.arity)])
        for f in F:
            if f.dom < self.dom:
                raise DomainError(f.dom-self.dom)
            elif f.dom < self.dom:
                raise DomainError(self.dom-f.dom)
            
    def compose(self,F):
        """ Compose with a list of operations
        
        :param F: a list of Operations to compose with
        :returns: The operation self(g1,g2,...,gk), where k is the arity of this operation and F={g1,g2,...,gk}.
        :rtype: :class:`ExplicitOperation`
        
        .. note:: Subclasses should override this operation if there
            is a more efficient implementation which can return an element
            of that subclass.  
        """
        self.check_compose(F)
        f = dict()
        k = F[0].arity
        for x in product(range(self.dom),repeat=k):
            f[x] = self[tuple(F[i][x] for i in range(self.arity))]
        return ExplicitOperation(k,self.dom,f)

    def restrict(self,A):
        """ Restrict the domain
        
        :returns: An operation defined on the domain {0,1,...,|A|-1} which is isomorphic to the restriction of this operation to A.
        :rtype: :class:`ExplicitOperation`
        """
        newf = dict()
        for t in product(range(len(A)),repeat=self.arity):
            newf[t] = self[tuple(A[i] for i in t)]
        return ExplicitOperation(self.arity,len(A),newf)
    
    def value_tuple(self):
        """ Return the value-tuple representation
        
        :returns: the tuple of output values of this Operation.
        """
        d = self.dom
        k = self.arity
        return tuple(self[x] for x in product(range(d),repeat=k))

    def check_input(self,x):
        # Error checking
        if len(x) != self.arity:
            raise ArityError(len(x), self.arity)
        if max(x) >= self.dom:
            raise DomainError(max(x)-self.dom)
        if min(x) < 0:
            print x
            raise DomainError(min(x))

class ExplicitOperation(Operation):
    """
    A class for an operation defined explicitly by a table mapping
    inputs to output values. This gives a default, but inefficient,
    implementation of the abstract methods of Operation. It is
    recommended that users implement specialised subclasses where
    possible.

    :param arity: The arity.
    :type arity: integer
    :param dom: The size of the domain.
    :type dom: integer
    :param f: The mapping defining this operation.
    :type f: :py:class:`dict` mapping :py:func:`tuple` of integers to
        integers.
    """

    def __init__(self,arity,dom,f):
        """
        Create a new ExplicitOperation object.
        """
        Operation.__init__(self,arity,dom)
        self.f = f

    def __getitem__(self,x):
        """ Apply this operation to a tuple.

        :returns: the value self.f[x]
        :rtype: integer
        """

        Operation.check_input(self,x)
        return self.f[x]

    def __repr__(self):
        """ Return a string representation of this instance of
        ExplicitOperation.
        """
        return "ExplicitOperation(%d, %d, %s)" % (self.arity,
                                                  self.dom,
                                                  repr(self.f))

    def __str__(self):
        """ Return a string containing a description of this operation.

        :returns: A string representation of the dictionary defining
            the operation.
        """
        return str(self.f)
    
class Projection(Operation):
    """
    A class representing a projection operation. This is an operation
    defined by an index, which returns the value at that index on
    every input.

    :param arity: the arity
    :type arity: integer
    :param dom: the domain size
    :type dom: integer
    :param index: the projection index
    :type index: integer
    """

    def __init__(self,arity,dom,index):
        """ Creates a new Projection object.

        :param arity: the arity
        :type arity: integer
        :param dom: the domain size
        :type dom: integer
        :param index: the index to project to
        :type index: integer
        """
        Operation.__init__(self,arity,dom)
        self.index = index

    def __getitem__(self,x):
        """ 
        :returns: the i-th value in x.
        """
        Operation.check_input(self,x)        
        return x[self.index]

    def __repr__(self):
        return "Projection(%d, %d, %d)" % (self.arity,self.dom,self.index)
        
    def __str__(self):
        return "x[%d]" % self.index

    def __eq__(self,other):
        """ 
        :param: other: The Operation to be compared to.
        :type other: Operation
        :returns: True if the other operation is the same projection
        
        .. note:: If the other operation is a projection, we only have to
            check that they both return the same index. Otherwise, we call
            the __eq__ method in Operation to perform the test.
        """
        if other.__class__.__name__ == 'Projection':
            return self.index == other.index
        elif other.__class__.__name__ == 'Semiprojection':
            return min(other[x] == x[other.index]
                       for x in it.permutations(range(other.dom),other.arity))
        else:
            return Operation.__eq__(self,other)

    def __hash__(self):
        """ Return the hash value of this operation.

        :returns: the hash value of this operation. 
        :rtype: integer
        """
        d = self.dom
        k = self.arity
        return sum(i*(d**(k-1)) for i in range(d))
    
    def is_projection(self):
        return True

    def is_sharp(self):
        return False
        
    def compose(self,F):
        """
        :param F: a list of Operations to compose with
        :returns: the i-th component of F
        :rtype: :class:`Operation`
        """
        return F[self.index]

