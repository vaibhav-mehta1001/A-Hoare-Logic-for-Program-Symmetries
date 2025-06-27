#D4 dihedral group in straight line
from verifier import *
x = Variable('x')
y = Variable('y')
v = Variable('v')
a = Variable('a')
theta = Variable('theta')
dt = Variable('dt')


# D6
GroupAction = [{'x': Neg(y), 'y': x, 'theta': Plus(theta, Div(Pi2(), Literal(1.5))) , 'dt':dt, 'v':v, 'a' : a },
  {'x': x, 'y': Neg(y), 'theta': Neg(theta), 'dt':dt, 'v':v,'a' : a }]
GroupAction2 = [{'x': Neg(y), 'y': x, 'theta': Plus(theta, Div(Pi2(), Literal(1.5))) , 'dt':dt, 'v':v , 'a' : a},
  {'x': x, 'y': Neg(y), 'theta': Neg(theta), 'dt':dt, 'v':v }]


assign_xr = Assignment(x, Plus(Mult(Cos(theta),Mult(v,dt)),x))
assign_x2r = Assignment(y, Plus(Mult(Sin(theta),Mult(v,dt)),y))
program = Program([assign_xr, assign_x2r, Assignment(v, Plus(Mult(dt, a), v))])

for s in program.statements:
    print(s.to_string())
truth, postg, time = (verify_assignments(program.statements, ['x','y','v', 'dt', 'theta', 'a'], convert_gas(GroupAction),   None, None))
if truth != False:
    print(f"Verification of D6 Car in Straight Line successful in {time} seconds!")
else:
    print(f"Verification of D6 Car in Straight Line failed in {time} seconds!")