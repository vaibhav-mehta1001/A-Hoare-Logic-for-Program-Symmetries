from sympy import *
import sympy as sympy
import z3 as z3
import itertools
import math
import time
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

# Base class for all AST nodes
class ASTNode:
    pass
# Expressions in the language
class Expression(ASTNode):
    pass

class Literal(Expression):
    return_type = "int"
    argument_types = []
    def __init__(self, value):
        self.value = value

    def to_string(self):
      return str(self.value)
    def cost(self):
        return 1
class Variable(Expression):
    return_type = "int"
    argument_types = []
    def __init__(self, name):
        self.name = name + " "

    def to_string(self):
      return self.name

    def cost(self):
        return 1
# tangent
class Tan(Expression):
    def __init__(self, left):
        self.left = left
    def to_string(self):
        return f"tan({self.left.to_string()})"
    def cost(self):
        return self.left.cost() + 1
class Plus(Expression):
    return_type = "int"
    argument_types = ["int","int"]
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def to_string(self):
        return '('+self.left.to_string() + ' + ' + self.right.to_string()+')'

    def cost(self):
        return self.right.cost() + self.left.cost()
# --- Additional Expression: TupleExpression ---
class TupleExpression(Expression):
    def __init__(self, exprs):
        self.exprs = exprs  # List of Expression objects.
    def to_string(self):
        return "(" + ", ".join(expr.to_string() for expr in self.exprs) + ")"
    def cost(self):
        return sum(expr.cost() for expr in self.exprs)

# --- Function Definition ---
class FunctionDefinition(ASTNode):
    def __init__(self, name, params, body_exprs):
        # params: list of Variable nodes.
        # body_exprs: list of Expression objects (one per coordinate).
        self.name = name
        self.params = params
        self.body_exprs = body_exprs
    def to_string(self):
        # Parameters are declared as simple ints.
        params_str = ", ".join("float " + param.to_string().strip() for param in self.params)
        # Body as an array literal (using braces, with no extra semicolon inside).
        body_str = "{ " + ", ".join(expr.to_string() for expr in self.body_exprs) + " }"
        return f"float[{len(self.body_exprs)}]  {self.name}({params_str}) {{ return {body_str};}}"


class Minus(Expression):
    return_type = "int"
    argument_types = ["int","int"]
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def to_string(self):
        return '('+self.left.to_string() + ' - (' + self.right.to_string()+'))'
    def cost(self):
        return self.right.cost() + self.left.cost()


class Power(Expression):
    return_type = "int"
    argument_types = ["int","int"]
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def to_string(self):
        if isinstance(self.right, Literal):
            if self.right.value == 2:
                return self.left.to_string()  + ' * ' + self.left.to_string()
            if self.right.value == 3:
                return self.left.to_string()  + ' * ' + self.left.to_string() + ' * ' + self.left.to_string()
        return self.left.to_string() + ' ^' + self.right.to_string()
    def cost(self):
        return self.right.cost() + self.left.cost()


class Neg(Expression):
    return_type = "int"
    argument_types = ["int"]
    def __init__(self, left):
        self.left = left

    def to_string(self):
        return ' -  (' + self.left.to_string() +')'
    def cost(self):
        return  self.left.cost()

class Gt(Expression):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def to_string(self):
        return self.left.to_string() + ' > ' + self.right.to_string()

    def cost(self):
        return self.right.cost() + self.left.cost()

class Mult(Expression):
    return_type = "int"
    argument_types = ["int","int"]
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def to_string(self):
        return '('+self.left.to_string() + ' * ' + self.right.to_string()+')'
    def cost(self):
        return self.right.cost() + self.left.cost()

class Div(Expression):
    return_type = "int"
    argument_types = ["int","int"]
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def to_string(self):
        return '(' + self.left.to_string() + ' / ' + self.right.to_string() +')'
    def cost(self):
        return self.right.cost() + self.left.cost()

class Cos(Expression):
    return_type = "int"
    argument_types = ["int"]
    def __init__(self, left):
        self.left = left

    def to_string(self):
        return ' cos(' + self.left.to_string() + ') '
    def cost(self):
        return 1

