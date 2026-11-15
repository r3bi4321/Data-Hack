import math

DEFENDER_RADIUS = 0.4
GOAL_WIDTH = 1.83

def calculate_shot_line_coverage(
    shooter_x,
    shooter_y,
    defender_positions,
    goal_x,
    goal_y=0,
    r=DEFENDER_RADIUS
):
    """
    Calculates the percentage of the visible goal angle
    covered by opposing defenders.

    Parameters
    ----------
    shooter_x, shooter_y : float
        Position of the shooter.
    defender_positions : list of tuples
        Positions of opposing skaters (x, y).
    goal_x : float
        Target goal position: 26 or -26.
    goal_y : float
        Center of the goal (default: 0).
    r : float
        Assumed defender radius (default: 0.4 m).

    Returns
    -------
    dict
        covered_angle: Total covered angle in radians.
        goal_angle: Visible goal angle in radians.
        coverage: Percentage of the goal angle covered.
        coverage_factor: 100 - coverage.
    """

    post1 = (goal_x, goal_y - GOAL_WIDTH / 2)
    post2 = (goal_x, goal_y + GOAL_WIDTH / 2)

    theta1 = math.atan2(
        post1[1] - shooter_y,
        post1[0] - shooter_x
    )

    theta2 = math.atan2(
        post2[1] - shooter_y,
        post2[0] - shooter_x
    )

    angle_difference = math.atan2(
        math.sin(theta2 - theta1),
        math.cos(theta2 - theta1)
    )

    alpha_goal = abs(angle_difference)

    goal_center_angle = math.atan2(
        math.sin(theta1) + math.sin(theta2),
        math.cos(theta1) + math.cos(theta2)
    )

    half_goal_angle = alpha_goal / 2

    covered_intervals = []

    for defender_x, defender_y in defender_positions:

        dx = defender_x - shooter_x
        dy = defender_y - shooter_y

        distance = math.sqrt(dx**2 + dy**2)

        if distance == 0:
            continue

        theta_i = math.atan2(dy, dx)

        alpha_i = 2 * math.asin(
            min(1.0, r / distance)
        )

        relative_angle = math.atan2(
            math.sin(theta_i - goal_center_angle),
            math.cos(theta_i - goal_center_angle)
        )

        theta_min = relative_angle - alpha_i / 2
        theta_max = relative_angle + alpha_i / 2

        intersection_min = max(
            theta_min,
            -half_goal_angle
        )

        intersection_max = min(
            theta_max,
            half_goal_angle
        )

        if intersection_min < intersection_max:
            covered_intervals.append(
                (intersection_min, intersection_max)
            )

    covered_intervals.sort()

    total_covered_angle = 0.0

    if covered_intervals:

        current_min, current_max = covered_intervals[0]

        for next_min, next_max in covered_intervals[1:]:

            if next_min <= current_max:

                current_max = max(
                    current_max,
                    next_max
                )

            else:

                total_covered_angle += (
                    current_max - current_min
                )

                current_min = next_min
                current_max = next_max

        total_covered_angle += (
            current_max - current_min
        )

    if alpha_goal > 0:

        coverage = (
            total_covered_angle / alpha_goal
        ) * 100

    else:
        coverage = 0.0

    coverage = max(0.0, min(100.0, coverage))

    coverage_factor = 100 - coverage

    return {
        "covered_angle": total_covered_angle,
        "goal_angle": alpha_goal,
        "coverage": coverage,
        "coverage_factor": coverage_factor
    }