"""Tests for `expat_fatcat` package."""

import pytest
from datetime import datetime

import expat_fatcat
from expat_fatcat.expat_fatcat import DummyRateConverter

@pytest.fixture
def dummy_rate_converter():
    return DummyRateConverter('USD')


@pytest.fixture
def dummy_calculator(dummy_rate_converter):
    return expat_fatcat.FatcatCalculator(dummy_rate_converter)


def test_date_conversion(dummy_calculator):
    assert dummy_calculator._parse_date('2019-04-18') == datetime(2019, 4, 18)
    

def test_get_rate(dummy_calculator):
    rate = dummy_calculator.get_rate('FOO', '2019-04-18')
    assert rate == 1.125