import pandas as pd
from pathlib import Path

# =====================================================
# CONFIG
# =====================================================

INPUT_FILES = [
    "data/raw/Unfallorte2022.csv",
    "data/raw/Unfallorte2023.csv",
    "data/raw/Unfallorte2024.csv"
]

OUTPUT_FILE = "data/processed/accidents_final.csv"

# =====================================================
# OUTPUT DIRECTORY
# =====================================================

Path("data/processed").mkdir(
    parents=True,
    exist_ok=True
)

# =====================================================
# LOAD + TRANSFORM
# =====================================================

frames = []

for file in INPUT_FILES:

    print(f"Loading {file}")

    df = pd.read_csv(
        file,
        sep=";",
        low_memory=False
    )

    # -------------------------------------------------
    # Administrative Codes
    # -------------------------------------------------

    state_code = (
        df["ULAND"]
        .astype(str)
        .str.zfill(2)
    )

    district_code = (
        state_code
        + df["UREGBEZ"]
            .astype(str)
            .str.strip()
        + df["UKREIS"]
            .astype(str)
            .str.zfill(2)
    )

    municipality_code = (
        district_code
        + df["UGEMEINDE"]
            .astype(str)
            .str.zfill(3)
    )

    # -------------------------------------------------
    # Coordinates
    # Use WGS84 only
    # -------------------------------------------------

    longitude = (
        df["XGCSWGS84"]
        .astype(str)
        .str.replace(",", ".", regex=False)
    )

    latitude = (
        df["YGCSWGS84"]
        .astype(str)
        .str.replace(",", ".", regex=False)
    )

    # -------------------------------------------------
    # Output
    # -------------------------------------------------

    out = pd.DataFrame({

        "source_year": df["UJAHR"],

        "year": df["UJAHR"],

        "month": df["UMONAT"],

        "weekday": df["UWOCHENTAG"],

        "hour": df["USTUNDE"],

        "state_code": state_code,

        "district_code": district_code,

        "municipality_code": municipality_code,

        "category": df["UKATEGORIE"],

        "accident_type": df["UART"],

        "accident_subtype": df["UTYP1"],

        "light_condition": df["ULICHTVERH"],

        "road_condition": df["IstStrassenzustand"],

        "is_bicycle": df["IstRad"],

        "is_car": df["IstPKW"],

        "is_pedestrian": df["IstFuss"],

        "is_motorcycle": df["IstKrad"],

        "is_commercial_vehicle": df["IstGkfz"],

        "is_other_vehicle": df["IstSonstige"],

        "longitude": longitude,

        "latitude": latitude
    })

    frames.append(out)

# =====================================================
# COMBINE
# =====================================================

print("Combining datasets...")

accidents = pd.concat(
    frames,
    ignore_index=True
)

# =====================================================
# SAVE
# =====================================================

accidents.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    f"Saved: {OUTPUT_FILE}"
)

print(
    f"Total accidents: {len(accidents):,}"
)