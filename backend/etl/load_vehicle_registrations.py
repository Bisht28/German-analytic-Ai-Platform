import pandas as pd

from sqlalchemy.orm import Session

from app.models.region import Region
from app.models.indicator import Indicator
from app.models.indicator_value import IndicatorValue
from app.models.import_run import ImportRun


FILE_PATH = "gaap_data/genesis/vehicle_registrations.csv"


INDICATORS = {
    "Insgesamt": (
        "VEHICLES_TOTAL",
        "Vehicle Registrations Total"
    ),
    "Pkw": (
        "VEHICLES_CARS",
        "Passenger Cars"
    ),
    "Lkw": (
        "VEHICLES_TRUCKS",
        "Trucks"
    ),
    "Krafträder": (
        "VEHICLES_MOTORCYCLES",
        "Motorcycles"
    ),
    "Zugmaschinen": (
        "VEHICLES_TRACTORS",
        "Tractors"
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
        unit="vehicles",
        source_system="GENESIS"
    )

    db.add(indicator)
    db.commit()
    db.refresh(indicator)

    return indicator


def load_vehicle_registrations(
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

    for _, (code, name) in INDICATORS.items():

        indicator = get_indicator(
            db,
            code,
            name
        )

        indicator_map[code] = indicator

    inserted = 0

    for _, row in df.iterrows():

        value = str(row["value"]).strip()

        if value in ["-", ".", "", "nan"]:
            continue

        vehicle_type = str(
            row["2_variable_attribute_label"]
        ).strip()

        if vehicle_type not in INDICATORS:
            continue

        indicator_code = (
            INDICATORS[vehicle_type][0]
        )

        indicator = indicator_map[
            indicator_code
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
            source="genesis_vehicle_registrations",
            file_name="vehicle_registrations.csv",
            record_count=inserted,
            licence="GENESIS"
        )
    )

    db.commit()

    print(
        f"Inserted {inserted} vehicle values"
    )