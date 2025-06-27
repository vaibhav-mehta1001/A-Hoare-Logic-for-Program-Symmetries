from sympy import symbols, Eq, solve, sympify
from  verifier import *

def transform_inverse_sketch(inverse_exp, prog_vars, assgn_var, assgn_expr, GroupAction):
    converter = SymPyConverter()
    for a in prog_vars:
       GroupAction[a] = converter.visit(GroupAction[a])
    assgn_expr = converter.visit(assgn_expr)
    var_exps = {assgn_var: assgn_expr}
    for var in prog_vars:
            if var != assgn_var:
              var_exps[var] = Symbol(var) #GroupAction[var]
    var_exps_new = {}

    for var in prog_vars:
          var_exps_new[var] = ((GroupAction[var]).subs(var_exps))
    # print(var_exps_new)

    free = list(inverse_exp.free_symbols)
    f = Lambda(free, inverse_exp)
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
    # print(new_ga)
    return new_ga


def compute_precondition_candidate(assignment, GroupAction):
    """
    Generalized candidate pre-condition computation.
    """
    # Extract the assigned variable name.
    var_name = assignment.variable.to_string().strip()
    # Create sympy symbols: x_sym for the variable, u for its "old" value, and y for the new value.
    x_sym = symbols(var_name)
    u = symbols("u_" + var_name)
    y = symbols("y_" + var_name)

    # Convert the assignment expression to a sympy expression.
    # (Assume that the AST's to_string returns an expression in terms of var_name.)
    try:
        f_expr = sympify(assignment.expression.to_string())
    except Exception as e:
        print("Error parsing expression:", e)
        return None

    # Substitute the assigned variable x with u.
    inverse = Symbol('i')
    # Solve the equation: f_expr_sub = y for u.
    try:
       sol = solve(f_expr - inverse, x_sym)
    except:
      return None
    sol[0] = sol[0].subs(inverse, x_sym)
    sol[0] = sol[0].simplify()
    if len(sol) == 1:
        # Substitute back: candidate = solution with y replaced by x.
        candidate = sol[0].subs(inverse, x_sym)
        return transform_inverse_sketch(candidate, GroupAction.keys(), var_name, assignment.expression, GroupAction)
        # return candidate
    else:
        # If no unique solution exists, return None.
        return None

def substitute(expr, mapping):
    """
    Recursively substitute variables in expr according to mapping.
    mapping is a dictionary from variable name (string) to an Expression.
    """
    if isinstance(expr, Variable):
        var_name = expr.to_string().strip()
        if var_name in mapping:
            return mapping[var_name]
        else:
            return expr
    elif isinstance(expr, Literal):
        return expr
    elif isinstance(expr, Plus):
        return Plus(substitute(expr.left, mapping), substitute(expr.right, mapping))
    elif isinstance(expr, Minus):
        return Minus(substitute(expr.left, mapping), substitute(expr.right, mapping))
    elif isinstance(expr, Mult):
        return Mult(substitute(expr.left, mapping), substitute(expr.right, mapping))
    elif isinstance(expr, Div):
        return Div(substitute(expr.left, mapping), substitute(expr.right, mapping))
    elif isinstance(expr, Abs):
        return Abs(substitute(expr.expr, mapping))
    elif isinstance(expr, Power):
        return Power(substitute(expr.base, mapping), substitute(expr.exp, mapping))
    else:
        return expr

# --- Function Composition ---
def compose_functions(outer, inner):
    """
    Given two FunctionDefinition objects, outer and inner, compute their composition:
         h(x) = outer(inner(x))
    The number of coordinates in inner.body_exprs must equal the number of parameters of outer.
    For each parameter in outer, substitute it with the corresponding coordinate from inner.
    The resulting composite function has the same parameters as inner.
    """
    if len(outer.params) != len(inner.body_exprs):
        raise ValueError("Dimension mismatch in function composition.")
    mapping = {}
    for i, param in enumerate(outer.params):
        # Substitute each outer parameter with the i-th expression from inner.
        mapping[param.to_string().strip()] = inner.body_exprs[i]
    new_body_exprs = [substitute(expr, mapping) for expr in outer.body_exprs]
    return FunctionDefinition(outer.name + "_comp", inner.params, new_body_exprs)


# --- SKETCH Starter Functions ---
def create_variable_generator(program_vars, typ):
    args = ",".join(typ + " " + x for x in program_vars)
    header = f"generator {typ} var_gen({args})"
    body = 'return {| 0.0| 1.0| -1.0| 6.0| Pi()/2.0|'
    for var in program_vars:
        body += var + " |"
    body = body + "};"
    return header + "{\n " + body + "\n}"

def gen_p_generator(program_vars, typ, ops, n=None):
    if n is None:
        n = 1
    args = ",".join(typ + " " + x for x in program_vars)
    var_gen_args = ",".join(" " + x for x in program_vars)
    header = f"generator {typ} gen_p({args})"
    op_regx = "|".join(" " + op for op in ops)
    op_regx = "(" + op_regx + ")"
    body = "return " + "{|"
    body = body + f"var_gen({var_gen_args})"
    for var in program_vars[n:]:
        body = body + f"{op_regx}  var_gen({var_gen_args})"
    body = body + "|};"
    return header + "{\n " + body + "\n}"

def list_variable_names(n):
    return [f"v{i}" for i in range(1, n+1)]

