import pytest
import numpy as np
import pandas as pd
from numpy.testing import assert_equal, assert_allclose
from sciparse import sampling_period, title_to_quantity, \
         to_standard_quantity, frequency_bin_size, quantity_to_title, \
         dict_to_string, string_to_dict, is_scalar, column_from_unit, \
         cname_from_unit, assertDataDictEqual
from sciparse import assert_allclose_qt, assert_equal_qt, ureg

def test_sampling_period():
    data = pd.DataFrame({'Time (ms)': [0, 0.1, 0.2, 0.3, 0.4],
                         'Values': [0, 1, 2, 3, 4]})
    actual_period = sampling_period(data)
    desired_period = ureg.ms * 0.1
    assert actual_period == desired_period

def test_sampling_period_error():
    data = pd.DataFrame({'Time (ms)': [0],
                         'Values': [0]})
    with pytest.raises(ValueError):
        actual_period = sampling_period(data)

def test_frequency_bin_error():
    data = pd.DataFrame({'frequency (Hz)': [0],
                         'Values': [0]})
    with pytest.raises(ValueError):
        actual_bin = frequency_bin_size(data)

def test_quantity_to_title():
    quantity = ureg.mV*1.0
    desired_title = 'voltage (mV)'
    actual_title = quantity_to_title(quantity)
    assert_equal(actual_title, desired_title)

    quantity = ureg.nA**2*1.0
    desired_title = 'power (nA ** 2)'
    actual_title = quantity_to_title(quantity)
    assert_equal(actual_title, desired_title)

def test_quantity_to_title_with_name():
    quantity = ureg.mV * 1.0
    desired_name = 'photovoltage'
    desired_title = 'photovoltage (mV)'
    actual_title = quantity_to_title(quantity, desired_name)
    assert_equal(actual_title, desired_title)

def testExtractTimeUnits():
    unit_string = 'time (s)'
    desired_unit = 1 * ureg.s
    actual_unit = title_to_quantity(unit_string)
    assert desired_unit == actual_unit

    unit_string = 'time (ms)'
    desired_unit = 1 * ureg.ms
    actual_unit = title_to_quantity(unit_string)
    assert desired_unit == actual_unit

    unit_string = 'time (us)'
    desired_unit = 1 * ureg.us
    actual_unit = title_to_quantity(unit_string)
    assert desired_unit == actual_unit

    unit_string = 'time (ns)'
    desired_unit = 1 * ureg.ns
    actual_unit = title_to_quantity(unit_string)
    assert desired_unit == actual_unit

    unit_string = 'time (ps)'
    desired_unit = 1 * ureg.ps
    actual_unit = title_to_quantity(unit_string)
    assert desired_unit == actual_unit

def testExtractElectricalUnits(ureg):
    unit_string = 'Photocurrent (pA)'
    desired_unit = 1 * ureg.pA
    actual_unit = title_to_quantity(unit_string)
    assert desired_unit == actual_unit

    unit_string = 'Photocurrent (nA)'
    desired_unit = 1 * ureg.nA
    actual_unit = title_to_quantity(unit_string)
    assert desired_unit == actual_unit

    unit_string = 'current (uA)'
    desired_unit = 1 * ureg.uA
    actual_unit = title_to_quantity(unit_string)
    assert desired_unit == actual_unit

    unit_string = 'Jordans (mA)'
    desired_unit = 1 * ureg.mA
    actual_unit = title_to_quantity(unit_string)
    assert desired_unit == actual_unit

    unit_string = 'More Current (A)'
    desired_unit = 1 * ureg.A
    actual_unit = title_to_quantity(unit_string)
    assert desired_unit == actual_unit

    unit_string = 'Photovoltage (V)'
    desired_unit = 1 * ureg.V
    actual_unit = title_to_quantity(unit_string)
    assert desired_unit == actual_unit

    unit_string = 'Photovoltage (mV)'
    desired_unit = 1 * ureg.mV
    actual_unit = title_to_quantity(unit_string)
    assert desired_unit == actual_unit

    unit_string = 'Photovoltage (uV)'
    desired_unit = 1 * ureg.uV
    actual_unit = title_to_quantity(unit_string)
    assert desired_unit == actual_unit

    unit_string = 'Photovoltage (nV)'
    desired_unit = 1 * ureg.nV
    actual_unit = title_to_quantity(unit_string)
    assert desired_unit == actual_unit

def testExtractSquaredUnits():
    unit_string = 'voltage (mV^2)'
    desired_unit = 1 * ureg.mV ** 2
    actual_unit = title_to_quantity(unit_string)
    assert desired_unit == actual_unit

def test_title_to_quantity_squared_2():
    unit_string = 'voltage (mV ** 2)'
    desired_unit = 1 * ureg.mV ** 2
    actual_unit = title_to_quantity(unit_string)
    assert desired_unit == actual_unit

