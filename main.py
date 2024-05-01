from parsing import tokenize, parse
from ast import Environment

def execute(env, source):
    try:
        tokens = tokenize(source)
        ast = parse(tokens)
        r = ast.eval(env)
        return r
    except Exception as e:
        print(e)
        return None


if __name__ == '__main__':
    env = Environment()
    with open('test.lisp', 'r') as file:
        execute(env, file.read())

    while True:
        try:
            result = execute(env,
                input('dlisp> '))
            if result: print(result)
        except (EOFError, KeyboardInterrupt):
            print(); exit(1)
