from pathlib import Path
import pandas as pd

# Create output directory if missing
Path("data/processed").mkdir(
    parents=True,
    exist_ok=True
)

files = [
    "data/raw/Unfallorte2022.csv",
    "data/raw/Unfallorte2023.csv",
    "data/raw/Unfallorte2024.csv"
]

frames = []

for file in files:
    print(f"Loading {file}")

    df = pd.read_csv(
        file,
        sep=";",
        low_memory=False
    )

    # State code
    df["state_code"] = (
        df["ULAND"]
        .astype(str)
        .str.zfill(2)
    )

    # District code
    df["district_code"] = (
        df["ULAND"].astype(str).str.zfill(2)
        + df["UREGBEZ"].astype(str)
        + df["UKREIS"].astype(str).str.zfill(2)
    )

    # Municipality code
    df["municipality_code"] = (
        df["ULAND"].astype(str).str.zfill(2)
        + df["UREGBEZ"].astype(str)
        + df["UKREIS"].astype(str).str.zfill(2)
        + df["UGEMEINDE"].astype(str).str.zfill(3)
    )

    frames.append(df)

print("Combining datasets...")

accidents = pd.concat(
    frames,
    ignore_index=True
)

print(f"Total accidents: {len(accidents):,}")

output_file = "data/processed/accidents.csv"

accidents.to_csv(
    output_file,
    index=False
)

print(f"Saved: {output_file}")
