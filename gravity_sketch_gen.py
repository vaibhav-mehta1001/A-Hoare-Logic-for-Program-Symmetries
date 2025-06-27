from sketch_gen import *
def main():
    # Full state for gravity simulation: x1, x2, v1, v2, m1, m2, G, dt.
    x1 = Variable("x1")
    x2 = Variable("x2")
    v1 = Variable("v1")
    v2 = Variable("v2")
    m1 = Variable("m1")
    m2 = Variable("m2")
    G  = Variable("G")
    dt = Variable("dt")
    f1 = Variable("f1")

    # Assignment 1: F1 update.
    # F1 := ( (G * m1 * m2) * (x1 - x2) ) / ( |x1 - x2|^3 )
    diff = Minus(x1, x2)
    numerator = Mult(Mult(Mult(G, m1), m2), diff)
    denominator = Power(Abs(diff), Literal(3))
    F1_expr = Div(numerator, denominator)
    F1 = FunctionDefinition("C", [f1, x1, x2, v1, v2, m1, m2, G, dt], [F1_expr, x1, x2, v1, v2, m1, m2, G, dt])
    
    # Group action for F1: h_F1 swaps x1<->x2, m1<->m2, v1<->v2 and negates F1.
    neg_F1 = Minus(Literal(0.0), f1)
    h_F1 = FunctionDefinition("h", [f1, x1, x2, v1, v2, m1, m2, G, dt], [neg_F1, x2, x1, v2, v1, m2, m1, G, dt])

    # Assignment 2: v1 update.
    # v1 := v1 + (F1/m1)*dt.
    v1_update_expr = Plus(v1, Mult(Div(f1, m1), dt))
    v1_update = FunctionDefinition("C", [f1, x1, x2, v1, v2, m1, m2, G, dt], [f1, x1, x2, v1_update_expr, v2, m1, m2, G, dt])
    # Group action for v1: h_v1 swaps v1 and v2.
    h_v1 = FunctionDefinition("h", [f1, x1, x2, v1, v2, m1, m2, G, dt], [neg_F1, x2, x1, Plus(Mult(Neg(dt),Div(f1, m2)),v2), Plus(Mult(Neg(dt),Div(f1, m1)),v1) ,m2, m1, G, dt])

    # Assignment 3: v2 update.
    # v2 := v2 - (F1/m2)*dt.
    v2_update_expr = Minus(v2, Mult(Div(f1, m2), dt))
    v2_update = FunctionDefinition("C", [f1, x1, x2, v1, v2, m1, m2, G, dt], [f1,x1, x2, v1,v2_update_expr, m1,m2,G,dt])
    # Group action for v2: h_v2 swaps v1 and v2.
    h_v2 = FunctionDefinition("h", [f1, x1, x2, v1, v2, m1, m2, G, dt], [neg_F1, x2, x1, v2, v1, m2, m1, G, dt])

    # Assignment 4: x1 update.
    # x1 := x1 + v1*dt.
    x1_update_expr = Plus(x1, Mult(v1, dt))
    x1_update = FunctionDefinition("C", [f1, x1, x2, v1, v2, m1, m2, G, dt], [f1,x1_update_expr, x2, v1, v2, m1, m2, G, dt])
    # Group action for x1: h_x1 swaps x1 and x2.
    h_x1 = FunctionDefinition("h", [f1, x1, x2, v1, v2, m1, m2, G, dt], [neg_F1, Plus(x2, Mult(dt, v2)),Plus(x1, Mult(Neg(dt),v1)), v2, v1, m2, m1, G, dt])

    # Assignment 5: x2 update.
    # x2 := x2 + v2*dt.
    x2_update_expr = Plus(x2, Mult(v2, dt))
    x2_update = FunctionDefinition("C", [f1, x1, x2, v1, v2, m1, m2, G, dt], [f1, x1, x2_update_expr, v1, v2, m1, m2, G, dt])
    # Group action for x2: h_x2 swaps x1 and x2.
    h_x2 = FunctionDefinition("h", [f1, x1, x2, v1, v2, m1, m2, G, dt], [neg_F1, x2, x1, v2, v1, m2, m1, G, dt])

    assignments = [
        ("F1_update_gravity", F1, h_F1,  Assignment(F1, F1_expr), {
            "f1": neg_F1, 'x2': x1, 'x1': x2, 'v2': v1, 'v1': v2, 'm1': m2, 'm2': m1, 'G': G, 'dt': dt
        }),
         ("v1_update_gravity", v1_update, h_v1, Assignment(v1, v1_update_expr), {
            "f1": neg_F1, 'x2': x1, 'x1': x2, 'v2': Plus(Mult(Neg(dt),Div(f1, m2)),v2), 'v1': Plus(Mult(Neg(dt),Div(f1, m1)),v1), 'm1': m2, 'm2': m1, 'G': G, 'dt': dt
        }),
        ("v2_update_gravity", v2_update, h_v2, Assignment(v2, v2_update_expr), {
            "f1": neg_F1, 'x2': x1, 'x1': x2, 'v2': v1, 'v1': v2, 'm1': m2, 'm2': m1, 'G': G, 'dt': dt
        }),
        ("x1_update_gravity", x1_update, h_x1, Assignment(x1, x1_update_expr), {
            "f1": neg_F1, 'x1': Plus(x2, Mult(dt, v2)), 'x2': Plus(x1, Mult(Neg(dt),v1)), 'v2': v1, 'v1': v2, 'm1': m2, 'm2': m1, 'G': G, 'dt': dt
        }),
        ("x2_update_gravity", x2_update, h_x2,  Assignment(x2, x2_update_expr) ,{
            "f1": neg_F1, 'x2': x1, 'x1': x2, 'v2': v1, 'v1': v2, 'm1': m2, 'm2': m1, 'G': G, 'dt': dt
        })
    ]

    for label, funcC, funcH, a, g in assignments:
        assert(a is not None)
        
        prog = generate_sketch_program_from_AST(funcC, funcH, a, g)
        # Write prog to a .sk file in the directory sketch-1.7.6/sketch-frontend/test/sk/
        with open(f"sketch-1.7.6/sketch-frontend/test/sk/{label.replace(' ', '_')}.sk", "w") as f:
            f.write(prog)
       
        # print(f"\n--- Sketch Program for {label} ---\n")
        # print(prog)


main()