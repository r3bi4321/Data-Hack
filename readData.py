from pathlib import Path
import pandas as pd

base = Path(__file__).parent
df = pd.read_csv("OneDrive_1_22.10.2026/U.S. Collegiate Selects_HC Davos_Game_Events_Periode 1_31_12_2025.csv")

# Wie gross ist der Datensatz?
print("Zeilen und Spalten:", df.shape)

# Welche Spalten sind vorhanden?
print(df.columns.tolist())

# Erste Einträge ansehen
print(df.head(30))

# Datentypen und fehlende Werte untersuchen
df.info()
print(df.isna().sum().sort_values(ascending=False).head(20))