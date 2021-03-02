# Code for wrapping the various interpolation functions
from .interpolate_ma import interpolate_ma
import pandas as pd

IMPLEMENTED_METHODS = ['ma']


def interpolate(data: pd.DataFrame, interpolate_vars: list, method: str, tvar: str, by_var: str, ma_num: int = 4):
    """
    General function for calling interpolation. Will be updated as additional interpolation
    methods are developed

    :param data: A pandas data frame, containing geospatial data with missingness included
    :param interpolate_vars: list of variable names to interpolate
    :param method: A string containing the interpolation method to use. Valid vales:
        - "ma": moving average method, see ``interpolate_ma``
    :param tvar: variable containing the time dimension
    :param by_var: single variable uniquely identifying each spatial division. If this information is contained
        in more than one variable in the intitial data, a separate ID column should be created.
    :param ma_num: Only used when method = "ma". The default size f the moving average window to use. Defaults to 3.
    :return: None, replaces missing values in the data frame in place
    """

    assert method in IMPLEMENTED_METHODS

    if method == "ma":
        data.sort_values(by=[tvar, by_var], inplace=True)
        id_vals = data[by_var].unique()

        for data_var in interpolate_vars:
            print("Interpolating", data_var)
            for id_val in id_vals:
                data.loc[data[by_var] == id_val, data_var] = interpolate_ma(data[data[by_var] == id_val][data_var],
                                                                            ma_num)

