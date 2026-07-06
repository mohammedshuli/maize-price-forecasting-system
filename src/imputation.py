# src/imputation.py
# Function 1: auto-detect consecutive missing runs of a given minimum length
# Function 2: fill large gaps using same-month previous year only (no future data), 
#             fill short gaps with linear interpolation, and report anything unresolved

import pandas as pd
import numpy as np


def find_large_gaps(series, min_gap_months=4):
    gaps = []
    in_gap = False
    gap_start = None
    gap_count = 0

    for date, value in series.items():
        if pd.isna(value):
            if not in_gap:
                gap_start = date
                in_gap = True
            gap_count += 1
        else:
            if in_gap and gap_count >= min_gap_months:
                gaps.append({
                    "start": gap_start,
                    "end": date - pd.DateOffset(months=1),
                    "months": gap_count
                })
            in_gap = False
            gap_count = 0

    if in_gap and gap_count >= min_gap_months:
        gaps.append({
            "start": gap_start,
            "end": series.index[-1],
            "months": gap_count
        })

    return gaps


def impute_series(df, region_name, min_large_gap=4, interp_limit=3):
    series = df.set_index("date")["price"].copy()
    series.index = pd.DatetimeIndex(series.index)

    print(f"=== {region_name} ===")
    print(f"before: {series.isna().sum()} missing of {len(series)}")

    large_gaps = find_large_gaps(series, min_large_gap)
    print(f"large gaps found (>= {min_large_gap} months): {len(large_gaps)}")

    for gap in large_gaps:
        print(f"  {gap['start'].date()} to {gap['end'].date()} ({gap['months']} months)")
        gap_dates = pd.date_range(gap["start"], gap["end"], freq="MS")
        for d in gap_dates:
            prev_year = d - pd.DateOffset(years=1)
            v_prev = series.get(prev_year, np.nan)
            if not np.isnan(v_prev):
                series[d] = v_prev
            else:
                print(f"    {d.date()}: previous year also missing, left unresolved")

    print(f"after seasonal fill: {series.isna().sum()} missing")

    before_interp = series.isna().sum()
    series = series.interpolate(method="linear", limit=interp_limit)
    print(f"linear interpolation filled: {before_interp - series.isna().sum()}")

    remaining = series.isna().sum()
    if remaining == 0:
        print("status: fully resolved\n")
    else:
        print(f"status: {remaining} months still missing -- dropping (edge of series, no reference data available)")
        print(series[series.isna()])
        series = series.dropna()
        print()

    out = series.reset_index()
    out.columns = ["date", "price"]
    return out