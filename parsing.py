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

    def end(): return pos >= len(tokens)

    def t(): return tokens[pos] if not end() else None

    def next():
        nonlocal pos
        current = t()
        pos += 1
        return current

    def lst():
        elements = []
        next() # skip (
        if t() == ')': next(); return Nil()

        while not end() and t() != ')':
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
        elif t() == 'T':
            next(); return T()
        elif t() == 'NIL':
            next(); return Nil()
        elif t() == None:
            return Nil()
        else:
            return Symbol(next())

    ast = stmt()
    assert pos == len(tokens), 'Unpaired ")"'
    return ast