class Sin(Expression):
    return_type = "int"
    argument_types = ["int"]
    def __init__(self, left):
        self.left = left

    def to_string(self):
        return ' sin(' + self.left.to_string() + ') '
    def cost(self):
        return 1

class Abs(Expression):
    return_type = "int"
    argument_types = ["int"]
    def __init__(self, left):
        self.left = left
    def to_string(self):
        return  'abs(' + self.left.to_string() + ' )'
    def cost(self):
        return self.left.cost() + 1

class Pi2(Expression):
    def __init__(self):
        self.left = math.pi / 2
    def to_string(self):
        return ' Pi()/2.0'
    def cost(self):
        return 1

class Equal(Expression):
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def to_string(self):
        return self.left.to_string() + " == " + self.right.to_string()
    def cost(self):
        return self.left.cost() + self.right.cost()

class Piecewise(Expression):
    # conditions: list of Expression nodes representing the guards
    # expressions: list of Expression nodes corresponding to the outcomes
    # default_expr: an optional Expression to use if none of the conditions hold
    def __init__(self, conditions, expressions, default_expr=None):
        self.conditions = conditions
        self.expressions = expressions
        self.default_expr = default_expr

    def to_string(self):
        parts = []
        for cond, expr in zip(self.conditions, self.expressions):
            parts.append(f"({cond.to_string()} : {expr.to_string()})")
        if self.default_expr:
            parts.append(f"(default : {self.default_expr.to_string()})")
        return "Piecewise(" + ", ".join(parts) + ")"

    def cost(self):
        total = sum(cond.cost() for cond in self.conditions) + \
                sum(expr.cost() for expr in self.expressions)
        if self.default_expr:
            total += self.default_expr.cost()
        return total

# Statements in the language
class Statement(ASTNode):
    pass

class Assignment(Statement):
    def __init__(self, variable, expression):
        self.variable = variable
        self.expression = expression

    def to_string(self):
      return self.variable.to_string() + " = " + self.expression.to_string()

class IfStatement(Statement):
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor):
        return visitor.visit_if_statement(self)

    def to_string(self):
      return "If( " + str(self.condition.to_string()) + ") { \n " + str(self.then_branch.to_string()) + "}  else {\n " + str(self.else_branch.to_string()) +" }"

class WhileStatement(Statement):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def accept(self, visitor):
        return visitor.visit_while_statement(self)

class Block(Statement):
    def __init__(self, statements):
        self.statements = statements
# A simple program containing a sequence of statements

class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements



