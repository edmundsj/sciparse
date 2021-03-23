import pint
from numpy.testing import assert_equal
import numpy as np
import warnings

def assert_equal_qt(actual_data, desired_data):
    if isinstance(actual_data, np.ndarray):
        assert_equal(actual_data, desired_data)
    elif isinstance(actual_data, pint.Quantity) or \
            isinstance(desired_data, pint.Quantity):
        assert_equal(isinstance(actual_data, pint.Quantity), True)
        assert_equal(isinstance(desired_data, pint.Quantity), True)
        with warnings.catch_warnings(record=True):
            assert_equal(np.array(actual_data), np.array(desired_data))
        assert actual_data.units == desired_data.units