def test_title_to_quantity_name():
    unit_string = 'photovoltage (kV)'
    desired_name = 'photovoltage'
    desired_quantity = 1 * ureg.kV
    actual_quantity, actual_name = title_to_quantity(
            unit_string, return_name=True)
    assert_equal_qt(actual_quantity, desired_quantity)
    assert_equal(actual_name, desired_name)

def testToStandardUnit():
    quantity = 0.1 * ureg.mV
    desired_quantity = 0.1 * 1e-3 * ureg.V
    actual_quantity = to_standard_quantity(quantity)
    assert desired_quantity == actual_quantity

def test_to_standard_quantity_squared():
    quantity = 0.1 * ureg.mV ** 2
    desired_quantity = 0.1 * 1e-6 * ureg.V ** 2
    actual_quantity = to_standard_quantity(quantity)
    assert desired_quantity == actual_quantity

def test_to_standard_quantity_psd():
    quantity = 0.1 * ureg.mA ** 2 / ureg.Hz
    desired_quantity = 0.1 * 1e-6 * ureg.A ** 2 / ureg.Hz
    actual_quantity = to_standard_quantity(quantity)
    assert desired_quantity == actual_quantity

def test_frequency_bin_size():
    psd_data = pd.DataFrame({
            'frequency (Hz)': [1.5, 3.0, 4.5],
            'power (V^2)': [0, 1, 2]})
    actual_quantity = frequency_bin_size(psd_data)
    desired_quantity = 1*ureg.Hz*1.5
    assert actual_quantity == desired_quantity

def test_dict_to_string():
    metadata = {
        'wavelength': 10 * ureg.nm,
        'material': 'Al',
        'replicate': 2}

    actual_string = dict_to_string(metadata)
    desired_dict = {
        'wavelength (nm)': 10,
        'material': 'Al',
        'replicate': 2}
    assert_equal(actual_string, str(desired_dict))

def test_string_to_dict():
    input_string = "{'wavelength (nm)': 10, 'material': 'Al', 'replicate': 2}"
    desired_dict = {
        'wavelength': 10*ureg.nm,
        'material': 'Al',
        'replicate': 2}
    actual_dict = string_to_dict(input_string)
    assertDataDictEqual(actual_dict, desired_dict)

def test_is_scalar():
    quantity = 5 * ureg.Hz
    data_scalar_actual = is_scalar(quantity)
    data_scalar_desired = True
    assert_equal(data_scalar_actual, data_scalar_desired)

    quantity = 6.0 * ureg.Hz
    data_scalar_actual = is_scalar(quantity)
    data_scalar_desired = True
    assert_equal(data_scalar_actual, data_scalar_desired)

    quantity = 6.0
    data_scalar_actual = is_scalar(quantity)
    data_scalar_desired = True
    assert_equal(data_scalar_actual, data_scalar_desired)

    quantity = np.array([6.0, 2.5]) * ureg.Hz
    data_scalar_actual = is_scalar(quantity)
    data_scalar_desired = False
    assert_equal(data_scalar_actual, data_scalar_desired)

def test_column_from_unit():
    input_data = pd.DataFrame({
        'Time (ms)': [0, 1, 2, 3],
        'Photovoltage (nV)': [0, 1, 4, 5]})
    desired_data = ureg.uV * 1e-3 * np.array([0., 1, 4, 5])
    actual_data = column_from_unit(input_data, ureg.uV)
    assert_allclose_qt(actual_data, desired_data, atol=1e-12)

    desired_data = ureg.s * 1e-3 * np.array([0, 1, 2, 3])
    actual_data = column_from_unit(input_data, ureg.s)
    assert_allclose_qt(actual_data, desired_data, atol=1e-12)

def test_column_from_unit_extra():
    input_data = pd.DataFrame({
        'Time': [0, 1, 2, 3],
        'Photovoltage (nV)': [0, 1, 4, 5],
        'Sync': [0, 0, 2, 1]
        })
    desired_data = ureg.uV * 1e-3 * np.array([0., 1, 4, 5])
    actual_data = column_from_unit(input_data, ureg.uV)
    assert_allclose_qt(actual_data, desired_data, atol=1e-12)

def test_column_not_found():
    input_data = pd.DataFrame({})
    with pytest.raises(ValueError):
        column_from_unit(input_data, ureg.ms)

def test_cname_from_unit():
    input_data = pd.DataFrame({
        'Time': [0, 1, 2, 3],
        'Photovoltage (nV)': [0, 1, 4, 5],
        'Sync': [0, 0, 2, 1]
        })
    desired_name = 'Photovoltage (nV)'
    actual_name = cname_from_unit(input_data, ureg.V)
    assert_equal(actual_name, desired_name)
