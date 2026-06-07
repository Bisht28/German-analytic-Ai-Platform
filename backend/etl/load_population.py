import pandas as pd

from sqlalchemy.orm import Session

from app.models.region import Region
from app.models.indicator import Indicator
from app.models.indicator_value import IndicatorValue
from app.models.import_run import ImportRun


FILE_PATH = "gaap_data/genesis/population_by_kreis.csv"


def load_population(db: Session) -> None:

    df = pd.read_csv(
        FILE_PATH,
        sep=";",
        encoding="latin1",
        low_memory=False,
    )

    df = df[
        df["1_variable_label"]
        == "Kreise und kreisfreie Städte"
    ].copy()

    indicator = (
        db.query(Indicator)
        .filter(
            Indicator.code == "POPULATION"
        )
        .first()
    )

    if not indicator:

        indicator = Indicator(
            code="POPULATION",
            name="Population",
            unit="persons",
            source_system="GENESIS",
        )

        db.add(indicator)
        db.commit()
        db.refresh(indicator)

    inserted = 0

    for _, row in df.iterrows():

        value = str(row["value"]).strip()

        if value in ["-", ".", "", "nan"]:
            continue

        ags = str(
            row["1_variable_attribute_code"]
        ).zfill(5)

        region = (
            db.query(Region)
            .filter(
                Region.ags == ags,
                Region.level == "kreis"
            )
            .first()
        )

        if not region:
            continue

        year = int(
            str(row["time"])[:4]
        )

        exists = (
            db.query(IndicatorValue)
            .filter(
                IndicatorValue.region_id
                == region.region_id,
                IndicatorValue.indicator_id
                == indicator.indicator_id,
                IndicatorValue.year == year,
            )
            .first()
        )

        if exists:
            continue

        try:
            numeric_value = float(value)
        except Exception:
            continue

        db.add(
            IndicatorValue(
                region_id=region.region_id,
                indicator_id=indicator.indicator_id,
                year=year,
                value=numeric_value,
            )
        )

        inserted += 1

    db.commit()

    db.add(
        ImportRun(
            source="genesis_population",
            file_name="population_by_kreis.csv",
            record_count=inserted,
            licence="GENESIS",
        )
    )

    db.commit()

    print(
        f"Inserted {inserted} population values"
    )