from numpy.testing import assert_equal, assert_allclose
from pandas.testing import assert_frame_equal
import numpy as np
import pandas as pd
from sciparse import find_lcr_dataline, parse_lcr_header, parse_lcr
from sciparse import convert_lcr_to_standard
import pytest
import os

@pytest.fixture
def filename():
    dir_name = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(dir_name, 'data/lcr_test_data.dat')
    filename = str(filename)
    return filename

@pytest.fixture
def metadata(filename):
    metadata = parse_lcr_header(filename)
    return metadata

@pytest.fixture
def data(filename):
    data, metadata = parse_lcr(filename)
    return data

def test_extract_header(metadata):
    desiredMode = "SWEEP"
    actualMode = metadata['mode']
    assert_equal(actualMode, desiredMode)

    desiredStartVoltage = 10
    actualStartVoltage = metadata['start_voltage']
    assert_equal(actualStartVoltage, desiredStartVoltage, err_msg="stop voltage")

    desiredStopVoltage = -20
    actualStopVoltage = metadata['stop_voltage']
    assert_equal(actualStopVoltage, desiredStopVoltage, err_msg="start voltage")

    desiredStepVoltage = -0.25
    actualStepVoltage = metadata['step_voltage']
    assert_equal(actualStepVoltage, desiredStepVoltage, err_msg="step voltage")

    desiredPoints = 121
    actualPoints = metadata['n_samples']
    assert_equal(actualPoints, desiredPoints, err_msg="number points")

def test_find_datalines(filename):
    desiredStartLine = 28
    actualStartLine = find_lcr_dataline(filename)
    assert_equal(actualStartLine, desiredStartLine)

def test_parse_data_header(data):
    # Confirm we got the right data types
    actualDataTypes = data.columns.values
    desiredDataTypes = ['Z', 'THETA', 'BIAS', 'VM', 'IM']
    assert_equal(actualDataTypes, desiredDataTypes)

def test_parse_data_length(data):
    # Confirm we got the right length of data
    desired_data_points = 121
    actual_data_points = len(data)
    assert_equal(actual_data_points, desired_data_points)

def test_parse_data(data):
    desiredZData = 5.57723*1e6
    actualZData = data['Z'].iloc[1]
    assert_allclose(desiredZData, actualZData)

    desiredBIASData = 8.5
    actualBIASData = data['BIAS'].iloc[6]
    assert_allclose(desiredBIASData, actualBIASData)

def test_convert_data_CP_RP():
    frequency = 1 / (2*np.pi) * 1000 # 1krad/s
    test_metadata = {'frequency': frequency}
    test_data = pd.DataFrame({'CP': [1e-9], 'RP': 1e6})
    desired_data = pd.DataFrame({
            'Z (ohm)': [1 / np.sqrt(2) * 1e6],
            'THETA (rad)': [-np.pi/4]})
    actual_data = convert_lcr_to_standard(test_data, test_metadata)
    assert_frame_equal(actual_data, desired_data)

def test_convert_data_CS_RS():
    frequency = 1 / (2*np.pi) * 1000 # 1krad/s
    test_metadata = {'frequency': frequency}
    test_data = pd.DataFrame({'CS': [1e-9], 'RS': 1e6})
    desired_data = pd.DataFrame({
            'Z (ohm)': [np.sqrt(2) * 1e6],
            'THETA (rad)': [-np.pi/4]})
    actual_data = convert_lcr_to_standard(test_data, test_metadata)
    assert_frame_equal(actual_data, desired_data)

def test_convert_data_C_Q():
    frequency = 1 / (2*np.pi) * 1000 # 1krad/s
    test_metadata = {'frequency': frequency}
    test_data = pd.DataFrame({'C': [1e-9], 'Q': 1})
    desired_data = pd.DataFrame({
            'Z (ohm)': [1 / np.sqrt(2) * 1e6],
            'THETA (rad)': [-np.pi/4]})
    actual_data = convert_lcr_to_standard(test_data, test_metadata)
    assert_frame_equal(actual_data, desired_data)

def test_convert_data_C_D():
    frequency = 1 / (2*np.pi) * 1000 # 1krad/s
    test_metadata = {'frequency': frequency}
    test_data = pd.DataFrame({'C': [1e-9], 'D': 1})
    desired_data = pd.DataFrame({
            'Z (ohm)': [1 / np.sqrt(2) * 1e6],
            'THETA (rad)': [-np.pi/4]})
    actual_data = convert_lcr_to_standard(test_data, test_metadata)
    assert_frame_equal(actual_data, desired_data)

def test_convert_raises_no_frequency():
    with pytest.raises(ValueError):
        test_data = pd.DataFrame({'C': [1e-9], 'D': 1})
        test_metadata = {}
        actual_data = convert_lcr_to_standard(test_data, test_metadata)

def test_convert_raises_wrong_model():
    with pytest.raises(ValueError):
        test_data = pd.DataFrame({'CCC': [1e-9], 'D': 1})
        test_metadata = {}
        actual_data = convert_lcr_to_standard(test_data, test_metadata)

