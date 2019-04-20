"""Tests for `expat_fatcat` package."""

import pytest
from datetime import datetime

import expat_fatcat
from expat_fatcat.expat_fatcat import AbsRateConverter

@pytest.fixture
def dummy_rate_converter():
    class DummyRateConverter(AbsRateConverter):

        def __init__(self, to_currency):
            self.to_currency = to_currency


        def _get_call_str(self, from_currency):
            if from_currency == 'FOO':
                return 'ECB/FOO' + self.to_currency
            else:
                raise NotImplementedError('Only FOO to {} rates are implemented'.format(self.to_currency))
        

        def _dummy_api_call(self, call_str):
            return 1.125


        def get_rate(self, from_currency, date):
            '''Returns dummy exchange rate'''
            call_str = self._get_call_str(from_currency)
            return self._dummy_api_call(call_str)
        
    return DummyRateConverter


@pytest.fixture
def calculator_foo(dummy_rate_converter):
    return expat_fatcat.FatcatCalculator(dummy_rate_converter)


def test_date_conversion(calculator_foo):
    assert calculator_foo._parse_date('2019-04-18') == datetime(2019, 4, 18)
    

def test_get_rate(calculator_foo):
    rate = calculator_foo._get_rate('FOO', '2019-04-18')
    assert rate == 1.125