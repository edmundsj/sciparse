from numpy.testing import assert_equal, assert_allclose
from sciparse import find_lcr_dataline, parse_lcr_header, parse_lcr
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
