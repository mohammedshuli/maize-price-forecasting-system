# src/modeling.py
"""
Forecasting Model Module.
Provides functions to load pre-trained SARIMA model pickles, run forecasts with
confidence intervals (including exponentiating log-transformed predictions),
and save forecast results to CSV format.
"""

import os
from typing import Tuple
import joblib
import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAXResultsWrapper, SARIMAX

from config import MODELS_DIR, OUTPUTS_DIR


def get_model_path(region: str) -> str:
    """
    Returns the absolute path to the pickled model for the specified region.
    """
    return os.path.join(MODELS_DIR, f"sarima_{region.lower()}.pkl")


def load_model(region: str) -> SARIMAXResultsWrapper:
    """
    Loads a pre-trained SARIMA model pickle for the given region.
    """
    path = get_model_path(region)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model file not found for region '{region}' at: {path}")
    return joblib.load(path)


def generate_forecast(
    region: str,
    steps: int = 3,
    alpha: float = 0.05
) -> pd.DataFrame:
    """
    Generates forecast prices and 95% confidence intervals for a region.
    Reverts the log-transformation used during training.

    Parameters:
        region: Region name (Mbeya or Iringa).
        steps: Number of forecast steps (months) to generate.
        alpha: Significance level for prediction interval (default 0.05 for 95% CI).

    Returns:
        DataFrame containing 'date', 'forecast', 'lower_95', 'upper_95', and 'region'.
    """
    model = load_model(region)
    
    # Generate predictions in the model's transformed space (log-space)
    forecast_res = model.get_forecast(steps=steps)
    summary = forecast_res.summary_frame(alpha=alpha)
    
    # Exponentiate to revert log-transform and return to actual prices
    forecast_val = np.exp(summary["mean"])
    lower_val = np.exp(summary["mean_ci_lower"])
    upper_val = np.exp(summary["mean_ci_upper"])
    
    forecast_df = pd.DataFrame({
        "date": summary.index,
        "forecast": forecast_val.values,
        "lower_95": lower_val.values,
        "upper_95": upper_val.values,
        "region": region
    })
    
    # Normalize index
    forecast_df["date"] = pd.to_datetime(forecast_df["date"])
    return forecast_df


def save_forecast_to_csv(region: str, forecast_df: pd.DataFrame) -> str:
    """
    Saves the forecast dataframe to a CSV file in the outputs folder.
    """
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUTS_DIR, f"{region.lower()}_forecast.csv")
    forecast_df.to_csv(out_path, index=False)
    print(f"[modeling] Saved {region} forecast to: {out_path}")
    return out_path


def fit_and_save_model(
    region: str,
    series: pd.Series,
    order: Tuple[int, int, int],
    seasonal_order: Tuple[int, int, int, int]
) -> SARIMAXResultsWrapper:
    """
    Fits a SARIMAX model on log-transformed prices and pickles it to disk.
    
    Parameters:
        region: Region name.
        series: Time-series of prices, indexed by DatetimeIndex.
        order: (p, d, q) order parameters.
        seasonal_order: (P, D, Q, s) seasonal order parameters.
    """
    log_series = np.log(series)
    model = SARIMAX(
        log_series,
        order=order,
        seasonal_order=seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False
    )
    results = model.fit(disp=False)
    
    os.makedirs(MODELS_DIR, exist_ok=True)
    path = get_model_path(region)
    joblib.dump(results, path)
    print(f"[modeling] Fitted and saved model for {region} to: {path}")
    return results
