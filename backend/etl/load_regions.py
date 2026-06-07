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

    inserted = 0

    state_map = {}
    kreis_map = {}

    # --------------------------------------------------
    # STATES (10)
    # --------------------------------------------------

    states = df[df[0].astype(str).str.strip() == "10"]

    print(f"States found: {len(states)}")

    for _, row in states.iterrows():

        ags = str(row[2]).zfill(2)

        region = Region(
            ags=ags,
            name=str(row[7]).strip(),
            level="state",
        )

        db.add(region)
        db.flush()

        state_map[ags] = region.region_id
        inserted += 1

    # --------------------------------------------------
    # KREISE (40)
    # --------------------------------------------------

    kreise = df[df[0].astype(str).str.strip() == "40"]

    print(f"Kreise found: {len(kreise)}")

    for _, row in kreise.iterrows():

        state_ags = str(row[2]).zfill(2)

        kreis_ags = (
            str(row[2]).zfill(2)
            + str(int(row[3])).zfill(1)
            + str(row[4]).zfill(2)
        )

        region = Region(
            ags=kreis_ags,
            name=str(row[7]).strip(),
            level="kreis",
            parent_region_id=state_map.get(state_ags),
        )

        db.add(region)
        db.flush()

        kreis_map[kreis_ags] = region.region_id
        inserted += 1

    # --------------------------------------------------
    # MUNICIPALITIES (60)
    # --------------------------------------------------

    municipalities = df[
        df[0].astype(str).str.strip() == "60"
    ]

    print(
        f"Municipalities found: {len(municipalities)}"
    )

    for _, row in municipalities.iterrows():

        municipality_ags = (
            str(int(row[2])).zfill(2)
            + str(int(row[3])).zfill(1)
            + str(int(row[4])).zfill(2)
            + str(int(row[5])).zfill(4)
            + str(int(row[6])).zfill(3)
        )

        kreis_ags = (
            str(int(row[2])).zfill(2)
            + str(int(row[3])).zfill(1)
            + str(int(row[4])).zfill(2)
        )

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
            ags=municipality_ags,
            name=str(row[7]).strip(),
            level="municipality",
            parent_region_id=kreis_map.get(kreis_ags),
            population=population,
            area_km2=area_km2,
            longitude=longitude,
            latitude=latitude,
        )

        db.add(region)
        inserted += 1

    db.commit()

    run = ImportRun(
        source="regions",
        file_name="municipalities.xlsx",
        record_count=inserted,
        licence="Datenlizenz Deutschland 2.0",
    )

    db.add(run)
    db.commit()

    print(f"Inserted {inserted} total regions")