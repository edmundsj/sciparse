import pytest
import pint

@pytest.fixture(scope='session')
def ureg():
    ureg = pint.UnitRegistry()
    return ureg
