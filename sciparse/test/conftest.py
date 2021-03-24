import pytest
import pint

@pytest.fixture(scope='session')
def ureg():
    ureg = pint.UnitRegistry()
    pint.set_application_registry(ureg)
    return ureg
