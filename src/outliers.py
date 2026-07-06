# src/outliers.py
# detects outliers using IQR method (3.0x threshold per proposal 3.6.3)
# does NOT auto-treat -- returns flagged points with context so a decision can be made
# adds is_outlier column to the dataframe for transparency either way

import pandas as pd
import numpy as np


def detect_outliers(df, region_name, threshold=3.0):
    series = df.set_index("date")["price"]

    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - threshold * iqr
    upper = q3 + threshold * iqr

    print(f"=== {region_name} ===")
    print(f"Q1: {q1:.0f}  Q3: {q3:.0f}  IQR: {iqr:.0f}")
    print(f"bounds: [{lower:.0f}, {upper:.0f}]")

    flagged = series[(series < lower) | (series > upper)]

    if len(flagged) == 0:
        print("no outliers flagged\n")
    else:
        print(f"{len(flagged)} outlier(s) flagged:")
        for date, value in flagged.items():
            idx = series.index.get_loc(date)
            before = series.iloc[idx - 1] if idx > 0 else None
            after = series.iloc[idx + 1] if idx < len(series) - 1 else None
            print(f"  {date.date()}: {value:.0f}  (prev: {before}, next: {after})")
        print()

    df_out = df.copy()
    df_out["is_outlier"] = df_out["date"].isin(flagged.index)

    return df_out, flagged