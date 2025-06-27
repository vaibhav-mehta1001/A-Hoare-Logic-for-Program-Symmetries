from sketch_gen import * 

def AAC():
   x = Variable('x')
   y = Variable('y')
   z = Variable('z')
   theta = Variable('theta')
   dt = Variable('dt')
   A = Variable('A')
   C = Variable('C')

   # GroupAction = [{'x': Neg(x) , 'y': Plus(Mult(Pi2(),Literal(2.0)), Neg(y)), 'z': Plus(z,Neg((Mult(Pi2(),Literal(2.0))))),  'theta' : theta, 'dt':dt, 'A':A, 'C':C}]

   assign_xr = Assignment(x, Plus(Mult(Plus(Mult(A, Sin(z)), (Mult(C, Cos(y)))),dt),x))
   assign_x2r = Assignment(y, Plus(Mult(Plus(Mult(A, Sin(x)), (Mult(A, Cos(z)))),dt),y))
   assign_z = Assignment(z, Plus(Mult(Plus(Mult(C, Sin(y)), (Mult(A, Cos(z)))),dt),z))
   program = Program([assign_xr, assign_x2r, assign_z])

   prog  = [s.to_string() for s in program.statements]

   x1_update_expr = Plus(Mult(Plus(Mult(A, Sin(z)), (Mult(C, Cos(y)))),dt),x)
   x1_update = FunctionDefinition("C", [x,y,z,theta,dt, A,C], [x1_update_expr, y, z, theta, dt, A, C])
   # Group action for x1: h_x1 swaps x1 and x2.
   h_x1 = FunctionDefinition("h", [x,y,z,theta,dt, A,C], [Neg(x), Plus(Mult(Pi2(),Literal(2.0)),Neg(y)),Plus(z,Neg((Mult(Pi2(),Literal(2.0))))), theta, dt, A, C])

   y_update_expr = Plus(Mult(Plus(Mult(A, Sin(x)), (Mult(A, Cos(z)))),dt),y)
   y_update = FunctionDefinition("C", [x,y,z,theta,dt, A,C], [x, y_update_expr, z, theta, dt, A, C])
   h_y1 = FunctionDefinition("h", [x,y,z,theta,dt, A,C], [Neg(x), Plus(Mult(Pi2(),Literal(2.0)),Neg(y)),Plus(z,Neg((Mult(Pi2(),Literal(2.0))))), theta, dt, A, C])

   z_update_expr = Plus(Mult(Plus(Mult(C, Sin(y)), (Mult(A, Cos(x)))),dt),z)
   z_update = FunctionDefinition("C", [x,y,z,theta,dt, A,C], [x, y, z_update_expr, theta, dt, A, C])
   h_z1 = FunctionDefinition("h", [x,y,z,theta,dt, A,C], [Neg(x), Plus(Mult(Pi2(),Literal(2.0)),Neg(y)),Plus(z,Neg((Mult(Pi2(),Literal(2.0))))), theta, dt, A, C])

   assignments = [
        ("x1_update_AAC", x1_update, h_x1, assign_xr,
           {'x': Neg(x) , 'y': Plus(Mult(Pi2(),Literal(2.0)),Neg(y)), 'z': Plus(z,Neg((Mult(Pi2(),Literal(2.0))))),  'theta' : theta, 'dt':dt, 'A':A, 'C':C}
        ),
        ("y1_update_AAC", y_update, h_y1, assign_x2r,
         {'x': Neg(x) , 'y': Plus(Mult(Pi2(),Literal(2.0)),Neg(y)), 'z': Plus(z,Neg((Mult(Pi2(),Literal(2.0))))),  'theta' : theta, 'dt':dt, 'A':A, 'C':C}),
        ("z1_update_AAC", z_update, h_z1, assign_z, {'x': Neg(x) , 'y': Plus(Mult(Pi2(),Literal(2.0)),Neg(y)), 'z': Plus(z,Neg((Mult(Pi2(),Literal(2.0))))),  'theta' : theta, 'dt':dt, 'A':A, 'C':C})

    ]

   for label, funcC, funcH, a, g in assignments:
        assert(a is not None)
        prog = generate_sketch_program_from_AST(funcC, funcH, a, g)
        with open(f"sketch-1.7.6/sketch-frontend/test/sk/{label.replace(' ', '_')}.sk", "w") as f:
            f.write(prog)

        # print(f"\n--- Sketch Program for {label} ---\n")
        # print(prog)


AAC()