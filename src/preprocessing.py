# src/preprocessing.py
"""
Data Preprocessing Pipeline.
Filters the raw food prices dataset to target wholesale maize in Mbeya and Iringa,
aggregates multiple markets into monthly averages, and reindexes to a shared calendar.
"""

from typing import List, Dict, Optional
import pandas as pd

from config import REGIONS


def filter_maize_wholesale(
    raw_csv_path: str,
    regions: Optional[List[str]] = None,
    commodity: str = "Maize",
    pricetype: str = "Wholesale",
    valid_unit: str = "100 KG"
) -> pd.DataFrame:
    """
    Loads raw CSV data and filters for a specific commodity, price type,
    geographic regions, and measuring units.
    """
    if regions is None:
        regions = REGIONS

    df = pd.read_csv(raw_csv_path)
    df["date"] = pd.to_datetime(df["date"])

    base_filter = (
        (df["commodity"] == commodity) &
        (df["pricetype"] == pricetype) &
        (df["admin1"].isin(regions))
    )

    all_matching = df[base_filter].copy()
    excluded_units = all_matching[all_matching["unit"] != valid_unit]
    filtered = all_matching[all_matching["unit"] == valid_unit].copy()

    print(f"[filter] total rows loaded: {len(df):,}")
    print(f"[filter] matching {commodity}/{pricetype}/{regions} (before unit filter): {len(all_matching):,}")
    
    if len(excluded_units) > 0:
        print(f"[filter] excluded {len(excluded_units)} row(s) with non-'{valid_unit}' unit:")
        print(excluded_units[["date", "admin1", "market", "unit", "price"]].to_string(index=False))
        
    print(f"[filter] final filtered rows (unit='{valid_unit}'): {len(filtered):,}")
    for region in regions:
        print(f"    {region}: {(filtered['admin1'] == region).sum()} rows")

    return filtered[["date", "admin1", "market", "unit", "price", "usdprice"]] \
        .sort_values(["admin1", "date"]).reset_index(drop=True)


def aggregate_to_monthly(
    filtered_df: pd.DataFrame,
    regions: Optional[List[str]] = None
) -> Dict[str, pd.DataFrame]:
    """
    Aggregates market-level transactions into a regional monthly mean price.
    """
    if regions is None:
        regions = REGIONS

    result = {}
    for region in regions:
        region_df = filtered_df[filtered_df["admin1"] == region].copy()
        n_markets = region_df["market"].nunique()

        # Extract month-start dates
        region_df["date"] = region_df["date"].values.astype("datetime64[M]")

        monthly = (
            region_df.groupby("date", as_index=False)["price"]
            .mean()
            .sort_values("date")
            .reset_index(drop=True)
        )

        print(f"[aggregate] {region}: {n_markets} market(s) -> {len(monthly)} months")
        result[region] = monthly

    return result


def reindex_to_full_calendar(
    monthly_dict: Dict[str, pd.DataFrame],
    freq: str = "MS"
) -> Dict[str, pd.DataFrame]:
    """
    Ensures that all regional time series share the exact same starting, ending,
    and step dates, filling missing periods with NaNs.
    """
    all_dates = pd.concat([df["date"] for df in monthly_dict.values()])
    start, end = all_dates.min(), all_dates.max()
    full_calendar = pd.date_range(start=start, end=end, freq=freq)

    print(f"[reindex] shared calendar: {start.date()} to {end.date()} ({len(full_calendar)} months)")

    result = {}
    for region, df in monthly_dict.items():
        reindexed = (
            df.set_index("date")
            .reindex(full_calendar)
            .rename_axis("date")
            .reset_index()
        )
        n_missing = reindexed["price"].isna().sum()
        n_total = len(reindexed)
        print(
            f"    {region}: {n_total} total, {n_total - n_missing} observed, "
            f"{n_missing} missing ({n_missing/n_total*100:.1f}%)"
        )
        result[region] = reindexed

    return result


def run_full_preprocessing(
    raw_csv_path: str,
    regions: Optional[List[str]] = None
) -> Dict[str, pd.DataFrame]:
    """
    Orchestrates the entire preprocessing pipeline.
    """
    if regions is None:
        regions = REGIONS

    print("=" * 60)
    print("RUNNING FULL PREPROCESSING PIPELINE")
    print("=" * 60)

    filtered = filter_maize_wholesale(raw_csv_path, regions)
    monthly = aggregate_to_monthly(filtered, regions)
    reindexed = reindex_to_full_calendar(monthly)

    print("=" * 60)
    print("PREPROCESSING COMPLETE")
    print("=" * 60)

    return reindexed