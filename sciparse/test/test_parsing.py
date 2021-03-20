import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from numpy.testing import assert_equal
from sciparse import parse_xrd, parse_default
import os

@pytest.fixture
def test_dir():
    file_location = os.path.dirname(os.path.abspath(__file__))
    location = file_location + '/data/'
    yield location
    filename = location + 'TEST1~wavelengths-1~temperatures-25.csv'
    try:
        os.remove(filename)
    except:
        print("default file not found. That's OK, we're creating it on the fly")

def test_load_xrd_data(test_dir):
    xrd_filename = test_dir + 'TEST1~1~type-locked_coupled~peak-Si.txt'
    data_desired = pd.DataFrame({
        'Angle (deg)': [69.05, 69.055, 69.06, 69.065, 69.07,69.075,69.08,
        69.085, 69.09, 69.095, 69.1, 69.105, 69.11, 69.115],
        'Counts': [24, 30, 28, 40, 132, 272, 3472, 16368,21970,10562,
                   1210,264,130,64]})
    data_actual, _ = parse_xrd(xrd_filename)
    assert_frame_equal(data_actual, data_desired)

def test_load_xrd_metadata(test_dir):
    xrd_filename = test_dir + 'TEST1~1~type-locked_coupled~peak-Si.txt'
    metadata_desired = {
        'date': '02/10/2021',
        'increment': 0.005, 'scantype': 'locked coupled',
        'start': 69.05, 'steps': 14, 'time': 1,
        'theta': 34.0, '2theta': 68.0, 'phi': 180.13, 'chi': -0.972}
    _, metadata_actual = parse_xrd(xrd_filename)
    assert_equal(metadata_actual, metadata_desired)

def test_load_metadata_default(test_dir):
    """
    Tests that we can load metadata from a file successfully
    """
    filename = test_dir + 'TEST1~wavelengths-1~temperatures-25.csv'
    with open(filename, 'w+') as fh:
        fh.write('{"frequency": 8500}\n')
        fh.write(f'Time, Data\n')
        fh.write(f'1, 2\n')

    _, metadata_actual = parse_default(filename)
    metadata_desired = {'frequency': 8500}
    assert_equal(metadata_actual, metadata_desired)

def test_load_data(test_dir):
    data_desired = pd.DataFrame({'wavelengths': [1, 2, 3],
                             'Mean': [1,2,4]})
    filename = test_dir + 'TEST1~wavelengths-1~temperatures-25.csv'
    metadata_desired = {'frequency': 8500}
    with open(filename, 'w+') as fh:
        fh.write(str(metadata_desired) + '\n')
        data_desired.to_csv(fh, mode='a', index=False)

    data_actual, _ = parse_default(filename)
    assert_frame_equal(data_actual, data_desired)

