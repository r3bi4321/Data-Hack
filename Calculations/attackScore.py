from Calculations.angle import calculate_shot_angle
from Calculations.distance import calculate_shot_distance
from Calculations.shotSpeed import calculate_shot_speed
from Calculations.entryToShot import calculate_entry_to_shot_time

from Calculations.pressure import (
    calculate_pressure,
    calculate_attack_pressure
)

from Calculations.shotLineCoverage import (
    calculate_shot_line_coverage
)

import pandas as pd
import ast


WEIGHTS = {
    "D": 2.0,
    "A": 2.0,
    "V": 1.0,
    "T": 1.0,
    "P": 3.0,
    "C_L": 3.0
}

def normalize_id(value):
    if pd.isna(value):
        return None

    try:
        number = float(value)
        if number.is_integer():
            return str(int(number))
    except (ValueError, TypeError):
        pass

    return str(value).strip()


def parse_coordinate(coordinate):
    if pd.isna(coordinate):
        return None

    try:
        position = ast.literal_eval(coordinate)
        return float(position[0]), float(position[1])
    except (ValueError, TypeError, SyntaxError, IndexError):
        return None


BEHIND_GOAL_SCORE = 5.0     # Goal only posible by a deflected shot 


def is_behind_goal(shooter_x, goal_x):
    """
    True, wenn der Schuetze auf oder hinter der Torlinie steht.
    goal_x ist 26 (rechtes Tor) oder -26 (linkes Tor). Von dort kann man
    nicht aufs Tor schiessen, weil das Tor selbst im Weg steht.
    """

    direction = 1 if goal_x >= 0 else -1

    return shooter_x * direction >= abs(goal_x)


def get_target_goal_x(shooter_x, shooter_y):
    right_goal = (26, 0)
    left_goal = (-26, 0)

    distance_right = (
        (right_goal[0] - shooter_x) ** 2
        + (right_goal[1] - shooter_y) ** 2
    )

    distance_left = (
        (left_goal[0] - shooter_x) ** 2
        + (left_goal[1] - shooter_y) ** 2
    )

    return 26 if distance_right <= distance_left else -26


def get_opponent_positions(shot):
    shooter_team = shot["EventPrimaryTeam"]

    goalie_ids = {
        normalize_id(shot["HomeGoalieOnIce"]),
        normalize_id(shot["AwayGoalieOnIce"])
    }

    goalie_ids.discard(None)

    opponent_positions = []

    for i in range(1, 13):

        player_id = normalize_id(shot[f"StartPlayerId{i}"])
        player_team = shot[f"StartPlayerTeam{i}"]
        coordinate = shot[f"StartPlayerCoordinates{i}"]

        if pd.isna(player_team) or pd.isna(coordinate):
            continue

        if player_id in goalie_ids:
            continue

        if str(player_team) == str(shooter_team):
            continue

        position = parse_coordinate(coordinate)

        if position is not None:
            opponent_positions.append(position)

    return opponent_positions


def get_shooter_slot(shot):
    """
    Findet den Schuetzen: der Spieler des schiessenden Teams, der zum
    Zeitpunkt des Schusses am naechsten an EventStartCoordinate steht.
    Gibt die Spaltennummer (1-12) zurueck oder None.
    """

    event_position = parse_coordinate(shot["EventStartCoordinate"])

    if event_position is None:
        return None

    event_x, event_y = event_position
    shooter_team = shot["EventPrimaryTeam"]

    best_slot = None
    best_distance = None

    for i in range(1, 13):

        player_team = shot[f"StartPlayerTeam{i}"]
        position = parse_coordinate(shot[f"StartPlayerCoordinates{i}"])

        if pd.isna(player_team) or position is None:
            continue

        if str(player_team) != str(shooter_team):
            continue

        distance = (
            (position[0] - event_x) ** 2
            + (position[1] - event_y) ** 2
        )

        if best_distance is None or distance < best_distance:
            best_distance = distance
            best_slot = i

    return best_slot


