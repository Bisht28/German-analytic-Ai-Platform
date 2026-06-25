-- =====================================================
-- ROADINSIGHT AI
-- DATABASE SCHEMA
-- =====================================================

CREATE SCHEMA IF NOT EXISTS roadinsight;

SET search_path TO roadinsight;

-- =====================================================
-- REGIONS
-- municipalities.xlsx
-- =====================================================

CREATE TABLE IF NOT EXISTS regions (

    municipality_code VARCHAR(8) PRIMARY KEY,

    district_code VARCHAR(5) NOT NULL,

    state_code VARCHAR(2) NOT NULL,

    name TEXT NOT NULL,

    area_km2 NUMERIC(12,2),

    population BIGINT,

    longitude DOUBLE PRECISION,

    latitude DOUBLE PRECISION,

    settlement_type TEXT
);

CREATE INDEX IF NOT EXISTS idx_regions_district
ON regions(district_code);

CREATE INDEX IF NOT EXISTS idx_regions_state
ON regions(state_code);

CREATE INDEX IF NOT EXISTS idx_regions_name
ON regions(name);

-- =====================================================
-- POPULATION
-- population_by_kreis.csv
--
-- IMPORTANT:
-- ETL MUST KEEP ONLY
-- 2_variable_attribute_code IS NULL
-- ("Insgesamt")
-- =====================================================

CREATE TABLE IF NOT EXISTS population (

    region_code VARCHAR(8) NOT NULL,

    region_name TEXT NOT NULL,

    year INTEGER NOT NULL,

    population BIGINT NOT NULL,

    PRIMARY KEY (
        region_code,
        year
    )
);

CREATE INDEX IF NOT EXISTS idx_population_region
ON population(region_code);

CREATE INDEX IF NOT EXISTS idx_population_year
ON population(year);

-- =====================================================
-- OFFICIAL RATES
-- accident_per_10000_per_city.csv
-- =====================================================

CREATE TABLE IF NOT EXISTS official_rates (

    district_code VARCHAR(5) PRIMARY KEY,

    district_name TEXT NOT NULL,

    rate_per_10000 NUMERIC(10,2) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_rates_name
ON official_rates(district_name);

-- =====================================================
-- ACCIDENTS
-- Unfallorte2022
-- Unfallorte2023
-- Unfallorte2024
--
-- WGS84 Coordinates Only
-- =====================================================

CREATE TABLE IF NOT EXISTS accidents (

    accident_id BIGSERIAL PRIMARY KEY,

    source_year INTEGER NOT NULL,

    year INTEGER NOT NULL,

    month INTEGER NOT NULL,

    weekday INTEGER,

    hour INTEGER,

    state_code VARCHAR(2) NOT NULL,

    district_code VARCHAR(5) NOT NULL,

    municipality_code VARCHAR(8) NOT NULL,

    category INTEGER,

    accident_type INTEGER,

    accident_subtype INTEGER,

    light_condition INTEGER,

    road_condition INTEGER,

    is_bicycle INTEGER,

    is_car INTEGER,

    is_pedestrian INTEGER,

    is_motorcycle INTEGER,

    is_commercial_vehicle INTEGER,

    is_other_vehicle INTEGER,

    longitude DOUBLE PRECISION,

    latitude DOUBLE PRECISION
);

CREATE INDEX IF NOT EXISTS idx_accidents_year
ON accidents(year);

CREATE INDEX IF NOT EXISTS idx_accidents_month
ON accidents(month);

CREATE INDEX IF NOT EXISTS idx_accidents_state
ON accidents(state_code);

CREATE INDEX IF NOT EXISTS idx_accidents_district
ON accidents(district_code);

CREATE INDEX IF NOT EXISTS idx_accidents_municipality
ON accidents(municipality_code);

CREATE INDEX IF NOT EXISTS idx_accidents_category
ON accidents(category);

CREATE INDEX IF NOT EXISTS idx_accidents_type
ON accidents(accident_type);

CREATE INDEX IF NOT EXISTS idx_accidents_year_district
ON accidents(year, district_code);

CREATE INDEX IF NOT EXISTS idx_accidents_year_state
ON accidents(year, state_code);

-- =====================================================
-- ANALYTICS VIEWS
-- =====================================================

CREATE OR REPLACE VIEW v_accident_counts_by_district AS
SELECT
    district_code,
    year,
    COUNT(*) AS accident_count
FROM accidents
GROUP BY district_code, year;

CREATE OR REPLACE VIEW v_accident_counts_by_state AS
SELECT
    state_code,
    year,
    COUNT(*) AS accident_count
FROM accidents
GROUP BY state_code, year;

-- =====================================================
-- ACCIDENT RATE VIEW
-- =====================================================

CREATE OR REPLACE VIEW v_accidents_per_10000 AS
SELECT
    a.district_code,
    a.year,
    COUNT(*) AS accidents,
    p.population,

    ROUND(
        (
            COUNT(*)::NUMERIC
            / NULLIF(p.population, 0)
        ) * 10000,
        2
    ) AS accidents_per_10000

FROM accidents a

JOIN population p
    ON a.district_code = p.region_code
   AND a.year = p.year

GROUP BY
    a.district_code,
    a.year,
    p.population;

-- =====================================================
-- DATA DISCOVERY VALIDATIONS
-- =====================================================

-- Regions expected:
-- 10953 rows

-- Population expected:
-- 14700 rows

-- Official rates expected:
-- 400 rows

-- Accidents expected:
-- 794059 rows

-- District code length:
-- 5

-- Municipality code length:
-- 8

-- Population duplicates:
-- 0

-- Preserve leading zeros.
-- All administrative codes must be stored as TEXT.
--
-- state_code        VARCHAR(2)
-- district_code     VARCHAR(5)
-- municipality_code VARCHAR(8)

-- Use:
-- XGCSWGS84
-- YGCSWGS84

-- Ignore:
-- LINREFX
-- LINREFY