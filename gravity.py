from verifier import *

#Gravity Example
x = Variable('x')
y = Variable('y')
z = Variable('z')
v = Variable('v')
F1 = Variable('f1')
m1 = Variable('m1')
F2 = Variable('f2')
m2 = Variable('m2')
v2 = Variable('v2')
theta = Variable('theta')
x2 = Variable('x2')
dt = Variable('dt')
G = Literal(6.31)
# x = 5;

assign_y = Assignment(v, Plus(Mult(Div(F1,m1),dt),v))
assign_x = Assignment(v2, Plus(Mult(Div(Neg(F1),m2),dt),v2))
assign_xr = Assignment(x, Plus(Mult(Cos(theta),Mult(v,dt)),x))
assign_x2r = Assignment(x2, Plus(Mult(Cos(theta),Mult(v2,dt)),x2))

assign_F = Assignment(F1, Div(Mult(G, Mult(m1,Mult(m2,Plus(x,Neg(x2))))), Power(Abs(Plus(x,Neg(x2))),Literal(2))))


GroupAction = {'x': x2, 'x2': x, 'v': v2, 'v2':v, 'm1':m2, 'm2':m1, 'f1':Neg(F1)}
GroupAction2 = {'x': x2, 'x2': x, 'v': v2, 'v2':v, 'm1':m2, 'm2':m1, 'f1':Neg(F1)}
assgn = ([GroupAction.copy()], [GroupAction2.copy()])

program = Program([assign_F, assign_y, assign_x, assign_xr, assign_x2r])

for s in program.statements:
    print(s.to_string())


truth, postg, time = verify_assignments(program.statements, ['x','x2','v', 'v2', 'm1','m2','f1'], [convert_ga(GroupAction)], [convert_ga_Z3(GroupAction2)],[assgn])

if truth != False: 
     print(f"Verification of Gravity successful in {time} seconds!")
else:
    print(f"Verification of Gravity failed in {time} seconds!")
