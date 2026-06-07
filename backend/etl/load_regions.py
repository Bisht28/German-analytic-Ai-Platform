import pandas as pd

from sqlalchemy.orm import Session

from app.models.region import Region
from app.models.import_run import ImportRun


FILE_PATH = "gaap_data/regions/municipalities.xlsx"


def load_regions(db: Session) -> None:

    df = pd.read_excel(
        FILE_PATH,
        sheet_name="Onlineprodukt_Gemeinden30092025",
        header=None,
    )

    # Keep only municipality rows (Satzart = 60)
    df = df[df[0].astype(str).str.strip() == "60"].copy()
    print(f"Municipality rows found: {len(df)}")

    inserted = 0

    for _, row in df.iterrows():

        ags = (
            str(int(row[2])).zfill(2)
            + str(int(row[3])).zfill(1)
            + str(int(row[4])).zfill(2)
            + str(int(row[5])).zfill(4)
            + str(int(row[6])).zfill(3)
        )

        existing = (
            db.query(Region)
            .filter(Region.ags == ags)
            .first()
        )

        if existing:
            continue

        longitude = None
        latitude = None

        try:
            longitude = float(
                str(row[15]).replace(",", ".")
            )
            latitude = float(
                str(row[16]).replace(",", ".")
            )
        except Exception:
            pass

        population = None
        area_km2 = None

        try:
            population = int(row[9])
        except Exception:
            pass

        try:
            area_km2 = float(row[8])
        except Exception:
            pass

        region = Region(
            ags=ags,
            name=str(row[7]).strip(),
            level="municipality",
            population=population,
            area_km2=area_km2,
            longitude=longitude,
            latitude=latitude,
        )

        db.add(region)
        inserted += 1

    db.commit()

    run = ImportRun(
        source="municipalities",
        file_name="municipalities.xlsx",
        record_count=inserted,
        licence="Datenlizenz Deutschland 2.0",
    )

    db.add(run)
    db.commit()

    print(f"Inserted {inserted} municipalities")