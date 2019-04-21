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
    payments = [
        {'amount': 10., 'date': '2019-03-15'},
        {'amount': 5., 'date': '2019-04-15'}
    ]
    return expat_fatcat.FatcatCalculator(dummy_rate_converter, 'FOO', payments)

class TestCalculatorBasics:
    '''
    Tests for the main functionality of rate calculators.
    Excludes edge cases such as missing values, invalid arguments, etc.
    '''
    def test_date_conversion(self, dummy_calculator):
        assert dummy_calculator._parse_date('2019-04-18') == datetime(2019, 4, 18)


    def test_get_rate(self, dummy_calculator):
        rate = dummy_calculator._get_rate('2019-04-18')
        assert rate == 1.125


    def test_get_converted_amount(self, dummy_calculator):
        amount = 10.
        assert dummy_calculator._get_converted_amount(amount, '2019-04-18') == 11.25


    def test_calculate_agg_payment(self, dummy_calculator):
        agg_payment = dummy_calculator()
        assert agg_payment == 16.875