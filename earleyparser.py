class ParseTree:

    def __init__(self, label, children):
        self.label = label
        self.children = children

    def __repr__(self):
        return(self.label + "(" + ",".join([ str(c) for c in self.children ]) + ")")

def show_sym(sym):
    if isinstance(sym,str): return('"' + sym + '"')
    if isinstance(sym,N): return(str(sym))

class N:

    def __init__(self,sym):
        self.symbol = sym

    def __repr__(self):
        return(self.symbol + "↓")

    def __eq__(self,other):
        return(isinstance(other,N) and\
               self.symbol == other.symbol)


class Rule:

    def __init__(self,lhs,rhs):
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        return(self.lhs + " -> " + " ".join([ show_sym(sym) for sym in self.rhs ]))

    def __eq__(self,other):
        return(isinstance(other, Rule) and\
               self.lhs == other.lhs and\
               self.rhs == other.rhs)

    def start(self, loc):
        return InProgressRule(self, 0, loc)


class InProgressRule:

    def __init__(self,rule,index,loc,children = [[]]):
        self.rule = rule
        self.index = index
        self.location = loc
        self.children = children

    def __repr__(self):
        return(self.rule.lhs + " -> " + " ".join([ show_sym(sym) for sym in self.rule.rhs[0:self.index] ])\
                 + " . " + " ".join([ show_sym(sym) for sym in self.rule.rhs[self.index:] ])\
                 + " @ " + str(self.location)\
                 + " (children: " + str(self.children) + ")")

    def __eq__(self,other):
        return(isinstance(other, InProgressRule) and\
               self.rule == other.rule and\
               self.index == other.index and\
               self.location == other.location)

    def is_done(self):
        return(self.index == len(self.rule.rhs))

    def next(self):
        if self.is_done():
            return(None)
        else:
            return(InProgressRule(self.rule, self.index+1, self.location, self.children))

    def waiting_for(self):
        if self.is_done():
            return(None)
        else:
            return(self.rule.rhs[self.index])

    def with_new_child(self,child_opts):
        new_children = [ children_option + [child_option] for children_option in self.children for child_option in child_opts ]
        return(InProgressRule(self.rule, self.index,self.location,new_children))

    def complete(self,end):
        parses = [ ParseTree(self.rule.lhs, children_option) for children_option in self.children ]
        return(CompletedRule(self.rule,self.location,end,parses))

class CompletedRule:

    def __init__(self,rule,startloc,endloc,parses):
        self.rule = rule
        self.start_location = startloc
        self.end_location = endloc
        self.parses = parses

    def __repr__(self):
        return(str(self.rule) + " @ " + str(self.start_location) + ":" + str(self.end_location)\
                + " (parses: " + " ".join([ str(t) for t in self.parses ]) + ")")

    def __eq__(self,other):
        return(isinstance(other, CompletedRule) and\
               self.rule == other.rule and\
               self.start_location == other.start_location and\
               self.end_location == other.end_location)


class Grammar:

    def __init__(self, start_sym, rules):
        self.start_symbol = start_sym
        self.rules = rules

    def rules_for_symbol(self,sym):
        return([ r for r in self.rules if r.lhs == sym.symbol ])


class ParseState:

    @classmethod
    def initial_itemsets(self,grammar):
        return([[ r.start(0) for r in grammar.rules_for_symbol(N(grammar.start_symbol)) ]])

    @classmethod
    def construct_parse_tree(completedsets, label, index):
        trees = []

        for item in completedsets[index]:
            if item.rule.lhs == label.symbol:
                pass

        return(trees)

    def __init__(self, grammar, input):
        self.grammar = grammar
        self.input = input
        self.current_token = 0
        self.itemsets = ParseState.initial_itemsets(grammar)
        self.completedsets = [[]]

    def is_done(self):
        return(self.current_token == len(self.input))

    def is_successful(self):
        for item in self.completedsets[self.current_token]:
            if item.rule.lhs == self.grammar.start_symbol and item.start_location == 0:
                return(True)
        return(False)



    def print_info(self):
        if self.is_done():
            print("Input State: Done")
        else:
            print("Input State: ", " ".join(self.input[0:self.current_token]), ">>", self.input[self.current_token], "<<", " ".join(self.input[self.current_token+1:]))
            print("Current Itemset:")
            for item in self.itemsets[self.current_token]: print("  ", item)
        print("Current Completedset:")
        for item in self.completedsets[self.current_token]: print("  ", item)

    def scanner(self):
        itemset = self.itemsets[self.current_token]
        tok = self.input[self.current_token]
        return([ ipr.with_new_child([tok]) for ipr in itemset if ipr.waiting_for() == tok ])

    def step(self):

        # Upward Sweep

        agenda = self.scanner()
        self.current_token += 1
        completed = []
        active = []

        while agenda:
            ipr = agenda.pop().next()
            #print("Processing IPR: ", ipr, " ...")
            if ipr.is_done():
                #print("Done.")
                cr = ipr.complete(self.current_token)
                completed += [cr]
                new_agenda = [ older_ipr.with_new_child(cr.parses) for older_ipr in self.itemsets[ipr.location] if older_ipr.waiting_for() == N(ipr.rule.lhs) ]
                if new_agenda:
                    #print("Adding new agenda items for older IPRs:")
                    for old in new_agenda: print(old)
                    agenda += new_agenda
            else:
                #print("Not done.")
                active += [ipr]
            #print("")

        #print(active)

        # Downward Sweep

        new_itemset = []

        while active:
            ipr = active.pop()
            new_itemset += [ipr]
            sym = ipr.waiting_for()
            if isinstance(sym,N):
                for rule in self.grammar.rules_for_symbol(sym):
                    new_item = rule.start(self.current_token)
                    if new_item not in new_itemset and new_item not in agenda:
                        new_itemset += [new_item]
                        agenda += [new_item]

        #print(new_itemset)

        self.itemsets += [new_itemset]
        self.completedsets += [completed]
