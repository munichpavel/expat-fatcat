"""Tests for `expat_fatcat` package."""

import pytest
from datetime import datetime

import expat_fatcat
from expat_fatcat.expat_fatcat import DummyRateConverterTo

@pytest.fixture
def rate_converter():
    return DummyRateConverterTo('USD')

@pytest.fixture
def salary():
    return [
         {'date': '2017-01-20', 'amount': 1000},
         {'date': '2017-02-20', 'amount': 1500}
    ]

@pytest.fixture
def calculator(rate_converter):
    return expat_fatcat.FatcatCalculator(rate_converter)

class TestCalculatorBasics:
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
