from verifier import *
count_1 = Variable("count_1")
count_2 = Variable("count_2")
b       = Variable("b")
winner  = Variable("winner")

# List to hold the assignment statements.
assignments = []

# For each variable v_i (from v_1 to v_20), update count_1 and count_2.
for i in range(1, 21):
    # Create the variable v_i.
    v_i = Variable("v" + str(i))

    # Assignment for count_1: if v_i == 0 then count_1 := count_1 + 1 else count_1.
    assign_count1 = Assignment(
        count_1,
        Piecewise(
            [Equal(v_i, Literal(0))],            # condition: v_i == 0
            [Plus(count_1, Literal(1))],           # true branch: count_1 + 1
            default_expr=count_1                   # false branch: count_1 (unchanged)
        )
    )
    assignments.append(assign_count1)

    # Assignment for count_2: if v_i == 1 then count_2 := count_2 + 1 else count_2.
    assign_count2 = Assignment(
        count_2,
        Piecewise(
            [Equal(v_i, Literal(1))],            # condition: v_i == 1
            [Plus(count_2, Literal(1))],           # true branch: count_2 + 1
            default_expr=count_2                   # false branch: count_2 (unchanged)
        )
    )
    assignments.append(assign_count2)

# Now, assign b = count_1 > count_2.
assign_b = Assignment(
    b,
    Gt(count_1, count_2)
)
# assignments.append(assign_b)

# Finally, determine the winner using a ternary expression (as Piecewise):
# If b is true then winner := 0, else winner := 1.
assign_winner = Assignment(
    winner,
    Piecewise(
        [ Gt(count_1, count_2)],                     # condition: b (if true)
        [Literal(0)],            # then: winner is 0
        default_expr=Literal(1)  # else: winner is 1
    )
)
assignments.append(assign_winner)

# Assemble the full program.
program = Program(assignments)

# Print the string representation of the program.
print(program)
for p in program.statements:
  print(p.to_string())

group_action = {}

for i in range(1, 21):
    if i % 2 == 1:
        neighbor = i + 1 if i < 20 else i
    else:
        neighbor = i - 1
    # Map variable "v{i}" to its swapped neighbor.
    group_action["v" + str(i)] = Variable("v" + str(neighbor))
group_action['count_1'] = count_1
group_action['count_2'] = count_2
group_action['b'] = b
group_action['winner'] = winner

group_action2 = {}
for i in range(1, 19):
    group_action2["v" + str(i)] = Variable("v" + str(i))

group_action2["v19"] = Variable("v20")
group_action2["v20"] = Variable("v19")
group_action2['count_1'] = count_1
group_action2['count_2'] = count_2
group_action2['b'] = b
group_action2['winner'] = winner

truth, postg, time = verify_assignments(program.statements, ['winner'], convert_gas([group_action]), None, None)
if truth != False:
    print(f"Verification of Twenty Voter successful in {time} seconds!")
else:
    print(f"Verification of Twenty Voter failed in {time} seconds!")
