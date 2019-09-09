import pandas as pd

def weekday_weekend_traffic_differences(df, week):
    """
    Calculates the difference between weekday and weekend traffic
    to approximate the number of commuters coming through the station.

    Args:
        df (DataFrame): A DataFrame for which the difference should be calculated
    Returns:
        A New Dataframe with the entry and exit differences
    """
    daily_entries = df.loc[df["WEEK"] == week].groupby(
        ["STATION", "WDAY", "LATITUDE", "LONGITUDE"]).sum().reset_index().sort_values(
        ["STATION", "WDAY"], ascending=False)

    daily_entries["WEEKEND"] = daily_entries["WDAY"] > 4

    average_daily_week_v_weekend_entries = daily_entries.groupby(
        ["STATION", "WEEKEND", "LATITUDE", "LONGITUDE"]).mean().reset_index().drop(
        ["WDAY", "index", "WEEK", "HOUR"], axis=1)

    average_daily_week_v_weekend_entries["Entry_diffs"] = average_daily_week_v_weekend_entries.groupby(
        ["STATION", "LATITUDE", "LONGITUDE"]).diff(periods=-1)["ENTRIES"]
    average_daily_week_v_weekend_entries["Exit_diffs"] = average_daily_week_v_weekend_entries.groupby(
        ["STATION", "LATITUDE", "LONGITUDE"]).diff(periods=-1)["EXITS"]

    average_daily_week_v_weekend_entries = average_daily_week_v_weekend_entries.dropna(how='any')
    average_daily_week_v_weekend_entries = average_daily_week_v_weekend_entries.drop(["ENTRIES",
                                                                                      "WEEKEND", "EXITS"], axis=1)

    return average_daily_week_v_weekend_entries