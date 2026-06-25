import getpass
from pathlib import Path

import psycopg

DB_NAME = "roadinsight"
DB_USER = "postgres"
DB_HOST = "localhost"
DB_PORT = 5432

FILES = [
    ("roadinsight.regions", "data/processed/regions_final.csv", 10953),
    ("roadinsight.population", "data/processed/population_final.csv", 12994),
    ("roadinsight.official_rates", "data/processed/rates_final.csv", 400),
    ("roadinsight.accidents", "data/processed/accidents_final.csv", 794059),
]

password = getpass.getpass("Postgres password: ")

conn = psycopg.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=password,
    host=DB_HOST,
    port=DB_PORT,
)

try:

    with conn:

        with conn.cursor() as cur:

            for table, csv_path, expected_rows in FILES:

                print(f"\nLoading {table}")

                csv_file = Path(csv_path)

                if table == "roadinsight.accidents":

                    copy_sql = """
                    COPY roadinsight.accidents (
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
                    FROM STDIN
                    WITH (FORMAT CSV, HEADER TRUE)
                    """

                else:

                    copy_sql = (
                        f"COPY {table} "
                        "FROM STDIN "
                        "WITH (FORMAT CSV, HEADER TRUE)"
                    )

                with open(
                    csv_file,
                    "r",
                    encoding="utf-8"
                ) as f:

                    with cur.copy(copy_sql) as copy:

                        while True:

                            chunk = f.read(
                                1024 * 1024
                            )

                            if not chunk:
                                break

                            copy.write(chunk)

                cur.execute(
                    f"SELECT COUNT(*) FROM {table}"
                )

                actual_rows = cur.fetchone()[0]

                print(
                    f"Rows loaded: {actual_rows}"
                )

                if actual_rows != expected_rows:

                    raise RuntimeError(
                        f"{table}: expected {expected_rows}, got {actual_rows}"
                    )

    print("\nSUCCESS")
    print("All datasets loaded correctly.")

except Exception as e:

    print("\nFAILED")
    print(str(e))
    raise

finally:

    conn.close()