class SymPyConverter:
    def visit(self, node):
        if isinstance(node, Literal):
            return self.visit_literal(node)
        elif isinstance(node, Variable):
            return self.visit_variable(node)
        elif isinstance(node, Plus):
            return self.visit_plus(node)
        elif isinstance(node, Minus):
            return self.visit_minus(node)
        elif isinstance(node, Gt):
            return self.visit_gt(node)
        elif isinstance(node, Mult):
            return self.visit_mult(node)
        elif isinstance(node, Div):
            return self.visit_div(node)
        elif isinstance(node, Neg):
            return self.visit_neg(node)
        elif isinstance(node, Cos):
            return self.visit_cos(node)
        elif isinstance(node, Sin):
            return self.visit_sin(node)
        elif isinstance(node, Tan):
            return self.visit_sin(node)
        elif isinstance(node, Pi2):
            return self.visit_pi2(node)
        elif isinstance(node, Abs):
            return self.visit_abs(node)
        elif isinstance(node, Power):
            return self.visit_pow(node)
        elif isinstance(node, Piecewise):
            return self.visit_piecewise(node)
        elif isinstance(node, Equal):
            return self.visit_equal(node)
        else:
            raise Exception(f"Unknown node type: {(node.to_string())}")

    def visit_literal(self, literal):
        return Float(literal.value)
    def visit_pi2(self, literal):
        return pi/2

    def visit_variable(self, variable):
        return Symbol(variable.name[:-1])

    def visit_plus(self, plus):
        return self.visit(plus.left) + self.visit(plus.right)

    def visit_minus(self, minus):
        return self.visit(minus.left) - self.visit(minus.right)

    def visit_mult(self, mult):
        return Mul(self.visit(mult.left) , self.visit(mult.right))

    def visit_div(self, mult):
        return self.visit(mult.left) /self.visit(mult.right)

    def visit_pow(self, mult):
        return Pow(self.visit(mult.left), self.visit(mult.right))

    def visit_gt(self, gt):
        return self.visit(gt.left) > self.visit(gt.right)

    def visit_neg(self, neg):
        return -(self.visit(neg.left))

    def visit_cos(self, neg):
        return cos(self.visit(neg.left))

    def visit_sin(self, neg):
        return sin(self.visit(neg.left))
    def visit_tan(self, neg):
        return tan(self.visit(neg.left))
    def visit_abs(self, neg):
        return sympy.Abs(self.visit(neg.left))

    def visit_piecewise(self, node):
        # Build a list of tuples (expression, condition)
        # pieces = []
        # for cond, expr in zip(node.conditions, node.expressions):
        #     pieces.append( (self.visit(expr), self.visit(cond)) )
        # # If there is a default, add it with True as condition
        # if node.default_expr is not None:
        #     pieces.append( (self.visit(node.default_expr), True) )
        # return sympy.Piecewise(*zip(*[(c, e) for e, c in pieces]))  # sympy.Piecewise expects (expr, cond)
        # # Alternatively, directly:
        return sympy.Piecewise(*[(self.visit(expr), self.visit(cond)) for cond, expr in zip(node.conditions, node.expressions)] +
                               ([(self.visit(node.default_expr), True)] if node.default_expr is not None else []))
    def visit_equal(self, node):
        # Using sympy.Eq to represent equality.
        return sympy.Eq(self.visit(node.left), self.visit(node.right))


# Define the Expression to Z3 Converter
class ExpressionToZ3Converter:
    def __init__(self):
        self.context = {}

    def visit(self, node):
        if isinstance(node, Literal):
            return self.convert_literal(node)
        elif isinstance(node, Variable):
            return self.convert_variable(node)
        elif isinstance(node, Plus):
            return self.convert_plus(node)
        elif isinstance(node, Minus):
            return self.convert_minus(node)
        elif isinstance(node, Neg):
            return self.convert_neg(node)
        elif isinstance(node, Gt):
            return self.convert_gt(node)
        elif isinstance(node, Mult):
            return self.convert_mult(node)
        elif isinstance(node, Div):
            return self.convert_div(node)
        elif isinstance(node, Power):
            return self.convert_pow(node)
        elif isinstance(node, Cos):
            return self.convert_cos(node)
        elif isinstance(node, Sin):
            return self.convert_sin(node)
        elif isinstance(node, Pi2):
            return self.convert_pi2(node)
        elif isinstance(node, Abs):
           return self.convert_abs(node)
        elif isinstance(node, Piecewise):
            return self.convert_piecewise(node)
        elif isinstance(node, Equal):
            return self.convert_equal(node)

        else:
            raise Exception(f"Unknown node type: {node.to_string()}")

    def convert_literal(self, node):
        return node.value  # Z3 can handle literal values like int or float

    def convert_variable(self, node):
        name = node.name[:-1]
        if name not in self.context:
            self.context[name] = z3.Real(name)  # Assume all variables are real numbers
        return self.context[name]

    def convert_plus(self, node):
        return self.visit(node.left) + self.visit(node.right)

    def convert_minus(self, node):
        return self.visit(node.left) - self.visit(node.right)

    def convert_pow(self, node):
        return self.visit(node.left) ** self.visit(node.right)

    def convert_neg(self, node):
        return -self.visit(node.left)

    def convert_gt(self, node):
        return self.visit(node.left) > self.visit(node.right)

    def convert_mult(self, node):
        return self.visit(node.left) * self.visit(node.right)

    def convert_div(self, node):
        return self.visit(node.left) / self.visit(node.right)

    def convert_cos(self, node):
        return cos(self.visit(node.left))

    def convert_abs(self, node):
        return z3.If(self.visit(node.left) >= 0,self.visit(node.left),-self.visit(node.left))

    def convert_sin(self, node):
        return sin(self.visit(node.left))

    def convert_pi2(self, node):
        return z3.RealVal(1.57)

    def convert_piecewise(self, node):
        # Process each (condition, expression) pair.
        # Nest z3.If calls. Assume conditions are checked in order.
        result = None
        # Start with default if provided, else you might raise an error
        if node.default_expr is not None:
            result = self.visit(node.default_expr)
        else:
            # If no default, then default to 0 (or raise an exception)
            result = 0

        # Reverse iterate so that the first condition gets priority
        for cond, expr in reversed(list(zip(node.conditions, node.expressions))):
            z3_cond = self.visit(cond)
            z3_expr = self.visit(expr)
            result = z3.If(z3_cond, z3_expr, result)
        return result
    def convert_equal(self, node):
        # Use Python's '==' operator for Z3 equality.
        return self.visit(node.left) == self.visit(node.right)

