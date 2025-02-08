import pandas as pd


def outlier_imputer(
    df: pd.DataFrame, column_list: list[str], iqr_factor: int
) -> pd.DataFrame:
    """
    Impute upper-limit values in specified columns based on their interquartile range.
    The IQR is computed for each column in column_list and values exceeding
    the upper threshold for each column are imputed with the upper threshold value.

    Args:
        df (pd.DataFrame): Dataframe to be cleaned
        column_list (list[int]): A list of columns to iterate over
        iqr_factor (int): A number representing x in the formula:
                    Q3 + (x * IQR). Used to determine maximum threshold,
                    beyond which a point is considered an outlier.
    """
    for col in column_list:
        df.loc[df[col] < 0, col] = 0

        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        upper_threshold = q3 + (iqr_factor * iqr)

        df.loc[df[col] > upper_threshold, col] = upper_threshold

        return df


def rush_hourizer(row: pd.Series) -> int:
    """
    Determine if a given hour is a rush hour.
    Args:
        row (pd.Series): A row from the DataFrame.

    Returns:
        int: 1 if the hour is a rush hour, 0 otherwise.
    """
    hour = row["rush_hour"]
    if 6 <= hour < 10 or 16 <= hour < 20:
        return int(1)
    return int(0)
