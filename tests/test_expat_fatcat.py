"""Tests for `expat_fatcat` package."""

import pytest
from datetime import datetime

import expat_fatcat

@pytest.fixture
def dummy_rate_converter():
    class DummyConverter(expat_fatcat.RateConverter):

        def __init__(self, currency):
            pass

        def _set_call(self):
            if self.currency == 'FOO':
                self.call_str = 'FOO/BAR'
            else:
                raise NotImplementedError('Only FOO to USD rates are implemented')


        def get_rate(self, date, target_currency, original_currency):
            '''Returns dummy exchange rate'''

            return 1.125
    return DummyConverter


@pytest.fixture
def converter_foo(dummy_rate_converter):
    return expat_fatcat.FatcatConverter('FOO', dummy_rate_converter)

def test_date_conversion(converter_foo):
    assert converter_foo._parse_date('2019-04-18') == datetime(2019, 4, 18)
    

def test_get_rate(converter_foo):
    rate = converter_foo._get_rate2usd('2019-04-18')
    assert rate == 1.125