\echo ==========================================
\echo LOADING REGIONS
\echo ==========================================

\copy roadinsight.regions(
municipality_code,
district_code,
state_code,
name,
area_km2,
population,
longitude,
latitude,
settlement_type
)
FROM ‘data/processed/regions_final.csv’
WITH (
FORMAT CSV,
HEADER TRUE
);

\echo ==========================================
\echo LOADING POPULATION
\echo ==========================================

\copy roadinsight.population(
region_code,
region_name,
year,
population
)
FROM ‘data/processed/population_final.csv’
WITH (
FORMAT CSV,
HEADER TRUE
);

\echo ==========================================
\echo LOADING OFFICIAL RATES
\echo ==========================================

\copy roadinsight.official_rates(
district_code,
district_name,
rate_per_10000
)
FROM ‘data/processed/rates_final.csv’
WITH (
FORMAT CSV,
HEADER TRUE
);

\echo ==========================================
\echo LOADING ACCIDENTS
\echo ==========================================

\copy roadinsight.accidents(
source_year,
year,
month,
weekday,
hour,
state_code,
district_code,
municipality_code,
category,
accident_type,
accident_subtype,
light_condition,
road_condition,
is_bicycle,
is_car,
is_pedestrian,
is_motorcycle,
is_commercial_vehicle,
is_other_vehicle,
longitude,
latitude
)
FROM ‘data/processed/accidents_final.csv’
WITH (
FORMAT CSV,
HEADER TRUE
);

\echo ==========================================
\echo VERIFYING COUNTS
\echo ==========================================

SELECT
‘regions’ AS table_name,
COUNT(*) AS row_count
FROM roadinsight.regions

UNION ALL

SELECT
‘population’,
COUNT(*)
FROM roadinsight.population

UNION ALL

SELECT
‘official_rates’,
COUNT(*)
FROM roadinsight.official_rates

UNION ALL

SELECT
‘accidents’,
COUNT(*)
FROM roadinsight.accidents;