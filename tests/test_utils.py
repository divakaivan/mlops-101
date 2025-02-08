import pandas as pd

from utils import outlier_imputer, rush_hourizer


def test_outlier_imputer_with_positive_outliers():
    """Test outlier_imputer function with positive outliers"""
    data = {
        "column1": [1, 5, 7, 100, 2000],
        "column2": [5, 25, 35, 50, 2000],
    }
    df = pd.DataFrame(data)
    column_list = ["column1", "column2"]
    iqr_factor = 1

    df_imputed = outlier_imputer(df, column_list, iqr_factor)

    assert df_imputed["column1"][3] == 100  # should be replaced by the upper threshold 195
    assert df_imputed["column1"][4] == 195  # should be replaced by the upper threshold 195
    assert df_imputed["column2"][4] == 75  # should be replaced by the upper threshold 75


def test_outlier_imputer_with_negative_values():
    """Test outlier_imputer function with negative values"""
    data = {
        "column1": [-10, -5, 0, 5, 10],
        "column2": [0, -2, -5, -10, -15],
    }
    df = pd.DataFrame(data)
    column_list = ["column1", "column2"]
    iqr_factor = 6

    df_imputed = outlier_imputer(df, column_list, iqr_factor)

    assert df_imputed["column1"][0] == 0
    assert df_imputed["column2"][1] == 0


def test_outlier_imputer_with_empty_column_list():
    """Test outlier_imputer function with an empty column list"""
    data = {
        "column1": [10, 15, 20, 100, 200],
        "column2": [5, 25, 35, 50, 200],
    }
    df = pd.DataFrame(data)
    column_list = []
    iqr_factor = 6

    df_imputed = outlier_imputer(df, column_list, iqr_factor)

    assert df.equals(df_imputed)


def test_rush_hourizer_for_rush_hour():
    """Test rush_hourizer function for rush hours"""
    data = {"rush_hour": [7, 8, 17, 19]}
    df = pd.DataFrame(data)

    assert rush_hourizer(df.iloc[0]) == 1  # 7 is a rush hour, etc
    assert rush_hourizer(df.iloc[1]) == 1
    assert rush_hourizer(df.iloc[2]) == 1
    assert rush_hourizer(df.iloc[3]) == 1


def test_rush_hourizer_for_non_rush_hour():
    """Test rush_hourizer function for non-rush hours"""
    data = {"rush_hour": [5, 10, 15, 21]}
    df = pd.DataFrame(data)

    assert rush_hourizer(df.iloc[0]) == 0  # 5 is not a rush hour, etc
    assert rush_hourizer(df.iloc[1]) == 0
    assert rush_hourizer(df.iloc[2]) == 0
    assert rush_hourizer(df.iloc[3]) == 0
