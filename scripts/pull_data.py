import json
import os

import pandas as pd
import requests

INDICATOR = "IT.NET.BBND"
COUNTRIES = "KEN;GHA;SEN"
YEARS = "2015:2024"
OUTPUT_NAME = "internet"

BASE_URL = "https://api.worldbank.org/v2"
RAW_DIR = "data/raw"


def fetch(indicator, countries, years):
    url = f"{BASE_URL}/country/{countries}/indicator/{indicator}"
    params = {"format": "json", "date": years, "per_page": 20000}
    print(f"Requesting {url}")
    r = requests.get(url, params=params, timeout=60)
    r.raise_for_status()
    payload = r.json()
    if len(payload) < 2 or payload[1] is None:
        raise RuntimeError(f"No data: {payload}")
    return payload


def tidy(payload):
    rows = []
    for record in payload[1]:
        rows.append({
            "country_code": record["countryiso3code"],
            "country": record["country"]["value"],
            "year": int(record["date"]),
            "value": record["value"],
        })
    df = pd.DataFrame(rows)
    df = df.dropna(subset=["value"])
    df = df.sort_values(["country", "year"]).reset_index(drop=True)
    return df


def main():
    os.makedirs(RAW_DIR, exist_ok=True)
    payload = fetch(INDICATOR, COUNTRIES, YEARS)
    df = tidy(payload)

    with open(f"{RAW_DIR}/{OUTPUT_NAME}_raw.json", "w") as f:
        json.dump(payload, f, indent=2)
    df.to_csv(f"{RAW_DIR}/{OUTPUT_NAME}.csv", index=False)

    print(f"Saved {len(df)} rows to {RAW_DIR}/{OUTPUT_NAME}.csv")
    print(df.head())


if __name__ == "__main__":
    main()
