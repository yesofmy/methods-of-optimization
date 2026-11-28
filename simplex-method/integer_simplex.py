
EPS = 1e-9
MAX_NODES = 100


def fmt(value):
    if value is None:
        return "—"
    if abs(value) < 1e-10:
        value = 0.0
    return f"{value:.4f}".rstrip("0").rstrip(".")


def print_table(number, T, basis, cb, costs, names):
    m = len(T)
    n = len(costs)

    headers = ["Cb", "Basis", "b"] + names
    widths = [8, 10, 10] + [10] * n

    print(f"\nTABLE {number}")
    print("-" * sum(widths))

    print("".join(str(v).ljust(w)
                  for v, w in zip(headers, widths)))
    print("-" * sum(widths))

    for i, row in enumerate(T):
        values = [
            fmt(costs[basis[i]]),
            names[basis[i]],
            fmt(row[-1])
        ]
        values += [fmt(v) for v in row[:-1]]

        print("".join(str(v).ljust(w)
                      for v, w in zip(values, widths)))

    zrow = [
        sum(cb[i] * T[i][j] for i in range(m))
        for j in range(n + 1)
    ]

    delta = [zrow[j] - costs[j] for j in range(n)]

    values = ["", "Delta", fmt(zrow[-1])]
    values += [fmt(v) for v in delta]

    print("-" * sum(widths))
    print("".join(str(v).ljust(w)
                  for v, w in zip(values, widths)))
    print("-" * sum(widths))

    return delta


# --------------------------------------------------
# PROBLEM TRANSFORMATION WITH VARIABLE BOUNDS
# --------------------------------------------------

def build_problem(A, b, c, lower, upper):

    n = len(c)
    A_new = []
    b_new = []

    for i in range(len(A)):
        shift = sum(A[i][j] * lower[j] for j in range(n))
        new_b = b[i] - shift

        if new_b < -EPS:
            return None

        A_new.append(A[i][:])
        b_new.append(max(0.0, new_b))

    # Add upper bounds for variables
    for j in range(n):
        if upper[j] is not None:
            if upper[j] < lower[j] - EPS:
                return None

            row = [0.0] * n
            row[j] = 1.0

            A_new.append(row)
            b_new.append(upper[j] - lower[j])

    return A_new, b_new


# --------------------------------------------------
# SIMPLEX METHOD
# --------------------------------------------------

def simplex_method(A, b, c, node_name):

    m = len(A)
    n = len(c)

    names = (
        [f"x{i + 1}" for i in range(n)] +
        [f"s{i + 1}" for i in range(m)]
    )

    costs = list(c) + [0.0] * m

    T = []

    for i in range(m):
        row = list(map(float, A[i]))

        for j in range(m):
            row.append(1.0 if i == j else 0.0)

        row.append(float(b[i]))
        T.append(row)

    basis = [n + i for i in range(m)]
    cb = [0.0] * m

    iteration = 0

    print("\n" + "=" * 90)
    print(f"SIMPLEX METHOD: {node_name}")
    print("=" * 90)

    while iteration < 100:

        delta = print_table(
            iteration, T, basis, cb, costs, names
        )

        candidates = [
            j for j, value in enumerate(delta)
            if value < -EPS
        ]

        if not candidates:
            print("\nOptimal solution of the linear problem found.")
            break

        entering = min(candidates, key=lambda j: delta[j])

        print(
            f"\nVariable {names[entering]} enters the basis."
        )

        ratios = []

        for row in T:
            a = row[entering]

            if a > EPS:
                ratios.append(row[-1] / a)
            else:
                ratios.append(None)

        print("Calculating theta:")

        for i, value in enumerate(ratios):
            print(f"  Row {i + 1}: {fmt(value)}")

        eligible = [
            (value, i)
            for i, value in enumerate(ratios)
            if value is not None and value >= -EPS
        ]

        if not eligible:
            print("The objective function is unbounded.")
            return None

        minimum = min(value for value, _ in eligible)

        leaving = next(
            i for value, i in eligible
            if abs(value - minimum) <= EPS
        )

        pivot = T[leaving][entering]

        print(f"Minimum theta = {fmt(minimum)}.")
        print(
            f"Variable {names[basis[leaving]]} leaves the basis."
        )
        print(f"Pivot element = {fmt(pivot)}.")

        # Gauss-Jordan elimination
        T[leaving] = [
            value / pivot for value in T[leaving]
        ]

        for i in range(m):

            if i == leaving:
                continue

            factor = T[i][entering]

            T[i] = [
                T[i][j] - factor * T[leaving][j]
                for j in range(n + m + 1)
            ]

        basis[leaving] = entering
        cb[leaving] = costs[entering]

        iteration += 1

        print("The simplex table has been updated.")

    else:
        print("Maximum number of iterations reached.")
        return None

    values = [0.0] * (n + m)

    for i, basic in enumerate(basis):
        values[basic] = T[i][-1]

    x = values[:n]
    objective = sum(c[j] * x[j] for j in range(n))

    print("\nSimplex method result:")

    for j, value in enumerate(x):
        print(f"  x{j + 1} = {fmt(value)}")

    print(f"  F = {fmt(objective)}")

    return x, objective


# --------------------------------------------------
# BRANCH AND BOUND METHOD
# --------------------------------------------------

