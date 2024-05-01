class UndefinedValueException(Exception):
    def __init__(self, variable_name):
        self.variable_name = variable_name
        super().__init__(
            f'Attempt to access an undefined value "{variable_name}"'
        )


class WrongArgumentsException(Exception):
    def __init__(self, expected, got):
        self.expected = expected
        self.got = got

    def __repr__(self):
        return f'expected "{self.expected}", but got "{self.got}"'

class Atom: pass


class Number(Atom):
    def __init__(self, value):
        self.value = value

    def __repr__(self): return str(self.value)
    def eval(self, env): return self

    def __add__(self, b): return Number(self.value + b.value)
    def __sub__(self, b): return Number(self.value - b.value)
    def __neg__(self): return Number(-self.value)

    @staticmethod
    def sum(numbers):
        return sum(numbers, start=Number(0))


class Symbol(Atom):
    def __init__(self, word):
        self.word = word

    def __repr__(self): return self.word

    def eval(self, env):
        return env[self.word]


class Function(Atom):
    def __init__(self, context, sign, body):
        self.context = context
        self.body = body
        self.sign = sign

    def __repr__(self):
        return 'lambda' + str(self.sign)

    def call(self, args):
        subenv = self.context.subenv(zip(self.sign.elements, args))
        return self.body.eval(subenv)


# ==== Args checking functions  ====

def as_list(arg):
    if type(arg) != List:
        raise WrongArgumentsException(List, type(arg))
    return arg

def as_number(arg):
    if type(arg) != Number:
        raise WrongArgumentsException(Number, type(arg))
    return arg

def as_symbol(arg):
    if type(arg) != Symbol:
        raise WrongArgumentsException(Symbol, type(arg))
    return arg

def as_func(arg):
    if type(arg) != Function:
        raise WrongArgumentsException(Function, type(arg))
    return arg

ONE_OR_MORE = -1 # Const for check args length

def check_length(args, length):
    if length == ONE_OR_MORE:
        if len(args) < 1: raise WrongArgumentsException()
    elif len(args) != length:
        raise WrongArgumentsException(None, None)

# ==================================

# ========= Environment ============

class Environment:
    def __init__(self, parent=None):
        self.parent = parent
        self.variables = dict()

    def __getitem__(self, key):
        if key in self.variables.keys():
           return self.variables[key]
        elif self.parent != None:
           return self.parent[key]
        else: raise UndefinedValueException(key)

    def __repr__(self):
        return str(self.parent) + ' {\n' + ''.join([
            f'  {key}: {value}\n'
            for key, value in self.variables.items()
        ]) + '}'

    def __setitem__(self, key, value):
        self.variables[key] = value

    def subenv(self, args=dict()):
        env = Environment(self)
        for key, value in args: env[key.word] = value
        return env

# ==================================

class List:
    def __init__(self, elements):
        self.elements = elements

    def __repr__(self):
        return '(' + ' '.join([ str(el) for el in self.elements ]) + ')'

    def __iter__(self): return self.elements.__iter__()
    def __getitem__(self, index): return self.elements[index]
    
    def eval(self, env):
        head, *args = self.elements
        fname = as_symbol(head).word

        def prepare(args):
            return [ arg.eval(env) for arg in args ]

        if fname == '+':
            check_length(args, ONE_OR_MORE)
            args = prepare(args)
            return Number.sum([ as_number(arg) for arg in args ])

        elif fname == '-':
            check_length(args, ONE_OR_MORE)
            args = prepare(args)
            if len(args) == 1: return -as_number(args[0])
            else: return as_number(args[0]) - Number.sum([
                as_number(arg) for arg in args[1:]
            ])

        elif fname == 'cons':
            check_length(args, 2)
            args = prepare(args)
            head, tail = args[0], as_list(args[1])
            return List([ head, *tail ])

        elif fname == 'eval':
            check_length(args, 1)
            args = prepare(args)
            return args[0].eval(env)

        elif fname == 'quote':
            check_length(args, 1)
            return args[0]

        elif fname == 'lambda':
            check_length(args, 2)
            sign, body = as_list(args[0]), args[1]
            for variable in sign.elements: as_symbol(variable)
            return Function(env, sign, body)

        elif fname == 'call':
            check_length(args, ONE_OR_MORE)
            func, *args = prepare(args)
            return func.call(args)

        elif fname == 'head':
            check_length(args, 1)
            args = prepare(args)
            return as_list(args[0])[0]

        elif fname == 'tail':
            check_length(args, 1)
            args = prepare(args)
            return List(as_list(args[0])[1:])

        elif fname == 'set':
            check_length(args, 2)
            args = prepare(args)
            name, value = as_symbol(args[0]), args[1]
            env[name.word] = value
            return name

        elif fname == 'progn':
            check_length(args, ONE_OR_MORE)
            args = prepare(args)
            return args[-1]

        elif fname == 'apply':
            check_length(args, 2)
            args = prepare(args)
            func, args = as_func(args[0]), as_list(args[1])
            return func.call(args[:])

        elif fname == 'map':
            check_length(args, 2)
            args = prepare(args)
            func, lst = as_func(args[0]), as_list(args[1])
            return List([func.call([el]) for el in lst])

        elif fname == 'reduce':
            check_length(args, 3)
            args = prepare(args)
            func, start, lst = as_func(args[0]), args[1], as_list(args[2])

            result = start
            for el in lst: result = func.call([result, el])
            return result

        

        elif func := as_func(env[fname]):
            args = prepare(args)
            return func.call(args)

        else:
            assert False, f'"{fname}" Not implemented'
