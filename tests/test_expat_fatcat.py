"""Tests for `expat_fatcat` package."""
import pytest
import numpy as np
from datetime import datetime

import pandas as pd

import expat_fatcat
from expat_fatcat.expat_fatcat import DummyRateConverterTo


class TestConverter:

    def test_asymmetric_rate_smoothing(self):
        dates_fx_rates = [
            (datetime(2017, 2, 19), 2.2),
            (datetime(2017, 2, 20), np.nan),
            (datetime(2017, 2, 21), np.nan),
        ]
        converter = DummyRateConverterTo('FOO', dates_fx_rates)
        assert converter.get_rate('FOO', datetime(2017, 2, 19)) == 2.2
        assert converter.get_rate('FOO', datetime(2017, 2, 20)) == 2.2

    def test_symmetric_rate_smoothing(self):
        dates_fx_rates = [
            (datetime(2017, 2, 18), 2.9),
            (datetime(2017, 2, 19), np.nan),
            (datetime(2017, 2, 20), np.nan),
            (datetime(2017, 2, 21), np.nan),
            (datetime(2017, 2, 22), 3.1),
        ]
        converter = DummyRateConverterTo('FOO', dates_fx_rates)
        assert converter.get_rate('FOO', datetime(2017, 2, 20)) == 3.0


@pytest.fixture
def rate_converter():
    return DummyRateConverterTo('USD', [
        (datetime(2019, 4, 18), 1.1),
        (datetime(2017, 1, 20), 1.1),
        (datetime(2017, 2, 20), 1.1),
        (datetime(2017, 1, 1), 1.1),
        (datetime(2017, 2, 1), 1.1)
    ])


@pytest.fixture
def calculator(rate_converter):
    return expat_fatcat.FatcatCalculator(rate_converter)


@pytest.fixture
def salary():
    return [
         {'date': '2017-01-20', 'amount': 1000},
         {'date': '2017-02-20', 'amount': 1500}
    ]


class TestCalculator:
    """
    Tests for the main functionality of rate calculators.
    Excludes edge cases such as missing values, invalid arguments, etc.
    """

    def test_date_conversion(self, calculator):
        assert (
            calculator.parse_date('2019-04-18', '%Y-%m-%d')
            == datetime(2019, 4, 18)
        )

    def test_get_rate(self, calculator):
        rate = calculator.get_rate('FOO', '2019-04-18', '%Y-%m-%d')
        assert rate == 1.1

    def test_get_converted_amount(self, calculator):
        amount = 10.
        assert (calculator.get_converted_amount(
            amount, 'FOO', '2019-04-18', '%Y-%m-%d')
            == pytest.approx(11.)
        )

    def test_calculate_agg_payment(self, calculator, salary):
        agg_payment = calculator(salary, 'FOO', '%Y-%m-%d')
        assert agg_payment == pytest.approx(2750.)

    def test_convert_payments(self, calculator, salary):
        res = calculator.convert_payments(salary, 'FOO', '%Y-%m-%d')
        expected = [
            {'date': '2017-01-20', 'amount': 1000, 'converted_amount': 1100.},
            {'date': '2017-02-20', 'amount': 1500, 'converted_amount': 1650.}
        ]
        pd.testing.assert_frame_equal(
            pd.DataFrame(res),
            pd.DataFrame(expected)
        )

# # ######################################
# # # f2555
# # ######################################


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
        {'tag': 'dividends', 'currency': 'FOO', 'payments': dividends},
    ]


class TestF2555:
    """Tests for form 2555 class F2555"""
    def test_f2555_call(self, rate_converter, f2555_data):

        res = expat_fatcat.f2555(rate_converter, f2555_data, '%Y-%m-%d')
        assert res.get('rent').get('amount') == pytest.approx(1430.)
        assert res.get('rent').get('currency') == 'FOO'
        assert res.get('salary').get('amount') == pytest.approx(2750.)
        assert res.get('salary').get('currency') == 'FOO'
        assert res.get('dividends').get('amount') == pytest.approx(66.)
        assert res.get('dividends').get('currency') == 'FOO'