def get_shot_position(shot, shooter_slot=None):
    """
    Position des Schuetzen = Koordinaten des Spielers
    (StartPlayerCoordinates), nicht die des Events.
    Nur wenn kein Schuetze gefunden wird, gilt EventStartCoordinate.
    """

    if shooter_slot is None:
        shooter_slot = get_shooter_slot(shot)

    if shooter_slot is not None:

        position = parse_coordinate(
            shot[f"StartPlayerCoordinates{shooter_slot}"]
        )

        if position is not None:
            return position

    return parse_coordinate(shot["EventStartCoordinate"])


def calculate_shot_pressure(shot):
    """Pressure fuer einen Schuss, mit der Spielerposition des Schuetzen."""

    position = get_shot_position(shot)
    opponents = get_opponent_positions(shot)

    if position is None or not opponents:
        return None

    return calculate_pressure(position[0], position[1], opponents)


def calculate_attack_score(D, A, V, T, P, C_L, weights=None):

    if weights is None:
        weights = WEIGHTS

    values = {
        "D": D,
        "A": A,
        "V": V,
        "T": T,
        "P": P,
        "C_L": C_L
    }

    if any(value is None or pd.isna(value) for value in values.values()):
        return None

    total_weight = sum(weights.values())

    if total_weight <= 0:
        raise ValueError("Total weight must be positive.")

    if any(weight < 0 for weight in weights.values()):
        raise ValueError("Weights cannot be negative.")

    weighted_sum = sum(
        weights[key] * values[key]
        for key in values
    )

    return round(weighted_sum / total_weight, 2)


def calculate_attack_score_for_shot(
    selected_shot, df, shooter_slot=None, goal_x=None
):
    """
    shooter_slot: Spaltennummer (1-12) des Schuetzen. Wenn None, wird er
    automatisch bestimmt (get_shooter_slot). Beim Verschieben von Spielern
    muss er aus der Original-Zeile bestimmt und hier uebergeben werden.

    goal_x: Tor, auf das das Team schiesst (26 oder -26). Beim Verschieben
    muss es aus der Originalposition bestimmt und hier uebergeben werden,
    sonst springt das Tor, sobald der Schuetze die Mittellinie ueberquert.
    """

    shot_position = get_shot_position(selected_shot, shooter_slot)

    if shot_position is None:
        return None

    shot_x, shot_y = shot_position

    if goal_x is None:
        goal_x = get_target_goal_x(shot_x, shot_y)

    if is_behind_goal(shot_x, goal_x):
        return BEHIND_GOAL_SCORE

    distance = calculate_shot_distance(
        shot_x, shot_y, goal_x=goal_x, goal_y=0
    )

    angle = calculate_shot_angle(
        shot_x, shot_y, goal_x=goal_x, goal_y=0
    )

    shot_speed = selected_shot["ShotSpeed"]

    if pd.isna(shot_speed):
        return None


    entry_to_shot = calculate_entry_to_shot_time(
        df,
        selected_shot.name
    )

    opponent_positions = get_opponent_positions(selected_shot)

    if not opponent_positions:
        return None

    pressure_values = df[df["EventType"] == "Shot"].apply(
        calculate_shot_pressure,
        axis=1
    ).dropna()

    pressure = calculate_pressure(
        shot_x,
        shot_y,
        opponent_positions
    )

    if pressure_values.empty:
        return None

    attack_pressure = calculate_attack_pressure(
        pressure,
        pressure_values.min(),
        pressure_values.max()
    )

    coverage_result = calculate_shot_line_coverage(
        shooter_x=shot_x,
        shooter_y=shot_y,
        defender_positions=opponent_positions,
        goal_x=goal_x,
        goal_y=0,
        r=0.4
    )

    coverage_factor = coverage_result["coverage_factor"]

    D = max(0, min(100, 100 * (1 - distance / 30)))
    A = max(0, min(100, 100 * (1 - angle / 90)))
    V = max(0, min(100, shot_speed))
    T = (
        max(0, min(100, 100 * (1 - entry_to_shot / 60)))
        if entry_to_shot is not None
        else None
    )
    return calculate_attack_score(
        D=D,
        A=A,
        V=V,
        T=T,
        P=attack_pressure,
        C_L=coverage_factor
    )