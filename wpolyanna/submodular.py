import string

from wpolyanna import Operation, Projection, Clone, WeightedOperation, CostFunction

class MinMax(Operation):
    """ A class for min/max operations

    Each k-ary monotone Boolean function can be defined by a Sperner
    family on [k], S (a set of subsets of [k] none of which contain
    each other). The value of the function is then
    f(x) = max(min(x[i]: i in s): s in S). 

    :Bases: :class:`wpolyanna.poly.Operation`
    
    :param arity: The arity of the operation.
    :type arity: :class:`int`
    :param S: A Sperner family S. 
    :type S: :class:`set` of :class:`set` of :class:`int`, Optional.
    :param dom: The size of the domain over which the operation is defined.  
    :type dom: :class:`int`
    
    .. note:: The default operation is max(x).    
    """
    
    def __init__(self,arity,S=None,dom=2):
        """ Create a new min/max operation. """
        Operation.__init__(self,arity,dom)

        # Default operation
        if S is None:
            S = frozenset(frozenset([i]) for i in range(arity))
        self.S = frozenset(MinMax.sperner(map(lambda s: frozenset(s),S)))

    def __getitem__(self,x):
        """ Return max(t(x) t in S), where each t is a min-term.

        :param x: the input
        """
        Operation.check_input(self,x)
        return max([min([x[i] for i in s]) for s in self.S])

    def __str__(self):
        """ Return a string representation of this operation."""
        # We assume empty S is a constant operation
        if len(self.S) == 0:
            return "0"
        # Need to allow random access
        S = tuple(self.S)
        if len(S) == 1:
            if len(S[0]) == 1:
                return "x[%d]" % tuple(S[0])[0]
            else:
                return (string.join(["min(x[%d]"]
                                    + [",x[%d]"]*(len(S[0])-1)
                                    + [")"],'') % tuple(S[0]))
        else:
            as_str = []
            for s in self.S:
                if len(s) == 1:
                    as_str.append("x[%d]" % tuple(s))
                else:
                    as_str.append(string.join(["min(x[%d]"] 
                                              + [",x[%d]"]*(len(s)-1)
                                              + [")"],'') % tuple(s))
            return (string.join(["max(%s"] + [",%s"]*(len(self.S)-1)
                                + [")"],'') % tuple(as_str))
    
    def __eq__(self,other):
        """
        Test if this operation is equal to another.

        If the other operation is another instance MinMax, then we can
        simply compare the families of sets defining each. Otherwise,
        we use the more expensive compare method from Operation.
        
        :param other: The other operation.
        :type other: :class:`Operation`
        """
        if other.__class__.__name__ == "MinMax":
            return self.S == other.S
        else:
            return Operation.__eq__(self,other)

    def __ne__(self,other):
        """ Check whether this operation is not equal to another.

        :param other: The other operation.
        :type other: :class:`Operation`
        """
        return self.S != other.S
    
    def __le__(self,other):
        """
        Check if this operation is less than or equal to another.

        This method is only defined for MinMax operations. An
        operation is less than another if every element of its Sperner
        family is contains some element of the others Sperner family.

        :param other: The other operation.
        :type other: :class:`MinMax`
        """
        if len(self.S) == 0:
            return True
        if len(self.S) > 0 and len(other.S) == 0:
            return False
        return min([max([t <= s for t in other.S]) for s in self.S])

    def __lt__(self,other):
        """ Test if this operation is strictly less than another.

        :param other: The other operation.
        :type other: :class:`MinMax`
        """
        return self <= other and other != self

    def __ge__(self,other):
        """
        Test if this operation is greater than or equal to another.

        :param other: The other operation.
        :type other: :class:`MinMax`
        """
        return other <= self

    def __gt__(self,other):
        """
        Test if this operation is strictly greater than another.

        :param other: The other operation.
        :type other: :class:`MinMax`
        """
        return self >= other and self != other
    
    def __add__(self,other):
        """
        For MinMax operations addition corresponds to taking the join
        of the two Sperner families.

        :param other: The other operation.
        :type other: :class:`MinMax`
        :rtype: :class:`MinMax`
        """
        return MinMax(self.arity,MinMax.sperner(self.S.union(other.S)),
                      self.dom)

    def __mul__(self,other):
        """
        For MinMax operations, multiplication corresponds to taking
        the meet of the two Sperner families.

        :param other: The other operation.
        :type other: :class:`MinMax`
        :rtype: :class:`MinMax`
        """
        return MinMax(self.arity,
                      MinMax.sperner([s.union(t) for s in self.S for t in
                                      other.S]),
                      self.dom) 
    
    def is_projection(self):
        """
        Test if this MinMax operation is a projection.

        Returns true if the Sperner family contains a single singleton
        set. 
        """
        if len(self.S) != 1:
            return False
        S = tuple(self.S)
        return len(S[0]) == 1

    def compose(self,F):
        """
        Compose this operation with a list of operations.

        :param F: The operations to compose with.
        :type F: :class:`list` of :class:`Operation`

        If every element of F is a MinMax operation, then we can
        compute the composition using addition and multiplication
        (meet and join) of Sperner families. Otherwise, we use the
        more expensive implementation of compose from Operation, and
        return an ExplicitOperation object.
        """

        if not min([f.__class__.__name__ == "MinMax" for f in F]):
            return Operation.compose(self,F)
        f = MinMax(F[0].arity,[],self.dom)
        for s in map(tuple,self.S):
            t = F[s[0]]
            for i in s[1:]:
                t = t * F[i]
            f = f + t
        return f

    def below(self):
        """
        :returns: the set of MinMax operations immediately below.

        This returns the set of MinMax operations of the same arity
        whose Sperner families occur immediately below this operations
        Sperner family, in the lattice of all Sperner families on a
        fixed set. 
        """
        S = tuple(self.S)
        k = self.arity
        ops = []
        for s in S:
            T = self.S - set([s])
            for i in set(range(k)) - s:
                T = T.union([s.union([i])])
            T = MinMax.sperner(T)
            if T != S and len(T) > 0:
                ops.append(MinMax(k,T,self.dom))
        return set(ops)

    @staticmethod
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
        T = list(T)
        while(i < len(T)):
            if sum([a <= T[i] for a in T]) >= 2:
                T.pop(i)
            else:
                i += 1
        return frozenset(T)

    @staticmethod
    def clone(arity,dom=2):
        """ Returns a fixed arity section of the clone generated by min
        and max.
    
        This function generates the {min,max}-clone recursively, using the 
        standard technique for enumerating monotone boolean functions.
    
        :param arity: The arity of the clone generated.
        :type arity: integer
        :param dom: The domain size.
        :type dom: integer, Optional.
        :rtype: :class:`Clone`
        """
        
        # Start with the 0-projection
        clone = [MinMax(arity,[set([0])],dom)]
        for i in range(1,arity):
            N = len(clone)
            
            clone.append(MinMax(arity,[set([i])],dom))
            
            # x[i] and t
            for t in clone[0:N]:
                clone.append(clone[N]*t)

            # x[i] or t
            for t in clone[0:N]:
                clone.append(clone[N]+t)

            # For each s,t with s <= t, we add s or (x[i] and t)
            for j in range(0,N):
                s = clone[j]
                for t in clone[j+1:N]:
                    if s <= t:
                        clone.append(s + clone[N]*t)
                    elif t <= s:
                        clone.append(t + clone[N]*s)

        return Clone(clone)

