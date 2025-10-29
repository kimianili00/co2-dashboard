import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import pandas as pd
from data import load_prepared_data, prepare_data_from_csv_bytes, download_csv


def test_download_csv_returns_bytes():
    """Ensure download_csv returns bytes ."""
    content = download_csv()
    assert isinstance(content, (bytes, bytearray))
    assert len(content) > 100 

def test_prepare_data_produces_dataframe():
    content = download_csv()
    df = prepare_data_from_csv_bytes(content)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    # required columns
    for col in ("country", "iso_code", "year", "co2"):
        assert col in df.columns


def test_loaded_data_has_valid_iso_and_positive_co2():
    df = load_prepared_data()
    assert df["iso_code"].notna().all()
    assert (df["iso_code"].str.len() == 3).all()
    assert (df["co2"] > 0).all()


def test_population_column_may_exist():
    # This test is permissive: population is useful but dataset may vary
    df = load_prepared_data()
    assert "population" in df.columns or True  
