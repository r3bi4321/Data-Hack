import streamlit as st
import ast
import pandas as pd
from pathlib import Path

from readData import df
from movePlayer import draw_movable_rink

from Calculations.attackScore import (
    calculate_attack_score_for_shot,
    get_shooter_slot,
    get_target_goal_x,
    is_behind_goal
)

from Calculations.distance import calculate_shot_distance


st.set_page_config(
    page_title="Chance Check",
    page_icon="assets/puck.png",
    layout="wide"
)


css_file = Path(__file__).resolve().parent / "style.css"

with open(css_file) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def html(text):
    """
    Entfernt Einrueckung und Leerzeilen aus HTML-Text.
    Streamlit liest st.markdown als Markdown, und Zeilen mit 4 oder mehr
    Leerzeichen (oder Leerzeilen im HTML) werden sonst als Code-Block
    angezeigt statt als HTML.
    """
    return "".join(line.strip() + " " for line in text.splitlines() if line.strip())


with st.sidebar:

    st.markdown(
        html("""
        <div class="sidebar-content">
            <h2 class="sidebar-subtitle">SPENGLER CUP</h2>

            <div class="sidebar-footer">
                DATA HACK 2026<br>
                Built with Python & Streamlit
            </div>

        </div>
        """),
        unsafe_allow_html=True
    )

def parse_coordinate(coordinate):

    if pd.isna(coordinate):
        return None

    try:
        position = ast.literal_eval(coordinate)
        return float(position[0]), float(position[1])

    except (ValueError, TypeError, SyntaxError, IndexError):
        return None

st.markdown(
    html("""
    <div class="main-page">
        <div class="title">
            <svg class="hockey-puck" viewBox="0 0 100 100" width="48">
                <ellipse cx="50" cy="50" rx="42" ry="17"
                    fill="#182b45"/>
                <ellipse cx="50" cy="40" rx="42" ry="17"
                    fill="#304966"/>
                <ellipse cx="50" cy="40" rx="42" ry="17"
                    fill="#182b45"/>
            </svg>
            <span>Chance Check</span>
        </div>
    </div>
    """),
    unsafe_allow_html=True
)

shots = df[df["EventType"] == "Shot"].copy()

if shots.empty:
    st.warning("No shots found in the dataset.")
    st.stop()


def format_attack_option(i):

    shot = shots.loc[i]

    period = shot["Period"]

    match_clock = int(shot["MatchClock"])

    minutes = match_clock // 60
    seconds = match_clock % 60

    timestamp = f"{minutes:02d}:{seconds:02d}"

    shooter = shot["EventPrimaryPlayerName"]

    if pd.isna(shooter):
        shooter = "Unknown"

    return f"Period {period} | {timestamp} | {shooter}"


selected_index = st.selectbox(
    "Select an attack:",
    shots.index,
    format_func=format_attack_option
)

selected_shot = shots.loc[selected_index]

shot_position = parse_coordinate(
    selected_shot["EventStartCoordinate"]
)

if shot_position is None:
    st.warning("Shot coordinates are not available.")
    st.stop()

shot_x, shot_y = shot_position

players = []

for i in range(1, 13):

    player_id = selected_shot.get(f"StartPlayerId{i}")
    jersey_number = selected_shot.get(f"StartPlayerJersey{i}")
    player_team = selected_shot.get(f"StartPlayerTeam{i}")

    coordinate = selected_shot.get(f"StartPlayerCoordinates{i}")

    position = parse_coordinate(coordinate)

    if position is None:
        continue

    x, y = position

    players.append({
        "id": player_id,
        "jersey": jersey_number,
        "team": player_team,
        "x": x,
        "y": y,
        "slot": i
    })

left, right = st.columns([1.8, 1])

with left:

    with st.container(border=True):

        st.subheader("Game Situation")

        shooter_slot = get_shooter_slot(selected_shot)

        shooter_index = next(
            (
                index
                for index, player in enumerate(players)
                if player["slot"] == shooter_slot
            ),
            None
        )

        goal_x = get_target_goal_x(shot_x, shot_y)

        players = draw_movable_rink(
            players,
            shot_x,
            shot_y,
            key=f"rink_{selected_index}",
            shooter_index=shooter_index,
            goal_x=goal_x
        )

moved_shot = selected_shot.copy()

for player in players:

    slot = player["slot"]

    moved_shot[f"StartPlayerCoordinates{slot}"] = str([
        player["x"],
        player["y"]
    ])


try:

    attack_score = calculate_attack_score_for_shot(
        moved_shot,
        df,
        shooter_slot=shooter_slot,
        goal_x=goal_x
    )

except Exception as e:

    attack_score = None
    st.error(f"Could not calculate AttackScore: {e}")

shooter = next(
    (
        player
        for player in players
        if player["slot"] == shooter_slot
    ),
    None
)

if shooter is not None:

    shot_distance = calculate_shot_distance(
        shooter["x"],
        shooter["y"],
        goal_x=goal_x,
        goal_y=0
    )

else:

    shot_distance = None

shot_speed = selected_shot["ShotSpeed"]

with right:

    with st.container(border=True):

        st.subheader("Attack Analysis")

        if attack_score is not None:

            st.metric(
                "AttackScore",
                f"{attack_score:.2f} / 100"
            )

        else:

            st.metric(
                "AttackScore",
                "N/A"
            )

        if shooter is not None and is_behind_goal(shooter["x"], goal_x):

            st.caption(
                "Shooter is behind the goal: no direct shot on goal possible."
            )

        st.divider()

        col1, col2 = st.columns(2)

        with col1:

            if shot_distance is not None:

                st.metric(
                    "Shot Distance",
                    f"{shot_distance:.2f} m"
                )

            else:

                st.metric(
                    "Shot Distance",
                    "N/A"
                )

        with col2:

            if pd.notna(shot_speed):

                st.metric(
                    "Shot Speed",
                    f"{shot_speed:.1f} km/h"
                )

            else:

                st.metric(
                    "Shot Speed",
                    "N/A"
                )