class Submodular(WeightedOperation):
    """
    A class for the weighted operations defining submodular cost
    functions.

    :Bases: :class:`WeightedOperation`
    """

    def __init__(self,dom=2):
        WeightedOperation.__init__(self,2,dom,
                                   [Projection(2,dom,0), Projection(2,dom,1),
                                    MinMax(2,[[0,1]],dom),
                                    MinMax(2,[[0],[1]],dom)],
                                   [-1,-1,1,1])

    def translations(self,arity,clone=None):
        """ Returns a generating set for the set of all translations
        by elements in the clone. 

        :param arity: the arity
        :param clone: the supporting clone
        :returns: all translations
        :rtype: a list of lists (a matrix)
        
        For the weighted polymorphisms <min,max>, we only need to
        consider translations by pairs of operations whose lub and glb
        are immediately above and below them respectively (in the
        lattice of MinMax operations).

        .. todo: Need to allow comparison of Operations if this is to work for
        larger clones
        """

        if clone is None:
            clone = MinMax.clone(arity,self.dom)
                        
        N = len(clone)
        A = []
        index = dict()
        for i in range(N):
            index[clone[i]] = i
                
        for i in range(N):
            for j in range(i+1,N):
                f = clone[i]
                g = clone[j]
                    
                if (not f < g
                    and not g < f
                    and (f*g in f.below() or g in (f+g).below())
                    and (f*g in g.below() or f in (f+g).below())
                    ):
                    row = [0 for _ in range(N)]
                    row[index[f]] = -1
                    row[index[g]] = -1
                    row[index[f+g]] = 1
                    row[index[f*g]] = 1
                    A.append(row)
        return A

    def in_wclone(self,other,clone=None):
        """
        Tests if another weighted polymorphism is in the weighted clone.

        This method is overloaded so that we use the more efficient
        procedure for generating the min/max clone when no clone is
        passed as input.

        :param other: The weighted operation we have testing.
        :type other: :class:`WeightedOperation`
        :param clone: The supporting clone.
        :type clone: :class:`Clone`
        """

        if clone is None:
            clone = MinMax.clone(other.arity,self.dom)
        return WeightedOperation.in_wclone(self,other,clone)
