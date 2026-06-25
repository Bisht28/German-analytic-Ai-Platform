import pandas as pd
from pathlib import Path

# --------------------------------------------------
# OUTPUT DIRECTORY
# --------------------------------------------------

Path("data/processed").mkdir(
    parents=True,
    exist_ok=True
)

# --------------------------------------------------
# LOAD MUNICIPALITIES
# --------------------------------------------------

df = pd.read_excel(
    "data/raw/municipalities.xlsx",
    sheet_name="Onlineprodukt_Gemeinden30092025",
    header=None
)

# municipality rows only

df = df[
    df[0].astype(str) == "60"
].copy()

# --------------------------------------------------
# BUILD CODES
# --------------------------------------------------

state_code = (
    df[2]
    .astype(str)
    .str.zfill(2)
)

district_code = (
    state_code
    + df[3].astype(str)
    + df[4].astype(str).str.zfill(2)
)

municipality_code = (
    district_code
    + df[6].astype(str).str.zfill(3)
)

# --------------------------------------------------
# OUTPUT
# --------------------------------------------------

regions = pd.DataFrame({

    "municipality_code": municipality_code,

    "district_code": district_code,

    "state_code": state_code,

    "name": df[7].astype(str),

    "area_km2": df[8],

    "population": df[9],

    "longitude": (
        df[14]
        .astype(str)
        .str.replace(",", ".", regex=False)
    ),

    "latitude": (
        df[15]
        .astype(str)
        .str.replace(",", ".", regex=False)
    ),

    "settlement_type": df[19]
})

# --------------------------------------------------
# SAVE
# --------------------------------------------------

regions = regions.drop_duplicates()

regions.to_csv(
    "data/processed/regions_final.csv",
    index=False
)

print(
    f"Saved {len(regions):,} rows"
)