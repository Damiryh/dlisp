from dlangtools.lex import CharIterator

class Atom:
  is_atom = True

class Number(Atom):
  def __init__(self, value):
    self.value = value

  def __repr__(self):
    return str(self.value)

  def eval(self, env):
    return self

class Symbol(Atom):
  def __init__(self, word):
    self.word = word

  def __repr__(self):
    return  self.word

  def eval(self, env):
    return env[self.word]

class Function(Atom):
  def __init__(self, sign, body):
    self.body = body
    self.sign = sign

  def __repr__(self):
    return 'lambda' + str(self.sign)

  def call(self, env, args):
    for k, v in zip(self.sign.elements, args):
      env[k.word] = v
    return self.body.eval(env)

class List:
  def __init__(self, elements):
    self.elements = elements

  def __repr__(self):
    return '(' + ' '.join([
      str(el) for el in self.elements
    ]) + ')'


  def eval(self, env):
    head, *args = self.elements
    fname = head.word

    def prepare_args(args):
      return [ arg.eval(env) for arg in args ]

    if fname == '+' and len(args) > 0:
      return Number(sum([
        arg.eval(env).value for arg
        in prepare_args(args)
      ]))
    elif fname == 'cons' and len(args) == 2:
      args = prepare_args(args)
      return List([
        args[0], *args[1].elements,
      ])
    elif fname == 'eval' and len(args) == 1:
      return prepare_args(args)[0].eval(env)
    elif fname == 'quote' and len(args) == 1:
      return args[0]
    elif fname == 'lambda' and len(args) == 2:
      sign, body = args
      return Function(sign, body)
    elif fname == 'apply' and len(args) >= 1:
      func, *args = prepare_args(args)
      subenv = env.copy()
      return func.call(subenv, args)
    elif fname == 'head' and len(args) == 1:
      args = prepare_args(args)
      return args[0].elements[0]
    elif fname == 'tail' and len(args) == 1:
      args = prepare_args(args)
      return List(args[0].elements[1:])
    elif fname == 'cons' and len(args) == 2:
      args = prepare_args(args)
      return List([ args[0], *args[1].elements ])
    else:
      assert False, 'Not implemented'

ast = List([
  Symbol('eval'),
  List([
    Symbol('cons'),
    Symbol('+'),
    List([
      Symbol('quote'),
      List([
        Number(1),
        Number(2),
        Number(3),
      ])
    ])
  ])
])

ast = List([
  Symbol('apply'),
  List([
    Symbol('lambda'),
      List([
        Symbol('a'),
        Symbol('b'),
      ]),
    List([
      Symbol('+'),
      Symbol('a'),
      Symbol('b'),
    ])
  ]),
  Number(1),
  Number(2),
])

ast = List([
  Symbol('tail'),
  List([
    Symbol('quote'),
    List([
      Number(1),
      Number(2),
      Number(3),
    ]),
  ]),
])

ast = List([
  Symbol('cons'),
  Number(123312),
  List([
    Symbol('quote'),
    List([
      Number(4234),
      Number(23),
    ])
  ])
])

env = dict()

print(ast)
result = ast.eval(env)
print(result)

def tokenize(s):
  it = CharIterator(s)
  tokens = []

  while not it.end():
    if it.check(str.isspace):
      it.skip(str.isspace)
    elif it.check('()'):
      tokens.append(it.next())
    elif it.check(str.isnumeric):
      number = it.consume(str.isnumeric)
      assert not it.check(str.isalpha)
      tokens.append(int(number))
    else:
      tokens.append(it.consume(
        lambda c: not (c in '()' or c.isspace())
      ))

  return tokens

def parse(tokens):
  pos = 0

  def next():
    nonlocal pos
    pos += 1
    return tokens[pos-1]

  def t():
    return tokens[pos]

  def lst():
    elements = []
    next()
    while t() != ')':
      assert pos < len(tokens), 'Unpaired "("'
      elements.append(stmt())
    assert next() == ')', 'Unpaired "("'
    return List(elements)

  def stmt():
    if t() == '(': return lst()
    elif type(t()) == int:
      return Number(next())
    else:
      return Symbol(next())

  ast = stmt()
  assert pos == len(tokens), 'Unpaired ")"'
  return ast

tokens = tokenize('''
  (apply (lambda (a b c) (+ a b c)) 1 2 3)
''')

print(tokens)

ast = parse(tokens)
print(ast)
r = ast.eval(env)
print(r)
