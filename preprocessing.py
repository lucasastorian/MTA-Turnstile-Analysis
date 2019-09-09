import numpy as np
import pandas as pd


def cleanse_data(df):
    """ Cleans the MTA Dataset and create some elementary features

    Args:
        df: A DataFrame with correctly formatted MTA Data

    Returns:
        A DataFrame with cleansed MTA Data
    """

    # Strip leading and trailing spaces for Headers and all alphanumeric entries
    df.columns = df.columns.str.strip()
    df = strip_spaces(df)

    # check that column names are correct
    check_column_names(df.columns)

    # Create DateTime Column
    df["DATETIME"] = pd.to_datetime((df["DATE"] + ' ' + df["TIME"]), format="%m/%d/%Y %H:%M:%S")

    # Create a Unique Identifier for each Turnstile.
    df["TURNSTILE_ID"] = df["C/A"] + '_' + df["UNIT"] + '_' + df["SCP"] + '_' + df["STATION"]

    # Deaggregate Entries and Exits
    df.sort_values(["TURNSTILE_ID", "DATETIME"], inplace=True)
    df["entry_diffs"] = df["ENTRIES"].diff()
    df["exit_diffs"] = df["EXITS"].diff()
    mask = df.TURNSTILE_ID != df.TURNSTILE_ID.shift(1)
    df.loc[mask, 'entry_diffs'] = np.nan
    df.loc[mask, 'exit_diffs'] = np.nan

    # Drop first entry for cumalative entries
    df = df.dropna(how='any')

    # Drop the Cummalative entry and exit columns
    df = df.drop(columns=["ENTRIES", "EXITS"])

    # Rename the new columns to ENTRIES and EXITS
    df = df.rename(columns={"entry_diffs": "ENTRIES", "exit_diffs": "EXITS"})

    # Drop Remaining Anomalous Entries
    df = df.loc[df["ENTRIES"] < 3000]
    df = df.loc[df["ENTRIES"] > 0]
    df = df.loc[df["EXITS"] < 3000]
    df = df.loc[df["ENTRIES"] > 0]

    # Create a Weekday Column
    days_of_the_week = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday"
    }

    df["WDAY"] = df["DATETIME"].apply(lambda x: x.weekday())
    df["WEEKDAY"] = df["WDAY"].map(days_of_the_week)

    # Create a Week Column
    df["WEEK"] = df["DATETIME"].apply(lambda x: x.week)

    # Create an Hour column
    df["HOUR"] = df["DATETIME"].apply(lambda x: x.hour)

    df.ENTRIES = df.ENTRIES.astype(int)
    df.EXITS = df.EXITS.astype(int)

    station_coordinates = pd.read_csv("./datasets/station_coordinates.csv")

    df = pd.merge(df, station_coordinates, on="STATION")

    return df


def strip_spaces(df):
    """Strips leading and trailing spaces for all columns of type `object`.

    Args:
        df (DataFrame): A DataFrame with alphanumeric columns.
    Returns:
        A DataFrame where leading and trailing spaces have been stripped.

    """
    if type(df) != pd.core.frame.DataFrame:
        assert TypeError('df must be a pandas DataFrame')
    if len(df.columns) == 0:
        assert ValueError('df cannot be an empty dataframe')

    for column in df.columns:
        if df[column].dtype == object:
            try:
                df[column] = df[column].str.strip()
            except:
                print('Could not strip leading and trailing spaces from: ', column)

    return df


def check_column_names(columns):
    """ Checks whether the column names match the MTA Column Names

    Args:
        columns: A list of column names
    Asserts:
        ValueError: If all columns are not equal to saved columns
    """

    correct_column_names = ['C/A', 'UNIT', 'SCP', 'STATION',
                            'LINENAME', 'DIVISION', 'DATE',
                            'TIME', 'DESC', 'ENTRIES', 'EXITS', ]

    if len(columns) != len(correct_column_names):
        assert ValueError('The DataFrame does not contain the correct number of columns.')
    if (columns != correct_column_names).any():
        assert ValueError('The columns are not correctly formatted MTA Data.')