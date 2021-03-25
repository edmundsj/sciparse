import pint
from numpy.testing import assert_equal, assert_allclose
import numpy as np
import warnings

def assert_equal_qt(actual_data, desired_data):
    if isinstance(actual_data, np.ndarray):
        assert_equal(actual_data, desired_data)
    elif isinstance(actual_data, pint.Quantity) or \
            isinstance(desired_data, pint.Quantity):
        assert_equal(isinstance(actual_data, pint.Quantity), True)
        assert_equal(isinstance(desired_data, pint.Quantity), True)
        assert_equal(actual_data.magnitude, desired_data.magnitude)
        assert actual_data.units == desired_data.units

def assert_allclose_qt(
        actual_data, desired_data, atol=1e-15, rtol=1e-14):
    if isinstance(actual_data, np.ndarray):
        assert_allclose(
                actual_data, desired_data, atol=atol, rtol=rtol)
    elif isinstance(actual_data, pint.Quantity) or \
            isinstance(desired_data, pint.Quantity):
        assert_equal(isinstance(actual_data, pint.Quantity), True)
        assert_equal(isinstance(desired_data, pint.Quantity), True)
        assert_allclose(
                actual_data.magnitude, desired_data.magnitude,
                atol=atol, rtol=rtol)
        assert actual_data.units == desired_data.units
