import math

def calculate_shot_distance(shot_x, shot_y, goal_x=26, goal_y=0):
    delta_x = goal_x - shot_x
    delta_y = goal_y - shot_y

    distance = math.sqrt(delta_x**2 + delta_y**2)

    return distance