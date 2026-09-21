import numpy as np
import pandas as pd


DATE_COLUMN = "Date Time Served"

BAR_COLUMN = "Bar Name"
BRAND_COLUMN = "Brand Name"

OPENING_COLUMN = "Opening Balance (ml)"
PURCHASE_COLUMN = "Purchase (ml)"
CONSUMED_COLUMN = "Consumed (ml)"
CLOSING_COLUMN = "Closing Balance (ml)"


def prepare_raw_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare raw inventory data for downstream processing.
    """

    df = df.copy()

    # Ensure datetime
    df[DATE_COLUMN] = pd.to_datetime(df[DATE_COLUMN])

    # Create calendar date
    df["Date"] = df[DATE_COLUMN].dt.date

    # Convert date to datetime64
    df["Date"] = pd.to_datetime(df["Date"])

    # Sort records
    df = df.sort_values(
        [BAR_COLUMN, BRAND_COLUMN, DATE_COLUMN]
    ).reset_index(drop=True)

    return df


def aggregate_daily_consumption(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate inventory records into daily Bar × Brand consumption.
    """

    daily = (
        df.groupby(
            ["Date", BAR_COLUMN, BRAND_COLUMN],
            as_index=False
        )
        .agg(
            daily_consumption_ml=(CONSUMED_COLUMN, "sum"),
            daily_purchase_ml=(PURCHASE_COLUMN, "sum"),
            opening_inventory_ml=(OPENING_COLUMN, "first"),
            closing_inventory_ml=(CLOSING_COLUMN, "last"),
            record_count=(BRAND_COLUMN, "size"),
        )
    )

    return daily


def prorate_daily_consumption(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a complete daily Bar × Brand series by prorating each snapshot's
    consumption across the days elapsed since the previous snapshot.

    Coverage per Bar × Brand is only ~20% (median gap ~3 days), so a literal
    daily aggregation would dump multi-day consumption onto one day and leave
    ~80% of days as artificial zeros.  Prorating spreads each snapshot's
    consumption evenly over the days it represents, which preserves the total
    while producing a realistic daily demand curve.
    """

    df = prepare_raw_data(df)

    series_list = []

    for (bar, brand), group in df.groupby([BAR_COLUMN, BRAND_COLUMN]):
        group = group.sort_values(DATE_COLUMN).reset_index(drop=True)

        dates = group["Date"]
        full_dates = pd.date_range(start=dates.min(), end=dates.max(), freq="D")

        day_consumption: dict = {}
        day_purchase: dict = {}
        day_opening: dict = {}
        day_closing: dict = {}
        day_count: dict = {}

        prev_date = None

        for _, rec in group.iterrows():
            day = rec["Date"]
            consumed = rec[CONSUMED_COLUMN]
            purchase = rec[PURCHASE_COLUMN]

            if prev_date is None:
                start = day
                span = 1
            else:
                elapsed = (day - prev_date).days
                start = prev_date + pd.Timedelta(days=1)
                span = max(elapsed, 1)
                if elapsed == 0:
                    start = day

            per_day = consumed / span
            for k in range(span):
                d = start + pd.Timedelta(days=k)
                day_consumption[d] = day_consumption.get(d, 0.0) + per_day

            day_purchase[day] = day_purchase.get(day, 0.0) + purchase
            day_opening[day] = rec[OPENING_COLUMN]
            day_closing[day] = rec[CLOSING_COLUMN]
            day_count[day] = day_count.get(day, 0) + 1

            prev_date = day

        out = pd.DataFrame({"Date": full_dates})
        out["daily_consumption_ml"] = [day_consumption.get(d, 0.0) for d in full_dates]
        out["daily_purchase_ml"] = [day_purchase.get(d, 0.0) for d in full_dates]
        out["opening_inventory_ml"] = [day_opening.get(d, np.nan) for d in full_dates]
        out["closing_inventory_ml"] = [day_closing.get(d, np.nan) for d in full_dates]
        out["record_count"] = [day_count.get(d, np.nan) for d in full_dates]

        out[BAR_COLUMN] = bar
        out[BRAND_COLUMN] = brand

        series_list.append(out)

    return pd.concat(series_list, ignore_index=True)