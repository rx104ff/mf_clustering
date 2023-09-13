import regex
from collections import OrderedDict

from services.helpers.func_builder.lexer import Lexer
from services.helpers.func_builder.parser import Parser


def strip_surrounding_parentheses(s):
    # Check if the string starts with "(" and ends with ")"
    if s.startswith('(') and s.endswith(')'):
        # Check if the string minus the outermost parentheses is balanced
        inner = s[1:-1]
        if inner.count('(') == inner.count(')'):
            return inner
    return s


class Compiler:
    def __init__(self, program):
        self.program = program
        self.env, self.expr = self.decompose_program()

    def decompose_program(self):
        env = self.program.split('|-')[0].strip()
        expr = self.program.split('|-')[1].strip()
        return env, expr

    def parse_fun_expression(self, fun_expr):

        env_pattern = r'\((?:[^\(\)]|(?R))*\)'
        fun_patter = r'\[(?:[^\[\]]|(?R))*\]'

        env_match = regex.search(env_pattern, fun_expr)
        env = env_match.group(0)
        if len(env) >= 2:
            env = env[1:-1]

        fun_match = regex.search(fun_patter, fun_expr[env_match.end(0)::])
        fun = fun_match.group(0)
        if len(fun) >= 2:
            fun = fun[1:-1]

        ident, expr = self.parse_fun(fun)

        return env, ident, expr

    @staticmethod
    def parse_fun(fun):
        pattern = r'fun\s+(\w+)\s+->\s+(.*)'
        match = regex.match(pattern, fun)
        if match:
            ident = match.group(1)
            expr = match.group(2)
            return ident, expr
        return None, None

    def parse_rec_fun_expression(self, rec_fun_expr):

        env_pattern = r'\((?:[^\(\)]|(?R))*\)'
        fun_patter = r'\[(?:[^\[\]]|(?R))*\]'

        env_match = regex.search(env_pattern, rec_fun_expr)
        env = env_match.group(0)
        if len(env) >= 2:
            env = env[1:-1]

        fun_match = regex.search(fun_patter, rec_fun_expr[env_match.end(0)::])
        fun = fun_match.group(0)
        if len(fun) >= 2:
            fun = fun[1:-1]

        ident_1, ident_2, expr = self.parse_rec_func(fun)

        return env, ident_1, ident_2, expr

    @staticmethod
    def parse_rec_func(s):
        pattern = r'rec\s+(\w+)\s+=\s+fun\s+(\w+)\s+->\s+(.*)'
        match = regex.match(pattern, s)
        if match:
            ident_1 = match.group(1)
            ident_2 = match.group(2)
            expression = match.group(3)

            return ident_1, ident_2, expression
        return None, None, None

    @staticmethod
    def decompose_fun(fun):
        pass

    @staticmethod
    def parse_environment(environment):
        environments = [s.strip() for s in environment.split(',')]
        od = OrderedDict()

        for env in environments:
            if env != '':
                ident = env.split('=', 1)[0].strip()
                expr = env.split('=', 1)[1].strip()
                od[ident] = expr

        return od

    @staticmethod
    def eval_int(environment, expr):
        value = expr
        evalto = f'{environment} |- {expr} evalto {value} by E-Int{{}};\n'
        return value, evalto

    @staticmethod
    def eval_bool(environment, expr):
        value = expr
        evalto = f'{environment} |- {expr} evalto {value} by E-bool{{}};\n'
        return value, evalto

    def eval_var(self, environment, expr):
        env_od = self.parse_environment(environment)
        key = list(env_od.items())[-1][0]
        if key.strip() == expr:
            return self.eval_var1(environment, expr)
        else:
            return self.eval_var2(environment, expr)

    def eval_var1(self, environment, expr):
        env_od = self.parse_environment(environment)
        value = list(env_od.items())[-1][1]
        evalto = f'{environment} |- {expr} evalto {value} by E-Var1{{}};\n'
        return value, evalto

    def eval_var2(self, environment, expr):
        new_env_list = [env.strip() for env in environment.split(',')]
        new_env_list.pop()
        new_env = ', '.join(new_env_list)
        value, evalto_1 = self.eval_expr(new_env, expr)
        evalto = (f'{environment} |- {expr} evalto {value} by E-Var1{{\n'
                  f'    {evalto_1}'
                  f'}};\n')
        return value, evalto

    def eval_plus(self, environment, expr_1, expr_2):
        value_1, evalto_1 = self.eval_expr(environment, expr_1)
        value_2, evalto_2 = self.eval_expr(environment, expr_2)
        value = int(value_1) + int(value_2)
        evalto = (f'{environment} |- {expr_1} + {expr_2} evalto {value} by E-Plus {{\n'
                  f'    {evalto_1}'
                  f'    {evalto_2}'
                  f'    {value_1} plus {value_2} is {value} by B-Plus{{}};'
                  f'}};\n')
        return value, evalto

    def eval_minus(self, environment, expr_1, expr_2):
        value_1, evalto_1 = self.eval_expr(environment, expr_1)
        value_2, evalto_2 = self.eval_expr(environment, expr_2)
        value = int(value_1) - int(value_2)
        evalto = (f'{environment} |- {expr_1} - {expr_2} evalto {value} by E-Minus {{\n'
                  f'    {evalto_1}'
                  f'    {evalto_2}'
                  f'    {value_1} minus {value_2} is {value} by B-Minus{{}};'
                  f'}};\n')
        return value, evalto

    def eval_times(self, environment, expr_1, expr_2):
        value_1, evalto_1 = self.eval_expr(environment, expr_1)
        value_2, evalto_2 = self.eval_expr(environment, expr_2)
        value = int(value_1) * int(value_2)
        evalto = (f'{environment} |- {expr_1} * {expr_2} evalto {value} by E-Times {{\n'
                  f'    {evalto_1}'
                  f'    {evalto_2}'
                  f'    {value_1} times {value_2} is {value} by B-Times{{}};'
                  f'}};\n')
        return value, evalto

    def eval_lt(self, environment, expr_1, expr_2):
        value_1, evalto_1 = self.eval_expr(environment, expr_1)
        value_2, evalto_2 = self.eval_expr(environment, expr_2)
        value = int(value_1) < int(value_2)
        evalto = (f'{environment} |- {expr_1} < {expr_2} evalto {value} by E-Lt {{\n'
                  f'    {evalto_1}'
                  f'    {evalto_2}'
                  f'    {value_1} less than {value_2} is {value} by B-Lt{{}};'
                  f'}};\n')
        return value, evalto

    def eval_let(self, environment, ident, expr_1, expr_2):
        value_1, evalto_1 = self.eval_expr(environment, expr_1)
        new_env = ''
        if environment == '':
            new_env = f'{ident} = {value_1}'
        else:
            new_env = f'{environment}, {ident} = {value_1}'

        value_2, evalto_2 = self.eval_expr(new_env, expr_2)
        evalto = (f'{environment} |- let {ident} = {expr_1} in {expr_2} evalto {value_2} by E-Let {{\n'
                  f'    {evalto_1}'
                  f'    {evalto_2}'
                  f'}};\n')
        return value_2, evalto

    def eval_if(self, environment, expr_1, expr_2, expr_3):
        value_1, evalto_1 = self.eval_expr(environment, expr_1)
        if bool(value_1):
            value, evalto_2 = self.eval_expr(environment, expr_2)
            evalto = (f'{environment} |- if {expr_1} then {expr_2} else {expr_3} evalto {value} by E-IfT {{\n'
                      f'    {evalto_1}'
                      f'    {evalto_2}'
                      f'}};\n')
        else:
            value, evalto_3 = self.eval_expr(environment, expr_3)
            evalto = (f'{environment} |- if {expr_1} then {expr_2} else {expr_3} evalto {value} by E-IfF {{\n'
                      f'    {evalto_1}'
                      f'    {evalto_3}'
                      f'}};\n')
        return value, evalto

    @staticmethod
    def eval_fun(environment, ident, expr):
        value = f'({environment})[fun {ident} -> {expr}]'
        evalto = f'{environment} |- fun {ident} -> {expr} evalto {value} by E-Fun{{}};\n'
        return value, evalto

    def eval_app_base(self, environment, expr_1, expr_2):
        value, _ = self.eval_expr(environment, expr_1)
        if 'let rec' in value:
            return self.eval_app_rec(environment, expr_1, expr_2)
        else:
            return self.eval_app(environment, expr_1, expr_2)

    def eval_app(self, environment, expr_1, expr_2):
        value_1, evalto_1 = self.eval_expr(environment, expr_1)
        value_2, evalto_2 = self.eval_expr(environment, expr_2)
        env_2, ident, evalto_0 = self.parse_fun_expression(value_1)
        value, evalto_3 = self.eval_expr(f'{environment}, {ident} = {value_2}', evalto_0)
        evalto = (f'{environment} |- {expr_1} {expr_2} evalto {value} by E-App {{\n'
                  f'    {evalto_1}'
                  f'    {evalto_2}'
                  f'    {evalto_3}'
                  f'}};\n')
        return value, evalto

    def eval_let_rec(self, environment, ident_1, ident_2, expr_1, expr_2):
        value, evalto_1 = self.eval_expr(f'{environment}, {ident_1} = ()[rec {ident_1} = fun {ident_2} -> {expr_1}]', expr_2)
        evalto = (f'{environment} |- let rec {ident_1} = fun {ident_2} -> {expr_1} in {expr_2} evalto {value} by E-LetRec {{\n'
                  f'    {evalto_1}'
                  f'}};\n')
        return value, evalto

    def eval_app_rec(self, environment, expr_1, expr_2):
        value_1, evalto_1 = self.eval_expr(environment, expr_1)
        env_2, ident_1, ident_2, expr_0 = self.parse_rec_fun_expression(value_1)
        value_2, evalto_2 = self.eval_expr(environment, expr_2)

        value, evalto_3 = self.eval_expr(f'{env_2}, {ident_1} = ({env_2})[rec {ident_1} = fun {ident_2} -> {expr_0}], {ident_2} = {value_2}', expr_0)
        evalto = (f'{environment} |- {expr_1} {expr_2} evalto {value} by E-AppRec {{\n'
                  f'    {evalto_1}'
                  f'    {evalto_2}'
                  f'    {evalto_3}'
                  f'}};\n')
        return value, evalto

    @staticmethod
    def eval_expr(environment, expr):
        program = f'{strip_surrounding_parentheses(environment)} |- {strip_surrounding_parentheses(expr)}'
        lex = Lexer(strip_surrounding_parentheses(expr))
        comp = Compiler(program)
        par = Parser(lex, comp)
        return par.program()


v, e = Compiler.eval_expr('', 'let twice = fun f -> fun x -> f (f x) in twice (fun x -> x * x) 2')
print(e)
