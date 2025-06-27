from verifier import *

x = Variable('x')
y = Variable('y')
z = Variable('z')
v = Variable('v')
a     = Variable("a")
u     = Variable("u")
phi   = Variable("phi")
theta = Variable("theta")
L     = Variable("L")
dt = Variable('dt')

GroupAction = [{'x': Plus(x,Literal(1.0)), 'y': y, 'theta': theta, 'v': v, 'a': a, 'dt': dt, 'u': u, 'phi': phi, 'L': L}, 
               {'x': x, 'y':Plus(y,Literal(1.0)), 'theta': theta, 'v': v, 'dt': dt, 'a': a, 'dt': dt, 'u': u, 'phi': phi, 'L': L} ] 
GroupAction2 = [{'x': Plus(x,Literal(1.0)), 'y': y, 'theta': theta, 'v': v, 'dt': dt, 'a': a, 'dt': dt, 'u': u, 'phi': phi, 'L': L},  
                {'x': x, 'y':Plus(y,Literal(1.0)), 'theta': theta, 'v': v, 'dt': dt, 'a': a, 'dt': dt, 'u': u, 'phi': phi, 'L': L} ] 
assign_v = Assignment(
    v,
    Plus(
        Mult(a, dt),
        v
    )
)

#  phi := u * dt + phi;
assign_phi = Assignment(
    phi,
    Plus(
        Mult(u, dt),
        phi
    )
)

#  theta := (v/L) * tan(phi) * dt + theta;
assign_theta = Assignment(
    theta,
    Plus(
        Mult(
            Mult(
                Div(v, L),
                Tan(phi)
            ),
            dt
        ),
        theta
    )
)

assign_xr = Assignment(x, Plus(Mult(Cos(theta),Mult(v,dt)),x))

assign_x2r = Assignment(y, Plus(Mult(Sin(theta),Mult(v,dt)),y))

program = Program([assign_xr, assign_x2r, assign_v, assign_phi, assign_theta])
for s in program.statements:
    print(s.to_string())
truth, postg, time = verify_assignments(program.statements, ['x','y','v', 'theta','dt', 'v', 'a', 'phi', 'L'], convert_gas(GroupAction), convert_gas_Z3(GroupAction2), None)
if truth != False:
    print(f"Verification of Car in Straight Line successful in {time} seconds!")
else:
    print(f"Verification of Car in Straight Line failed in {time} seconds!")    
# print(verify_assignments(program.statements, ['x','y','v', 'theta','dt', 'v', 'a', 'phi', 'L'], convert_gas(GroupAction), convert_gas_Z3(GroupAction2), None))