def sympy_to_z3(expr):
    if isinstance(expr, Symbol):  # Variable case
         if expr.is_negative:  # Handle negative numbers
             return - z3.Real(str(expr))
         return z3.Real(str(expr))
    elif isinstance(expr, Add):  # Addition
        return z3.simplify(sum([sympy_to_z3(arg) for arg in expr.args]))
    elif isinstance(expr, Mul):  # Multiplication
        res = sympy_to_z3(expr.args[0])
        for arg in expr.args[1:]:
            res = z3.simplify(res * sympy_to_z3(arg))
        return res
    elif isinstance(expr, Div):  # Division
        res = sympy_to_z3(expr.args[0])
        for arg in expr.args[1:]:
            res = z3.simplify(res / sympy_to_z3(arg))
        return res
    elif isinstance(expr, Pow):  # Power
        base, exp = expr.args
        return z3.simplify(sympy_to_z3(base) ** sympy_to_z3(exp))
    elif isinstance(expr, sin):  # Sine function
        return z3.sin(sympy_to_z3(expr.args[0]))
    # elif isinstance(expr, cos):  # Cosine function
    #     return z3.cos(sympy_to_z3(expr.args[0]))
    elif expr.func == Eq:  # Equality (sympy.Eq) case
        return z3.simplify(sympy_to_z3(expr.lhs) == sympy_to_z3(expr.rhs))
    elif isinstance(expr, sympy.Piecewise):
        # Convert a sympy.Piecewise by nesting z3.If calls
        # sympy.Piecewise expects tuples (expr, cond)
        # We process them in order, using the default if provided
        default = None
        pieces = expr.args
        # Check if the last piece is default (condition is True)
        if pieces and pieces[-1][1] == True:
            default = sympy_to_z3(pieces[-1][0])
            pieces = pieces[:-1]
        else:
            default = 0
        result = default
        for piece in reversed(pieces):
            piece_expr = sympy_to_z3(piece[0])
            piece_cond = sympy_to_z3(piece[1])
            result = z3.If(piece_cond, piece_expr, result)
        return result
    elif isinstance(expr, sympy.logic.boolalg.Boolean):
        if expr.func == sympy.And:
            return z3.And(*[sympy_to_z3(arg) for arg in expr.args])
        elif expr.func == sympy.Or:
            return z3.Or(*[sympy_to_z3(arg) for arg in expr.args])
        elif expr.func == sympy.Not:
            return z3.Not(sympy_to_z3(expr.args[0]))
        else:
            raise TypeError("Unsupported Boolean operator: " + str(expr))
    elif isinstance(expr, Basic):  # Literal numbers
         if expr == pi:
            if expr.is_negative:  # Handle negative numbers
              return z3.RealVal(-(3.14))
            return z3.RealVal(3.14)
         if expr.is_negative:  # Handle negative numbers
            return z3.RealVal(float((expr)))
         return z3.RealVal(float((expr)))
    # elif isinstance(expr, sympy.Neg):  # Handle negations of expressions
    #     return -sympy_to_z3(expr.args[0])
    else:
        raise TypeError(f"Unsupported type: {(expr.to_string())}")


