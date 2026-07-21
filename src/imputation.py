# src/imputation.py
"""
Data Imputation Module.
Detects consecutive gaps of missing values and fills them.
Large gaps (>= 4 months) are filled with the same-month previous year value,
and short gaps are filled using linear interpolation.
"""

from typing import List, Dict, Any
import pandas as pd
import numpy as np


def find_large_gaps(series: pd.Series, min_gap_months: int = 4) -> List[Dict[str, Any]]:
    """
    Finds contiguous runs of NaN values of length >= min_gap_months.
    Uses vectorized pandas aggregation to perform grouping.
    """
    isna = series.isna()
    if not isna.any():
        return []

    # Identify blocks of consecutive True/False values
    blocks = (isna != isna.shift()).cumsum()

    # Filter to only look at blocks representing NaNs
    nan_blocks = blocks[isna]

    # Count sizes of consecutive NaN blocks
    block_counts = nan_blocks.value_counts().sort_index()

    gaps = []
    for block_id, count in block_counts.items():
        if count >= min_gap_months:
            block_indices = series.index[blocks == block_id]
            gaps.append({
                "start": block_indices[0],
                "end": block_indices[-1],
                "months": int(count)
            })

    return gaps


def impute_series(
    df: pd.DataFrame,
    region_name: str,
    min_large_gap: int = 4,
    interp_limit: int = 3
) -> pd.DataFrame:
    """
    Fills missing values in a regional monthly price series.
    
    1. Large gaps (>= min_large_gap months) are filled using values from the same
       month in the previous year.
    2. Remaining small gaps are filled with linear interpolation up to interp_limit.
    3. Unresolved values at the edge of the series are dropped.
    """
    series = df.set_index("date")["price"].copy()
    series.index = pd.DatetimeIndex(series.index)

    print(f"=== {region_name} imputation ===")
    print(f"Before: {series.isna().sum()} missing of {len(series)}")

    large_gaps = find_large_gaps(series, min_large_gap)
    print(f"Large gaps found (>= {min_large_gap} months): {len(large_gaps)}")

    for gap in large_gaps:
        print(f"  {gap['start'].date()} to {gap['end'].date()} ({gap['months']} months)")
        gap_dates = pd.date_range(gap["start"], gap["end"], freq="MS")
        for d in gap_dates:
            prev_year = d - pd.DateOffset(years=1)
            # Safe lookup in DatetimeIndex
            if prev_year in series.index:
                v_prev = series.loc[prev_year]
            else:
                v_prev = np.nan

            if not pd.isna(v_prev):
                series.loc[d] = v_prev
            else:
                print(f"    {d.date()}: previous year also missing, left unresolved")

    print(f"After seasonal fill: {series.isna().sum()} missing")

    before_interp = series.isna().sum()
    series = series.interpolate(method="linear", limit=interp_limit)
    print(f"Linear interpolation filled: {before_interp - series.isna().sum()}")

    remaining = series.isna().sum()
    if remaining == 0:
        print("Status: fully resolved\n")
    else:
        print(
            f"Status: {remaining} months still missing -- dropping "
            "(edge of series, no reference data available)"
        )
        print(series[series.isna()])
        series = series.dropna()
        print()

    out = series.reset_index()
    out.columns = ["date", "price"]
    return out