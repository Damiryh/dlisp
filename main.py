from parsing import tokenize, parse
from ast import Environment

def execute(env, filename):
    with open(filename) as file:
        source = file.read()
        tokens = tokenize(source)
        ast = parse(tokens)
        r = ast.eval(env)
        return r
    return None

if __name__ == '__main__':
    env = Environment()
    execute(env, 'test.lisp')
    
    while True:
        try:
            source = input('dlisp> ')
            tokens = tokenize(source)
            ast = parse(tokens)
            r = ast.eval(env)
            print(r)
        except (KeyboardInterrupt, EOFError):
            print('\nInterrupted by user.')
            exit(1)
