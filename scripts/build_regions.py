from pathlib import Path
import pandas as pd

# Create output directory
Path("data/processed").mkdir(
    parents=True,
    exist_ok=True
)

print("Loading municipalities...")

mun = pd.read_excel(
    "data/raw/municipalities.xlsx",
    sheet_name="Onlineprodukt_Gemeinden30092025",
    header=None
)

mun = mun[mun[0].astype(str) == "60"]

regions = pd.DataFrame()

regions["state_code"] = (
    mun[2]
    .astype(str)
    .str.zfill(2)
)

regions["district_code"] = (
    mun[2].astype(str).str.zfill(2)
    + mun[3].astype(str)
    + mun[4].astype(str).str.zfill(2)
)

regions["municipality_code"] = (
    mun[2].astype(str).str.zfill(2)
    + mun[3].astype(str)
    + mun[4].astype(str).str.zfill(2)
    + mun[6].astype(str).str.zfill(3)
)

regions["name"] = mun[7].astype(str)

regions = regions.drop_duplicates()

regions.to_csv(
    "data/processed/regions.csv",
    index=False
)

print(f"Regions exported: {len(regions):,}")
print("Saved: data/processed/regions.csv")