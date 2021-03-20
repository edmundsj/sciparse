import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from numpy.testing import assert_equal
from sciparse import parse_xrd
import os

@pytest.fixture
def xrd_filename():
    file_location = os.path.dirname(os.path.abspath(__file__))
    filename = file_location + '/data/TEST1~1~type-locked_coupled~peak-Si.txt'
    yield filename

def test_load_xrd_data(xrd_filename):
    data_desired = pd.DataFrame({
        'Angle (deg)': [69.05, 69.055, 69.06, 69.065, 69.07,69.075,69.08,
        69.085, 69.09, 69.095, 69.1, 69.105, 69.11, 69.115],
        'Counts': [24, 30, 28, 40, 132, 272, 3472, 16368,21970,10562,
                   1210,264,130,64]})
    data_actual, _ = parse_xrd(xrd_filename)
    assert_frame_equal(data_actual, data_desired)

def test_load_xrd_metadata(xrd_filename):
    metadata_desired = {
        'date': '02/10/2021',
        'increment': 0.005, 'scantype': 'locked coupled',
        'start': 69.05, 'steps': 14, 'time': 1,
        'theta': 34.0, '2theta': 68.0, 'phi': 180.13, 'chi': -0.972}
    _, metadata_actual = parse_xrd(xrd_filename)
    assert_equal(metadata_actual, metadata_desired)
