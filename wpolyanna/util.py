def binary_search(L,target):
    """ Find the index of target in a sorted list L.

    :param L: a sorted list
    :param target: an object of the same type of the elements of L

    :returns: the index of of L such that L[i] <= a < L[i+1] and 
    """
    def binsearch(L,target,lo,hi):
        if hi == lo:
            return lo
        if hi == lo + 1:
            if target <= L[lo]:
                return lo
            else:
                return hi            
        else:
            mid = lo+(hi-lo)/2
            if L[mid] == target:
                return mid
            if L[mid] > target:
                return binsearch(L,target,lo,mid)
            else:
                return binsearch(L,target,mid+1,hi)

    if len(L) == 0:
        return 0
    else:
        return binsearch(L,target,0,len(L))
    

    
