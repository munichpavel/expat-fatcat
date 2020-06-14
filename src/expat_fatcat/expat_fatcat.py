"""Main module."""
import os
import warnings
import numpy as np
import pandas as pd

from datetime import datetime, timedelta

from abc import ABC, abstractmethod

import quandl


class FatcatCalculator():
    """Calculate fx rates and other tax related quantities for IRS and FATCA
    compliance"""
    def __init__(self, rate_converter):
        self.rate_converter = rate_converter
        self._check_converter()

    def _check_converter(self):
        if self.rate_converter.to_currency != 'USD':
            raise NotImplementedError(
                'Invalid to_currency: only to USD implemented'
            )

    def convert_payments(self, payments, from_currency, date_format):
        """
        Convert payment history from input currency to rate_converter target
        currency.

        Parameters
        ----------
        from_currency : str
            Currency of payment
        payments : list of dicts

        Returns
        -------
        res : list of dicts
            Payments with extra field for fx converted amount
        """
        res = payments.copy()
        for payment in res:
            payment['converted_amount'] = self.get_converted_amount(
                payment.get('amount'), from_currency, payment.get('date'),
                date_format
            )

        return res

    def get_converted_amount(
        self, amount, from_currency,
        date_string, date_format
    ):
        return self.get_rate(from_currency, date_string, date_format) * amount

    def get_rate(self, from_currency, date_string, date_format):
        date = self.parse_date(date_string, date_format)
        rate = self.rate_converter.get_rate(from_currency, date)
        return rate

    def parse_date(self, date_string, date_format):
        return datetime.strptime(date_string, date_format)

    def __call__(self, payments, from_currency, date_format):

        res = self.convert_payments(payments, from_currency, date_format)
        return pd.DataFrame(res)['converted_amount'].sum()


class AbsRateConverterTo(ABC):
    """Abstract class for conversions to a given currency"""
    def __init__(self, to_currency):
        self.to_currency = to_currency

    def get_rate(self, from_currency, date, offset=0):
        """Returns exchange rate, with smoothing if no fx rate for date"""
        call_str = self._get_call_str(from_currency)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            res = np.nanmean([
                self._rate_api_call(call_str, date + timedelta(offset)),
                self._rate_api_call(call_str, date + timedelta(-offset))
            ])

        if not np.isnan(res):
            return res
        else:
            offset += 1
            return self.get_rate(from_currency, date, offset)

    @abstractmethod
    def _get_call_str(self, from_currency):
        pass

    @abstractmethod
    def _rate_api_call(self, call_str, date):
        pass


class QuandlRateConverterToUSD(AbsRateConverterTo):
    """Get conversion rates to USD from the QUANDL python api"""
    def __init__(self):
        self.to_currency = 'USD'
        self._set_key()

    def _set_key(self):
        if 'QUANDL_KEY' in os.environ:
            quandl.ApiConfig.api_key = os.environ['QUANDL_KEY']

    def _get_call_str(self, from_currency):
        if from_currency == 'EUR':
            return 'ECB/EURUSD'
        elif from_currency == 'GBP':
            return 'FRED/DEXUSUK'
        else:
            raise NotImplementedError(
                'Only EUR and GBP to USD rates are implemented'
            )

    def _rate_api_call(self, call_str, date):
        r = quandl.get(call_str, start_date=date, end_date=date)
        try:
            res = r.iloc[0]['Value']
        except IndexError:
            warnings.warn(
                "Date {} is invalid, trying before and after".format(date)
            )
            res = np.nan

        return res


class DummyRateConverterTo(AbsRateConverterTo):
    """Dummy fx rate converter for testing and development"""
    def __init__(self, to_currency, dates_fx_rates):
        self.to_currency = to_currency
        self._dates_fx_rates = dates_fx_rates

    def _get_call_str(self, from_currency):
        if from_currency == 'FOO':
            return 'ECB/FOO' + self.to_currency
        elif from_currency == 'BAR':
            return 'ECB/BAR' + self.to_currency
        else:
            raise NotImplementedError(
                'Only FOO or BAR to {} rates are implemented'
                .format(self.to_currency)
            )

    def _rate_api_call(self, call_str, date):
        """Returns dummy value for all argument values"""
        return self._lookup_rate(date)

    def _lookup_rate(self, date):
        for r in self._dates_fx_rates:
            if r[0] == date:
                return r[1]


def f2555(rate_converter, data, date_format):
    """
    Calculate total payments in USD for form f2555.

    Parameters
    ----------
    rate_converter : AbsRateConverterTo()
    data : list of dicts with fields tag, currency, payments
    date_format : date format string

    Example usage
    -------------
    >>> converter = DummyRateConverterTo('USD')
    >>> data = [
    ...     {'tag': 'salary', 'currency': 'FOO',
    ...      'payments':  [
    ...          {'date': '2017-01-20', 'amount': 1000},
    ...          {'date': '2017-02-20', 'amount': 1500}
    ...      ]},
    ...     {'tag': 'dividends', 'currency': 'BAR',
    ...      'payments': [
    ...          {'date': '2017-01-01', 'amount': 10},
    ...          {'date': '2017-02-01', 'amount': 50}
    ...      ]}
    ... ]
    >>> f2555(converter, data, '%Y-%m-%d')
    {'salary': {'currency': 'FOO', 'amount': 2812.5}, 'dividends':
    {'currency': 'BAR', 'amount': 67.5}}
    """
    calculator = FatcatCalculator(rate_converter)
    res = {}
    for d in data:
        res[d['tag']] = {
            'currency': d['currency'],
            'amount': calculator(d['payments'], d['currency'], date_format)
        }

    return res
