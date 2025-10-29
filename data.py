from functools import lru_cache
from io import BytesIO
import requests
import pandas as pd
from typing import Optional

DATA_URL = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"


@lru_cache(maxsize=1)
def download_csv(url: str = DATA_URL, to_path: Optional[str] = None) -> bytes:
    """
    Download CSV bytes from a URL. Cached so repeated calls don't re-download.
    If to_path is provided, save a copy locally (useful for debugging).
    """
    print(f"[data.py] Downloading data from: {url}  (this may take a few seconds...)")
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
    except requests.exceptions.RequestException as exc:
        print("[data.py] ERROR: failed to download data:", exc)
        raise

    content = resp.content
    if to_path:
        try:
            with open(to_path, "wb") as f:
                f.write(content)
            print(f"[data.py] Saved raw CSV to: {to_path}")
        except OSError as oe:
            print("[data.py] Warning: could not save file locally:", oe)

    print("[data.py] Download finished.")
    return content


def prepare_data_from_csv_bytes(csv_bytes: bytes) -> pd.DataFrame:
    """
    Load CSV bytes into a DataFrame and apply cleaning:
     - keep relevant columns
     - coerce numeric columns
     - drop rows missing critical values
     - basic validation for ISO codes and positive CO2
    """
    df = pd.read_csv(BytesIO(csv_bytes))

    # Columns we need for the dashboard
    cols = ["country", "iso_code", "year", "co2", "population"]
    present = [c for c in cols if c in df.columns]
    df = df.loc[:, present].copy()

    df["co2"] = pd.to_numeric(df.get("co2"), errors="coerce")
    df = df.dropna(subset=["co2", "iso_code"])
    df = df[df["co2"] > 0]

    # ISO code check: keep 3-letter codes (OWID uses e.g. 'OWID_WRL' for world)
    # We remove codes that are not length 3 to focus on country-level data.
    df = df[df["iso_code"].str.len() == 3]

    # Year to int
    df["year"] = df["year"].astype(int)

    # Sort and reset index
    df = df.sort_values(by=["country", "year"]).reset_index(drop=True)

  
    # TODO: handle sparse countries separately (e.g. interpolation or flags)
    print(f"[data.py] Prepared DataFrame: rows={len(df)}, cols={len(df.columns)}")
    return df


def load_prepared_data() -> pd.DataFrame:
    """
    helper used by app.py. Downloads (cached) and prepares the dataset.
    Raises exception when download fails so the caller can decide what to show.
    """
    csv_bytes = download_csv()
    df = prepare_data_from_csv_bytes(csv_bytes)
    print("[data.py] Ready to use data in the app.")
    return df


if __name__ == "__main__":
    try:
        _df = load_prepared_data()
        print(_df.head(3).to_string(index=False))
    except Exception as e:
        print("[data.py] Local run failed:", e)

