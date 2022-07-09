import pint
from numpy.testing import assert_equal, assert_allclose
import numpy as np
from pandas.testing import assert_frame_equal
from pandas import DataFrame
import warnings
from itertools import zip_longest

def assert_equal_qt(actual_data, desired_data, atol=1e-6, rtol=1e-6):
    if isinstance(actual_data, np.ndarray):
        assert_equal(actual_data, desired_data)
    elif isinstance(actual_data, pint.Quantity) or \
            isinstance(desired_data, pint.Quantity):
        assert_equal(isinstance(actual_data, pint.Quantity), True)
        assert_equal(isinstance(desired_data, pint.Quantity), True)
        assert_equal(actual_data.to(desired_data.units).magnitude, \
                desired_data.magnitude)
        assert actual_data.to(desired_data.units).units == desired_data.units

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

def assertDataDictEqual(data_dict_actual, data_dict_desired):
# Check that they have the exact same set of keys
    assert_equal(type(data_dict_actual), dict)
    assert_equal(type(data_dict_desired), dict)
    actual_keys = set(data_dict_actual.keys())
    desired_keys = set(data_dict_desired.keys())
    assert_equal(actual_keys, desired_keys)

    for actual_key, actual_val in data_dict_actual.items():
        desired_val = data_dict_desired[actual_key]
        if isinstance(actual_val, DataFrame):
            assert_frame_equal(actual_val, desired_val)
        elif isinstance(actual_val, dict):
            assertDataDictEqual(actual_val, desired_val)
        else:
            assert_equal_qt(actual_val, desired_val)
