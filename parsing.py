from dlangtools.lex import CharIterator
from ast import *

def tokenize(s):
    s = s.replace('()', ' NIL ')
    it = CharIterator(s)
    tokens = []

    while not it.end():
        if it.check(str.isspace): it.skip(str.isspace)
        elif it.check('()'): tokens.append(it.next())
        elif it.check("'"): tokens.append(it.next())
        elif it.check(str.isnumeric):
            number = it.consume(str.isnumeric)
            assert not it.check(str.isalpha)
            tokens.append(int(number))
        else:
            word = it.consume(
                lambda c: not (c in '()' or c.isspace())
            )
            tokens.append(word)

    return tokens

def parse(tokens):
    pos = 0

    def next():
        nonlocal pos
        pos += 1
        return tokens[pos-1]

    def t(): return tokens[pos]

    def lst():
        elements = []
        next()
        while t() != ')':
            assert pos < len(tokens), 'Unpaired "("'
            elements.append(stmt())
        assert next() == ')', 'Unpaired "("'
        return List(elements)

    def quote():
        next()
        return List([Symbol('quote'), stmt()])

    def stmt():
        if t() == '(': return lst()
        elif t() == "'": return quote()
        elif t() == 'T':
            next(); return T()
        elif t() == 'NIL':
            next(); return Nil()
        elif type(t()) == int:
            return Number(next())
        else:
            return Symbol(next())

    ast = stmt()
    assert pos == len(tokens), 'Unpaired ")"'
    return ast
