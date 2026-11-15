import pandas as pd


def calculate_entry_to_shot_time(df, selected_shot_index):

    shot_position = df.index.get_loc(selected_shot_index)

    previous_events = df.iloc[:shot_position]

    crossings = previous_events[
        previous_events["EventType"]
        .astype(str)
        .str.replace(" ", "", regex=False)
        .str.lower() == "bluelinecrossing"
    ]

    if crossings.empty:
        return None

    last_crossing = crossings.iloc[-1]

    entry_timestamp = pd.to_datetime(
    last_crossing["Timestamp"],
    unit="ms",
    errors="coerce"
    )

    shot_timestamp = pd.to_datetime(
        df.loc[selected_shot_index, "Timestamp"],
        unit="ms",
        errors="coerce"
    )

    if pd.isna(entry_timestamp) or pd.isna(shot_timestamp):
        return None

    print("BluelineCrossing Timestamp:", last_crossing["Timestamp"])
    print("Shot Timestamp:", df.loc[selected_shot_index, "Timestamp"])

    print("Parsed Entry:", entry_timestamp)
    print("Parsed Shot:", shot_timestamp)

    time_difference = (
        shot_timestamp - entry_timestamp
    ).total_seconds()

    return time_difference