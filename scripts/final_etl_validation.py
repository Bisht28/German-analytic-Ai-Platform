import pandas as pd

print("=" * 80)
print("FINAL ETL VALIDATION")
print("=" * 80)

# --------------------------------------------------
# REGIONS
# --------------------------------------------------

regions = pd.read_csv(
    "data/processed/regions_final.csv",
    dtype=str
)

print("\nREGIONS")

print("Rows:", len(regions))

print(
    "Duplicate municipality codes:",
    regions["municipality_code"]
    .duplicated()
    .sum()
)

print(
    "Null municipality codes:",
    regions["municipality_code"]
    .isna()
    .sum()
)

print(
    "District lengths:"
)

print(
    regions["district_code"]
    .str.len()
    .value_counts()
    .to_dict()
)

print(
    "Municipality lengths:"
)

print(
    regions["municipality_code"]
    .str.len()
    .value_counts()
    .to_dict()
)

# --------------------------------------------------
# POPULATION
# --------------------------------------------------

population = pd.read_csv(
    "data/processed/population_final.csv",
    dtype=str
)

print("\nPOPULATION")

print("Rows:", len(population))

print(
    "Duplicates:",
    population.duplicated(
        ["region_code", "year"]
    ).sum()
)

print(
    "Null region codes:",
    population["region_code"]
    .isna()
    .sum()
)

print(
    "Code lengths:"
)

print(
    population["region_code"]
    .str.len()
    .value_counts()
    .to_dict()
)

# --------------------------------------------------
# RATES
# --------------------------------------------------

rates = pd.read_csv(
    "data/processed/rates_final.csv",
    dtype=str
)

print("\nRATES")

print("Rows:", len(rates))

print(
    "Duplicate districts:",
    rates["district_code"]
    .duplicated()
    .sum()
)

print(
    "Code lengths:"
)

print(
    rates["district_code"]
    .str.len()
    .value_counts()
    .to_dict()
)

# --------------------------------------------------
# ACCIDENTS
# --------------------------------------------------

accidents = pd.read_csv(
    "data/processed/accidents_final.csv",
    dtype=str
)

print("\nACCIDENTS")

print("Rows:", len(accidents))

print(
    "Null district codes:",
    accidents["district_code"]
    .isna()
    .sum()
)

print(
    "Null municipality codes:",
    accidents["municipality_code"]
    .isna()
    .sum()
)

print(
    "Null longitude:",
    accidents["longitude"]
    .isna()
    .sum()
)

print(
    "Null latitude:",
    accidents["latitude"]
    .isna()
    .sum()
)

print(
    "District lengths:"
)

print(
    accidents["district_code"]
    .str.len()
    .value_counts()
    .to_dict()
)

print(
    "Municipality lengths:"
)

print(
    accidents["municipality_code"]
    .str.len()
    .value_counts()
    .to_dict()
)

print("\n")
print("=" * 80)
print("VALIDATION COMPLETE")
print("=" * 80)