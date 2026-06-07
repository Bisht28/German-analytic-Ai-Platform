import pandas as pd

from sqlalchemy.orm import Session

from app.models.region import Region
from app.models.indicator import Indicator
from app.models.indicator_value import IndicatorValue
from app.models.import_run import ImportRun


FILE_PATH = "gaap_data/genesis/accident_statistics_by_kreis.csv"


INDICATORS = {
    "VER001": (
        "ACCIDENTS_TOTAL",
        "Accidents Total"
    ),
    "VER002": (
        "ACCIDENTS_WITH_INJURY",
        "Accidents With Injury"
    ),
    "VER005": (
        "ACCIDENTS_SERIOUS_PROPERTY_DAMAGE",
        "Serious Property Damage Accidents"
    ),
    "VER006": (
        "ACCIDENTS_ALCOHOL_DRUG_DAMAGE",
        "Alcohol/Drug Related Property Damage Accidents"
    ),
    "VER009": (
        "FATALITIES",
        "Fatalities"
    ),
    "VER019": (
        "INJURED_PERSONS",
        "Injured Persons"
    ),
}


def get_indicator(
    db: Session,
    code: str,
    name: str
) -> Indicator:

    indicator = (
        db.query(Indicator)
        .filter(Indicator.code == code)
        .first()
    )

    if indicator:
        return indicator

    indicator = Indicator(
        code=code,
        name=name,
        unit="count",
        source_system="GENESIS"
    )

    db.add(indicator)
    db.commit()
    db.refresh(indicator)

    return indicator


def load_accident_statistics(
    db: Session
) -> None:

    df = pd.read_csv(
        FILE_PATH,
        sep=";",
        encoding="latin1",
        low_memory=False
    )

    df = df[
        df["1_variable_label"]
        == "Kreise und kreisfreie Städte"
    ].copy()

    indicator_map = {}

    for source_code, (
        indicator_code,
        indicator_name
    ) in INDICATORS.items():

        indicator_map[source_code] = (
            get_indicator(
                db,
                indicator_code,
                indicator_name
            )
        )

    inserted = 0

    for _, row in df.iterrows():

        value = str(row["value"]).strip()

        if value in ["-", ".", "", "nan"]:
            continue

        source_code = str(
            row["value_variable_code"]
        ).strip()

        if source_code not in INDICATORS:
            continue

        indicator = indicator_map[
            source_code
        ]

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
                IndicatorValue.year == year
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
                value=numeric_value
            )
        )

        inserted += 1

    db.commit()

    db.add(
        ImportRun(
            source="genesis_accident_statistics",
            file_name="accident_statistics_by_kreis.csv",
            record_count=inserted,
            licence="GENESIS"
        )
    )

    db.commit()

    print(
        f"Inserted {inserted} accident values"
    )