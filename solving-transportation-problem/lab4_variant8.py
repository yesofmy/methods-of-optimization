
"""
Laboratory Work No. 4
Course: Optimization Methods
Topic: Transportation Problem
Variant: 8

Implemented methods:
1. North-West Corner Method.
2. Least Cost Method.
3. Average Coefficients Method.

Run: python lab4_variant8.py
No external libraries are required.
"""

SUPPLY = [1000, 1500, 2000, 500]
DEMAND = [2000, 1000, 2000, 1000]

COSTS = [
    [2, 1, 3, 1],
    [4, 2, 4, 5],
    [5, 6, 9, 3],
    [3, 5, 8, 6],
]

SUPPLIER_NAMES = ["A1", "A2", "A3", "A4"]
CONSUMER_NAMES = ["B1", "B2", "B3", "B4"]


def print_vector(title, values, names):
    """Print supply or demand values."""
    print(title)
    for name, value in zip(names, values):
        print(f"  {name}: {value}")


def print_matrix(title, matrix, row_names, col_names, cell_width=10):
    """Print a formatted matrix."""
    print(f"\n{title}")
    header = " " * 8 + "".join(
        f"{name:>{cell_width}}" for name in col_names
    )
    print(header)
    print(" " * 8 + "-" * (cell_width * len(col_names)))

    for name, row in zip(row_names, matrix):
        print(
            f"{name:<8}" +
            "".join(f"{value:>{cell_width}.2f}" for value in row)
        )


def balance_transport_problem(supply, demand, costs):
    """
    Check the balance of the transportation problem.
    If demand exceeds supply, add a dummy supplier.
    If supply exceeds demand, add a dummy consumer.
    Dummy transportation costs are zero.
    """

    supply = supply.copy()
    demand = demand.copy()
    costs = [row.copy() for row in costs]

    total_supply = sum(supply)
    total_demand = sum(demand)

    supplier_names = SUPPLIER_NAMES.copy()
    consumer_names = CONSUMER_NAMES.copy()

    print("\nBALANCE CHECK")
    print(f"Total supply: {total_supply}")
    print(f"Total demand: {total_demand}")

    if total_supply < total_demand:
        difference = total_demand - total_supply

        print(
            f"Demand exceeds supply by {difference}. "
            "Adding dummy supplier A5."
        )

        supply.append(difference)
        costs.append([0] * len(demand))
        supplier_names.append("A5*")

    elif total_supply > total_demand:
        difference = total_supply - total_demand

        print(
            f"Supply exceeds demand by {difference}. "
            "Adding dummy consumer B5."
        )

        demand.append(difference)

        for row in costs:
            row.append(0)

        consumer_names.append("B5*")

    else:
        print("The problem is balanced. No dummy points are needed.")

    return supply, demand, costs, supplier_names, consumer_names


def calculate_total_cost(plan, costs):
    """Calculate the total transportation cost."""
    return sum(
        plan[i][j] * costs[i][j]
        for i in range(len(plan))
        for j in range(len(plan[0]))
    )


def print_plan_result(
    method_name, plan, costs, supplier_names, consumer_names
):
    """Print the transportation plan and its total cost."""

    print_matrix(
        f"TRANSPORTATION PLAN — {method_name}",
        plan,
        supplier_names,
        consumer_names,
        cell_width=12,
    )

    total_cost = calculate_total_cost(plan, costs)

    print(f"\nTotal transportation cost: {total_cost:.2f}")
    print("Non-zero transportation allocations:")

    for i, row in enumerate(plan):
        for j, amount in enumerate(row):
            if amount > 0:
                print(
                    f"  {supplier_names[i]} -> {consumer_names[j]}: "
                    f"{amount:g} units at cost {costs[i][j]:g}"
                )

    return total_cost


# ------------------------------------------------------------
# 1. NORTH-WEST CORNER METHOD
# ------------------------------------------------------------

def north_west_corner(supply, demand):

    print("\n" + "=" * 68)
    print("1. NORTH-WEST CORNER METHOD")
    print("=" * 68)

    remaining_supply = supply.copy()
    remaining_demand = demand.copy()

    rows = len(supply)
    cols = len(demand)

    plan = [[0] * cols for _ in range(rows)]

    i = 0
    j = 0
    step = 1

    while i < rows and j < cols:

        quantity = min(
            remaining_supply[i],
            remaining_demand[j]
        )

        plan[i][j] += quantity

        remaining_supply[i] -= quantity
        remaining_demand[j] -= quantity

        print(
            f"Step {step}: cell ({i + 1}, {j + 1}), "
            f"allocation = min({remaining_supply[i] + quantity}, "
            f"{remaining_demand[j] + quantity}) = {quantity}"
        )

        print(
            f"       Remaining supply A{i + 1}: "
            f"{remaining_supply[i]}, "
            f"remaining demand B{j + 1}: "
            f"{remaining_demand[j]}"
        )

        step += 1

        supply_exhausted = remaining_supply[i] == 0
        demand_satisfied = remaining_demand[j] == 0

        if supply_exhausted:
            i += 1

        if demand_satisfied:
            j += 1

    return plan


