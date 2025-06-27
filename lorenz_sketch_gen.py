from sketch_gen import *

def lorenz():

  x = Variable('x')
  y = Variable('y')
  p = Variable('p')
  r = Variable('r')
  b = Variable('b')
  dt = Variable('dt')
  z = Variable('z')

  # Lorenz Attractor
  neg_xz = Minus(Literal(0.0), Mult(x, z))
  rx = Mult(r, x)
  sum_expr = Plus(neg_xz, rx)
  sub_expr = Minus(sum_expr, y)
  mult_dt2 = Mult(sub_expr, dt)
  new_y = Plus(mult_dt2, y)

  assign_xr = Assignment(x, Plus(Mult(Plus(Mult(Neg(p),x), Mult(p,y)),dt),x))
  assign_y =  Assignment(y, new_y)
  assign_z = Assignment(z, Plus(z, Mult(dt, Plus( Mult(Neg(x),y), Mult(Neg(b),z)))))
  program = Program([assign_xr, Assignment(y, new_y), assign_z])

  x1_update_expr = Plus(Mult(Plus(Mult(Neg(p),x), Mult(p,y)),dt),x)
  x1_update = FunctionDefinition("C", [x,y,z, p, r, b, dt], [x1_update_expr, y, z, p, r, b, dt])
  # Group action for x1: h_x1 swaps x1 and x2.
  h_x1 = FunctionDefinition("h",  [x,y,z, p, r, b, dt], [Neg(x), Neg(y), z, p, r, b, dt])

  y_update_expr = new_y
  y_update = FunctionDefinition("C", [x,y,z, p, r, b, dt], [x, y_update_expr, z, p, r, b, dt])
  h_y1 = FunctionDefinition("h",  [x,y,z, p, r, b, dt],[Neg(x), Neg(y), z, p, r, b, dt])

  z_update_expr = Plus(z, Mult(dt, Plus( Mult(Neg(x),y), Mult(Neg(b),z))))
  z_update = FunctionDefinition("C", [x,y,z, p, r, b, dt], [x, y, z_update_expr, p, r, b, dt])
  h_z1 = FunctionDefinition("h",  [x,y,z, p, r, b, dt],[Neg(x), Neg(y), z, p, r, b, dt])

  assignments = [
        ("x_update_lorenz", x1_update, h_x1,assign_xr,
           {'x': Neg(x), 'y': Neg(y), 'p': p , 'dt':dt, 'z':z,'b':b ,'r':r}
        ),
        ("y1_update_lorenz", y_update, h_y1, assign_y, {'x': Neg(x), 'y': Neg(y), 'p': p , 'dt':dt, 'z':z,'b':b ,'r':r}),
         ("z1_update_lorenz", z_update, h_z1, assign_z, {'x': Neg(x), 'y': Neg(y), 'p': p , 'dt':dt, 'z':z,'b':b ,'r':r})

    ]

  for label, funcC, funcH, a, g in assignments:
        # assert(a is not None)
        prog = generate_sketch_program_from_AST(funcC, funcH, a, g)
        # # Write prog to a .sk file in the directory sketch-1.7.6/sketch-frontend/test/sk/
        with open(f"sketch-1.7.6/sketch-frontend/test/sk/{label.replace(' ', '_')}.sk", "w") as f:
            f.write(prog)
        # print(f"\n--- Sketch Program for {label} ---\n")
        # print(prog)

lorenz()