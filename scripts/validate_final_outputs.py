import pandas as pd

print("=" * 80)
print("VALIDATING FINAL OUTPUTS")
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
    "Unique municipality codes:",
    regions["municipality_code"].nunique()
)

print(
    "District code lengths:"
)

print(
    regions["district_code"]
    .str.len()
    .value_counts()
)

print(
    "Municipality code lengths:"
)

print(
    regions["municipality_code"]
    .str.len()
    .value_counts()
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

dupes = population.duplicated(
    subset=[
        "region_code",
        "year"
    ]
).sum()

print("Duplicates:", dupes)

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
    "Unique districts:",
    rates["district_code"].nunique()
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
    "Unique districts:",
    accidents["district_code"].nunique()
)

print(
    "Unique municipalities:",
    accidents["municipality_code"].nunique()
)

print(
    "District lengths:"
)

print(
    accidents["district_code"]
    .str.len()
    .value_counts()
)

print(
    "Municipality lengths:"
)

print(
    accidents["municipality_code"]
    .str.len()
    .value_counts()
)

# --------------------------------------------------
# EXPECTED
# --------------------------------------------------

print("\nEXPECTED")

print("Regions     : 10953")
print("Population  : 14700")
print("Rates       : 400")
print("Accidents   : 794059")