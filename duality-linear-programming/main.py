
EPS = 1e-9


def print_table(title, table, basis, headers):
    print("\n" + title)
    print("-" * 85)

    print(f"{'Basis':<10}", end="")
    for name in headers:
        print(f"{name:>12}", end="")
    print()

    for i, row in enumerate(table):
        if i < len(basis):
            name = basis[i]
        else:
            name = "Z"

        print(f"{name:<10}", end="")
        for value in row:
            print(f"{value:>12.4f}", end="")
        print()

    print("-" * 85)


def simplex_method():
    # Initial simplex tableau.
    # Variables: x1, x2, s1, s2, s3, B

    table = [
        [2,  1, 1, 0, 0, 8],
        [1, -1, 0, 1, 0, 2],
        [-1, 1, 0, 0, 1, 3],
        [3, -1, 0, 0, 0, 0]
    ]

    basis = ["s1", "s2", "s3"]
    headers = ["x1", "x2", "s1", "s2", "s3", "B"]

    print("\n" + "=" * 85)
    print("SOLVING THE PRIMAL PROBLEM USING THE SIMPLEX METHOD")
    print("=" * 85)

    print_table("Initial Simplex Tableau", table, basis, headers)

    iteration = 0

    while True:
        # Find the entering column.
        objective = table[-1]
        entering = None

        for j in range(len(headers) - 1):
            if objective[j] < -EPS:
                entering = j
                break

        # If there are no negative coefficients,
        # the optimal solution has been found.
        if entering is None:
            break

        # Find the leaving row using the minimum ratio test.
        leaving = None
        min_ratio = float("inf")

        for i in range(len(basis)):
            coefficient = table[i][entering]

            if coefficient > EPS:
                ratio = table[i][-1] / coefficient

                if ratio < min_ratio:
                    min_ratio = ratio
                    leaving = i

        if leaving is None:
            print("The problem is unbounded.")
            return None

        iteration += 1

        print(f"\nITERATION {iteration}")
        print(f"Entering column: {headers[entering]}")
        print(f"Leaving row: {basis[leaving]}")
        print(f"Pivot element: {table[leaving][entering]:.4f}")

        # Normalize the pivot row.
        pivot = table[leaving][entering]

        table[leaving] = [
            value / pivot for value in table[leaving]
        ]

        # Transform the remaining rows.
        for i in range(len(table)):
            if i != leaving:
                factor = table[i][entering]

                table[i] = [
                    table[i][j] - factor * table[leaving][j]
                    for j in range(len(headers))
                ]

        basis[leaving] = headers[entering]

        print_table(
            f"Simplex Tableau After Iteration {iteration}",
            table,
            basis,
            headers
        )

    # Determine the values of the basic variables.
    solution = {
        "x1": 0.0,
        "x2": 0.0,
        "s1": 0.0,
        "s2": 0.0,
        "s3": 0.0
    }

    for i, variable in enumerate(basis):
        solution[variable] = table[i][-1]

    optimal_z = table[-1][-1]

    print("\nOPTIMAL SOLUTION OF THE PRIMAL PROBLEM")
    print(f"x1 = {solution['x1']:.4f}")
    print(f"x2 = {solution['x2']:.4f}")
    print(f"Zmax = {optimal_z:.4f}")

    return solution, optimal_z, table, basis


def solve_dual(table, basis):
    print("\n" + "=" * 85)
    print("SOLVING THE DUAL PROBLEM")
    print("=" * 85)

    print("\nDual objective function:")
    print("Q = 8y1 + 2y2 + 3y3 -> min")

    print("\nConstraints:")
    print("2y1 + y2 - y3 >= -3")
    print("y1 - y2 + y3 >= 1")
    print("y1, y2, y3 >= 0")

    # Obtain the dual variable values
    # from the last row of the optimal simplex tableau.

    dual = {
        "y1": table[-1][2],
        "y2": table[-1][3],
        "y3": table[-1][4]
    }

    y1 = dual["y1"]
    y2 = dual["y2"]
    y3 = dual["y3"]

    q = 8 * y1 + 2 * y2 + 3 * y3

    print("\nOptimal Values of Dual Variables:")
    print(f"y1 = {y1:.4f}")
    print(f"y2 = {y2:.4f}")
    print(f"y3 = {y3:.4f}")

    print(f"\nQmin = 8*{y1:.4f} + 2*{y2:.4f} + 3*{y3:.4f}")
    print(f"Qmin = {q:.4f}")

    return dual, q


def resource_analysis(solution, dual):
    print("\n" + "=" * 85)
    print("RESOURCE SCARCITY ANALYSIS")
    print("=" * 85)

    x1 = solution["x1"]
    x2 = solution["x2"]

    # Left-hand side values of the constraints.
    used = [
        2 * x1 + x2,
        x1 - x2,
        -x1 + x2
    ]

    # Available resource amounts.
    available = [8, 2, 3]

    names = ["Resource 1", "Resource 2", "Resource 3"]

    dual_values = [
        dual["y1"],
        dual["y2"],
        dual["y3"]
    ]

    print("\nResource Usage Analysis:")

    for i in range(3):
        remaining = available[i] - used[i]

        print(f"\n{names[i]}:")
        print(f"  Available amount: {available[i]:.4f}")
        print(f"  Left-hand side value: {used[i]:.4f}")
        print(f"  Remaining amount: {remaining:.4f}")
        print(f"  Dual value: {dual_values[i]:.4f}")

        if abs(dual_values[i]) < EPS:
            print("  Conclusion: The resource is non-scarce.")
        else:
            print("  Conclusion: The resource is scarce.")

    print("\nGENERAL CONCLUSION:")

    positive = [
        i + 1 for i, value in enumerate(dual_values)
        if value > EPS
    ]

    if positive:
        print(
            "Scarce resources:",
            ", ".join(map(str, positive))
        )

        maximum = max(dual_values)

        most_deficient = [
            i + 1 for i, value in enumerate(dual_values)
            if abs(value - maximum) < EPS
        ]

        print(
            "Most scarce resources:",
            ", ".join(map(str, most_deficient))
        )
    else:
        print("There are no scarce resources.")


def main():
    print("=" * 85)
    print("LABORATORY WORK No. 3")
    print("DUALITY IN LINEAR PROGRAMMING PROBLEMS")
    print("VARIANT 8")
    print("=" * 85)

    print("\nPRIMAL PROBLEM:")
    print("Z = -3x1 + x2 -> max")
    print("2x1 + x2 <= 8")
    print("x1 - x2 <= 2")
    print("-x1 + x2 <= 3")
    print("x1, x2 >= 0")

    result = simplex_method()

    if result is None:
        return

    solution, optimal_z, table, basis = result

    dual, optimal_q = solve_dual(table, basis)

    resource_analysis(solution, dual)

    print("\n" + "=" * 85)
    print("DUALITY THEOREM VERIFICATION")
    print("=" * 85)

    print(f"Primal optimal value: Zmax = {optimal_z:.4f}")
    print(f"Dual optimal value: Qmin = {optimal_q:.4f}")

    if abs(optimal_z - optimal_q) < EPS:
        print("Equality holds.")
        print("The solution is optimal.")
    else:
        print("Equality does not hold.")

    print("\nLABORATORY WORK COMPLETED SUCCESSFULLY.")


if __name__ == "__main__":
    main()
