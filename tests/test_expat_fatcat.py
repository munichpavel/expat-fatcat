"""Tests for `expat_fatcat` package."""
from io import StringIO
import pytest
from contextlib import contextmanager

import numpy as np
from datetime import datetime

import pandas as pd

import expat_fatcat
from expat_fatcat.expat_fatcat import DummyRateConverterTo



dates_rates_asym = [
    (datetime(2017, 2, 19), 2.2),
    (datetime(2017, 2, 20), np.nan),
    (datetime(2017, 2, 21), np.nan),
]
expected_asym = 2.2

dates_rates_sym = [
    (datetime(2017, 2, 18), 2.9),
    (datetime(2017, 2, 19), np.nan),
    (datetime(2017, 2, 20), np.nan),
    (datetime(2017, 2, 21), np.nan),
    (datetime(2017, 2, 22), 3.1),
]
expected_sym = 3.0

@contextmanager
def does_not_raise():
    yield

def nan_test_equals(x,y):
    if np.isnan(x) and np.isnan(y):
        return True
    else:
        return x == y


@pytest.mark.parametrize(
    'converter_input,rates_expected,from_currency,\
        date_input,error_expectation,lookup_rate_expected,rate_expected',
    [
        (
            DummyRateConverterTo('USD'), (None, 1.125), 'FOO',  
            datetime(2017, 2, 20), pytest.raises(TypeError), np.nan, 1.125
        ),
        (
            DummyRateConverterTo('USD', dates_rates_asym), dates_rates_asym, 'FOO', 
            datetime(2017, 2, 20), does_not_raise(), np.nan, expected_asym
        ),
        (
            DummyRateConverterTo('USD', dates_rates_sym), dates_rates_sym, 'FOO', 
            datetime(2017, 2, 20), does_not_raise(), np.nan, expected_sym
        )
    ]
)
class TestConverter:

    def test_rates_init(
        self, converter_input, rates_expected,
        from_currency, date_input, error_expectation,lookup_rate_expected, rate_expected
    ):
        assert converter_input._dates_rates == rates_expected
        with error_expectation:
            assert nan_test_equals(converter_input._lookup_rate(date_input), lookup_rate_expected)
        assert converter_input.get_rate(from_currency, date_input) == rate_expected

    
@pytest.fixture
def salary():
    return [
         {'date': '2017-01-20', 'amount': 1000},
         {'date': '2017-02-20', 'amount': 1500}
    ]


@pytest.fixture
def rate_converter():
    return DummyRateConverterTo('USD')


@pytest.fixture
def calculator(rate_converter):
    return expat_fatcat.FatcatCalculator(rate_converter)


class TestCalculator:
    '''
    Tests for the main functionality of rate calculators.
    Excludes edge cases such as missing values, invalid arguments, etc.
    '''    
        
    def test_date_conversion(self, calculator):
        assert calculator._parse_date('2019-04-18') == datetime(2019, 4, 18)


    def test_get_rate(self, calculator):
        rate = calculator._get_rate('FOO', '2019-04-18')
        assert rate == 1.125


    def test_get_converted_amount(self, calculator):
        amount = 10.
        assert calculator._get_converted_amount('FOO', amount, '2019-04-18') == 11.25


    def test_calculate_agg_payment(self, calculator, salary):
        agg_payment = calculator('FOO', salary)
        assert agg_payment == 2812.5
        
    def test_convert_payments(self, calculator, salary):
        res = calculator.convert_payments('FOO', salary)
        expected = [
            {'date': '2017-01-20', 'amount': 1000, 'converted_amount': 1125.},
            {'date': '2017-02-20', 'amount': 1500, 'converted_amount': 1687.5}
        ]
        pd.testing.assert_frame_equal(
            pd.DataFrame(res),
            pd.DataFrame(expected)
        )

# ######################################
# # f2555
# ######################################

@pytest.fixture
def rent():
    return [
         {'date': '2017-01-20', 'amount': 650},
         {'date': '2017-02-20', 'amount': 650},
     ]

@pytest.fixture
def dividends():
    return [
         {'date': '2017-01-01', 'amount': 10},
         {'date': '2017-02-01', 'amount': 50},
    ]

@pytest.fixture
def f2555_data(salary, rent, dividends):
        return [
            {'tag': 'rent', 'currency': 'FOO', 'payments': rent},
             {'tag': 'salary', 'currency': 'FOO', 'payments': salary},
             {'tag': 'dividends', 'currency': 'BAR', 'payments': dividends},
        ]
            
class TestF2555:
    '''Tests for form 2555 class F2555'''
    def test_f2555_call(self, rate_converter, f2555_data):

        res = expat_fatcat.f2555(rate_converter, f2555_data)
        assert res.get('rent').get('amount') == 1462.5
        assert res.get('rent').get('currency') == 'FOO'
        assert res.get('salary').get('amount') == 2812.5
        assert res.get('salary').get('currency') == 'FOO'
        assert res.get('dividends').get('amount') == 67.5
        assert res.get('dividends').get('currency') == 'BAR'
