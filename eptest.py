from earleyparser import *

g = Grammar("S",\
            [ Rule("S", ["a", "b"])\
            , Rule("S", ["a", N("S"), "b"])\
            , Rule("S", ["c"])\
            ])
print("Grammar: ", g.rules)

ps = ParseState(g, ["a", "a", "b", "b"])
print("Parse State Initial Itemsets: ", ps.itemsets)
