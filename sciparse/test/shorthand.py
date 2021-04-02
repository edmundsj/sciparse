import pint
from numpy.testing import assert_equal, assert_allclose
import numpy as np
from pandas.testing import assert_frame_equal
from pandas import DataFrame
import warnings
from itertools import zip_longest

def assert_equal_qt(actual_data, desired_data):
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
    assert_equal(type(data_dict_actual), dict)
    assert_equal(type(data_dict_desired), dict)
    for actual_name, desired_name in \
        zip_longest(data_dict_actual.keys(),
                    data_dict_desired.keys()):
        assert_equal(actual_name, desired_name)

    for actual_data, desired_data in \
         zip_longest(data_dict_actual.values(),
                     data_dict_desired.values()):
        if isinstance(actual_data, DataFrame):
            assert_frame_equal(actual_data, desired_data)
        elif isinstance(actual_data, dict):
            assertDataDictEqual(actual_data, desired_data)
        else:
            assert_equal_qt(actual_data, desired_data)
