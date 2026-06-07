import os
import sys

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from app.core.database import SessionLocal
from etl.load_regions import load_regions


def main():

    db = SessionLocal()

    try:
        print("Loading regions...")
        load_regions(db)

        print("ETL completed successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    main()