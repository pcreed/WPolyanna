class CompositionError(Exception):

    def __init__(self,t):
        self.t = t;

class ArityError(Exception):

    def __init__(self,actual,expected):
        self.actual = actual
        self.expected = expected

class DomainError(Exception):

    def __init__(self,diff):
        self.diff = diff

    def __repr__(self):
        return "DomainError(" + diff + ")"
