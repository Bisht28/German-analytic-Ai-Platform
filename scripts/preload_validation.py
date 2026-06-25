import sys
import pandas as pd

errors = []

print("=" * 80)
print("PRELOAD VALIDATION")
print("=" * 80)

# =====================================================
# REGIONS
# =====================================================

print("\n[REGIONS]")

regions = pd.read_csv(
    "data/processed/regions_final.csv",
    dtype=str
)

print("Rows:", len(regions))

if len(regions) != 10953:
    errors.append(
        f"Regions row count mismatch: {len(regions)}"
    )

dup = regions["municipality_code"].duplicated().sum()

print("Duplicate municipality_code:", dup)

if dup:
    errors.append(
        f"Regions duplicates: {dup}"
    )

if (
    regions["municipality_code"]
    .str.len()
    .ne(8)
    .any()
):
    errors.append(
        "Regions municipality_code length invalid"
    )

if (
    regions["district_code"]
    .str.len()
    .ne(5)
    .any()
):
    errors.append(
        "Regions district_code length invalid"
    )

if (
    regions["state_code"]
    .str.len()
    .ne(2)
    .any()
):
    errors.append(
        "Regions state_code length invalid"
    )

for col in [
    "area_km2",
    "population",
    "longitude",
    "latitude"
]:
    bad = pd.to_numeric(
        regions[col],
        errors="coerce"
    ).isna()

    bad = bad & regions[col].notna()

    if bad.sum():
        errors.append(
            f"Regions invalid numeric values in {col}: {bad.sum()}"
        )

# =====================================================
# POPULATION
# =====================================================

print("\n[POPULATION]")

population = pd.read_csv(
    "data/processed/population_final.csv",
    dtype=str
)

print("Rows:", len(population))

if len(population) != 12994:
    errors.append(
        f"Population row count mismatch: {len(population)}"
    )

dup = population.duplicated(
    ["region_code", "year"]
).sum()

print("Duplicate PK:", dup)

if dup:
    errors.append(
        f"Population duplicates: {dup}"
    )

bad = pd.to_numeric(
    population["population"],
    errors="coerce"
).isna()

if bad.sum():
    errors.append(
        f"Population invalid values: {bad.sum()}"
    )

# =====================================================
# RATES
# =====================================================

print("\n[RATES]")

rates = pd.read_csv(
    "data/processed/rates_final.csv",
    dtype=str
)

print("Rows:", len(rates))

if len(rates) != 400:
    errors.append(
        f"Rates row count mismatch: {len(rates)}"
    )

dup = rates["district_code"].duplicated().sum()

print("Duplicate district_code:", dup)

if dup:
    errors.append(
        f"Rates duplicates: {dup}"
    )

bad = pd.to_numeric(
    rates["rate_per_10000"],
    errors="coerce"
).isna()

if bad.sum():
    errors.append(
        f"Rates invalid values: {bad.sum()}"
    )

# =====================================================
# ACCIDENTS
# =====================================================

print("\n[ACCIDENTS]")

acc = pd.read_csv(
    "data/processed/accidents_final.csv",
    dtype=str
)

print("Rows:", len(acc))

if len(acc) != 794059:
    errors.append(
        f"Accidents row count mismatch: {len(acc)}"
    )

if (
    acc["state_code"]
    .str.zfill(2)
    .str.len()
    .ne(2)
    .any()
):
    errors.append(
        "Accidents state_code length invalid"
    )

if (
    acc["district_code"]
    .str.zfill(5)
    .str.len()
    .ne(5)
    .any()
):
    errors.append(
        "Accidents district_code length invalid"
    )

if (
    acc["municipality_code"]
    .str.zfill(8)
    .str.len()
    .ne(8)
    .any()
):
    errors.append(
        "Accidents municipality_code length invalid"
    )

integer_columns = [
    "source_year",
    "year",
    "month",
    "weekday",
    "hour",
    "category",
    "accident_type",
    "accident_subtype",
    "light_condition",
    "road_condition",
    "is_bicycle",
    "is_car",
    "is_pedestrian",
    "is_motorcycle",
    "is_commercial_vehicle",
    "is_other_vehicle"
]

for col in integer_columns:

    bad = pd.to_numeric(
        acc[col],
        errors="coerce"
    ).isna()

    if bad.sum():
        errors.append(
            f"Accidents invalid integers in {col}: {bad.sum()}"
        )

for col in [
    "longitude",
    "latitude"
]:

    bad = pd.to_numeric(
        acc[col],
        errors="coerce"
    ).isna()

    if bad.sum():
        errors.append(
            f"Accidents invalid coordinates in {col}: {bad.sum()}"
        )

# =====================================================
# RESULT
# =====================================================

print("\n" + "=" * 80)

if errors:

    print("PRELOAD VALIDATION FAILED\n")

    for e in errors:
        print("-", e)

    sys.exit(1)

print("PRELOAD VALIDATION PASSED")
print("=" * 80)