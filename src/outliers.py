# src/outliers.py
"""
Outlier Detection Module.
Identifies outliers using the IQR (Interquartile Range) method.
Flags anomalous data points without modifying the underlying values.
"""

from typing import Tuple
import pandas as pd


def detect_outliers(
    df: pd.DataFrame,
    region_name: str,
    threshold: float = 3.0
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Flags outliers using the IQR (3.0x threshold by default).
    Returns a copy of the dataframe with an 'is_outlier' boolean column,
    and a Series containing only the flagged outlier values.

    Parameters:
        df: Input DataFrame with 'date' and 'price' columns.
        region_name: Geographic name for logging.
        threshold: IQR multiplier threshold (default is 3.0).
    """
    # Ensure index is date for scanning neighbors
    series = df.set_index("date")["price"]

    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - threshold * iqr
    upper = q3 + threshold * iqr

    print(f"=== {region_name} outlier detection ===")
    print(f"Q1: {q1:.0f}  Q3: {q3:.0f}  IQR: {iqr:.0f}")
    print(f"Bounds: [{lower:.0f}, {upper:.0f}]")

    flagged = series[(series < lower) | (series > upper)]

    if len(flagged) == 0:
        print("No outliers flagged\n")
    else:
        print(f"{len(flagged)} outlier(s) flagged:")
        for date, value in flagged.items():
            try:
                idx = series.index.get_loc(date)
                # Handle potential duplicate indexes or integer position retrieval
                if isinstance(idx, slice):
                    idx = idx.start
                elif isinstance(idx, (list, pd.Index)):
                    idx = idx[0]
                
                before = series.iloc[idx - 1] if idx > 0 else None
                after = series.iloc[idx + 1] if idx < len(series) - 1 else None
                print(f"  {date.date()}: {value:.0f}  (prev: {before}, next: {after})")
            except Exception as e:
                # Safe fallback if indexing fails
                print(f"  {date.date()}: {value:.0f} (neighbor context unavailable: {e})")
        print()

    df_out = df.copy()
    df_out["is_outlier"] = df_out["date"].isin(flagged.index)

    return df_out, flagged