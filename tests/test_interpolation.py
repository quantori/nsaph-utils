import unittest
import nsaph_utils
from nsaph_utils.interpolation.interpolate_ma import *



class InterpolationTest(unittest.TestCase):
    def test_ma_interpolation(self):
        array = np.array([1.0  + i for i in range(100)])
        array[10:20] = np.nan

        self.assertTrue((interpolate_ma(array[10:21], 1) == 21).all())


if __name__ == '__main__':
    unittest.main()
