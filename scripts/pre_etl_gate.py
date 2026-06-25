import pandas as pd
import sys

print("=" * 80)
print("PRE ETL GATE")
print("=" * 80)

errors = []

# --------------------------------------------------
# ACCIDENTS
# --------------------------------------------------

acc = pd.read_csv(
    "data/raw/Unfallorte2024.csv",
    sep=";",
    low_memory=False
)

district_codes = (
    acc["ULAND"].astype(str).str.zfill(2)
    + acc["UREGBEZ"].astype(str)
    + acc["UKREIS"].astype(str).str.zfill(2)
)

municipality_codes = (
    district_codes
    + acc["UGEMEINDE"].astype(str).str.zfill(3)
)

if district_codes.str.len().nunique() != 1:
    errors.append("District code length inconsistent")

if district_codes.str.len().iloc[0] != 5:
    errors.append("District code length != 5")

if municipality_codes.str.len().nunique() != 1:
    errors.append("Municipality code length inconsistent")

if municipality_codes.str.len().iloc[0] != 8:
    errors.append("Municipality code length != 8")

core_cols = [
    "ULAND",
    "UKREIS",
    "UGEMEINDE",
    "UJAHR",
    "UMONAT",
    "UKATEGORIE",
    "XGCSWGS84",
    "YGCSWGS84"
]

for col in core_cols:
    nulls = acc[col].isna().sum()

    if nulls > 0:
        errors.append(f"{col} contains {nulls} nulls")

# --------------------------------------------------
# POPULATION
# --------------------------------------------------

pop = pd.read_csv(
    "data/raw/population_by_kreis.csv",
    encoding="latin1",
    sep=";",
    low_memory=False
)

pop = pop[
    pop["1_variable_label"]
    == "Kreise und kreisfreie Städte"
]

pop = pop[
    pop["2_variable_attribute_code"].isna()
]

dupes = pop.duplicated(
    subset=[
        "1_variable_attribute_code",
        "time"
    ]
).sum()

if dupes != 0:
    errors.append(
        f"Population duplicates found: {dupes}"
    )

# --------------------------------------------------
# REPORT
# --------------------------------------------------

if errors:

    print("\nFAILED\n")

    for e in errors:
        print("ERROR:", e)

    sys.exit(1)

print("\nPASSED")
print("ETL may proceed.")