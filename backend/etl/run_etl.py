import os
import sys

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from app.core.database import SessionLocal

from etl.load_population import load_population


def main():

    db = SessionLocal()

    try:

        print("Loading population...")
        load_population(db)

        print("ETL completed successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    main()