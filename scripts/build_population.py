from pathlib import Path
import pandas as pd

Path("data/processed").mkdir(
    parents=True,
    exist_ok=True
)

print("Loading population file...")

df = pd.read_csv(
    "data/raw/population_by_kreis.csv",
    encoding="latin1",
    sep=";",
    low_memory=False
)

df = df[
    df["1_variable_label"]
    == "Kreise und kreisfreie Städte"
]

population = pd.DataFrame()

population["region_code"] = (
    df["1_variable_attribute_code"]
    .astype(str)
    .str.strip()
)

population["region_name"] = (
    df["1_variable_attribute_label"]
    .astype(str)
    .str.strip()
)

population["year"] = (
    pd.to_datetime(
        df["time"],
        errors="coerce"
    ).dt.year
)

population["population"] = pd.to_numeric(
    df["value"],
    errors="coerce"
)

population = population.dropna(
    subset=[
        "year",
        "population"
    ]
)

population = population.drop_duplicates()

population.to_csv(
    "data/processed/population.csv",
    index=False
)

print(f"Population rows: {len(population):,}")
print("Saved: data/processed/population.csv")