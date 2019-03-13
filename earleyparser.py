class Rule:

    def __init__(self,lhs,rhs):
        self.lhs = lhs
        self.rhs = rhs

class InProgressRule:

    def __init__(self,lhs,rhs_done,rhs_next):
        self.lhs = lhs
        self.rhs_done = rhs_done
        self.rhs_next = rhs_next

    def is_done(self):
        return(0 == len(self.rhs_next))

    def next(self):
        if self.is_done():
            return(None)
        else:
            return(InProgressRule(self.lhs, self.rhs_done + self.rhs_next[0:1], self.rhs_next[1:]))

    def __eq__(self,other):
        return(self.lhs == other.lhs and\
               self.rhs_done == other.rhs_done and\
               self.rhs_next == other.rhs_next)

    def __repr__(self):
        return(self.lhs + " -> " + " ".join(self.rhs_done) + " . " + " ".join(self.rhs_next))
