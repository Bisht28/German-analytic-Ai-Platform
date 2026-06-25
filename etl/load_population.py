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
# LOAD SOURCE
# --------------------------------------------------

df = pd.read_csv(
    "data/raw/population_by_kreis.csv",
    encoding="latin1",
    sep=";",
    low_memory=False
)

print("Raw rows:", len(df))

# --------------------------------------------------
# DISTRICTS + DISTRICT CITIES ONLY
# --------------------------------------------------

df = df[
    df["1_variable_label"]
    == "Kreise und kreisfreie Städte"
].copy()

print("After district filter:", len(df))

# --------------------------------------------------
# TOTAL POPULATION ONLY
# --------------------------------------------------

df = df[
    df["2_variable_attribute_code"].isna()
].copy()

print("After total population filter:", len(df))

# --------------------------------------------------
# CLEAN POPULATION VALUES
# --------------------------------------------------

df["value"] = pd.to_numeric(
    df["value"],
    errors="coerce"
)

before = len(df)

df = df[
    df["value"].notna()
].copy()

removed = before - len(df)

print(
    "Removed invalid population rows:",
    removed
)

# --------------------------------------------------
# BUILD OUTPUT
# --------------------------------------------------

population = pd.DataFrame({
    "region_code":
        df["1_variable_attribute_code"]
        .astype(str),

    "region_name":
        df["1_variable_attribute_label"]
        .astype(str),

    "year":
        df["time"]
        .astype(str)
        .str[:4],

    "population":
        df["value"].astype("int64")
})

# --------------------------------------------------
# VALIDATION
# --------------------------------------------------

print()

print(
    "Duplicates:",
    population.duplicated(
        ["region_code", "year"]
    ).sum()
)

print(
    "Rows:",
    len(population)
)

# --------------------------------------------------
# SAVE
# --------------------------------------------------

population.to_csv(
    "data/processed/population_final.csv",
    index=False
)

print()
print(
    "Saved:",
    len(population)
)