Z3Converter = ExpressionToZ3Converter()
converter = SymPyConverter()


def convert_gas(group_actions):
    group_actions2 = []
    for group_action in group_actions:
       group_actions2.append(convert_ga(group_action))
    return group_actions2

def convert_ga(group_action):
    for vars in group_action.keys():
        group_action[vars] = converter.visit(group_action[vars])
    return group_action

def convert_gas_Z3(group_actions):
    group_actions2 = []
    for group_action in group_actions:
     for vars in group_action.keys():
        group_action[vars] = Z3Converter.visit(group_action[vars])
     group_actions2.append(group_action)
    return group_actions2

def convert_ga_Z3(group_action):
    for vars in group_action.keys():
        group_action[vars] = Z3Converter.visit(group_action[vars])
    return group_action

def convert_sympy_ga_to_Z3(group_action):
    for vars in group_action.keys():
        group_action[vars] = sympy_to_z3(group_action[vars].simplify())
    return group_action

def transform_inverse(inverse_exp, prog_vars, assgn_var, assgn_expr, GroupAction):
    var_exps = {assgn_var: inverse_exp}
    for var in prog_vars:
            if var != assgn_var:
              var_exps[var] = Symbol(var) #GroupAction[var]
    var_exps_new = {}

    for var in prog_vars:
          var_exps_new[var] = ((GroupAction[var]).subs(var_exps))
    # print(var_exps_new)

    free = list(assgn_expr.free_symbols)
    f = Lambda(free, assgn_expr)
    # print(f)
    # print(free)
    args =[]
    for v in free:
        if str(v) in set(var_exps_new.keys()):
            args.append(var_exps_new[str(v)])
        else:
            args.append(Symbol(str(v)))
    new_ga = {assgn_var :  simplify(f(*args))}
    # print(args)
    for vars in prog_vars:
        if vars != assgn_var:
          new_ga[vars] = simplify(var_exps_new[vars])
    return new_ga

def deep_copy(xs):
    r = []
    for x in xs:
        r.append(x.copy())
    return r

def invert_piecewise(f, x, y):
    """
    Invert a piecewise function f (which can be either a Sympy Piecewise
    or a custom object with attributes 'conditions', 'expressions', and
    'default_expr') to obtain its inverse as a Sympy Piecewise in variable y.

    Parameters:
      f:   A piecewise function, either a Sympy Piecewise or a custom object.
      x:   The original independent variable.
      y:   The new variable for the inverse (i.e. f_inv(y) such that f(f_inv(y)) = y).

    Returns:
      A Sympy Piecewise function representing the inverse.

    Raises:
      ValueError if any branch does not yield a unique solution.
    """
    # Determine the branches based on the type of f.
    # print(f.args[0])
    if hasattr(f, 'args'):
        # f is a Sympy Piecewise
        branches = f.args
    else:
        # Assume f is a custom Piecewise-like object with:
        #   f.conditions, f.expressions, and f.default_expr.
        branches = []

        branches.append(f.conditions)
        branches.append(f.expressions)
        # if hasattr(f, 'default_expr') and f.default_expr is not None:
        #     branches.append((f.default_expr, True))
    # branches = f.args
    inv_branches = []

    for expr, cond in branches:
        # Solve the equation: y = expr for x.
        sol = solve(expr - y, x)
        if len(sol) == 1:
            inv_expr = list(sol)[0]
            # Using True as a placeholder condition for the inverse branch.
            inv_branches.append((inv_expr, cond))
        else:
            return None

    if not inv_branches:
        raise None

    # Assemble the inverse as a Sympy Piecewise function.
    return sympy.Piecewise(*[(expr, cond) for expr, cond in inv_branches])

