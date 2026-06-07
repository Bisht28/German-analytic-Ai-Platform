import os
import sys

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from app.core.database import SessionLocal

from etl.load_population import load_population

from etl.load_vehicle_registrations import (
    load_vehicle_registrations
)

from etl.load_accident_statistics import (
    load_accident_statistics
)

from etl.load_unfallatlas import (
    load_unfallatlas
)


def main():

    db = SessionLocal()

    try:

        print("Loading population...")
        load_population(db)

        print(
            "Loading vehicle registrations..."
        )
        load_vehicle_registrations(db)

        print(
            "Loading accident statistics..."
        )
        load_accident_statistics(db)

        print(
            "Loading Unfallatlas..."
        )
        load_unfallatlas(db)

        print(
            "ETL completed successfully."
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()