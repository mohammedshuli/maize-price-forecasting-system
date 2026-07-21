# src/verification.py
"""
Data Verification & Quality Assurance Module.
Provides validations for raw, processed, and forecasted price datasets to
prevent data corruption and ensure pipeline integrity.
"""

import pandas as pd


def verify_raw_data(df: pd.DataFrame) -> bool:
    """
    Validates the structure and content of raw price data from WFP.
    
    Raises:
        ValueError if schemas, column types, or basic expectations are not met.
    """
    required_cols = {"date", "admin1", "market", "commodity", "pricetype", "unit", "price"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"[verify] Raw data is missing required columns: {missing}")

    if df["price"].isnull().all():
        raise ValueError("[verify] Raw price column is completely empty.")

    negative_prices = (df["price"] < 0).sum()
    if negative_prices > 0:
        raise ValueError(f"[verify] Raw price column contains {negative_prices} negative values.")

    print("[verify] Raw data validation passed successfully.")
    return True


def verify_processed_data(df: pd.DataFrame, region_name: str) -> bool:
    """
    Validates that preprocessed and imputed datasets are ready for model training/viewing.
    Ensures no NaNs exist, timestamps are unique, and date indexes are strictly monotonic.
    """
    required_cols = {"date", "price"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"[verify] Processed data for {region_name} is missing columns: {missing}")

    # Ensure date can be parsed
    dates = pd.to_datetime(df["date"])

    # Check for NaN values
    nans = df["price"].isna().sum()
    if nans > 0:
        raise ValueError(f"[verify] Processed data for {region_name} contains {nans} missing values.")

    # Check for duplicates
    if dates.duplicated().any():
        raise ValueError(f"[verify] Processed data for {region_name} contains duplicate dates.")

    # Check for monotonicity
    if not dates.is_monotonic_increasing:
        raise ValueError(f"[verify] Processed data for {region_name} is not strictly sorted by date.")

    print(f"[verify] Processed data for {region_name} passed validation checks.")
    return True


def verify_forecast_data(df: pd.DataFrame, region_name: str) -> bool:
    """
    Validates the output forecasts.
    Verifies column names, absence of NaNs, and bounds ordering (lower_95 <= forecast <= upper_95).
    """
    required_cols = {"date", "forecast", "lower_95", "upper_95", "region"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"[verify] Forecast data for {region_name} is missing columns: {missing}")

    if df.isna().any().any():
        raise ValueError(f"[verify] Forecast data for {region_name} contains NaN values.")

    # Validate ordering of bounds
    invalid_bounds = (df["lower_95"] > df["forecast"]).sum() + (df["forecast"] > df["upper_95"]).sum()
    if invalid_bounds > 0:
        raise ValueError(
            f"[verify] Forecast for {region_name} contains {invalid_bounds} records with "
            "invalid confidence intervals (lower > forecast or forecast > upper)."
        )

    print(f"[verify] Forecast data for {region_name} passed confidence interval validation.")
    return True
