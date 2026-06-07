import os

import pandas as pd

from sqlalchemy.orm import Session

from app.models.accident import Accident
from app.models.region import Region
from app.models.import_run import ImportRun


DATA_DIR = "gaap_data/unfallatlas_all"

FILES = [
    "Unfallorte2016.csv",
    "Unfallorte2017.csv",
    "Unfallorte2018.csv",
    "Unfallorte2019.csv",
    "Unfallorte2020.csv",
    "Unfallorte2021.csv",
    "Unfallorte2022.csv",
    "Unfallorte2023.csv",
    "Unfallorte2024.csv",
]

BATCH_SIZE = 5000


def to_int(value):

    try:

        if pd.isna(value):
            return None

        return int(value)

    except Exception:
        return None


def to_float(value):

    try:

        if pd.isna(value):
            return None

        return float(value)

    except Exception:
        return None


def get_column(df, candidates):

    for col in candidates:

        if col in df.columns:
            return col

    return None


def build_region_lookup(db: Session):

    regions = (
        db.query(Region)
        .filter(Region.level == "kreis")
        .all()
    )

    return {
        region.ags: region.region_id
        for region in regions
    }


def flush_batch(db, batch):

    if not batch:
        return

    db.bulk_save_objects(batch)
    db.commit()
    batch.clear()


def load_unfallatlas(db: Session) -> None:

    region_lookup = build_region_lookup(db)

    total_inserted = 0
    unmatched_ags = set()

    for file_name in FILES:

        path = os.path.join(
            DATA_DIR,
            file_name
        )

        print(f"Processing {file_name}...")

        df = pd.read_csv(
            path,
            sep=";",
            encoding="latin1",
            low_memory=False
        )

        light_col = get_column(
            df,
            [
                "ULICHTVERH",
                "LICHT"
            ]
        )

        road_col = get_column(
            df,
            [
                "IstStrasse",
                "STRZUSTAND",
                "IstStrassenzustand"
            ]
        )

        sonstige_col = get_column(
            df,
            [
                "IstSonstig",
                "IstSonstige"
            ]
        )

        batch = []
        inserted = 0

        for _, row in df.iterrows():

            try:

                ags = (
                    str(
                        int(row["ULAND"])
                    ).zfill(2)
                    +
                    str(
                        int(row["UREGBEZ"])
                    ).zfill(1)
                    +
                    str(
                        int(row["UKREIS"])
                    ).zfill(2)
                )

            except Exception:
                continue

            region_id = region_lookup.get(ags)

            if not region_id:

                unmatched_ags.add(ags)
                continue

            accident = Accident(
                year=to_int(
                    row.get("UJAHR")
                ),
                month=to_int(
                    row.get("UMONAT")
                ),
                hour=to_int(
                    row.get("USTUNDE")
                ),
                weekday=to_int(
                    row.get("UWOCHENTAG")
                ),
                category=to_int(
                    row.get("UKATEGORIE")
                ),
                type=to_int(
                    row.get("UART")
                ),
                accident_subtype=to_int(
                    row.get("UTYP1")
                ),
                light=to_int(
                    row.get(light_col)
                ) if light_col else None,
                road_condition=to_int(
                    row.get(road_col)
                ) if road_col else None,
                ist_rad=to_int(
                    row.get("IstRad")
                ),
                ist_pkw=to_int(
                    row.get("IstPKW")
                ),
                ist_fuss=to_int(
                    row.get("IstFuss")
                ),
                ist_krad=to_int(
                    row.get("IstKrad")
                ),
                ist_gkfz=to_int(
                    row.get("IstGkfz")
                ),
                ist_sonstige=to_int(
                    row.get(sonstige_col)
                ) if sonstige_col else None,
                longitude=to_float(
                    row.get("XGCSWGS84")
                ),
                latitude=to_float(
                    row.get("YGCSWGS84")
                ),
                region_id=region_id
            )

            batch.append(accident)
            inserted += 1

            if len(batch) >= BATCH_SIZE:
                flush_batch(
                    db,
                    batch
                )

        flush_batch(
            db,
            batch
        )

        db.add(
            ImportRun(
                source="unfallatlas",
                file_name=file_name,
                record_count=inserted,
                licence="Unfallatlas"
            )
        )

        db.commit()

        total_inserted += inserted

        print(
            f"Inserted {inserted} accidents"
        )

    print(
        f"Total accidents inserted: {total_inserted}"
    )

    print(
        f"Unmatched AGS codes: {len(unmatched_ags)}"
    )

    if unmatched_ags:

        print(
            sorted(
                list(unmatched_ags)
            )[:50]
        )