"""
Generic object for testing for data quality issues.

Tester class contains list of tests to run on data. Tests contain a variable name, a condition, and a severity
"""

from enum import Enum, auto
import pandas as pd
import numpy as np
import yaml


class Condition(Enum):

    less_than = "lt"
    greater_than = "gt"
    data_type = "dtype"
    no_missing = "no_nan"
    count_missing = "count_nan"


class Severity(Enum):

    debug = auto()
    info = auto()
    warning = auto()
    error = auto()



class Test:

    def __init__(self, variable, condition, severity, val=None, name=None):
        self.variable = variable
        self.condition = condition
        self.val = val
        """
        Value to compare against, can be excluded for a ``no_missing`` check
        """
        self.severity = severity
        self.name = name

        if not name:
            self.name = self.variable + "_" + self.condition.value
            if self.val:
                self.name += "_" + str(self.val)


    def check(self, df: pd.DataFrame):
        """
        Check variable of input dataframe to see if it meets conditions
        :param df: Pandas data frame
        :return: boolean of if the data passed the test
        """

        message = None
        result = None

        if self.condition == Condition.count_missing:
            count = sum(np.isnan(df[self.variable]))
            result = count < self.val
            if not result:
                message = self.name+ ":" + self.severity.name + ": " + str(count) + \
                          " missing values observed for " + self.variable
        else:
            if self.condition == Condition.less_than:
                result = (df[self.variable] < self.val).all()
            elif self.condition == Condition.greater_than:
                result = (df[self.variable] > self.val).all()
            elif self.condition == Condition.data_type:
                result = type(df.loc[0, self.variable]).__name__ == self.val
            elif self.condition == Condition.no_missing:
                result = not np.isnan(df[self.variable]).any()

            if not result:
                message = self.name + ":" + self.severity.name + ": check failed"

        if message:
            print(message)
        return result


class Tester:

    def __init__(self, name, yaml_file=None):
        self.name = name
        self.tests = []

    def add(self, t: Test):
        self.tests.append(t)

    def load_yaml(self, yaml_file):
        with open(yaml_file) as f:
            test_list = yaml.load(f, Loader=yaml.FullLoader)

        for item in test_list:
            item['condition'] = Condition[item['condition']]
            item['severity'] = Severity[item['severity']]
            self.add(Test(**item))

    def check(self, df: pd.DataFrame):

        for t in self.tests:
            t.check(df)