def branch_and_bound(A, b, c):

    n = len(c)

    # Initial variable bounds
    initial_lower = [0.0] * n
    initial_upper = [None] * n

    nodes = [{
        "lower": initial_lower,
        "upper": initial_upper,
        "name": "Initial problem"
    }]

    best_solution = None
    best_value = float("-inf")

    node_counter = 0

    print("\n" + "=" * 90)
    print("BRANCH AND BOUND METHOD")
    print("=" * 90)

    while nodes:

        if node_counter >= MAX_NODES:
            print("\nMaximum number of nodes reached.")
            break

        node = nodes.pop()

        node_counter += 1

        lower = node["lower"]
        upper = node["upper"]

        print("\n" + "#" * 90)
        print(f"NODE #{node_counter}: {node['name']}")
        print("#" * 90)

        print("Lower bounds:", [fmt(v) for v in lower])

        print(
            "Upper bounds:",
            [fmt(v) if v is not None else "∞" for v in upper]
        )

        problem = build_problem(
            A, b, c, lower, upper
        )

        if problem is None:
            print("The node is infeasible.")
            continue

        A_node, b_node = problem

        result = simplex_method(
            A_node, b_node, c, node["name"]
        )

        if result is None:
            continue

        y, objective = result

        # Restore original variable values
        x = [
            y[j] + lower[j]
            for j in range(n)
        ]

        print("\nCurrent node solution:")

        for j, value in enumerate(x):
            print(f"  x{j + 1} = {fmt(value)}")

        print(
            f"  F = {fmt(objective + sum(c[j] * lower[j] for j in range(n)))}"
        )

        # Calculate the objective function with the shift
        objective += sum(
            c[j] * lower[j] for j in range(n)
        )

        # Bound checking
        if best_solution is not None and objective <= best_value + EPS:
            print(
                "Node pruned: its bound is not better than the current best solution."
            )
            continue

        # Find a fractional variable
        fractional = None

        for j in range(n):
            if abs(x[j] - round(x[j])) > EPS:
                fractional = j
                break

        # If all variables are integers
        if fractional is None:

            integer_x = [round(value) for value in x]

            print("\nAn integer feasible solution has been found!")

            for j, value in enumerate(integer_x):
                print(f"  x{j + 1} = {value}")

            print(f"  F = {fmt(objective)}")

            if objective > best_value + EPS:
                best_value = objective
                best_solution = integer_x

                print("A new best solution has been found.")

            continue

        # Branching on a fractional variable
        j = fractional

        floor_value = int(x[j] // 1)
        ceil_value = floor_value + 1

        print("\nFractional variable found:")
        print(f"  x{j + 1} = {fmt(x[j])}")

        print(
            f"\nCreating two branches:"
            f"\n  1) x{j + 1} <= {floor_value}"
            f"\n  2) x{j + 1} >= {ceil_value}"
        )

        # Right branch: x_j >= ceil_value
        right_lower = lower[:]
        right_lower[j] = max(right_lower[j], ceil_value)

        if upper[j] is None or right_lower[j] <= upper[j] + EPS:
            nodes.append({
                "lower": right_lower,
                "upper": upper[:],
                "name": f"x{j + 1} >= {ceil_value}"
            })

        # Left branch: x_j <= floor_value
        left_upper = upper[:]

        if left_upper[j] is None:
            left_upper[j] = floor_value
        else:
            left_upper[j] = min(
                left_upper[j], floor_value
            )

        if left_upper[j] >= lower[j] - EPS:
            nodes.append({
                "lower": lower[:],
                "upper": left_upper,
                "name": f"x{j + 1} <= {floor_value}"
            })

    # --------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------

    print("\n" + "=" * 90)
    print("OPTIMAL INTEGER SOLUTION")
    print("=" * 90)

    if best_solution is None:
        print("No integer feasible solution was found.")
        return

    for j, value in enumerate(best_solution):
        print(f"x{j + 1} = {value}")

    print(f"Fmax = {fmt(best_value)}")

    print("\nConstraint verification:")

    for i in range(len(A)):
        left = sum(
            A[i][j] * best_solution[j]
            for j in range(n)
        )

        status = (
            "SATISFIED"
            if left <= b[i] + EPS
            else "NOT SATISFIED"
        )

        print(
            f"  {i + 1}) {fmt(left)} <= {fmt(b[i])} — {status}"
        )

    print("\nInteger condition verification:")

    for j, value in enumerate(best_solution):
        print(f"  x{j + 1} = {value} — integer")

    print(f"\nNumber of processed nodes: {node_counter}")
    print("=" * 90)


# --------------------------------------------------
# MAIN FUNCTION
# --------------------------------------------------

def solve_integer_task():

    # F = x1 + x2 -> max
    c = [1.0, 1.0]

    # System of constraints
    A = [
        [2.0, 1.0],
        [1.0, -1.0],
        [-1.0, 1.0]
    ]

    b = [8.0, 2.0, 3.0]

    print("=" * 90)
    print("INTEGER PROGRAMMING PROBLEM")
    print("=" * 90)

    print("\nObjective function:")
    print("F = x1 + x2 -> max")

    print("\nConstraints:")
    print("2*x1 + x2 <= 8")
    print("x1 - x2 <= 2")
    print("-x1 + x2 <= 3")

    print("\nConditions:")
    print("x1 >= 0")
    print("x2 >= 0")
    print("x1, x2 must be integers")

    branch_and_bound(A, b, c)


if __name__ == "__main__":
    solve_integer_task()
    input("\nPress Enter to exit...")
