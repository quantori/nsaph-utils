import unittest
from nsaph_utils.qc.tester import Tester, Test, Condition
import pandas as pd
import numpy as np

class QCTests(unittest.TestCase):

    def test_tests(self):
        df = pd.DataFrame({"x": [a for a in range(100)],
                                "y": ["a" for a in range(100, 0, -1)],
                                "z": [np.nan for a in range(100)],
                                "w": [1 for a in range(100)]})
        tester = Tester("test", yaml_file="test_data/test_list.yml")
        self.assertFalse(tester.check(df))

        df = pd.DataFrame({"x": [70 for a in range(100)],
                           "y": ["a" for a in range(100, 0, -1)],
                           "z": [np.nan for a in range(100)],
                           "w": [1 for a in range(100)]})
        self.assertFalse(tester.check(df))


if __name__ == '__main__':
    unittest.main()