def get_free_vars(expr, i):
    """
    Recursively collects free variable names (as stripped strings) from an AST expression.
    """
    # If the expression is a variable, return its name (strip extra whitespace).
    if isinstance(expr, Variable):
        return {expr.name.strip()}

    # Literals do not contribute any free variables.
    elif isinstance(expr, Literal):
        return set()

    # For binary operators, union the free variables of both operands.
    elif isinstance(expr, (Plus, Minus, Mult, Div, Power, Equal, Gt)):
        return get_free_vars(expr.left, i) | get_free_vars(expr.right, i)

    # For unary operators, return the free variables of its operand.
    elif isinstance(expr, (Neg, Cos, Sin, Abs)):
        return get_free_vars(expr.left, i)

    # For a Piecewise node, combine the free variables from each condition and each branch.
    elif isinstance(expr, Piecewise):
        vars_set = set()
        # Assume Piecewise has attributes "conditions" (a list), "expressions" (a list),
        # and optionally "default_expr" (which may be None)
        for cond, branch_expr in zip(expr.conditions, expr.expressions):
            vars_set |= get_free_vars(cond, i)
            vars_set |= get_free_vars(branch_expr, i)
        if expr.default_expr is not None:
            vars_set |= get_free_vars(expr.default_expr, i)
        # if i < 10:
        return vars_set
        # return set()

    # Fallback: if expr is a more complex AST node, try to iterate its children if available.
    else:
         raise Exception(f"Unknown node type: {expr.to_string()}")

# Function to check that for an assignment statement the free variables in its RHS
#    are left unchanged by the group action.
def check_assignment_rhs_identity(assign, group_action, i):
    """
    Given an assignment statement (an AST node of type Assignment) and a group_action
    dictionary mapping variable names (strings) to AST expressions (their transformation),
    this function checks that for every free variable on the RHS of the assignment, if
    that variable has a group action specified, the transformation is the identity.

    Identity is defined as a Variable node whose name equals the variable name.

    Parameters:
      assign       : an Assignment AST node.
      group_action : dict mapping variable names (str) to AST expressions.

    Returns:
      bool: True if every free variable in the RHS is unchanged (when a group action is specified),
            False otherwise.
    """
    free_vars = get_free_vars(assign.expression, i)
    for var_name in free_vars:
        # If there is a transformation for var_name, check if it is the identity.
        if var_name in group_action.keys():
            # The identity transformation for a variable is simply Variable(var_name).
            identity = Variable(var_name)
            # Compare using the to_string() method (or define an equality method on your AST nodes).
            if not isinstance(group_action[var_name], Symbol):
              return False
            if group_action[var_name].name != identity.to_string():
                # Found a variable on the RHS that is transformed nontrivially.
                return False
    return True


