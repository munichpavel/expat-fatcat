"""Tests for `expat_fatcat` package."""

import pytest
from datetime import datetime

import expat_fatcat
from expat_fatcat.expat_fatcat import DummyRateConverter

@pytest.fixture
def dummy_rate_converter():
    return DummyRateConverter('USD')


@pytest.fixture
def calculator_foo(dummy_rate_converter):
    return expat_fatcat.FatcatCalculator(dummy_rate_converter)


def test_date_conversion(calculator_foo):
    assert calculator_foo._parse_date('2019-04-18') == datetime(2019, 4, 18)
    

def test_get_rate(calculator_foo):
    rate = calculator_foo.get_rate('FOO', '2019-04-18')
    assert rate == 1.125