# ------------------------------------------------------------
# 2. LEAST COST METHOD
# ------------------------------------------------------------

def least_cost_method(supply, demand, costs, real_supplier_count):

    print("\n" + "=" * 68)
    print("2. LEAST COST METHOD")
    print("=" * 68)

    remaining_supply = supply.copy()
    remaining_demand = demand.copy()

    rows = len(supply)
    cols = len(demand)

    plan = [[0] * cols for _ in range(rows)]

    step = 1

    while (
        any(value > 0 for value in remaining_supply)
        and any(value > 0 for value in remaining_demand)
    ):

        # Find the cheapest available cell.
        # In case of equal costs, select the first cell
        # according to row and column order.

        candidates = [
            (costs[i][j], i, j)
            for i in range(real_supplier_count)
            for j in range(cols)
            if remaining_supply[i] > 0
            and remaining_demand[j] > 0
        ]

        if not candidates:
            break

        tariff, i, j = min(candidates)

        quantity = min(
            remaining_supply[i],
            remaining_demand[j]
        )

        plan[i][j] += quantity

        remaining_supply[i] -= quantity
        remaining_demand[j] -= quantity

        print(
            f"Step {step}: selected cell ({i + 1}, {j + 1}), "
            f"minimum available cost = {tariff}"
        )

        print(
            f"       Allocation = min({remaining_supply[i] + quantity}, "
            f"{remaining_demand[j] + quantity}) = {quantity}"
        )

        print(
            f"       Remaining supply A{i + 1}: "
            f"{remaining_supply[i]}, "
            f"remaining demand B{j + 1}: "
            f"{remaining_demand[j]}"
        )

        step += 1

    # The dummy supplier is used only after real suppliers.
    for i in range(real_supplier_count, rows):
        for j in range(cols):

            if remaining_demand[j] > 0:

                quantity = min(
                    remaining_supply[i],
                    remaining_demand[j]
                )

                if quantity > 0:

                    plan[i][j] += quantity

                    remaining_supply[i] -= quantity
                    remaining_demand[j] -= quantity

                    print(
                        f"Dummy supplier {i + 1}: "
                        f"allocation to B{j + 1} = {quantity}"
                    )

    return plan


# ------------------------------------------------------------
# 3. AVERAGE COEFFICIENTS METHOD
# ------------------------------------------------------------

def average_coefficients_method(
    original_costs,
    balanced_supply,
    balanced_demand,
    balanced_costs,
    supplier_names,
    consumer_names,
    real_supplier_count,
    real_consumer_count,
):

    print("\n" + "=" * 68)
    print("3. AVERAGE COEFFICIENTS METHOD")
    print("=" * 68)

    # Calculate average costs for the balanced matrix.
    # This includes a dummy point if one is required.
    # c_i = (c_i1 + c_i2 + ... + c_in) / n

    row_averages = [
        sum(row) / len(balanced_demand)
        for row in balanced_costs
    ]

    # c_j = (c_1j + c_2j + ... + c_mj) / m

    column_averages = [
        sum(
            balanced_costs[i][j]
            for i in range(len(balanced_supply))
        ) / len(balanced_supply)
        for j in range(len(balanced_demand))
    ]

    print("\nAverage row coefficients:")

    for i, value in enumerate(row_averages):
        print(f"  c{i + 1} = {value:.2f}")

    print("\nAverage column coefficients:")

    for j, value in enumerate(column_averages):
        print(f"  c{j + 1} = {value:.2f}")

    # k_ij = c_ij - (c_i + c_j)

    coefficient_matrix = [
        [
            balanced_costs[i][j]
            - (row_averages[i] + column_averages[j])
            for j in range(len(balanced_demand))
        ]
        for i in range(len(balanced_supply))
    ]

    print_matrix(
        "AVERAGE COEFFICIENT MATRIX k_ij",
        coefficient_matrix,
        supplier_names,
        consumer_names,
    )

    remaining_supply = balanced_supply.copy()
    remaining_demand = balanced_demand.copy()

    rows = len(balanced_supply)
    cols = len(balanced_demand)

    plan = [[0] * cols for _ in range(rows)]

    step = 1

    # First, distribute the supply of real suppliers.
    # The dummy supplier, if present, is used last.

    while (
        any(
            remaining_supply[i] > 0
            for i in range(real_supplier_count)
        )
        and any(value > 0 for value in remaining_demand)
    ):

        candidates = [
            (coefficient_matrix[i][j], i, j)
            for i in range(real_supplier_count)
            for j in range(real_consumer_count)
            if remaining_supply[i] > 0
            and remaining_demand[j] > 0
        ]

        if not candidates:
            break

        coefficient, i, j = min(candidates)

        quantity = min(
            remaining_supply[i],
            remaining_demand[j]
        )

        plan[i][j] += quantity

        remaining_supply[i] -= quantity
        remaining_demand[j] -= quantity

        print(
            f"Step {step}: minimum available k_ij = "
            f"{coefficient:.2f}; "
            f"cell ({supplier_names[i]}, {consumer_names[j]})"
        )

        print(f"       Transportation quantity: {quantity}")

        print(
            f"       Remaining supply {supplier_names[i]}: "
            f"{remaining_supply[i]}"
        )

        print(
            f"       Remaining demand {consumer_names[j]}: "
            f"{remaining_demand[j]}"
        )

        step += 1

    # The dummy supplier fills the remaining demand.

    if len(balanced_supply) > real_supplier_count:

        dummy_i = real_supplier_count

        print(
            f"\nUsing dummy supplier "
            f"{supplier_names[dummy_i]} as the last option:"
        )

        for j in range(cols):

            if remaining_demand[j] > 0:

                quantity = min(
                    remaining_supply[dummy_i],
                    remaining_demand[j],
                )

                if quantity > 0:

                    plan[dummy_i][j] += quantity

                    remaining_supply[dummy_i] -= quantity
                    remaining_demand[j] -= quantity

                    print(
                        f"  {supplier_names[dummy_i]} -> "
                        f"{consumer_names[j]}: {quantity}"
                    )

    # Also handle the case of a dummy consumer.

    if len(balanced_demand) > real_consumer_count:

        dummy_j = real_consumer_count

        print(
            f"\nSending excess supply to dummy consumer "
            f"{consumer_names[dummy_j]}:"
        )

        for i in range(rows):

            if remaining_supply[i] > 0:

                quantity = min(
                    remaining_supply[i],
                    remaining_demand[dummy_j],
                )

                if quantity > 0:

                    plan[i][dummy_j] += quantity

                    remaining_supply[i] -= quantity
                    remaining_demand[dummy_j] -= quantity

                    print(
                        f"  {supplier_names[i]} -> "
                        f"{consumer_names[dummy_j]}: {quantity}"
                    )

    return plan