def verify_assignments(program, program_vars, group_actions, final_group_action, annotations=None):
    t = time.time()
    inverse = Symbol('i')
    i = 0
    annotation_index = 0
    for stmt in program:
        if isinstance(stmt.expression, Piecewise):
          if check_assignment_rhs_identity(stmt, group_actions[0], i):
               i += 1
               continue
                # print(stmt.to_string())
                # print(stmt.expression.to_string())
                # print(converter.visit_piecewise(stmt.expression))
          x = invert_piecewise(converter.visit(stmt.expression), Symbol(stmt.variable.name[:-1]), inverse)
          if x is not None:
                sol = [x]
          else:
              continue
        else:
            sol = (solve(converter.visit(stmt.expression) - inverse, Symbol(stmt.variable.name[:-1])))
        # print('----')
        # print(sol)
        i += 1
        if len(sol) != 1:
            if annotations is not None:
                pre, post = annotations[annotation_index]
                pre_temp, post_temp = [], []
                pre_copy = deep_copy(pre)
                pre_copy2 = deep_copy(pre)
                post_copy = deep_copy(post)
                for p in pre:
                    pre_temp.append(convert_ga_Z3(p))
                for p in post:
                    post_temp.append(convert_ga_Z3(p))
                pre = pre_temp
                post = post_temp
                group_action_fake= []
                p = check_sem_assgn_forall(stmt, program_vars, pre_copy, post_copy)
                if p:
                    ga_temp = []
                    group_action_copy = deep_copy(group_actions)
                    for group_action in group_action_copy:
                        ga_temp.append(convert_sympy_ga_to_Z3(group_action))
                    if check_implication(ga_temp, pre, program_vars):
                        annotation_index += 1
                        for f in pre_copy2:
                            group_action_fake.append(convert_ga(f))
                        group_actions = group_action_fake
                        continue
                else:
                 print("Wrong Annotation")
                 return False, {}
            else:
              print("Need Annotation")
              return False, {}
            continue
        else:
        #  print(" injective")
         temp = []
         for group_action in group_actions:
          sol[0] = sol[0].subs(inverse, Symbol(stmt.variable.name[:-1]))
          sol[0] = sol[0].simplify()
          group_action = transform_inverse(sol[0], program_vars, stmt.variable.name[:-1], converter.visit(stmt.expression), group_action)
          temp.append(group_action)
         group_actions = temp
         i += 1
    # print(((group_actions)))
    # t4 = time.time()
    b = None
    if final_group_action is not None:
       ga_z3 =[]
      #  print("Checking implication")
       for group_action in group_actions:
           ga_z3.append(convert_sympy_ga_to_Z3(group_action.copy()))
      #  print(ga_z3)
       b =  check_implication(final_group_action, ga_z3, program_vars)
    t2 = time.time()
    time_taken =  t2 -t
    return b, group_actions, time_taken


def functionFromExpr(args, expr):
    return lambda *fargs: z3.substitute(expr, [(a, f) for a, f in zip(args, fargs)])

def check_sem_assgn(stmt, program_vars, pre_group_action, post_group_action):
    s = z3.Solver()
    s.reset()
    conjuncts = []
    pre_state = {}
    for var in program_vars:
        pre_state[var] = Z3Converter.visit(pre_group_action[var])
    assgn_expr = Z3Converter.visit(stmt.expression)
    z3_vars = []
    original_post_state = {}
    for var in program_vars:
        z3_vars.append(z3.Real(var))
        original_post_state[var] = z3.Real(var)

    f = functionFromExpr(z3_vars, assgn_expr)
    args = []
    for var in program_vars:
        args.append(pre_state[var])
    # print(args)
    # print(assgn_expr)

    pre_state[stmt.variable.name[:-1]] = f(*args)
    original_post_state[stmt.variable.name[:-1]] = f(*z3_vars)

    args_post  = []
    for var in program_vars:
        args_post.append(original_post_state[var])

    modified_orginal_post = {}
    for post_group_a in post_group_action:
     for var in program_vars:
        action_exp = Z3Converter.visit(post_group_a[var])
        f_pg = functionFromExpr(z3_vars, action_exp)
        modified_orginal_post[var] = f_pg(*args_post)
    #  print(modified_orginal_post)
    #  print(pre_state)
     l = []
     for var in program_vars:
          l.append((modified_orginal_post[var] == pre_state[var]))
     conjuncts.append(z3.And(l))
    s.add(z3.ForAll(z3_vars, z3.Or(conjuncts)))
    # z3.pp(s)
    # print(s.check())
    return s.check()


def check_sem_assgn_forall(stmt, program_vars, pre_group_action, post_group_action):
    for gen in pre_group_action:
        res = check_sem_assgn(stmt, program_vars, gen, post_group_action)
        if(res == z3.sat):
            continue
        return False
    return True

def check_implication(antecedent, consequent, program_vars):

    for pre in antecedent:
     s = z3.Solver()
     z3_vars = []
     for var in program_vars:
        z3_vars.append(z3.Real(var))

     conjuncts = []
     l = []
     for post in consequent:
      for var in program_vars:
          l.append((pre[var] == post[var]))
      conjuncts.append(z3.And(l))
      l = []
     s.add(z3.ForAll(z3_vars, z3.Or(conjuncts)))
     conjuncts = []
     l = []
    #  print(s)
     if(s.check() == z3.sat):
        #  s.reset()
         continue
     else:
         return False
    return True