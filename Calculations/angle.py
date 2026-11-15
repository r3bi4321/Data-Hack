import sys
import math
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from readData import df
import ast

def calculate_shot_angle(shot_x, shot_y, goal_x=26, goal_y=0):

    delta_x = goal_x - shot_x
    delta_y = goal_y - shot_y

    angle = math.degrees(
        math.atan2(abs(delta_y), abs(delta_x))
    )

    return angle