def synthesize_component(param, expr_h, all_params, assignment=None, GroupAction=None):
    """
    For a given parameter (a Variable) and its corresponding component from h,
    generate a regex-style grammar that offers multiple alternatives.
    We allow alternatives that combine the parameter with a fixed set of constants and with
    other parameters.
    """
    param_str = param.to_string().strip()
    # ID Rule : if h's component is exactly the parameter, then return identity.
    if isinstance(expr_h, Variable) and expr_h.to_string().strip() == param_str:
        return "{| " + param_str + " |}"

    if GroupAction is not None:
        alternatives = [str(GroupAction[param_str]).replace('pi', 'Pi() ')]
    else:
        alternatives = []
    other_vars = [v.to_string().strip() for v in all_params if v.to_string().strip() != param_str]
    # Option 1: if h's component is of the form (p + _), include that.
    if isinstance(expr_h, Plus):
        if (isinstance(expr_h.left, Variable) and expr_h.left.to_string().strip() == param_str
            and isinstance(expr_h.right, Literal)):
            try:
                const_val = float(expr_h.right.value)
                candidate = f"{param_str} + {const_val}"
                alternatives.append(candidate)
            except:
                pass
    if isinstance(expr_h, Minus):
        if (isinstance(expr_h.left, Literal) and expr_h.left.value == "0.0"
            or isinstance(expr_h.right, Variable)):
            try:
                candidate = f"-{param_str}"
                alternatives.append(candidate)
                return "{| -" + param_str + " |}"
            except:
                pass
    # else:
    #   print("NOT HERE")
    #   print(param_str)

    for  q in set(other_vars):
        candidate = f"  {q} "
        if candidate not in alternatives:
            alternatives.append(candidate)
    alternatives.append(f"{expr_h.to_string().strip()} | - ({expr_h.to_string().strip()})")
    # Option 2: alternatives "p + c" for each allowed constant.
    allowed_constants = ["-1.0", "0.0", "1.0"] + other_vars
    for c in allowed_constants:
        candidate = f"{param_str} + {c}"
        if candidate not in alternatives:
            alternatives.append(candidate)
    # Option 3: alternatives "p + q" for each other parameter.
    for q in other_vars:
        candidate = f"{param_str} + {q}"
        if candidate not in alternatives:
            alternatives.append(candidate)
    if GroupAction is not None:
        grammar = "{| " + " | ".join(alternatives) + " |}"
        return grammar
    # Option 4: alternatives "p + c + q" for each constant and other parameter.
    for c in allowed_constants:
            candidate = f"{param_str} (+ | - | * ) {c} + {q}"
            if candidate not in alternatives:
                alternatives.append(candidate)
    # Combine all alternatives into a regex-style grammar.
    grammar = "{| " + " | ".join(alternatives) + " |}"
    return grammar

def synthesize_generator_grammar(C, h, assignment=None, GroupAction=None):
    """
    Given function definitions C and h (FunctionDefinition objects) that return arrays,
    synthesize a regex-style grammar for g coordinate-wise.
    Return a list of grammar strings (one per parameter).
    """
    candidates = []
    if assignment is not None:
      pre_candidate = compute_precondition_candidate(assignment, GroupAction)

    for i, param in enumerate(C.params):
        comp_h = h.body_exprs[i] if i < len(h.body_exprs) else Variable(param.to_string().strip())
        grammar = synthesize_component(param, comp_h, C.params, assignment, pre_candidate)
        candidates.append(grammar)
    return candidates



# --- Assemble a Valid SKETCH Program from C and h ---
def generate_sketch_program_from_AST(C, h, assignment, GroupAction):
    """
    Given function definitions C and h (in our AST format) that return arrays,
    generate a SKETCH program that sketches a bijection g such that for all inputs:
         h(C(x1, ..., xn)) = C(g(x1), ..., g(xn))
    We generate one generator function per parameter using regex-style grammars and then
    combine them into an array generator. The harness asserts coordinate-wise equality.
    """
    assert(assignment is not None)
    C_code = C.to_string()
    h_code = h.to_string()
    g_candidate_list = synthesize_generator_grammar(C, h, assignment, GroupAction)
    # full parameter list declaration (all parameters)
    full_param_decl = ", ".join("float " + p.to_string().strip() for p in C.params)
    arg_list = ", ".join(p.to_string().strip() for p in C.params)
    # Generate one generator function per parameter.
    g_generators = ""
    for p in C.params:
        p_str = p.to_string().strip()
        candidate_grammar = g_candidate_list.pop(0)
        g_generators += f"""
generator float g_{p_str}({full_param_decl}) {{
    return {candidate_grammar};
}}
"""
    # Assemble a combined generator g that returns an array.
    param_decl = ", ".join("float " + p.to_string().strip() for p in C.params)
    arg_list = ", ".join(p.to_string().strip() for p in C.params)
    new_coords = []
    for p in C.params:
        p_str = p.to_string().strip()
        new_coords.append(f"g_{p_str}({arg_list})")
    array_literal = "{ " + ", ".join(new_coords) + " }"
    g_array_generator = f"""
generator float[{len(C.params)}] g({full_param_decl}) {{
    return {array_literal};
}}
"""
    # Build a harness that checks coordinate-wise.
    n = len(C.body_exprs)
    harness_code = f"harness void main({param_decl}) {{\n"
    # First, call C to get an array and extract its coordinates.
    harness_code += f"  float[{n}] tempC = C({arg_list});\n"
    harness_code += f"  float[{n}] lhs = h(" + ", ".join(f"tempC[{i}]" for i in range(n)) + ");\n"
    # Then, call g and feed its coordinates into C.
    harness_code += f"  float[{n}] tempG = g({arg_list});\n"
    harness_code += f"  float[{n}] rhs = C(" + ", ".join(f"tempG[{i}]" for i in range(n)) + ");\n"
    for i in range(n):
        harness_code += f"  assert(lhs[{i}] == rhs[{i}]);\n"
    harness_code += "}"
    preamble = 'include "math.skh";\n'
    sketch_program = "\n".join([preamble, h_code, C_code, g_generators, g_array_generator, harness_code])
    return sketch_program
