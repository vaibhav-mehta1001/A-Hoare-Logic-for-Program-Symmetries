from sketch_gen import *

def car():
  
  x = Variable('x')
  y = Variable('y')
  v = Variable('v')
  a     = Variable("a")
  u     = Variable("u")
  phi   = Variable("phi")
  theta = Variable("theta")
  l     = Variable("L")
  dt = Variable('dt')


  
  assign_xr= Assignment(x, Plus(Mult(Cos(theta),Mult(v,dt)),x))
  assign_y = Assignment(y, Plus(Mult(Sin(theta),Mult(v,dt)),y))


  x1_update_expr = Plus(Mult(Cos(theta),Mult(v,dt)),x)
  x1_update = FunctionDefinition("C", [x,y,v, a,u,phi ,theta, l, dt], [x1_update_expr, y, v, a, u, phi,theta, l, dt])
  h_x1 = FunctionDefinition("h",   [x,y,v, a, u,phi ,theta, l, dt], [Plus(x, Literal(1.0)), Plus(y, Literal(1.0)), v,a, u, phi,theta,l, dt])

  y_update_expr = Plus(Mult(Sin(theta),Mult(v,dt)),y)
  y_update =  FunctionDefinition("C",  [x,y,v, a, u,phi ,theta, l, dt], [x, y_update_expr, v,a,u,phi, theta, l, dt])
  h_y1 = FunctionDefinition("h",   [x,y,v, a, u,phi ,theta, l, dt], [Plus(x, Literal(1.0)), Plus(y, Literal(1.0)), v,a, u, phi,theta,l, dt])

  assign_v = Assignment(
    v,
    Plus(
        Mult(a, dt),
        v
    )
  )
  v_update_expr = Plus(Mult(a, dt), v)
  v_update = FunctionDefinition("C", [x,y,v, a, u,phi ,theta, l, dt], [x, y, v_update_expr, a, u, phi,theta,l, dt])
  h_v1 = FunctionDefinition("h",  [x,y,v, a, u,phi ,theta, l, dt], [Plus(x, Literal(1.0)), Plus(y, Literal(1.0)), v,a, u, phi,theta,l, dt])

  assign_phi = Assignment(
    phi,
    Plus(
        Mult(u, dt),
        phi
    )
  )
  phi_update_expr = Plus(Mult(u, dt), phi)
  phi_update = FunctionDefinition("C", [x,y,v, a, u,phi ,theta, l, dt], [x, y, v, a, u, phi_update_expr,theta,l, dt])
  h_phi1 = FunctionDefinition("h",   [x,y,v, a, u,phi ,theta, l, dt], [Plus(x, Literal(1.0)), Plus(y, Literal(1.0)), v,a, u, phi,theta,l, dt]) 
  #  theta := (v/L) * tan(phi) * dt + theta;
  assign_theta = Assignment(
    theta,
    Plus(
        Mult(
            Mult(
                Div(v,l),
                Tan(phi)
            ),
            dt
        ),
        theta
    )
  )
  theta_update_expr = Plus(Mult(Mult(Div(v, l), Tan(phi)), dt), theta)
  theta_update = FunctionDefinition("C", [x,y,v, a, u,phi ,theta, l, dt], [x, y, v, a, u, phi, theta_update_expr,l, dt])
  h_theta1 = FunctionDefinition("h",  [x,y,v, a, u,phi, theta, l, dt], [Plus(x, Literal(1.0)), Plus(y, Literal(1.0)), v,a, u, phi,theta,l, dt])

  assignments = [
        ("car_x1 update", x1_update, h_x1,assign_xr,
           {'x':  Plus(x, Literal(1.0)), 'y': Plus(y, Literal(1.0)), 'theta': theta, 'dt':dt, 'v':v, 'L' : l, 'u' : u, 'a' : a , 'phi' : phi },
        ),
        ("car_y1_update", y_update, h_y1, assign_y,   {'x':  Plus(x, Literal(1.0)), 'y': Plus(y, Literal(1.0)), 'theta': theta, 'dt':dt, 'v':v, 'L' : l, 'u' : u, 'a' : a , 'phi' : phi }),
        ("car_v1_update", v_update, h_v1, assign_v,   {'x':  Plus(x, Literal(1.0)), 'y': Plus(y, Literal(1.0)), 'theta': theta, 'dt':dt, 'v':v, 'L' : l, 'u' : u, 'a' : a , 'phi' : phi }),
        ("car_phi1_update", phi_update, h_phi1, assign_phi, {'x':  Plus(x, Literal(1.0)), 'y': Plus(y, Literal(1.0)), 'theta': theta, 'dt':dt, 'v':v, 'L' : l, 'u' : u, 'a' : a , 'phi' : phi },),
        ("car_theta1_update", theta_update, h_theta1, assign_theta,  {'x':  Plus(x, Literal(1.0)), 'y': Plus(y, Literal(1.0)), 'theta': theta, 'dt':dt, 'v':v, 'L' : l, 'u' : u, 'a' : a , 'phi' : phi })
    ]

  for label, funcC, funcH, a, g in assignments:
        assert(a is not None)
        prog = generate_sketch_program_from_AST(funcC, funcH, a, g)
        with open(f"sketch-1.7.6/sketch-frontend/test/sk/{label.replace(' ', '_')}.sk", "w") as f:
            f.write(prog)
        # print(f"\n--- Sketch Program for {label} 2nd Generator ---\n")
        # print(prog)


car()