from sketch_gen import * 


def D4_G1():
  x = Variable('x')
  y = Variable('y')
  v = Variable('v')
  a = Variable('a')
  theta = Variable('theta')
  dt = Variable('dt')


  # D4
  GroupAction = [{'x': Neg(y), 'y': x, 'theta': Plus(theta, Div(Pi2(), Literal(1.0))) , 'dt':dt, 'v':v, 'a' : a },
    {'x': x, 'y': Neg(y), 'theta': Neg(theta), 'dt':dt, 'v':v,'a' : a }]

  assign_xr= Assignment(x, Plus(Mult(Cos(theta),Mult(v,dt)),x))
  assign_y = Assignment(y, Plus(Mult(Sin(theta),Mult(v,dt)),y))


  x1_update_expr = Plus(Mult(Cos(theta),Mult(v,dt)),x)
  x1_update = FunctionDefinition("C", [x,y,v, a, theta, dt], [x1_update_expr, y, v, a, theta, dt])

  h_x1 = FunctionDefinition("h",  [x,y,v, a, theta, dt], [Plus(Mult(Mult(Neg(dt), v),Sin(theta)),Neg(y) ), Plus(Mult(Mult(Neg(dt), v),Cos(theta)),(x)), v, a, Plus(theta, Div(Pi2(), Literal(1.0))) , dt])

  y_update_expr = Plus(Mult(Sin(theta),Mult(v,dt)),y)
  y_update =  FunctionDefinition("C", [x,y,v, a, theta, dt], [x, y_update_expr, v, a, theta, dt])
  h_y1 = FunctionDefinition("h",  [x,y,v, a, theta, dt], [Neg(y), x, v, a, Plus(theta, Div(Pi2(), Literal(1.0))) , dt])

  assignments = [
        ("D4_x1 update", x1_update, h_x1,assign_xr,
           {'x':Plus(Mult(Mult(Neg(dt), v),Sin(theta)),Neg(y) ), 'y': Plus(Mult(Mult(Neg(dt), v),Cos(theta)),(x)), 'theta': Plus(theta, Div(Pi2(), Literal(1.0))), 'dt':dt, 'v':v, 'a' : a},

        ),
        ("D4_y1_update", y_update, h_y1, assign_y, {'x': Neg(y), 'y': x, 'theta': Plus(theta, Div(Pi2(), Literal(1.0))) , 'dt':dt, 'v':v, 'a' : a }),
    ]

  for label, funcC, funcH, a, g in assignments:
        assert(a is not None)
        prog = generate_sketch_program_from_AST(funcC, funcH, a, g)
        with open(f"sketch-1.7.6/sketch-frontend/test/sk/{label.replace(' ', '_')}.sk", "w") as f:
            f.write(prog)
        # print(f"\n--- Sketch Program for {label} 2nd Generator ---\n")
        # print(prog)


def D4_G2():
  x = Variable('x')
  y = Variable('y')
  v = Variable('v')
  a = Variable('a')
  theta = Variable('theta')
  dt = Variable('dt')


  assign_xr= Assignment(x, Plus(Mult(Cos(theta),Mult(v,dt)),x))
  assign_y = Assignment(y, Plus(Mult(Sin(theta),Mult(v,dt)),y))
  # program = Program([assign_xr, assign_x2r, Assignment(v, Plus(Mult(dt, a), v))])


  x1_update_expr = Plus(Mult(Cos(theta),Mult(v,dt)),x)
  x1_update = FunctionDefinition("C", [x,y,v, a, theta, dt], [x1_update_expr, y, v, a, theta, dt])

  h_x1 = FunctionDefinition("h",  [x,y,v, a, theta, dt], [x, Neg(y), v, a, Neg(theta) , dt])


  ## Second Generator
  # h_x1 = FunctionDefinition("h",  [x,y,v, a, theta, dt], [Plus(Mult(Mult(Neg(dt), v),Sin(theta)),Neg(y) ), Plus(Mult(Mult(Neg(dt), v),Cos(theta)),(x)), v, a, Plus(theta, Div(Pi2(), Literal(1.0))) , dt])
  y_update_expr = Plus(Mult(Sin(theta),Mult(v,dt)),y)
  y_update =  FunctionDefinition("C", [x,y,v, a, theta, dt], [x, y_update_expr, v, a, theta, dt])
  assign_y = Assignment(y, Plus(Mult(Sin(theta),Mult(v,dt)),y))
  h_y1 = FunctionDefinition("h",  [x,y,v, a, theta, dt], [x, Neg(y), v, a, Neg(theta) , dt])
  assignments = [
        ("D4_x1_update_2", x1_update, h_x1,assign_xr,
          {'x': x, 'y': Neg(y), 'theta': Neg(theta), 'dt':dt, 'v':v, 'a' : a },

        ),
        ("D4_y1_update_2", y_update, h_y1, assign_y, {'x': x, 'y': Neg(y), 'theta': Neg(theta), 'dt':dt, 'v':v, 'a' : a }),

    ]

  for label, funcC, funcH, a, g in assignments:
        assert(a is not None)
        prog = generate_sketch_program_from_AST(funcC, funcH, a, g)
        with open(f"sketch-1.7.6/sketch-frontend/test/sk/{label.replace(' ', '_')}.sk", "w") as f:
            f.write(prog)
        # print(f"\n--- Sketch Program for {label} 2nd Generator ---\n")
        # print(prog)

D4_G1()
D4_G2()