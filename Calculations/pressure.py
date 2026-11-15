
def calculate_pressure(shooter_x, shooter_y, opponent_positions, epsilon=1e-6):
    """Calculate pressure from opposing skaters, excluding the goalie."""

    pressure = 0.0

    for opponent_x, opponent_y in opponent_positions:
        distance_squared = (
            (opponent_x - shooter_x) ** 2
            + (opponent_y - shooter_y) ** 2
        )

        pressure += 1 / (distance_squared + epsilon)

    return pressure


def normalize_pressure(pressure, p_min, p_max):
    """Normalize pressure to a value between 1 and 100."""

    if p_max == p_min:
        return 1.0

    normalized = 1 + 99 * (
        (pressure - p_min) / (p_max - p_min)
    )

    return max(1.0, min(100.0, normalized))


def calculate_attack_pressure(pressure, p_min, p_max):
    """Convert normalized pressure into an attack score."""

    p_norm = normalize_pressure(pressure, p_min, p_max)

    return 101 - p_norm
