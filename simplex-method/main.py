EPS = 1e-9


def fmt(v):
    if v is None:
        return "—"
    if abs(v) < 1e-10:
        v = 0.0
    return f"{v:.4f}".rstrip("0").rstrip(".")


def print_table(number, basis, T, cb, costs, theta=None):
    names = ["x1", "x2", "s1", "s2", "s3"]
    headers = ["Cb", "Basis", "b"] + names + ["θ"]
    widths = [7, 9, 9, 9, 9, 9, 9, 9, 9]

    print(f"\nTABLE {number}")
    print("-" * 88)
    print("".join(str(v).ljust(w) for v, w in zip(headers, widths)))
    print("-" * 88)

    for i, row in enumerate(T):
        values = [fmt(costs[basis[i]]), names[basis[i]], fmt(row[-1])]
        values += [fmt(v) for v in row[:-1]]
        values += [fmt(theta[i]) if theta is not None else "—"]

        print("".join(str(v).ljust(w) for v, w in zip(values, widths)))

    zrow = [
        sum(cb[i] * T[i][j] for i in range(len(T)))
        for j in range(len(costs) + 1)
    ]

    delta = [zrow[j] - costs[j] for j in range(len(costs))]

    values = ["", "Delta", fmt(zrow[-1])] + [fmt(v) for v in delta] + [""]

    print("-" * 88)
    print("".join(str(v).ljust(w) for v, w in zip(values, widths)))
    print("-" * 88)

    return delta


def solve_task_8():
    costs = [-3.0, 1.0, 0.0, 0.0, 0.0]
    names = ["x1", "x2", "s1", "s2", "s3"]

    T = [
        [2.0,  1.0, 1.0, 0.0, 0.0, 8.0],
        [1.0, -1.0, 0.0, 1.0, 0.0, 2.0],
        [-1.0, 1.0, 0.0, 0.0, 1.0, 3.0],
    ]

    basis = [2, 3, 4]
    cb = [0.0, 0.0, 0.0]

    print("=" * 88)
    print("SOLUTION OF TASK 8 USING THE SIMPLEX METHOD")
    print("=" * 88)

    print("max F = -3*x1 + x2")
    print("2*x1 + x2 <= 8")
    print("x1 - x2 <= 2")
    print("-x1 + x2 <= 3")
    print("x1, x2 >= 0")

    print("\nEvaluation: Delta = Zj - Cj.")
    print("For maximization, we select the most negative evaluation.")

    iteration = 0

    while True:
        delta = print_table(iteration, basis, T, cb, costs)

        candidates = [
            j for j, d in enumerate(delta) if d < -EPS
        ]

        if not candidates:
            print("\nThere are no negative evaluations. The optimal solution has been found.")
            break

        entering = min(candidates, key=lambda j: delta[j])

        print(f"\nSTEP {iteration + 1}: {names[entering]} enters the basis.")

        ratios = []

        for row in T:
            a = row[entering]
            ratios.append(row[-1] / a if a > EPS else None)

        print("Calculating theta = b / a:")

        for i, value in enumerate(ratios):
            print(f"  Row {i + 1}: {fmt(value)}")

        eligible = [
            (v, i) for i, v in enumerate(ratios)
            if v is not None and v >= -EPS
        ]

        if not eligible:
            print("The objective function is unbounded.")
            return

        minimum = min(v for v, _ in eligible)

        leaving = next(
            i for v, i in eligible
            if abs(v - minimum) <= EPS
        )

        pivot = T[leaving][entering]

        print(f"Minimum theta = {fmt(minimum)}.")
        print(
            f"{names[basis[leaving]]} leaves the basis. "
            f"Pivot row: {leaving + 1}."
        )
        print(f"Pivot element = {fmt(pivot)}.")

        # Jordan-Gauss transformation

        T[leaving] = [v / pivot for v in T[leaving]]

        for i in range(len(T)):
            if i == leaving:
                continue

            factor = T[i][entering]

            T[i] = [
                T[i][j] - factor * T[leaving][j]
                for j in range(len(T[i]))
            ]

        basis[leaving] = entering
        cb[leaving] = costs[entering]

        iteration += 1

        print("The table has been recalculated using the Jordan-Gauss method.")

    values = [0.0] * len(costs)

    for i, basic in enumerate(basis):
        values[basic] = T[i][-1]

    x1, x2 = values[0], values[1]

    result = -3 * x1 + x2

    print("\n" + "=" * 88)
    print("OPTIMAL SOLUTION")
    print("=" * 88)

    print(f"x1 = {fmt(x1)}")
    print(f"x2 = {fmt(x2)}")
    print(f"Fmax = -3*({fmt(x1)}) + {fmt(x2)} = {fmt(result)}")

    print("\nConstraint verification:")

    checks = [
        (2*x1 + x2, 8),
        (x1 - x2, 2),
        (-x1 + x2, 3)
    ]

    for i, (left, right) in enumerate(checks, 1):
        status = (
            "satisfied"
            if left <= right + 1e-7
            else "NOT satisfied"
        )

        print(f"  {i}) {fmt(left)} <= {fmt(right)} — {status}")

    print(f"\nNumber of transitions between tables: {iteration}")
    print("=" * 88)


if __name__ == "__main__":
    solve_task_8()
    input("\nPress Enter to exit...")