# ------------------------------------------------------------
# MAIN FUNCTION
# ------------------------------------------------------------

def main():

    print("=" * 68)
    print("LABORATORY WORK NO. 4 — TRANSPORTATION PROBLEM")
    print("Course: Optimization Methods | Variant 8")
    print("=" * 68)

    print_vector(
        "Initial supplier capacities:",
        SUPPLY,
        SUPPLIER_NAMES
    )

    print_vector(
        "Consumer demands:",
        DEMAND,
        CONSUMER_NAMES
    )

    print_matrix(
        "Transportation cost matrix C:",
        COSTS,
        SUPPLIER_NAMES,
        CONSUMER_NAMES
    )

    # Store the dimensions of the original problem.

    real_supplier_count = len(SUPPLY)
    real_consumer_count = len(DEMAND)

    # Balance the transportation problem.

    (
        supply,
        demand,
        costs,
        supplier_names,
        consumer_names
    ) = balance_transport_problem(SUPPLY, DEMAND, COSTS)

    print_vector(
        "Balanced supply:",
        supply,
        supplier_names
    )

    print_vector(
        "Balanced demand:",
        demand,
        consumer_names
    )

    print_matrix(
        "Balanced transportation cost matrix:",
        costs,
        supplier_names,
        consumer_names
    )

    # Method 1: North-West Corner Method.

    plan_nw = north_west_corner(supply, demand)

    total_nw = print_plan_result(
        "North-West Corner Method",
        plan_nw,
        costs,
        supplier_names,
        consumer_names
    )

    # Method 2: Least Cost Method.

    plan_lc = least_cost_method(
        supply,
        demand,
        costs,
        real_supplier_count
    )

    total_lc = print_plan_result(
        "Least Cost Method",
        plan_lc,
        costs,
        supplier_names,
        consumer_names
    )

    # Method 3: Average Coefficients Method.

    plan_avg = average_coefficients_method(
        COSTS,
        supply,
        demand,
        costs,
        supplier_names,
        consumer_names,
        real_supplier_count,
        real_consumer_count,
    )

    total_avg = print_plan_result(
        "Average Coefficients Method",
        plan_avg,
        costs,
        supplier_names,
        consumer_names
    )

    # Compare the results.

    print("\n" + "=" * 68)
    print("RESULT COMPARISON")
    print("=" * 68)

    results = [
        ("North-West Corner", total_nw),
        ("Least Cost", total_lc),
        ("Average Coefficients", total_avg),
    ]

    for name, value in results:
        print(f"{name:<30} {value:>12.2f}")

    best_name, best_value = min(
        results,
        key=lambda item: item[1]
    )

    print("-" * 68)
    print(f"Lowest obtained transportation cost: {best_value:.2f}")
    print(f"Obtained using: {best_name}")

    print(
        "\nConclusion: All three methods constructed feasible "
        "initial transportation plans. The plans were compared "
        "based on their total transportation costs."
    )

    print(
        "Note: These methods construct initial plans. "
        "Checking and improving the plan to obtain an optimal solution "
        "using the potential method is covered in Laboratory Work No. 5."
    )


if __name__ == "__main__":
    main()
