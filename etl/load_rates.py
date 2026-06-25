import pandas as pd
from pathlib import Path

Path("data/processed").mkdir(
    parents=True,
    exist_ok=True
)

df = pd.read_csv(
    "data/raw/accident_per_10000_per_city.csv",
    sep=";",
    skiprows=3,
    header=None
)

rates = pd.DataFrame({

    "district_code":
        df[0]
        .astype(str)
        .str.zfill(5),

    "district_name":
        df[1]
        .astype(str),

    "rate_per_10000":
        df[2]
})

rates.to_csv(
    "data/processed/rates_final.csv",
    index=False
)

print(
    f"Saved {len(rates):,} rows"
)