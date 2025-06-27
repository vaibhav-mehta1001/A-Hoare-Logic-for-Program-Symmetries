from verifier import *

#dihedral group in straight line

x = Variable('x')
y = Variable('y')
v = Variable('v')
a = Variable('a')
theta = Variable('theta')
dt = Variable('dt')


# D4
GroupAction = [{'x': Neg(y), 'y': x, 'theta': Plus(theta, Div(Pi2(), Literal(1.0))) , 'dt':dt, 'v':v, 'a' : a },
  {'x': x, 'y': Neg(y), 'theta': Neg(theta), 'dt':dt, 'v':v,'a' : a }]
GroupAction2 = [{'x': Neg(y), 'y': x, 'theta': Plus(theta, Div(Pi2(), Literal(1.0))) , 'dt':dt, 'v':v , 'a' : a},
  {'x': x, 'y': Neg(y), 'theta': Neg(theta), 'dt':dt, 'v':v }]

# D8
GroupActionD8 = [{'x': Neg(y), 'y': x, 'theta': Plus(theta, ( Div(Pi2(), Literal(2.0)))) , 'dt':dt, 'v':v, 'a' : a},
  {'x': x, 'y': Neg(y), 'theta': Neg(theta), 'dt':dt, 'v':v,'a' : a }]

GroupAction2D8 = [{'x': Neg(y), 'y': x, 'theta': Plus(theta, ( Div(Pi2(), Literal(2.0)))) , 'dt':dt, 'v':v , 'a' : a},
  {'x': x, 'y': Neg(y), 'theta': Neg(theta), 'dt':dt, 'v':v }]
# D512
GroupActionD512 = [{'x': Neg(y), 'y': x, 'theta': Plus(theta, ( Div(Pi2(), Literal(128.0)))) , 'dt':dt, 'v':v, 'a' : a},
  {'x': x, 'y': Neg(y), 'theta': Neg(theta), 'dt':dt, 'v':v,'a' : a }]
GroupAction2D512 = [{'x': Neg(y), 'y': x, 'theta': Plus(theta, ( Div(Pi2(), Literal(128.0)))) , 'dt':dt, 'v':v , 'a' : a},
  {'x': x, 'y': Neg(y), 'theta': Neg(theta), 'dt':dt, 'v':v }]  

# D32
GroupActionD32 = [{'x': Neg(y), 'y': x, 'theta': Plus(theta, ( Div(Pi2(), Literal(8.0)))) , 'dt':dt, 'v':v, 'a' : a},
   {'x': x, 'y': Neg(y), 'theta': Neg(theta), 'dt':dt, 'v':v,'a' : a }]
GroupAction2D32 = [{'x': Neg(y), 'y': x, 'theta': Plus(theta, ( Div(Pi2(), Literal(8.0)))) , 'dt':dt, 'v':v , 'a' : a},
   {'x': x, 'y': Neg(y), 'theta': Neg(theta), 'dt':dt, 'v':v }]


#D 1024
GroupAction1024 = [{'x': Neg(y), 'y': x, 'theta': Plus(theta, (Div(Pi2(), Literal(512.0)))) , 'dt':dt, 'v':v, 'a' : a},
  {'x': x, 'y': Neg(y), 'theta': Neg(theta), 'dt':dt, 'v': v, 'a' : a }]
GroupAction221024 = [{'x': Neg(y), 'y': x, 'theta': Plus(theta, ( Div(Pi2(), Literal(512.0)))), 'dt':dt, 'v':v, 'a' : a},
  {'x': x, 'y': Neg(y), 'theta': Neg(theta), 'dt':dt, 'v': v, 'a' : a }]


assign_xr = Assignment(x, Plus(Mult(Cos(theta),Mult(v,dt)),x))
assign_x2r = Assignment(y, Plus(Mult(Sin(theta),Mult(v,dt)),y))
program = Program([assign_xr, assign_x2r, Assignment(v, Plus(Mult(dt, a), v))])


for s in program.statements:
    print(s.to_string())

D4t, _, D4time = verify_assignments(program.statements, ['x','y','v', 'dt', 'theta', 'a'], convert_gas(GroupAction),   None, None)

D8t, _, D8time = verify_assignments(program.statements, ['x','y','v', 'dt', 'theta', 'a'], convert_gas(GroupActionD8),   None, None)
D32t, _, D32time = verify_assignments(program.statements, ['x','y','v', 'dt', 'theta', 'a'], convert_gas(GroupActionD32),   None, None)
D512t, _, D512time = verify_assignments(program.statements, ['x','y','v', 'dt', 'theta', 'a'], convert_gas(GroupActionD512),   None, None)
D1024t, _, D1024time = verify_assignments(program.statements, ['x','y','v', 'dt', 'theta', 'a'], convert_gas(GroupAction1024),   None, None)

# Display results in a table format
print(f"{'Group':<10} {'Time (s)':<10} {'Result':<10}")
print(f"{'D4':<10} {D4time:<10.6f} {'Success' if D4t != False else 'Failure':<10}")
print(f"{'D8':<10} {D8time:<10.6f} {'Success' if D8t != False else 'Failure':<10}")
print(f"{'D32':<10} {D32time:<10.6f} {'Success' if D32t != False else 'Failure':<10}")
print(f"{'D512':<10} {D512time:<10.6f} {'Success' if D512t != False else 'Failure':<10}")
print(f"{'D1024':<10} {D1024time:<10.6f} {'Success' if D1024t != False else 'Failure':<10}")

