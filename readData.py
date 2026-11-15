
from pathlib import Path
import os
import pandas as pd
from dotenv import load_dotenv

base = Path(__file__).resolve().parent
load_dotenv(base / ".env")

data_paths = [
    os.getenv("DATA_PATH_1"),
    os.getenv("DATA_PATH_2"),
    os.getenv("DATA_PATH_3")
]

if any(path is None or path.strip() == "" for path in data_paths):
    raise ValueError(
        "One or more data paths are missing in the .env file."
    )


dataframes = []

for i, path in enumerate(data_paths, start=1):

    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Data file for period {i} not found: {file_path}"
        )

    period_df = pd.read_csv(file_path)

    dataframes.append(period_df)

    print(f"Period {i} loaded: {len(period_df)} rows")

df = pd.concat(dataframes, ignore_index=True)

for i in range(1, 13):

    name_column = f"StartPlayerName{i}"
    jersey_column = f"StartPlayerJersey{i}"

    if name_column in df.columns:

        df[jersey_column] = (
            df[name_column]
            .str.extract(r"#(\d+)", expand=False)
        )

print("\n========== DATENÜBERSICHT ==========")
print("Zeilen:", len(df))
print("Spalten:", len(df.columns))

